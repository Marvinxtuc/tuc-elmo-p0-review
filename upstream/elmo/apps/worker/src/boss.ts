import { isP0Offline } from "@workspace/lib/constants";
import { PgBoss } from "pg-boss";

let boss: PgBoss | undefined;

// Built on first use rather than at import so startup env validation runs first.
export function getBoss(): PgBoss {
	boss ??= new PgBoss({
		connectionString: process.env.DATABASE_URL,
		schema: "pgboss",
		...(isP0Offline() ? { migrate: false, supervise: false, schedule: false } : {}),
		maintenanceIntervalSeconds: 30,
	});
	return boss;
}
