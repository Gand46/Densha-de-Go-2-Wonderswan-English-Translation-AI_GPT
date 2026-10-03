#!/usr/bin/env python3
"""Build v0.4.17: repair result-heading glyphs; original JP ROM is the sole ROM input."""
from pathlib import Path
import sys,json,hashlib
from codec import dec_stream,compress_ws
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'vendor'))
from ws_patch_tools import ips,bps
sha=lambda b:hashlib.sha256(b).hexdigest()
JP='3ec68e02fa964383d6a0792aca7e53ab005e17a768a8546eb6dc5ed482db7c29'
PREV='643363ab9f8d5c466a0e01ca14b22a4c8e65d76c7a5bb927139ec8e755a45f3b'
def main():
 orig=(Path(sys.argv[1]) if len(sys.argv)>1 else ROOT/'original/Densha_de_Go_2_Japan.ws').read_bytes();assert sha(orig)==JP and len(orig)==4194304
 base=ips.apply(orig,(ROOT/'assets/baseline_v0416_cumulative.ips').read_bytes());assert sha(base)==PREV
 rom=bytearray(base);font=json.loads((ROOT/'assets/font5x7.json').read_text());allowed=set();changes=[]
 for off,jp,text in [(0x3D61C0,'運転終了','RUN ENDED'),(0x3D63E8,'運転中止','RUN ABORTED')]:
  raw,oldsize=dec_stream(base,off);_,capacity=dec_stream(orig,off);assert len(raw)==1152
  # Consumer is twelve tiles wide. Only its first two rows contain the heading.
  # Clear all 24 heading tiles; preserve GAME OVER and all unused rows byte for byte.
  pixels=[[0]*96 for _ in range(16)];points=[];x=(96-(len(text)*6-1))//2
  for ch in text:
   if ch!=' ':
    for y,line in enumerate(font[ch]):
     for dx,v in enumerate(line):
      if v=='1':points.append((x+dx,4+y))
   x+=6
  # Consumer palette 5: index 1 is dark, 2 is the light outline, 0 is background.
  for x,y in points:
   for dy in (-1,0,1):
    for dx in (-1,0,1):
     if 0<=x+dx<96 and 0<=y+dy<16:pixels[y+dy][x+dx]=2
  for x,y in points:pixels[y][x]=1
  new=bytearray(raw)
  for tile in range(24):
   tx=tile%12*8;ty=tile//12*8;buf=bytearray()
   for y in range(8):
    row=pixels[ty+y][tx:tx+8];buf.extend([sum(((v&1)!=0)<<(7-i) for i,v in enumerate(row)),sum(((v&2)!=0)<<(7-i) for i,v in enumerate(row))])
   new[tile*16:(tile+1)*16]=buf
  new=bytes(new);assert new[384:]==raw[384:]
  packed=compress_ws(new);assert len(packed)<=capacity and dec_stream(packed,0)==(new,len(packed))
  rom[off:off+len(packed)]=packed;allowed.update(range(off,off+len(packed)))
  changes.append({'source_jp':jp,'en':text,'stream':hex(off),'original_capacity':capacity,'before_compressed':oldsize,'after_compressed':len(packed),'raw_bytes':len(new),'heading_tiles':list(range(24)),'remaining_48_tiles_unchanged':True,'reason':'Replace malformed inherited English heading with coherent 5x7 glyphs, using the actual consumer palette.'})
  (ROOT/'assets'/f'{text.replace(" ","_")}_v0417.raw').write_bytes(new)
 rom[-2:]=(sum(rom[:-2])&65535).to_bytes(2,'little');allowed.update([len(rom)-2,len(rom)-1]);rom=bytes(rom)
 diffs=[i for i,(a,b) in enumerate(zip(base,rom)) if a!=b];unexpected=[i for i in diffs if i not in allowed];assert not unexpected
 (ROOT/'roms/Densha_de_Go_2_EN_v0.4.17.ws').write_bytes(rom);patches=[]
 for label,source in [('CUMULATIVE',orig),('from_v0.4.16_INCREMENTAL',base)]:
  for ext,lib in [('bps',bps),('ips',ips)]:
   patch=lib.create(source,rom);assert lib.apply(source,patch)==rom
   name=f'Densha_de_Go_2_EN_v0.4.17_{label}.{ext}';(ROOT/'patches'/name).write_bytes(patch);patches.append({'name':name,'bytes':len(patch),'sha256':sha(patch),'roundtrip_exact':True})
 rep={'version':'0.4.17','rom_sha256':sha(rom),'original_sha256':sha(orig),'previous_sha256':sha(base),'rom_bytes':len(rom),'checksum':hex(int.from_bytes(rom[-2:],'little')),'changed_bytes_from_v0416':len(diffs),'unexpected_offsets':unexpected,'changes':changes,'patches':patches,'gameplay_code_unchanged':base[0x3e0000:-2]==rom[0x3e0000:-2]}
 (ROOT/'reports/BUILD_VALIDATION.json').write_text(json.dumps(rep,indent=2,ensure_ascii=False));print(json.dumps(rep,indent=2,ensure_ascii=False))
if __name__=='__main__':main()
