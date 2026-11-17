import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

root = Path(__file__).resolve().parents[1]
run = root / Path(json.loads((root / 'config/active-run.json').read_text())['path'])
runtime = Path(json.loads((root / 'config/local-runtime.json').read_text())['runtime_root'])
env = dict(os.environ, DOCKER_HOST=f'unix://{runtime}/colima/tuc-p0/docker.sock', DOCKER_CONFIG=str(runtime / 'docker-client'))
container = 'tuc-elmo-p0-postgres'
def docker(*args):
    return subprocess.check_output(['/opt/homebrew/bin/docker', *args], env=env)
def sql(database, query):
    if database not in ['tuc_elmo_p0_test', 'tuc_elmo_p0_restore']: raise ValueError('database outside scope')
    return docker('exec', container, 'psql', '-X', '-U', 'tuc_p0', '-d', database, '-At', '-c', query).decode().strip()
operation = sys.argv[1]
if operation == 'backup':
    folder = root / 'runtime/restore-backups'
    folder.mkdir(mode=0o700, parents=True, exist_ok=True)
    records = []
    for database in ['tuc_elmo_p0_test', 'tuc_elmo_p0_restore']:
        data = docker('exec', container, 'pg_dump', '-U', 'tuc_p0', '-Fc', database)
        target = folder / f'{database}-before-b1.dump'
        with target.open('xb') as stream: stream.write(data)
        target.chmod(0o600)
        records.append(dict(database=database, bytes=len(data), sha256=hashlib.sha256(data).hexdigest()))
    (run / 'restore-backups.redacted.json').write_text(json.dumps(records, indent=2)+'\n')
elif operation == 'snapshot':
    label = sys.argv[2]
    result = {'at_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'databases': {}}
    for database in ['tuc_elmo_p0_test', 'tuc_elmo_p0_restore']:
        tables = sql(database, "SELECT tablename FROM pg_tables WHERE schemaname='public' ORDER BY tablename").splitlines()
        hashes = {}
        for table in tables:
            quoted = '"' + table.replace('"', '""') + '"'
            digest = sql(database, f"SELECT json_build_object('rows',count(*),'md5',md5(coalesce(string_agg(to_jsonb(t)::text,E'\\n' ORDER BY to_jsonb(t)::text),''))) FROM public.{quoted} t")
            hashes[table] = json.loads(digest)
        jobs = json.loads(sql(database, "SELECT coalesce(json_agg(t ORDER BY t.id),'[]') FROM (SELECT id,name,state,retry_count,data FROM pgboss.job) t"))
        result['databases'][database] = {'public_tables':hashes,'jobs':jobs,
            'schedules': json.loads(sql(database,"SELECT coalesce(json_agg(t),'[]') FROM pgboss.schedule t"))}
    (run / f'database-{label}.json').write_text(json.dumps(result,indent=2)+'\n')
elif operation == 'tunnel':
    state = json.loads(docker('inspect', container))[0]
    assert state['HostConfig']['Memory'] <= 6 * 1024**3
    networks = state['NetworkSettings']['Networks']
    assert set(networks) == {'tuc-elmo-p0_internal'}
    assert state['HostConfig']['PortBindings'] == {'5432/tcp': [{'HostIp': '127.0.0.1', 'HostPort': '17332'}]}
    ip = networks['tuc-elmo-p0_internal']['IPAddress']
    log = (run / 'logs/database-tunnel.log').open('x')
    command = ['/usr/bin/ssh','-F',str(runtime/'lima/colima-tuc-p0/ssh.config'),'-o','ControlMaster=no',
        '-o','ControlPath=none','-o','ExitOnForwardFailure=yes','-N','-L',f'127.0.0.1:17332:{ip}:5432','lima-colima-tuc-p0']
    process = subprocess.Popen(command,cwd='/tmp',stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
    (run/'tunnel-process.json').write_text(json.dumps({'pid':process.pid,'command':command},indent=2)+'\n')
    print(json.dumps({'pid':process.pid,'local_port':17332,'container_ip':ip}))
else:
    raise SystemExit('unknown operation')
