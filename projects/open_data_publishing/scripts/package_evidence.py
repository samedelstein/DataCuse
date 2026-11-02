"""Preserve fetched evidence with a checksum manifest, without publishing raw folders."""
import datetime as dt
import hashlib
import json
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data'
files = sorted([* (DATA / 'raw').glob('*'), * (DATA / 'research').glob('*')])
files = [file for file in files if file.is_file()]
manifest = {'packaged_at': dt.datetime.now(dt.timezone.utc).isoformat(), 'files': []}
destination = DATA / 'snapshots' / 'evidence-20261027.zip'
destination.parent.mkdir(exist_ok=True)
with zipfile.ZipFile(destination, 'w', zipfile.ZIP_DEFLATED) as archive:
    for file in files:
        content = file.read_bytes()
        name = file.relative_to(DATA).as_posix()
        archive.writestr(name, content)
        manifest['files'].append({'path': name, 'bytes': len(content), 'sha256': hashlib.sha256(content).hexdigest()})
    archive.writestr('manifest.json', json.dumps(manifest, indent=2))
print(f'Preserved {len(files)} responses in {destination.name} ({destination.stat().st_size:,} bytes)')
