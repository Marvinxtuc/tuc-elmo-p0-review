import { isP0Offline } from "../constants";
import type { Provider, StructuredResearchOptions, StructuredResearchResult } from "./types";

export function guardProvider(provider: Provider): Provider {
	const run = provider.run.bind(provider);
	provider.run = async (...args) => {
		if (isP0Offline()) throw new Error("P0 offline policy blocks direct provider requests");
		return run(...args);
	};
	const research = provider.runStructuredResearch;
	if (research) {
		provider.runStructuredResearch = async <T>(
			options: StructuredResearchOptions<T>,
		): Promise<StructuredResearchResult<T>> => {
			if (isP0Offline()) throw new Error("P0 offline policy blocks direct research requests");
			return research<T>(options);
		};
	}
	return provider;
}
