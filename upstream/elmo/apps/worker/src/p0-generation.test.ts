import { afterEach, expect, it, vi } from "vitest";
import { analyzeBrandJob } from "./jobs/analyze-brand";
import { deriveRunsJob } from "./jobs/derive-runs";
import { generateReportJob } from "./jobs/generate-report";
import { processPromptJob } from "./jobs/process-prompt";
import { reprocessJob, requestReprocessesJob } from "./jobs/reprocess";
import { suggestPromptsJob } from "./jobs/suggest-prompts";

const writes = vi.hoisted(() => ({ insert: vi.fn(), update: vi.fn(), delete: vi.fn(), transaction: vi.fn() }));
vi.mock("@workspace/lib/db/db", () => ({ db: writes }));
afterEach(() => vi.unstubAllEnvs());

it("rejects direct onboarding, prompt suggestion and report jobs before database writes", async () => {
	vi.stubEnv("TUC_P0_OFFLINE", "1");
	for (const run of [
		analyzeBrandJob,
		generateReportJob,
		suggestPromptsJob,
		processPromptJob,
		deriveRunsJob,
		reprocessJob,
	]) {
		await expect(run([])).rejects.toThrow("before side effects");
	}
	await expect(requestReprocessesJob()).rejects.toThrow("before side effects");
	for (const write of Object.values(writes)) expect(write).not.toHaveBeenCalled();
});
