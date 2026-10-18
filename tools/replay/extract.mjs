// usage: node extract.mjs <assets_dir> <replay.repl26a> <out.json>
// Loads a replay into the visualiser's wasm engine and dumps one omniscient
// snapshot per round (plus every step's event kind) as JSON.
import fs from 'fs';
import path from 'path';
import { pathToFileURL } from 'url';

const [assets, replayPath, outPath] = process.argv.slice(2);
const PC = await import(pathToFileURL(path.join(assets, 'PanelChrome-DDwagTqG.js')).href);
const readHeader = PC.P, readFull = PC.F, OMNI = PC.T, ITEM_NAMES = PC.B ?? null;

async function load(version) {
  let mem;
  const dec = new TextDecoder();
  const out = { s: '' };
  const wasi = {
    random_get(p, n) { new Uint8Array(mem.buffer, p, n).fill(7); return 0; },
    clock_time_get(id, _p, r) { new DataView(mem.buffer).setBigUint64(r, 0n, true); return 0; },
    environ_sizes_get(a, b) { const d = new DataView(mem.buffer); d.setUint32(a, 0, true); d.setUint32(b, 0, true); return 0; },
    environ_get() { return 0; },
    args_sizes_get(a, b) { const d = new DataView(mem.buffer); d.setUint32(a, 0, true); d.setUint32(b, 0, true); return 0; },
    args_get() { return 0; },
    fd_close() { return 0; },
    fd_fdstat_get(fd, p) { const d = new DataView(mem.buffer); d.setUint8(p, 2); d.setUint16(p + 2, 0, true); d.setBigUint64(p + 8, 0n, true); d.setBigUint64(p + 16, 0n, true); return 0; },
    fd_prestat_get() { return 8; }, fd_prestat_dir_name() { return 8; },
    fd_read(fd, a, b, n) { new DataView(mem.buffer).setUint32(n, 0, true); return 0; },
    fd_seek() { return 70; },
    fd_write(fd, iov, cnt, nw) {
      const d = new DataView(mem.buffer); let c = 0;
      for (let i = 0; i < cnt; i++) { const p = d.getUint32(iov + i * 8, true), l = d.getUint32(iov + i * 8 + 4, true); out.s += dec.decode(new Uint8Array(mem.buffer, p, l)); c += l; }
      d.setUint32(nw, c, true); return 0;
    },
    proc_exit(c) { throw Error('exit ' + c); },
  };
  const bytes = fs.readFileSync(path.join(assets, version + '.wasm'));
  const { instance } = await WebAssembly.instantiate(bytes, {
    wasi_snapshot_preview1: wasi,
    deep_wasm: { on_assert_fail_impl() { return 1; } },
  });
  mem = instance.exports.memory;
  instance.exports._initialize();
  return instance.exports;
}

function run(x) {
  const dv = () => new DataView(x.memory.buffer);
  const outBuf = x.Engine_Malloc(32);
  const check = (rc) => {
    if (rc === 0) return;
    const p = x.GetLastErrorMsg(); const u = new Uint8Array(x.memory.buffer); let e = p; while (u[e]) e++;
    throw Error('engine ' + rc + ': ' + new TextDecoder().decode(u.subarray(p, e)));
  };
  const rb = fs.readFileSync(replayPath);
  const rp = x.Engine_Malloc(rb.length);
  new Uint8Array(x.memory.buffer, rp, rb.length).set(rb);
  check(x.Game_FromReplayFileBytes(rp, rb.length, outBuf));
  const h = dv().getBigUint64(outBuf, true);
  const snap = x.Engine_Malloc(x.Game_Visualiser_SnapshotSize());
  const args = x.Engine_Malloc(128);
  const persp = args + 48;
  check(x.Game_Visualiser_Timeline_GetMain(h, outBuf));
  const tl = dv().getBigUint64(outBuf, true);
  check(x.Game_Visualiser_Timeline_Info(h, tl, args, args + 8, args + 16));
  const size = dv().getUint32(args, true);
  check(x.Game_Visualiser_Timeline_Seek(h, tl, 0, 0));
  const read = () => {
    const d = dv(); d.setUint32(persp, OMNI.team, true); d.setUint32(persp + 4, OMNI.champion, true);
    check(x.Game_Visualiser_ReadState(h, persp, snap));
    return { header: readHeader(dv(), snap), full: readFull(dv(), snap) };
  };
  const rounds = []; const events = [];
  let last = -1, guard = 0, prev = null;
  for (;;) {
    const { header, full } = read();
    events.push([header.round, header.step.kind, header.step.actor.kind, header.step.actor.index, header.step.from.x, header.step.from.y, header.step.to.x, header.step.to.y, header.step.abilitySlot ?? -1]);
    if (header.round !== last) { rounds.push({ ...full, _h: header }); last = header.round; }
    prev = { header, full };
    if (header.outcome || (header.awaitingInput && header.inputPosition >= size)) break;
    check(x.Game_Visualiser_Timeline_ReplayNext(h, 1));
    if (++guard > 5e6) throw Error('no end');
  }
  rounds.push({ ...prev.full, _h: prev.header, final: true });
  return { size, rounds, events };
}

let res, err;
for (const v of ['v0_0_3', 'v0_0_2', 'v0_0_1']) {
  try { res = run(await load(v)); res.version = v; break; } catch (e) { err = e; }
}
if (!res) { console.error('FAILED', replayPath, err.message); process.exit(1); }
fs.writeFileSync(outPath, JSON.stringify(res, (k, v) => typeof v === 'bigint' ? Number(v) : v));
console.log(path.basename(path.dirname(replayPath)), res.version, 'rounds', res.rounds.length, 'events', res.events.length);
