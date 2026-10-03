#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
import hashlib, json, sys, csv
import numpy as np
from PIL import Image, ImageDraw

ROOT=Path('/mnt/data')
BASE=ROOT/'Densha_de_Go_2_EN_v0.4.10_package'/'Densha_de_Go_2_EN_v0.4.10.ws'
OUT=ROOT/'Densha_de_Go_2_EN_v0.4.11.ws'
DELTA=ROOT/'Densha_de_Go_2_EN_v0.4.11_from_v0.4.10.ips'
CUM_BASE=ROOT/'Densha_de_Go_2_EN_v0.4.10_package'/'Densha_de_Go_2_EN_v0.4.10.ips'
CUM=ROOT/'Densha_de_Go_2_EN_v0.4.11.ips'
WORK=ROOT/'densha_v0411_work'
PREV=WORK/'previews'; REP=WORK/'reports'; RUNTIME=WORK/'runtime'
for d in (WORK,PREV,REP,RUNTIME): d.mkdir(parents=True,exist_ok=True)

sys.path.insert(0,str(Path(__file__).parent))
import build_densha_v0410 as prev

dec_stream=prev.dec_stream
compress_ws=prev.compress_ws
tiles_arrays=prev.tiles_arrays
arrays_to_data=prev.arrays_to_data
text_canvas=prev.text_canvas
put_canvas=prev.put_canvas
ips_create=prev.ips_create
ips_apply=prev.ips_apply
ips_write_map=prev.ips_write_map
map_to_ips=prev.map_to_ips
PALETTE=prev.PALETTE

ATLAS_OFF=0x028537
BLOCK={'name':'deduction_label','jp':'減点','en':'LOSS','top':36,'cols':3,'font':'5x7'}

def sha(b:bytes)->str:return hashlib.sha256(b).hexdigest()

def block_indices(top:int,cols:int)->list[int]:
    return list(range(top,top+cols))+list(range(top+cols,top+2*cols))

def canvas_from_indices(raw:bytes,top:int,cols:int)->np.ndarray:
    arrs=tiles_arrays(raw); c=np.zeros((16,cols*8),dtype=np.uint8)
    for row in range(2):
        for col in range(cols): c[row*8:(row+1)*8,col*8:(col+1)*8]=arrs[top+row*cols+col]
    return c

def render_canvas(c:np.ndarray,path:Path,scale:int=8)->None:
    img=Image.fromarray(PALETTE[c],mode='L').resize((c.shape[1]*scale,c.shape[0]*scale),Image.Resampling.NEAREST)
    img.save(path)

def make_contact(before:np.ndarray,after:np.ndarray,path:Path)->None:
    scale=8; lab=26
    w=max(before.shape[1],after.shape[1])*scale
    h=max(before.shape[0],after.shape[0])*scale
    out=Image.new('RGB',(w*2+30,h+lab+20),'white');d=ImageDraw.Draw(out)
    d.text((4,4),'v0.4.10: JP',fill='black');d.text((w+22,4),'v0.4.11: LOSS',fill='black')
    for x,c in ((4,before),(w+22,after)):
        im=Image.fromarray(PALETTE[c],mode='L').resize((c.shape[1]*scale,c.shape[0]*scale),Image.Resampling.NEAREST).convert('RGB')
        out.paste(im,(x,lab))
    out.save(path)

def main():
    base=BASE.read_bytes()
    if len(base)!=4*1024*1024: raise RuntimeError('Expected 4 MiB WonderSwan ROM')
    raw,cons=dec_stream(base,ATLAS_OFF)
    if len(raw)!=2816: raise RuntimeError(f'Unexpected atlas size {len(raw)}')
    before=raw
    old_canvas=canvas_from_indices(before,BLOCK['top'],BLOCK['cols'])
    new_canvas=text_canvas(BLOCK['en'],BLOCK['cols']*8,BLOCK['font'])
    after=put_canvas(before,BLOCK['top'],BLOCK['cols'],new_canvas)
    target=set(block_indices(BLOCK['top'],BLOCK['cols']))
    ba=tiles_arrays(before); aa=tiles_arrays(after)
    changed=[i for i,(x,y) in enumerate(zip(ba,aa)) if not np.array_equal(x,y)]
    if set(changed)!=target: raise RuntimeError(f'Changed tiles {changed} != target {sorted(target)}')
    for i,(x,y) in enumerate(zip(ba,aa)):
        if i not in target and not np.array_equal(x,y): raise RuntimeError(f'Non-target tile {i} changed')
    packed=compress_ws(after)
    dec2,used2=dec_stream(packed,0)
    if dec2!=after or used2!=len(packed): raise RuntimeError('Codec round-trip failed')
    if len(packed)>cons: raise RuntimeError(f'Atlas overflow {len(packed)}>{cons}')
    rom=bytearray(base)
    rom[ATLAS_OFF:ATLAS_OFF+len(packed)]=packed
    # Clear stale bytes inside old compressed allocation for deterministic output.
    if len(packed)<cons: rom[ATLAS_OFF+len(packed):ATLAS_OFF+cons]=b'\x00'*(cons-len(packed))
    rom[-2:]=b'\x00\x00'
    chk=sum(rom[:-2])&0xffff
    rom[-2:]=chk.to_bytes(2,'little')
    final=bytes(rom); OUT.write_bytes(final)
    fraw,fcons=dec_stream(final,ATLAS_OFF)
    if fraw!=after or fcons!=len(packed): raise RuntimeError('Final stream mismatch')
    diffs=[i for i,(a,b) in enumerate(zip(base,final)) if a!=b]
    unexpected=[i for i in diffs if not (ATLAS_OFF<=i<ATLAS_OFF+cons or i>=len(final)-2)]
    if unexpected: raise RuntimeError(f'Unexpected diffs: {unexpected[:20]}')
    delta=ips_create(base,final); DELTA.write_bytes(delta)
    if ips_apply(base,delta)!=final: raise RuntimeError('Incremental IPS does not reproduce final ROM')
    cm=ips_write_map(CUM_BASE.read_bytes()); dm=ips_write_map(delta); cm.update(dm)
    cump=map_to_ips(cm); CUM.write_bytes(cump)
    cm2=ips_write_map(cump); oldm=ips_write_map(CUM_BASE.read_bytes())
    if not all(cm2[k]==v for k,v in dm.items()): raise RuntimeError('Cumulative delta override failed')
    if not all(cm2[k]==v for k,v in oldm.items() if k not in dm): raise RuntimeError('Cumulative prior bytes changed')
    render_canvas(old_canvas,PREV/'V0411_deduction_before.png')
    render_canvas(new_canvas,PREV/'V0411_deduction_after.png')
    make_contact(old_canvas,new_canvas,PREV/'V0411_deduction_before_after.png')
    manifest={
      'version':'0.4.11','base_version':'0.4.10','resource':'0x028537 shared evaluation atlas',
      'block':BLOCK,'changed_tiles':changed,'changed_tile_count':len(changed),
      'old_compressed_bytes':cons,'new_compressed_bytes':len(packed),'free_bytes_vs_v0410_allocation':cons-len(packed),
      'non_target_tiles_byte_identical':True,
    }
    (REP/'V0411_ATLAS_PATCH_MANIFEST.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    val={
      'version':'0.4.11','base_version':'0.4.10','base_sha256':sha(base),'rom_sha256':sha(final),'rom_bytes':len(final),
      'ws_checksum_stored':f'0x{int.from_bytes(final[-2:],"little"):04X}','ws_checksum_calculated':f'0x{sum(final[:-2])&0xffff:04X}',
      'atlas':{'offset':'0x028537','decompressed_bytes':len(after),'old_compressed_bytes':cons,'new_compressed_bytes':len(packed),'changed_tiles':changed,'non_target_tiles_byte_identical':True},
      'translation':{'jp':'減点','en':'LOSS','runtime_context':'RE-ACCEL [LOSS] 10 SEC','tilemap_runtime_rows':'screen map 0x1000 row 4/5 cols 19-21'},
      'diff':{'changed_bytes_vs_v0410':len(diffs),'unexpected_changes':0},
      'incremental_ips':{'bytes':len(delta),'sha256':sha(delta),'reapplication_exact':True},
      'cumulative_ips':{'bytes':len(cump),'sha256':sha(cump),'composition_from_v0410_cumulative_plus_delta':True,'direct_original_reapplication':'not_retested_original_rom_absent'},
      'runtime_validation':'pending'
    }
    (REP/'V0411_BINARY_VALIDATION.json').write_text(json.dumps(val,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(val,ensure_ascii=False,indent=2))

if __name__=='__main__': main()
