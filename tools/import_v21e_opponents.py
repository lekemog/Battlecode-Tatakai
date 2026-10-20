#!/usr/bin/env python3
"""Import only frozen public opponent source blobs, never platform submissions."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT/'research/v21e-candidates/opponents.json'

def blob_sha(data):
    return hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--verify-only', action='store_true')
    args = parser.parse_args()
    count = 0
    for repo in json.loads(MANIFEST.read_text()):
        for f in repo['files']:
            relative = Path(f['local'])
            if relative.is_absolute() or '..' in relative.parts or relative.parts[:2] != ('bots', repo['name']) or relative.suffix not in {'.cpp','.h','.hpp'}:
                raise ValueError(f'unsafe source path: {relative}')
            target = ROOT/relative
            if target.exists():
                installed = target.read_bytes()
                # The measured connector/apply_patch import added exactly one final LF.
                if installed.endswith(b'\n') and blob_sha(installed[:-1]) == f['sha']:
                    count += 1
                    continue
                raise RuntimeError(f'{relative}: differs from measured snapshot; preserve it and use a clean checkout')
            if args.verify_only:
                raise RuntimeError(f'{relative}: missing')
            result = subprocess.run(['gh', 'api', f"repos/{repo['repo']}/git/blobs/{f['sha']}"],
                check=True, text=True, capture_output=True)
            data = base64.b64decode(json.loads(result.stdout)['content'])
            if blob_sha(data) != f['sha']:
                raise RuntimeError(f'{relative}: upstream blob hash mismatch')
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data+b'\n')
            count += 1
    print(f'{count} frozen opponent source files verified')

if __name__ == '__main__':
    main()

