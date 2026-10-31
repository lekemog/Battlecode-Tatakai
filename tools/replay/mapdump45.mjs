// #45: dump walls and altars of the map embedded in a replay.
// usage: node mapdump45.mjs <visualiser_assets_dir> <engine wasm file name, e.g. v2_0_0-hWOQ1R8f.wasm> <replay.repl26a>
// prints {W,H,wall:[rows],altar:[rows]} as JSON ('1' = set).
import fs from 'fs'; import path from 'path';
const [assets, wasmName, replayPath] = process.argv.slice(2);
let mem; const dec = new TextDecoder();
const wasi = { random_get(p,n){new Uint8Array(mem.buffer,p,n).fill(7);return 0}, clock_time_get(i,_p,r){new DataView(mem.buffer).setBigUint64(r,0n,true);return 0},
 environ_sizes_get(a,b){const d=new DataView(mem.buffer);d.setUint32(a,0,true);d.setUint32(b,0,true);return 0}, environ_get(){return 0},
 args_sizes_get(a,b){const d=new DataView(mem.buffer);d.setUint32(a,0,true);d.setUint32(b,0,true);return 0}, args_get(){return 0}, fd_close(){return 0},
 fd_fdstat_get(fd,p){const d=new DataView(mem.buffer);d.setUint8(p,2);return 0}, fd_prestat_get(){return 8}, fd_prestat_dir_name(){return 8},
 fd_read(fd,a,b,n){new DataView(mem.buffer).setUint32(n,0,true);return 0}, fd_seek(){return 70},
 fd_write(fd,iov,cnt,nw){const d=new DataView(mem.buffer);let c=0;for(let i=0;i<cnt;i++){c+=d.getUint32(iov+i*8+4,true)}d.setUint32(nw,c,true);return 0}, proc_exit(c){throw Error('exit '+c)} };
const { instance } = await WebAssembly.instantiate(fs.readFileSync(path.join(assets,wasmName)), { wasi_snapshot_preview1: wasi, deep_wasm: { on_assert_fail_impl(){return 1} } });
const x = instance.exports; mem = x.memory; x._initialize();
const out = x.Engine_Malloc(64); const dv=()=>new DataView(mem.buffer);
const chk=(rc,w)=>{ if(rc!==0){const p=x.GetLastErrorMsg();const u=new Uint8Array(mem.buffer);let e=p;while(u[e])e++;throw Error(w+' rc '+rc+': '+dec.decode(u.subarray(p,e)))} };
const rb=fs.readFileSync(replayPath); const rp=x.Engine_Malloc(rb.length); new Uint8Array(mem.buffer,rp,rb.length).set(rb);
chk(x.Game_FromReplayFileBytes(rp,rb.length,out),'load'); const h=dv().getBigUint64(out,true);
chk(x.Game_GetBitboardMetadata(h,out),'meta'); const W=dv().getInt32(out,true), H=dv().getInt32(out+4,true);
const res={W,H,sig:{wall:x.Game_GetWall.length,altar:x.Game_GetAltar.length},wall:[],altar:[]};
for (const [k,f] of [['wall',x.Game_GetWall],['altar',x.Game_GetAltar]]) {
  for (let y=0;y<H;y++){ let row=''; for(let xx=0;xx<W;xx++){ dv().setUint32(out,0,true); const rc=f(h,xx,y,out); if(rc!==0) chk(rc,k); row+= dv().getUint8(out)?'1':'0'; } res[k].push(row); }
}
console.log(JSON.stringify(res));
