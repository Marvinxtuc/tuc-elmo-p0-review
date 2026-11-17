import { afterEach, describe, expect, it, vi } from "vitest";
import { z } from "zod";
import { isP0Offline } from "./constants";
import { createMentionAnalyzer } from "./mention-judge/analyze";
import { typesafeTransport } from "./mention-judge/jev";
import { getProvider } from "./providers";
import { structuredResearch } from "./providers/registry/ai-sdk";
import { openaiApi } from "./providers/registry/openai-api";

afterEach(() => vi.unstubAllEnvs());

describe("P0 offline request policy", () => {
	it("defaults to offline and ignores an unapproved off flag outside quality checks", () => {
		vi.stubEnv("TUC_P0_STAGE", undefined);
		vi.stubEnv("TUC_P0_OFFLINE", undefined);
		expect(isP0Offline()).toBe(true);
		vi.stubEnv("TUC_P0_OFFLINE", "0");
		expect(isP0Offline()).toBe(true);
		expect(() => getProvider("openai-api")).toThrow("blocks non-stub");
	});

	it("blocks a directly imported adapter and judge before their transports run", async () => {
		vi.stubEnv("TUC_P0_OFFLINE", "1");
		const transport = vi.fn();
		await expect(openaiApi.run("chatgpt", "synthetic prompt")).rejects.toThrow("direct provider");
		await expect(
			typesafeTransport("synthetic-account-a", transport)({ model: "fixture", state: {}, questions: {} }),
		).rejects.toThrow("direct judge");
		expect(transport).not.toHaveBeenCalled();
	});
	it("allows the upstream stub and rejects real provider selection", () => {
		vi.stubEnv("TUC_P0_OFFLINE", "1");
		expect(getProvider("stub").id).toBe("stub");
		expect(() => getProvider("openai-api")).toThrow("blocks non-stub providers");
		expect(() => getProvider("openrouter")).toThrow("blocks non-stub providers");
	});

	it("rejects real judge credentials and fallback selection in offline mode", () => {
		vi.stubEnv("TUC_P0_OFFLINE", "1");
		expect(() => createMentionAnalyzer("synthetic-canary", () => undefined)).toThrow("requires the stub judge");
		expect(() => createMentionAnalyzer(undefined, () => "synthetic-canary")).toThrow("requires the stub judge");
		expect(createMentionAnalyzer("stub", () => "synthetic-canary").judgeVersion).toBe("stub+request-1");
	});

	it("allows configured provider objects in the transport-isolated quality stage", () => {
		vi.stubEnv("TUC_P0_OFFLINE", "0");
		expect(getProvider("openai-api").id).toBe("openai-api");
		expect(getProvider("openrouter").id).toBe("openrouter");
	});
});

describe("SDK retry policy", () => {
	it("exposes default SDK retries with a fake transport and disables them explicitly", async () => {
		const { default: Anthropic } = await import("@anthropic-ai/sdk");
		const request = {
			model: "synthetic-model",
			max_tokens: 1,
			messages: [{ role: "user" as const, content: "synthetic" }],
		};
		for (const maxRetries of [undefined, 0]) {
			const fetch = vi.fn(async () =>
				Response.json(
					{ type: "error", error: { type: "rate_limit_error", message: "synthetic" } },
					{ status: 429, headers: { "retry-after-ms": "1" } },
				),
			);
			const client = new Anthropic({
				apiKey: "synthetic-account-a",
				fetch,
				...(maxRetries === undefined ? {} : { maxRetries }),
			});
			await expect(client.messages.create(request)).rejects.toThrow();
			expect(fetch).toHaveBeenCalledTimes(maxRetries === 0 ? 1 : 3);
		}
	});
});

it("rejects direct structured research before constructing a model request", async () => {
	vi.stubEnv("TUC_P0_OFFLINE", "1");
	await expect(structuredResearch("synthetic-model", { prompt: "synthetic", schema: z.object({}) })).rejects.toThrow(
		"direct structured research",
	);
});
