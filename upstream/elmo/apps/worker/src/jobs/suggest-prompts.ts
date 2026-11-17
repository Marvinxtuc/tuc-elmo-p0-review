import { isP0Offline } from "@workspace/lib/constants";
import { type OnboardingPrompt, type SuggestPromptsOptions, suggestPrompts } from "@workspace/lib/onboarding";
import type { Job } from "pg-boss";

export interface SuggestPromptsData extends SuggestPromptsOptions {
	brandId: string;
}

export interface SuggestPromptsResult {
	prompts: OnboardingPrompt[];
}

export async function suggestPromptsJob(jobs: Job<SuggestPromptsData>[]): Promise<SuggestPromptsResult> {
	if (isP0Offline()) throw new Error("P0 rejects unapproved generation jobs before side effects");
	const [job] = jobs;
	if (!job) {
		throw new Error("suggest-prompts handler received an empty batch");
	}

	return { prompts: await suggestPrompts(job.data) };
}
