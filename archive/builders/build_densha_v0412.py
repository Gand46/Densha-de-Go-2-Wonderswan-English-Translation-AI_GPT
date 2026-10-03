#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
import hashlib, json, sys
import numpy as np
from PIL import Image, ImageDraw
ROOT=Path('/mnt/data')
BASE=ROOT/'Densha_de_Go_2_EN_v0.4.11.ws'
OUT=ROOT/'Densha_de_Go_2_EN_v0.4.12.ws'
DELTA=ROOT/'Densha_de_Go_2_EN_v0.4.12_from_v0.4.11.ips'
CUM_BASE=ROOT/'Densha_de_Go_2_EN_v0.4.11_package'/'Densha_de_Go_2_EN_v0.4.11.ips'
CUM=ROOT/'Densha_de_Go_2_EN_v0.4.12.ips'
WORK=ROOT/'densha_v0412_work'; PREV=WORK/'previews'; REP=WORK/'reports'; RUNTIME=WORK/'runtime'
for d in (WORK,PREV,REP,RUNTIME): d.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(ROOT/'Densha_de_Go_2_EN_v0.4.11_package'/'tools'))
import build_densha_v0410 as prev
dec_stream=prev.dec_stream; compress_ws=prev.compress_ws; tiles_arrays=prev.tiles_arrays
text_canvas=prev.text_canvas; put_canvas=prev.put_canvas; ips_create=prev.ips_create; ips_apply=prev.ips_apply
ips_write_map=prev.ips_write_map; map_to_ips=prev.map_to_ips; PALETTE=prev.PALETTE
ATLAS_OFF=0x028537
BLOCK={'name':'stop_position','jp':'停止位置','en':'STOP POS','top':106,'cols':6,'font':'5x7'}
def sha(b): return hashlib.sha256(b).hexdigest()
def inds(top,cols): return list(range(top,top+cols))+list(range(top+cols,top+2*cols))
def canvas(raw,top,cols):
 a=tiles_arrays(raw); c=np.zeros((16,cols*8),dtype=np.uint8)
 for r in range(2):
  for x in range(cols): c[r*8:(r+1)*8,x*8:(x+1)*8]=a[top+r*cols+x]
 return c
def render(c,p,scale=8): Image.fromarray(PALETTE[c],mode='L').resize((c.shape[1]*scale,c.shape[0]*scale),Image.Resampling.NEAREST).save(p)
def main():
 base=BASE.read_bytes(); assert len(base)==4194304
 raw,cons=dec_stream(base,ATLAS_OFF); assert len(raw)==2816
 old=canvas(raw,BLOCK['top'],BLOCK['cols']); new=text_canvas(BLOCK['en'],BLOCK['cols']*8,BLOCK['font'])
 after=put_canvas(raw,BLOCK['top'],BLOCK['cols'],new); target=set(inds(BLOCK['top'],BLOCK['cols']))
 ba=tiles_arrays(raw); aa=tiles_arrays(after); changed=[i for i,(x,y) in enumerate(zip(ba,aa)) if not np.array_equal(x,y)]
 assert set(changed)==target,(changed,sorted(target))
 assert all(np.array_equal(x,y) for i,(x,y) in enumerate(zip(ba,aa)) if i not in target)
 packed=compress_ws(after); check,used=dec_stream(packed,0); assert check==after and used==len(packed); assert len(packed)<=cons
 rom=bytearray(base); rom[ATLAS_OFF:ATLAS_OFF+len(packed)]=packed
 if len(packed)<cons: rom[ATLAS_OFF+len(packed):ATLAS_OFF+cons]=b'\0'*(cons-len(packed))
 rom[-2:]=b'\0\0'; checksum=sum(rom[:-2])&0xffff; rom[-2:]=checksum.to_bytes(2,'little'); final=bytes(rom); OUT.write_bytes(final)
 fr,fu=dec_stream(final,ATLAS_OFF); assert fr==after and fu==len(packed)
 diffs=[i for i,(x,y) in enumerate(zip(base,final)) if x!=y]
 unexpected=[i for i in diffs if not(ATLAS_OFF<=i<ATLAS_OFF+cons or i>=len(final)-2)]; assert not unexpected
 delta=ips_create(base,final); DELTA.write_bytes(delta); assert ips_apply(base,delta)==final
 cm=ips_write_map(CUM_BASE.read_bytes()); dm=ips_write_map(delta); cm.update(dm); cumulative=map_to_ips(cm); CUM.write_bytes(cumulative)
 cm2=ips_write_map(cumulative); oldm=ips_write_map(CUM_BASE.read_bytes()); assert all(cm2[k]==v for k,v in dm.items()); assert all(cm2[k]==v for k,v in oldm.items() if k not in dm)
 render(old,PREV/'V0412_stop_position_before.png'); render(new,PREV/'V0412_stop_position_after.png')
 scale=8; w=max(old.shape[1],new.shape[1])*scale; h=old.shape[0]*scale
 out=Image.new('RGB',(w*2+32,h+30),'white'); d=ImageDraw.Draw(out); d.text((4,4),'v0.4.11 JP',fill='black');d.text((w+20,4),'v0.4.12 EN',fill='black')
 for x,c in [(4,old),(w+20,new)]: out.paste(Image.fromarray(PALETTE[c],mode='L').resize((c.shape[1]*scale,c.shape[0]*scale),Image.Resampling.NEAREST).convert('RGB'),(x,24))
 out.save(PREV/'V0412_stop_position_before_after.png')
 report={'version':'0.4.12','base_version':'0.4.11','resource':'0x028537 shared evaluation atlas','translation':BLOCK,'changed_tiles':changed,'changed_tile_count':len(changed),'non_target_tiles_byte_identical':True,'atlas_decompressed_bytes':2816,'old_compressed_bytes':cons,'new_compressed_bytes':len(packed),'free_bytes_vs_v0411_allocation':cons-len(packed),'rom_bytes':len(final),'rom_sha256':sha(final),'checksum_stored':f'0x{int.from_bytes(final[-2:],"little"):04X}','checksum_calculated':f'0x{sum(final[:-2])&0xffff:04X}','changed_bytes_vs_v0411':len(diffs),'unexpected_changes':0,'incremental_ips':{'bytes':len(delta),'sha256':sha(delta),'reapplication_exact':True},'cumulative_ips':{'bytes':len(cumulative),'sha256':sha(cumulative),'composition_verified':True,'direct_original_reapplication':'not_retested_original_rom_absent'},'runtime_validation':'pending'}
 (REP/'V0412_BINARY_VALIDATION.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8'); (REP/'V0412_ATLAS_PATCH_MANIFEST.json').write_text(json.dumps({'block':BLOCK,'changed_tiles':changed},ensure_ascii=False,indent=2)+'\n',encoding='utf-8'); print(json.dumps(report,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
