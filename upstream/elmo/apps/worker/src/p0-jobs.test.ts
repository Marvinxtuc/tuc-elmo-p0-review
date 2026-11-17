import { afterEach, expect, it, vi } from "vitest";
import { assertP0Job } from "./p0-jobs";

afterEach(() => vi.unstubAllEnvs());

it("refuses legacy and model jobs, including jobs carrying the current batch identity", () => {
	vi.stubEnv("TUC_P0_OFFLINE", "1");
	vi.stubEnv("TUC_P0_BATCH_ID", "synthetic-batch");
	expect(() => assertP0Job("process-prompt", { p0BatchId: "synthetic-batch" })).toThrow("outside");
	expect(() => assertP0Job("refresh-rollups", {})).toThrow("outside");
	expect(() => assertP0Job("refresh-rollups", { p0BatchId: "old-batch" })).toThrow("outside");
	expect(() => assertP0Job("refresh-rollups", { p0BatchId: "synthetic-batch" })).not.toThrow();
});
