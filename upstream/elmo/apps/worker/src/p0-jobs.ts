import { isP0Offline } from "@workspace/lib/constants";
import { REFRESH_ROLLUPS_QUEUE } from "@workspace/lib/rollups/constants";
import type { PgBoss } from "pg-boss";

export function assertP0Job(name: string, data: unknown): void {
	if (!isP0Offline()) return;
	const batch = process.env.TUC_P0_BATCH_ID;
	if (
		!batch ||
		name !== REFRESH_ROLLUPS_QUEUE ||
		typeof data !== "object" ||
		data === null ||
		!("p0BatchId" in data) ||
		data.p0BatchId !== batch
	) {
		throw new Error("P0 job is outside the approved finite batch");
	}
}

export async function quarantineP0Jobs(boss: PgBoss): Promise<void> {
	let afterQueue: string | undefined;
	for (;;) {
		const queues = await boss.getQueues(undefined, { limit: 100, after: afterQueue });
		if (queues.length === 0) break;
		for (const queue of queues) {
			await quarantineQueue(boss, queue.name);
		}
		afterQueue = queues.at(-1)?.name;
	}
}

async function quarantineQueue(boss: PgBoss, name: string): Promise<void> {
	await boss.unschedule(name);
	let afterJob: string | undefined;
	for (;;) {
		const jobs = await boss.findJobs(name, { limit: 100, after: afterJob });
		if (jobs.length === 0) break;
		for (const job of jobs) {
			if (!["created", "retry", "active"].includes(job.state)) continue;
			try {
				assertP0Job(name, job.data);
			} catch {
				await boss.cancel(name, job.id);
				console.log(JSON.stringify({ event: "P0_JOB_QUARANTINED", queue: name, id: job.id, state: job.state }));
			}
		}
		afterJob = jobs.at(-1)?.id;
	}
}
