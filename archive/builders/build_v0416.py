#!/usr/bin/env python3
"""Reproduce v0.4.16 from the hash-locked Japanese ROM, without patch chains."""
from pathlib import Path
import hashlib,json,sys
from codec import dec_stream,compress_ws
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'vendor'))
from ws_patch_tools import ips,bps
SHA_JP='3ec68e02fa964383d6a0792aca7e53ab005e17a768a8546eb6dc5ed482db7c29'
SHA_PREV='fb9df07a3d3478158ea38b0fdeb6b567e2aa0cd825d35918b7a8dd9d5c9b4490'
sha=lambda b:hashlib.sha256(b).hexdigest()
def main():
 original_path=Path(sys.argv[1]) if len(sys.argv)>1 else ROOT/'original/Densha_de_Go_2_Japan.ws'
 original=original_path.read_bytes();assert len(original)==4194304 and sha(original)==SHA_JP,'Wrong Japanese source ROM'
 baseline=ips.apply(original,(ROOT/'assets/baseline_v0415_cumulative.ips').read_bytes());assert sha(baseline)==SHA_PREV
 rom=bytearray(baseline);manifest=[];allowed=set()
 # EASY: ten tiles within the options atlas, top row 67..71, bottom 83..87.
 off=0x3D5D07;raw,old_size=dec_stream(baseline,off);original_raw,capacity=dec_stream(original,off)
 assert len(raw)==2560 and baseline[off-2:off]==b'\x00\xc0'
 newraw=bytearray(raw)
 font=json.loads((ROOT/'assets/font5x7.json').read_text());canvas=[[0]*40 for _ in range(16)]
 text='EASY';x=(40-(5*len(text)+len(text)-1))//2;y=4
 for ch in text:
  for gy,line in enumerate(font[ch]):
   for gx,bit in enumerate(line):
    if bit=='1':canvas[y+gy][x+gx]=3
  x+=6
 targets=list(range(67,72))+list(range(83,88))
 for row,top in [(0,67),(1,83)]:
  for col in range(5):
   tile=bytearray()
   for gy in range(8):
    line=canvas[row*8+gy][col*8:col*8+8]
    plane=sum((1<<(7-gx)) for gx,v in enumerate(line) if v)
    tile.extend([plane,plane])
   newraw[(top+col)*16:(top+col+1)*16]=tile
 newraw=bytes(newraw)
 assert all(newraw[i*16:(i+1)*16]==raw[i*16:(i+1)*16] for i in range(160) if i not in targets)
 packed=compress_ws(newraw);assert dec_stream(packed,0)==(newraw,len(packed))
 assert len(packed)<=capacity
 rom[off:off+len(packed)]=packed;allowed.update(range(off,off+capacity))
 manifest.append({'id':'W16-001','jp':'イージー','en':'EASY','stream':hex(off),'descriptor_index':0,'raw_bytes':len(raw),'modified_local_tiles':targets,'original_capacity':capacity,'previous_compressed':old_size,'new_compressed':len(packed),'unchanged_other_tiles':150,'runtime_load':'WRAM 0x2010','consumer_tilemap':['0x1960..0x1968','0x19A0..0x19A8']})
 # English typo inherited from the Japanese release. OAM descriptor E -> O.
 credit=0x3E2BD2;assert rom[credit:credit+4]==bytes.fromhex('05 0c 68 50')
 rom[credit]=15;allowed.add(credit)
 manifest.append({'id':'W16-002','source':'COORDINATER','en':'COORDINATOR','offset':hex(credit),'old':5,'new':15,'consumer':'E000:BE14 writes AX to WRAM OAM 0x0EF8 from ES:DI = 3000:2BD2','sprite_position':[80,104],'shared_font_changed':False})
 # GAMESTART -> START centered in the same 9-cell field. No layout or navigation changes.
 instruction=0x3F587B;old_values=[0x870,0x86b,0x876,0x877,0x868,0x86a,0x86b,0x86c,0x86a]
 new_values=[0x800,0x800,0x868,0x86a,0x86b,0x86c,0x86a,0x800,0x800];changes=[]
 for i,(before,after) in enumerate(zip(old_values,new_values)):
  at=instruction if i==0 else instruction+4+(i-1)*5
  prefix=b'\xc7\x07' if i==0 else bytes([0xc7,0x47,2*i])
  assert bytes(rom[at:at+len(prefix)])==prefix
  pos=at+len(prefix);assert int.from_bytes(rom[pos:pos+2],'little')==before
  rom[pos:pos+2]=after.to_bytes(2,'little');allowed.update([pos,pos+1]);changes.append({'offset':hex(pos),'before':hex(before),'after':hex(after)})
 manifest.append({'id':'W16-003','source':'GAMESTART','en':'START','reason':'Natural start command; centered using the existing glyphs within the existing button.','tilemap_start':'0x1AC8','opcode_and_displacements_unchanged':True,'changes':changes})
 rom[-2:]=(sum(rom[:-2])&65535).to_bytes(2,'little');allowed.update([len(rom)-2,len(rom)-1]);final=bytes(rom)
 diffs=[i for i,(a,b) in enumerate(zip(baseline,final)) if a!=b];unexpected=[i for i in diffs if i not in allowed];assert not unexpected
 assert dec_stream(final,off)[0]==newraw
 out=ROOT/'roms';out.mkdir(exist_ok=True);(out/'Densha_de_Go_2_EN_v0.4.16.ws').write_bytes(final)
 patches=ROOT/'patches';patches.mkdir(exist_ok=True);patch_records=[]
 for label,source in [('CUMULATIVE',original),('from_v0.4.15_INCREMENTAL',baseline)]:
  for ext,lib in [('bps',bps),('ips',ips)]:
   patch=lib.create(source,final);assert lib.apply(source,patch)==final
   name=f'Densha_de_Go_2_EN_v0.4.16_{label}.{ext}';(patches/name).write_bytes(patch)
   patch_records.append({'name':name,'sha256':sha(patch),'bytes':len(patch),'roundtrip_exact':True})
 report={'version':'0.4.16','original_sha256':sha(original),'previous_sha256':sha(baseline),'rom_sha256':sha(final),'rom_bytes':len(final),'checksum_stored':hex(int.from_bytes(final[-2:],'little')),'checksum_calculated':hex(sum(final[:-2])&65535),'changed_bytes_from_v0415':len(diffs),'unexpected_offsets':unexpected,'changes':manifest,'patches':patch_records}
 (ROOT/'reports/BUILD_VALIDATION.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
 (ROOT/'assets/options_atlas_v0416.raw').write_bytes(newraw)
 print(json.dumps(report,indent=2,ensure_ascii=False))
if __name__=='__main__':main()
