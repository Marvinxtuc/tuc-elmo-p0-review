export function isP0Offline(): boolean {
	if (typeof process === "undefined") return true;
	const policy = (globalThis as Record<symbol, { stage?: string } | undefined>)[Symbol.for("tuc.p0.policy-loaded")];
	return process.env.TUC_P0_STAGE !== "quality" || policy?.stage !== "quality" || process.env.TUC_P0_OFFLINE !== "0";
}

export function assertP0Runtime(): void {
	const policy = (globalThis as Record<symbol, unknown>)[Symbol.for("tuc.p0.policy-loaded")];
	if (
		!policy ||
		process.env.RUNS_PER_PROMPT !== "1" ||
		process.env.DEPLOYMENT_MODE !== "local" ||
		process.env.TUC_P0_STAGE !== "runtime" ||
		process.env.TUC_P0_OFFLINE !== "1" ||
		process.env.SCRAPE_TARGETS !== "stub:stub" ||
		process.env.ONBOARDING_LLM_TARGET !== "stub:stub" ||
		process.env.TYPESAFE_API_KEY !== "stub"
	) {
		throw new Error("P0 runtime requires the enforced offline launcher and stub configuration");
	}
}

export const RUNS_PER_PROMPT_FALLBACK = 5;

/**
 * Answers vary between identical calls, so sampling several makes a mention rate
 * a measurement, at that multiple of provider spend. Outside cloud only; cloud
 * takes it from the plan. Server-only.
 */
export function getRunsPerPrompt(): number {
	const raw = typeof process !== "undefined" ? process.env.RUNS_PER_PROMPT : undefined;
	if (!raw) return RUNS_PER_PROMPT_FALLBACK;
	const parsed = Number(raw);
	if (!Number.isInteger(parsed) || parsed < 1) return RUNS_PER_PROMPT_FALLBACK;
	return parsed;
}

export const DEFAULT_DELAY_HOURS_FALLBACK = 24;

/** Server-only; client code reads clientConfig.defaultDelayHours. */
export function getDefaultDelayHours(): number {
	const raw = typeof process !== "undefined" ? process.env.DEFAULT_DELAY_HOURS : undefined;
	if (!raw) return DEFAULT_DELAY_HOURS_FALLBACK;
	const parsed = Number(raw);
	if (!Number.isFinite(parsed) || parsed <= 0) return DEFAULT_DELAY_HOURS_FALLBACK;
	return parsed;
}

export const MAX_COMPETITORS = 500;
export const MAX_PROMPTS = 100;

export const PROMPT_SUGGESTION_RUNS_PER_DAY = 5;

/** For a search that happened but whose query strings the provider withholds. Fan-out reads filter it out. */
export const WEB_QUERIES_UNAVAILABLE = "unavailable";
