#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
import csv, hashlib, json, sys
import numpy as np
from PIL import Image, ImageDraw

ROOT=Path('/mnt/data')
BASEPKG=ROOT/'Densha_de_Go_2_EN_v0.4.12_package'
BASE=BASEPKG/'Densha_de_Go_2_EN_v0.4.12.ws'
OUT=ROOT/'Densha_de_Go_2_EN_v0.4.13.ws'
DELTA=ROOT/'Densha_de_Go_2_EN_v0.4.13_from_v0.4.12.ips'
CUM_BASE=BASEPKG/'Densha_de_Go_2_EN_v0.4.12.ips'
CUM=ROOT/'Densha_de_Go_2_EN_v0.4.13.ips'
WORK=ROOT/'densha_v0413_build'; PREV=WORK/'previews'; REP=WORK/'reports'; RUNTIME=WORK/'runtime'
for d in (WORK,PREV,REP,RUNTIME): d.mkdir(parents=True,exist_ok=True)

sys.path.insert(0,str(BASEPKG/'tools'))
import build_densha_v0410 as h

dec_stream=h.dec_stream; compress_ws=h.compress_ws; tiles_arrays=h.tiles_arrays
arrays_to_data=h.arrays_to_data; text_canvas=h.text_canvas; put_canvas=h.put_canvas
ips_create=h.ips_create; ips_apply=h.ips_apply; ips_write_map=h.ips_write_map; map_to_ips=h.map_to_ips
PALETTE=h.PALETTE
ATLAS_OFF=0x028537
BLOCK={'name':'signal_ignored','jp':'信号無視','en':'SIGNAL IGNORED','top':148,'cols':9,'font':'5x7'}
# Proven code consumer in ROM: mov ax,0x06D4 (tile 212 = atlas base 64 + local 148),
# mov bx,0x1182, mov cx,0x0209 (2 rows x 9 cols), call tilemap copier.
CONSUMER_OFF=0x3F56E9
CONSUMER_BYTES=bytes.fromhex('B8 D4 06 BB 82 11 B9 09 02')
SEPARATOR_LOCAL_TILE=166

def sha(b:bytes)->str: return hashlib.sha256(b).hexdigest()
def block_indices(top:int,cols:int)->list[int]: return list(range(top,top+cols))+list(range(top+cols,top+2*cols))
def canvas(raw:bytes,top:int,cols:int)->np.ndarray:
    a=tiles_arrays(raw); c=np.zeros((16,cols*8),dtype=np.uint8)
    for r in range(2):
        for x in range(cols): c[r*8:(r+1)*8,x*8:(x+1)*8]=a[top+r*cols+x]
    return c

def render(c:np.ndarray,p:Path,scale:int=8)->None:
    Image.fromarray(PALETTE[c],mode='L').resize((c.shape[1]*scale,c.shape[0]*scale),Image.Resampling.NEAREST).save(p)

def main()->None:
    base=BASE.read_bytes(); assert len(base)==4194304
    assert base[CONSUMER_OFF:CONSUMER_OFF+len(CONSUMER_BYTES)]==CONSUMER_BYTES, 'consumer signature changed'
    raw,cons=dec_stream(base,ATLAS_OFF); assert len(raw)==2816
    arr_before=tiles_arrays(raw)
    separator_before=arr_before[SEPARATOR_LOCAL_TILE].copy()
    old=canvas(raw,BLOCK['top'],BLOCK['cols'])
    new=text_canvas(BLOCK['en'],BLOCK['cols']*8,BLOCK['font'])
    after=put_canvas(raw,BLOCK['top'],BLOCK['cols'],new)
    arr_after=tiles_arrays(after)
    target=set(block_indices(BLOCK['top'],BLOCK['cols']))
    changed=[i for i,(x,y) in enumerate(zip(arr_before,arr_after)) if not np.array_equal(x,y)]
    assert set(changed)==target,(changed,sorted(target))
    assert SEPARATOR_LOCAL_TILE not in target
    assert np.array_equal(arr_after[SEPARATOR_LOCAL_TILE],separator_before), 'shared separator tile 166 changed'
    for i,(x,y) in enumerate(zip(arr_before,arr_after)):
        if i not in target: assert np.array_equal(x,y),f'non-target tile {i} changed'
    packed=compress_ws(after); check,used=dec_stream(packed,0); assert check==after and used==len(packed); assert len(packed)<=cons
    rom=bytearray(base); rom[ATLAS_OFF:ATLAS_OFF+len(packed)]=packed
    if len(packed)<cons: rom[ATLAS_OFF+len(packed):ATLAS_OFF+cons]=b'\0'*(cons-len(packed))
    rom[-2:]=b'\0\0'; checksum=sum(rom[:-2])&0xffff; rom[-2:]=checksum.to_bytes(2,'little'); final=bytes(rom); OUT.write_bytes(final)
    fr,fu=dec_stream(final,ATLAS_OFF); assert fr==after and fu==len(packed)
    assert final[CONSUMER_OFF:CONSUMER_OFF+len(CONSUMER_BYTES)]==CONSUMER_BYTES
    diffs=[i for i,(x,y) in enumerate(zip(base,final)) if x!=y]
    unexpected=[i for i in diffs if not(ATLAS_OFF<=i<ATLAS_OFF+cons or i>=len(final)-2)]; assert not unexpected
    delta=ips_create(base,final); DELTA.write_bytes(delta); assert ips_apply(base,delta)==final
    cm=ips_write_map(CUM_BASE.read_bytes()); dm=ips_write_map(delta); cm.update(dm); cumulative=map_to_ips(cm); CUM.write_bytes(cumulative)
    # Verify the composed cumulative preserves every delta byte in the map.
    cm2=ips_write_map(cumulative); assert all(cm2[k]==v for k,v in dm.items())
    # previews
    render(old,PREV/'V0413_signal_ignored_before.png'); render(new,PREV/'V0413_signal_ignored_after.png')
    scale=8; w=max(old.shape[1],new.shape[1])*scale; hh=old.shape[0]*scale
    out=Image.new('RGB',(w*2+36,hh+34),'white'); d=ImageDraw.Draw(out)
    d.text((5,4),'v0.4.12 JP',fill='black'); d.text((w+24,4),'v0.4.13 EN',fill='black')
    for x,c in ((5,old),(w+24,new)):
        im=Image.fromarray(PALETTE[c],mode='L').resize((c.shape[1]*scale,c.shape[0]*scale),Image.Resampling.NEAREST).convert('RGB'); out.paste(im,(x,24))
    out.save(PREV/'V0413_signal_ignored_before_after.png')
    h.render_atlas(after,PREV/'V0413_atlas_after.png',scale=4,labels=False)
    report={
      'version':'0.4.13','base_version':'0.4.12','resource':'0x028537 shared evaluation atlas',
      'translation':BLOCK,'changed_tiles':changed,'changed_tile_count':len(changed),'non_target_tiles_byte_identical':True,
      'shared_separator_tile_166_byte_identical':True,
      'consumer_trace':{
        'rom_offset':'0x3F56E9','instruction':'MOV AX,0x06D4; MOV BX,0x1182; MOV CX,0x0209; CALL 0x3F618E',
        'atlas_base_tile':64,'local_tile_start':148,'dimensions':'9x2','local_tiles_consumed':'148-165',
        'separate_separator_instruction':'0x3F572D MOV AX,0x06E6; repeat 26',
        'conclusion':'SIGNAL IGNORED block is isolated from shared separator tile 166.'},
      'atlas_decompressed_bytes':2816,'old_compressed_bytes':cons,'new_compressed_bytes':len(packed),'free_bytes_vs_v0412_allocation':cons-len(packed),
      'rom_bytes':len(final),'rom_sha256':sha(final),'checksum_stored':f'0x{int.from_bytes(final[-2:],"little"):04X}','checksum_calculated':f'0x{sum(final[:-2])&0xffff:04X}',
      'changed_bytes_vs_v0412':len(diffs),'unexpected_changes':0,
      'incremental_ips':{'bytes':len(delta),'sha256':sha(delta),'reapplication_exact':True},
      'cumulative_ips':{'bytes':len(cumulative),'sha256':sha(cumulative),'composition_verified':True,'direct_original_reapplication':'not_retested_original_rom_absent'},
      'runtime_validation':'pending'
    }
    (REP/'V0413_BINARY_VALIDATION.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (REP/'V0413_CONSUMER_TRACE.json').write_text(json.dumps(report['consumer_trace'],ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (REP/'V0413_ATLAS_PATCH_MANIFEST.json').write_text(json.dumps({'block':BLOCK,'changed_tiles':changed,'separator_tile_166_preserved':True},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))
if __name__=='__main__': main()
