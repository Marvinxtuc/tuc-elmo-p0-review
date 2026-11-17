import pg from '../upstream/elmo/packages/lib/node_modules/pg/lib/index.js';
const client = new pg.Client({ connectionString: process.env.DATABASE_URL, connectionTimeoutMillis: 3000 });
try {
  await client.connect();
  const result = await client.query('SELECT current_database() AS database,count(*)::integer AS runs FROM prompt_runs');
  console.log(JSON.stringify(result.rows));
} finally {
  await client.end();
}
