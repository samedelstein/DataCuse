"""Collect candidate metadata and source files, then validate known extracts."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys
import requests

from catalog import collect, write
from extract import run

ROOT = Path(__file__).resolve().parents[1]

def refresh(output, documents_only=False):
    if not documents_only:
        collect(output, ROOT / 'data/catalog.json')
    elif not (output / 'report.json').exists() or not (output / 'catalog.json').exists():
        raise ValueError('A collected candidate is required before a document-only retry.')
    manifest = json.loads((ROOT / 'sources/manifest.json').read_text(encoding='utf-8'))
    docs, changes = [], []
    for old in manifest:
        current = dict(old, checked_at=datetime.now(timezone.utc).isoformat())
        try:
            # Use the same ordinary HTTP client as initial document collection.
            # The city CDN rejects the custom metadata crawler user agent.
            response = requests.get(old['download'], timeout=60)
            response.raise_for_status()
            blob = response.content
            current['sha256'] = hashlib.sha256(blob).hexdigest()
            path = output / 'source-files' / old['local_file']
            path.parent.mkdir(parents=True,exist_ok=True)
            path.write_bytes(blob)
            current.update(http_status=200,bytes=len(blob))
            changes.append({'file':old['local_file'],'change':'unchanged' if current['sha256']==old['sha256'] else 'checksum-changed','before':old['sha256'],'after':current['sha256']})
            docs.append(current)
        except (OSError, requests.RequestException) as exc:
            changes.append({'file':old['local_file'],'change':'unavailable','error':str(exc),'approved_data':'preserved'})
    write(output / 'downloads.json',docs)
    report = json.loads((output / 'report.json').read_text(encoding='utf-8'))
    report['document_changes'] = changes
    failed = len(docs) != len(manifest)
    try:
        if not failed:
            run(output/'source-files', output/'downloads.json',output/'extracts')
    except (ValueError,AssertionError) as exc:
        report['extraction_error'] = str(exc)
        failed = True
    report['status'] = 'review-required' if failed else 'candidate-ready-for-review'
    report['publication'] = 'No approved files changed. Compare report and sources before copying candidate outputs.'
    write(output / 'report.json',report)
    return 1 if failed else 0

if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',type=Path,default=ROOT/'candidate')
    parser.add_argument('--documents-only',action='store_true',help='Retry documents against an existing candidate inventory.')
    args=parser.parse_args()
    sys.exit(refresh(args.output,args.documents_only))
