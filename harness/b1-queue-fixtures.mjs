import { createRequire } from 'node:module';
import { readFileSync, writeFileSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const require = createRequire(path.join(root, 'upstream/elmo/apps/worker/package.json'));
const { PgBoss } = require('pg-boss');
const { Client } = require('pg');
const client = new Client({ connectionString: process.env.DATABASE_URL });
const boss = new PgBoss({ connectionString: process.env.DATABASE_URL, migrate: false, supervise: false, schedule: false });
const run = path.resolve(root, JSON.parse(readFileSync(path.join(root,'config/active-run.json'))).path);
const privateFile = path.join(root,'runtime/restore-backups/brand-before-fixture.json');
const action = process.argv[2];
try {
  await client.connect();
  if (action === 'seed') {
    const brands = (await client.query('SELECT id,aliases,analysis_versions,enabled FROM brands ORDER BY id')).rows;
    const competitors = (await client.query('SELECT id,aliases FROM competitors ORDER BY id')).rows;
    writeFileSync(privateFile, JSON.stringify({ brands, competitors }), { flag:'wx', mode:0o600 });
    await client.query("UPDATE brands SET aliases=array_append(aliases,'synthetic-b1-alias'),analysis_versions='{}'::jsonb,enabled=false");
    await client.query("UPDATE competitors SET aliases=array_append(aliases,'synthetic-b1-competitor')");
    await client.query('UPDATE brands SET enabled=true');
    await boss.start();
    const ids = [];
    for (const name of ['process-prompt','derive-runs','reprocess','request-reprocesses','rollup-catch-up']) {
      ids.push({ name, id: await boss.send(name, { brandId: brands[0].id, p0BatchId: process.env.TUC_P0_BATCH_ID,
        aliases: ['synthetic-b1-alias'], judgeVersion:'synthetic-new-judge', source:'B1_TEST_FIXTURE' }) });
    }
    const active = await boss.send('process-prompt',{ source:'B1_TEST_FIXTURE', fixtureState:'active' });
    const retry = await boss.send('process-prompt',{ source:'B1_TEST_FIXTURE', fixtureState:'retry' });
    await client.query("UPDATE pgboss.job SET state='active' WHERE id=$1",[active]);
    await client.query("UPDATE pgboss.job SET state='retry' WHERE id=$1",[retry]);
    ids.push({ name:'process-prompt', id:active },{ name:'process-prompt', id:retry });
    writeFileSync(path.join(run,'queue-fixtures.json'),JSON.stringify({ action, ids, modified_brand_count:brands.length,
      modified_competitor_count:competitors.length, mutation:'aliases/competitors/analysis_versions/disable-reenable' },null,2));
    console.log(JSON.stringify({ action, fixture_jobs:ids.length, brands:brands.length, competitors:competitors.length }));
  } else if (action === 'competitor') {
    const brand = (await client.query('SELECT id FROM brands ORDER BY id LIMIT 1')).rows[0];
    const result = await client.query("INSERT INTO competitors(id,brand_id,name,domains,aliases) VALUES('11111111-1111-4111-8111-111111111111',$1,'Synthetic B1 Competitor',ARRAY['synthetic.invalid'],ARRAY['synthetic-initial']) RETURNING id",[brand.id]);
    await client.query("UPDATE competitors SET aliases=ARRAY['synthetic-changed'] WHERE id=$1",[result.rows[0].id]);
    writeFileSync(path.join(run,'competitor-fixture.json'),JSON.stringify({id:result.rows[0].id,synthetic:true,retained_for_audit:true,alias_changed:true}));
    console.log(JSON.stringify({action,fixture_created:true,alias_changed:true}));
  } else if (action === 'rollup') {
    await boss.start();
    const id = await boss.send('refresh-rollups',{ source:'B1_TEST_FIXTURE',p0BatchId:process.env.TUC_P0_BATCH_ID });
    writeFileSync(path.join(run,'tagged-rollup.json'),JSON.stringify({ id, batch:process.env.TUC_P0_BATCH_ID }));
    console.log(JSON.stringify({ action,id }));
  } else if (action === 'restore-config') {
    const previous = JSON.parse(readFileSync(privateFile));
    await client.query('BEGIN');
    for (const brand of previous.brands) await client.query('UPDATE brands SET aliases=$2,analysis_versions=$3,enabled=$4 WHERE id=$1',
      [brand.id,brand.aliases,brand.analysis_versions,brand.enabled]);
    for (const competitor of previous.competitors) await client.query('UPDATE competitors SET aliases=$2 WHERE id=$1',[competitor.id,competitor.aliases]);
    await client.query('COMMIT');
    console.log(JSON.stringify({ action,restored:true }));
  } else throw new Error('unknown action');
} finally {
  await boss.stop();
  await client.end();
}
