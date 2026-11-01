// #55 (from mapxform45.mjs): also accepts non-square maps (3 transforms: flip x, flip y, rotate 180); square maps get all 7.
// #45: write flipped/rotated copies of a square map (e.g. 02the-pack) so a deterministic local match-up
// can be replayed on several equivalent boards (the seed comes from the map, so each copy is a new game).
// Only for maps with ROTATIONAL180 symmetry: every dihedral transform commutes with it, so team B's
// spawn (derived from the symmetry) stays the mirror of team A's.
// usage: node mapxform45.mjs <visualiser_assets_dir> <engine wasm, e.g. v2_0_0-hWOQ1R8f.wasm> <in.map26a> <out_dir>
// writes <name>-x<k>.map26a for k = 1..7 (k = 0 is the original).
import fs from 'fs';
import path from 'path';

const [assets, wasmName, inPath, outDir] = process.argv.slice(2);
let mem;
const dec = new TextDecoder();
const wasi = {
  random_get(p, n) { new Uint8Array(mem.buffer, p, n).fill(7); return 0; },
  clock_time_get(i, _p, r) { new DataView(mem.buffer).setBigUint64(r, 0n, true); return 0; },
  environ_sizes_get(a, b) { const d = new DataView(mem.buffer); d.setUint32(a, 0, true); d.setUint32(b, 0, true); return 0; },
  environ_get() { return 0; },
  args_sizes_get(a, b) { const d = new DataView(mem.buffer); d.setUint32(a, 0, true); d.setUint32(b, 0, true); return 0; },
  args_get() { return 0; }, fd_close() { return 0; },
  fd_fdstat_get(fd, p) { new DataView(mem.buffer).setUint8(p, 2); return 0; },
  fd_prestat_get() { return 8; }, fd_prestat_dir_name() { return 8; },
  fd_read(fd, a, b, n) { new DataView(mem.buffer).setUint32(n, 0, true); return 0; }, fd_seek() { return 70; },
  fd_write(fd, iov, cnt, nw) { const d = new DataView(mem.buffer); let c = 0; for (let i = 0; i < cnt; i++) c += d.getUint32(iov + i * 8 + 4, true); d.setUint32(nw, c, true); return 0; },
  proc_exit(c) { throw Error('exit ' + c); },
};
const { instance } = await WebAssembly.instantiate(fs.readFileSync(path.join(assets, wasmName)),
  { wasi_snapshot_preview1: wasi, deep_wasm: { on_assert_fail_impl() { return 1; } } });
const x = instance.exports; mem = x.memory; x._initialize();
const out = x.Engine_Malloc(64);
const dv = () => new DataView(mem.buffer);
const chk = (rc, what) => {
  if (rc === 0) return;
  const p = x.GetLastErrorMsg(); const u = new Uint8Array(mem.buffer); let e = p; while (u[e]) e++;
  throw Error(`${what}: rc ${rc} ${dec.decode(u.subarray(p, e))}`);
};

function load() {
  const b = fs.readFileSync(inPath); const p = x.Engine_Malloc(b.length);
  new Uint8Array(mem.buffer, p, b.length).set(b);
  chk(x.MapBuilder_FromFileBytes(p, b.length, out), 'load');
  return dv().getBigUint64(out, true);
}

const probe = load();
chk(x.MapBuilder_GetBitboardMetadata(probe, out), 'meta');
const W = dv().getInt32(out, true), H = dv().getInt32(out + 4, true);
chk(x.MapBuilder_GetSymmetry(probe, out), 'symmetry');
const sym = dv().getInt32(out, true);
const SQUARE = W === H;
if (sym !== 2) throw Error('map symmetry is not ROTATIONAL180 (' + sym + ')');
x.MapBuilder_Destroy(probe);

// The 8 dihedral transforms of a W x W board.
const T = [
  (a, b) => [a, b], (a, b) => [W - 1 - a, b], (a, b) => [a, H - 1 - b], (a, b) => [W - 1 - a, H - 1 - b],
  (a, b) => [b, a], (a, b) => [W - 1 - b, a], (a, b) => [b, W - 1 - a], (a, b) => [W - 1 - b, W - 1 - a],
];
const tiles = (h, getter) => {
  const r = [];
  for (let yy = 0; yy < H; yy++) for (let xx = 0; xx < W; xx++) {
    dv().setUint32(out, 0, true);
    chk(getter(h, xx, yy, out), 'get tile');
    if (dv().getUint8(out)) r.push([xx, yy]);
  }
  return r;
};

fs.mkdirSync(outDir, { recursive: true });
const name = path.basename(inPath).replace(/\.map26a$/, '');
for (let k = 1; k < (SQUARE ? 8 : 4); k++) {
  const h = load();
  const f = T[k];
  // Terrain: collect, clear, re-add transformed.
  for (const [get, rem, add] of [
    [x.MapBuilder_GetBush, x.MapBuilder_RemoveBush, x.MapBuilder_AddBush],
    [x.MapBuilder_GetWall, x.MapBuilder_RemoveWall, x.MapBuilder_AddWall],
    [x.MapBuilder_GetHole, x.MapBuilder_RemoveHole, x.MapBuilder_AddHole],
    [x.MapBuilder_GetAltar, x.MapBuilder_RemoveAltar, x.MapBuilder_AddAltar],
  ]) {
    const set = tiles(h, get);
    for (const [a, b] of set) chk(rem(h, a, b), 'remove tile');
    for (const [a, b] of set) { const [c, d] = f(a, b); chk(add(h, c, d), 'add tile'); }
  }
  // Camps: the map stores one camp of each mirrored pair (the engine adds the ROTATIONAL180 mirror).
  // Move each stored camp to its transformed tile; its mirror follows (transforms commute with the
  // symmetry). Handles are looked up by tile before every move because moves can re-index them.
  chk(x.MapBuilder_GetNumCamps(h, out), 'numCamps');
  const n = dv().getUint32(out, true);
  const rot = (a, b) => [W - 1 - a, H - 1 - b];
  const camps = [];
  for (let i = 0; i < n; i++) {
    chk(x.MapBuilder_GetCampHandle(h, i, out), 'camp handle');
    const ch = dv().getBigUint64(out, true);
    chk(x.MapBuilder_GetCamp(h, ch, out), 'get camp');
    camps.push({ id: i, type: dv().getInt32(out, true), x: dv().getInt32(out + 4, true), y: dv().getInt32(out + 8, true) });
  }
  const owner = new Map();  // tile -> camp id (stored tile and its mirror)
  const claim = (c) => { owner.set(c.x + ',' + c.y, c.id); const m = rot(c.x, c.y); owner.set(m[0] + ',' + m[1], c.id); };
  const release = (c) => { owner.delete(c.x + ',' + c.y); const m = rot(c.x, c.y); owner.delete(m[0] + ',' + m[1]); };
  camps.forEach(claim);
  const free = (c, a, b) => { const o1 = owner.get(a + ',' + b), m = rot(a, b), o2 = owner.get(m[0] + ',' + m[1]); return (o1 === undefined || o1 === c.id) && (o2 === undefined || o2 === c.id); };
  const move = (c, a, b, what) => {
    chk(x.MapBuilder_GetCampHandleAt(h, c.x, c.y, out), 'handle at ' + c.x + ',' + c.y);
    const ch = dv().getBigUint64(out, true);
    chk(x.MapBuilder_SetCamp(h, ch, c.type, a, b), what);
    release(c); c.x = a; c.y = b; claim(c);
  };
  let pending = camps.map(c => ({ c, to: f(c.x, c.y) })).filter(e => !(e.to[0] === e.c.x && e.to[1] === e.c.y));
  for (let guard = 0; pending.length && guard < 10 * n; guard++) {
    const next = [];
    let moved = false;
    for (const e of pending) {
      if (!free(e.c, e.to[0], e.to[1])) { next.push(e); continue; }
      move(e.c, e.to[0], e.to[1], 'set camp');
      moved = true;
    }
    if (!moved && next.length) {  // a cycle: park one camp on a free tile pair, retry its move later
      const e = next[0];
      let park = null;
      for (let yy = 0; yy < H && !park; yy++) for (let xx = 0; xx < W && !park; xx++) {
        const m = rot(xx, yy);
        const own = (xx === e.c.x && yy === e.c.y) || (m[0] === e.c.x && m[1] === e.c.y);
        const targeted = next.some(o => (o.to[0] === xx && o.to[1] === yy) || (o.to[0] === m[0] && o.to[1] === m[1]));
        if (!(m[0] === xx && m[1] === yy) && !own && !targeted && free(e.c, xx, yy)) park = [xx, yy];
      }
      move(e.c, park[0], park[1], 'park camp');
    }
    pending = next;
  }
  if (pending.length) throw Error('could not place all camps: ' + JSON.stringify(pending.slice(0, 6).map(e => [e.c.x, e.c.y, e.to])));
  // Team A spawn rectangle.
  chk(x.MapBuilder_GetTeamASpawnArea(h, out), 'spawn');
  const s = [dv().getInt32(out, true), dv().getInt32(out + 4, true), dv().getInt32(out + 8, true), dv().getInt32(out + 12, true)];
  const p1 = f(s[0], s[1]), p2 = f(s[2], s[3]);
  dv().setInt32(out, Math.min(p1[0], p2[0]), true); dv().setInt32(out + 4, Math.min(p1[1], p2[1]), true);
  dv().setInt32(out + 8, Math.max(p1[0], p2[0]), true); dv().setInt32(out + 12, Math.max(p1[1], p2[1]), true);
  chk(x.MapBuilder_SetTeamASpawnArea(h, out), 'set spawn');
  chk(x.MapBuilder_VerifyIntegrity(h), 'verify');
  chk(x.MapBuilder_Encode(h, out, out + 4), 'encode');
  const ptr = dv().getUint32(out, true), len = dv().getUint32(out + 4, true);
  fs.writeFileSync(path.join(outDir, `${name}-x${k}.map26a`), Buffer.from(new Uint8Array(mem.buffer, ptr, len)));
  console.log(`${name}-x${k}.map26a`, len, 'bytes', camps.length, 'camps', 'spawnA', [Math.min(p1[0], p2[0]), Math.min(p1[1], p2[1]), Math.max(p1[0], p2[0]), Math.max(p1[1], p2[1])]);
  x.MapBuilder_Destroy(h);
}
