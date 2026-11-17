import { afterEach, describe, expect, it, vi } from "vitest";
import { createMentionAnalyzer } from "./mention-judge/analyze";
import { getProvider } from "./providers";

afterEach(() => vi.unstubAllEnvs());

describe("P0 offline request policy", () => {
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

	it("preserves configured provider availability outside the isolated mode", () => {
		vi.stubEnv("TUC_P0_OFFLINE", "");
		expect(getProvider("openai-api").id).toBe("openai-api");
		expect(getProvider("openrouter").id).toBe("openrouter");
	});
});
