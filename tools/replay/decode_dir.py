"""decode_dir.py IN_DIR OUT_DIR [JOBS] : decode every .repl26a (platform downloads and lab bundles are zips holding replay.repl26a)
in IN_DIR to OUT_DIR/<name>.json with extract5.mjs (engine 3). Skips files already decoded."""
import concurrent.futures as cf
import glob
import io
import os
import subprocess
import sys
import tempfile
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = glob.glob(os.path.expanduser('~/.cache/cambc/assets/*/visualiser/assets'))[0]


def one(path, out_dir):
    name = os.path.basename(path)[:-len('.repl26a')]
    out = os.path.join(out_dir, name + '.json')
    if os.path.exists(out) and os.path.getsize(out) > 0:
        return name, 'cached'
    data = open(path, 'rb').read()
    if data[:2] == b'PK':
        data = zipfile.ZipFile(io.BytesIO(data)).read('replay.repl26a')
    with tempfile.NamedTemporaryFile(suffix='.repl26a') as t:
        t.write(data); t.flush()
        r = subprocess.run(['node', os.path.join(HERE, 'extract5.mjs'), ASSETS, t.name, out], capture_output=True, text=True)
    return name, 'ok' if r.returncode == 0 else 'FAILED ' + r.stderr[-200:]


def main():
    src, dst = sys.argv[1], sys.argv[2]
    jobs = int(sys.argv[3]) if len(sys.argv) > 3 else 4
    os.makedirs(dst, exist_ok=True)
    files = sorted(glob.glob(os.path.join(src, '*.repl26a')))
    with cf.ThreadPoolExecutor(jobs) as ex:
        for name, st in ex.map(lambda p: one(p, dst), files):
            if st != 'cached':
                print(name, st, flush=True)


if __name__ == '__main__':
    main()
