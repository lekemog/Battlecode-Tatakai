// Extract the embedded .map26a from a .repl26a replay and validate it with the engine's MapBuilder.
const fs = require('fs');
const { load } = require('./engine.js');
const [wasm, replay, outPath] = process.argv.slice(2);
const E = load(wasm);
const all = fs.readFileSync(replay);
const start = all.indexOf(Buffer.from('w62pam'));
if (start < 0) throw new Error('no embedded map');

function tryParse(buf) {
  const p = E.bytesIn(buf);
  const code = E.ex.MapBuilder_FromFileBytes(p, buf.length, E.out);
  E.ex.Engine_Free(p);
  return code === 0 ? E.handle() : null;
}

// Find the shortest prefix the parser accepts, then re-encode it canonically.
let handle = null;
for (let len = 64; len <= all.length - start && !handle; len++) handle = tryParse(all.subarray(start, start + len));
if (!handle) throw new Error('parser rejected every prefix');
E.check(E.ex.MapBuilder_VerifyIntegrity(handle), 'verify');
E.check(E.ex.MapBuilder_Encode(handle, E.out, E.out + 4), 'encode');
const p = E.u32(E.out), n = E.u32(E.out + 4);
fs.writeFileSync(outPath, Buffer.from(new Uint8Array(E.ex.memory.buffer, p, n)));
E.check(E.ex.MapBuilder_GetBitboardMetadata(handle, E.out), 'meta');
console.log(JSON.stringify({ outPath, bytes: n, w: E.i32(E.out), h: E.i32(E.out + 4) }));
