#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
import hashlib, json, sys
import numpy as np
from PIL import Image, ImageDraw

PKG=Path(__file__).resolve().parents[1]
BASE=PKG/'base'/'Densha_de_Go_2_EN_v0.4.14.ws'
CUM_BASE=PKG/'base'/'Densha_de_Go_2_EN_v0.4.14.ips'
REBUILD=PKG/'rebuild'; REBUILD.mkdir(parents=True,exist_ok=True)
OUT=REBUILD/'Densha_de_Go_2_EN_v0.4.15.ws'
DELTA=REBUILD/'Densha_de_Go_2_EN_v0.4.15_from_v0.4.14.ips'
CUM=REBUILD/'Densha_de_Go_2_EN_v0.4.15.ips'
PREV=REBUILD/'previews'; REP=REBUILD/'reports'
for d in (PREV,REP): d.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(PKG/'tools'))
import build_densha_v0410 as h

TITLE_OFF=0x3D4627
TITLE_DECOMP=4096
# At the title screen this stream is loaded to WRAM 0x2CC0, i.e. tile 204.
WRAM_LOAD=0x2CC0
TILE_BASE=204
# Screen tilemap at WRAM 0x1000 maps the Japanese logo rectangle x=2..17,y=0..5.
# None means shared blank tile 204 and must never be modified.
SCREEN_LOCAL=[
 [None,1,2,3,4,5,6,7,8,9,None,None,None,None,None,None],
 [16,17,18,19,20,21,22,23,24,25,None,None,None,None,None,None],
 [32,33,34,35,36,37,38,39,40,41,None,None,None,None,None,None],
 [48,49,50,51,52,53,54,55,56,57,58,None,None,None,None,None],
 [64,65,66,67,68,69,70,71,72,73,74,None,None,None,None,None],
 [80,81,82,83,84,85,86,87,88,89,90,91,92,93,94,95],
]
BG=3
PAL=np.array([255,176,88,0],dtype=np.uint8)

def sha(b:bytes)->str:return hashlib.sha256(b).hexdigest()

def mask_text(text:str,scale:int=2,spacing:int=1)->np.ndarray:
    font=h.FONT5; widths=[len(font.get(ch,font[' '])[0])*scale for ch in text]
    m=np.zeros((7*scale,sum(widths)+spacing*(len(text)-1)),dtype=bool); cx=0
    for ch,w in zip(text,widths):
        g=font.get(ch,font[' '])
        for gy,row in enumerate(g):
            for gx,c in enumerate(row):
                if c=='1':m[gy*scale:(gy+1)*scale,cx+gx*scale:cx+(gx+1)*scale]=True
        cx+=w+spacing
    return m

def stamp(canvas:np.ndarray,text:str,x:int,y:int,scale:int=2,spacing:int=1)->None:
    m=mask_text(text,scale,spacing); hh,ww=m.shape
    # shadow +2,+2, gray outline, white body; matches the existing GO!2 visual hierarchy.
    canvas[y+2:y+2+hh,x+2:x+2+ww][m]=2
    dm=np.zeros((hh+2,ww+2),dtype=bool)
    for yy in range(hh):
        for xx in range(ww):
            if m[yy,xx]:dm[yy:yy+3,xx:xx+3]=True
    canvas[y-1:y+hh+1,x-1:x+ww+1][dm]=1
    canvas[y:y+hh,x:x+ww][m]=0

def make_rect(raw:bytes)->tuple[np.ndarray,np.ndarray,list[np.ndarray]]:
    arr=[a.copy() for a in h.tiles_arrays(raw)]; assert len(arr)==256
    before=np.full((48,128),BG,dtype=np.uint8)
    for ry,row in enumerate(SCREEN_LOCAL):
        for rx,li in enumerate(row):
            if li is not None:before[ry*8:(ry+1)*8,rx*8:(rx+1)*8]=arr[li]
    after=np.full_like(before,BG)
    # global screen DENSHA x=26,y=3 -> rect x=10; DE x=60,y=27 -> rect x=44.
    stamp(after,'DENSHA',10,3,2,1)
    stamp(after,'DE',44,27,2,2)
    # Ensure foreground never requires shared blank positions.
    allowed=np.zeros_like(after,dtype=bool)
    for ry,row in enumerate(SCREEN_LOCAL):
        for rx,li in enumerate(row):
            if li is not None:allowed[ry*8:(ry+1)*8,rx*8:(rx+1)*8]=True
    assert not np.any((after!=BG)&~allowed)
    return before,after,arr

def contact(a:np.ndarray,b:np.ndarray,path:Path)->None:
    s=3; w=a.shape[1]*s; hh=a.shape[0]*s
    out=Image.new('RGB',(w*2+32,hh+34),'white');d=ImageDraw.Draw(out)
    d.text((5,5),'v0.4.14: Japanese logo',fill='black');d.text((w+21,5),'v0.4.15: DENSHA DE',fill='black')
    for x,c in ((5,a),(w+21,b)):
        im=Image.fromarray(PAL[c],mode='L').resize((w,hh),Image.Resampling.NEAREST).convert('RGB');out.paste(im,(x,25))
    out.save(path)

def main()->None:
    base=BASE.read_bytes(); assert len(base)==4*1024*1024
    raw,old_comp=h.dec_stream(base,TITLE_OFF); assert len(raw)==TITLE_DECOMP
    before,after_rect,arr=h.make_rect(raw) if False else make_rect(raw)
    target=[]
    for ry,row in enumerate(SCREEN_LOCAL):
        for rx,li in enumerate(row):
            if li is not None:
                arr[li]=after_rect[ry*8:(ry+1)*8,rx*8:(rx+1)*8].copy();target.append(li)
    assert len(target)==67 and len(set(target))==67 and 0 not in target
    newraw=h.arrays_to_data(arr); packed=h.compress_ws(newraw); chk,used=h.dec_stream(packed,0)
    assert chk==newraw and used==len(packed) and len(packed)<=old_comp
    rom=bytearray(base);rom[TITLE_OFF:TITLE_OFF+len(packed)]=packed
    # Preserve old trailing allocation bytes; the new compressed stream terminates before them.
    rom[-2:]=b'\0\0';checksum=sum(rom[:-2])&0xffff;rom[-2:]=checksum.to_bytes(2,'little');final=bytes(rom);OUT.write_bytes(final)
    fraw,fcons=h.dec_stream(final,TITLE_OFF);assert fraw==newraw and fcons==len(packed)
    diffs=[i for i,(a,b) in enumerate(zip(base,final)) if a!=b]
    unexpected=[i for i in diffs if not(TITLE_OFF<=i<TITLE_OFF+old_comp or i>=len(final)-2)];assert not unexpected
    delta=h.ips_create(base,final);DELTA.write_bytes(delta);assert h.ips_apply(base,delta)==final
    cm=h.ips_write_map(CUM_BASE.read_bytes());dm=h.ips_write_map(delta);oldm=dict(cm);cm.update(dm);cump=h.map_to_ips(cm);CUM.write_bytes(cump)
    cm2=h.ips_write_map(cump);assert all(cm2[k]==v for k,v in dm.items());assert all(cm2[k]==v for k,v in oldm.items() if k not in dm)
    Image.fromarray(PAL[before],mode='L').resize((512,192),Image.Resampling.NEAREST).save(PREV/'V0415_title_before.png')
    Image.fromarray(PAL[after_rect],mode='L').resize((512,192),Image.Resampling.NEAREST).save(PREV/'V0415_title_after.png')
    contact(before,after_rect,PREV/'V0415_title_static_before_after.png')
    val={
      'version':'0.4.15','base_version':'0.4.14','translation':{'jp':'電車でGO!2','en':'DENSHA DE GO!2','policy':'romanize franchise title; preserve original GO!2 art'},
      'resource':{'offset':'0x3D4627','decompressed_bytes':4096,'runtime_load':'WRAM 0x2CC0','tile_base':204,'old_compressed_bytes':old_comp,'new_compressed_bytes':len(packed),'free_bytes':old_comp-len(packed)},
      'screen_patch':{'tilemap_runtime':'WRAM 0x1000','screen_rect_pixels':[16,0,143,47],'modified_unique_tiles':len(target),'shared_blank_tile_204_modified':False,'GO2_pixels_preserved_by_screen_space_patch':True},
      'rom':{'bytes':len(final),'sha256':sha(final),'checksum_stored':f'0x{int.from_bytes(final[-2:],"little"):04X}','checksum_calculated':f'0x{sum(final[:-2])&0xffff:04X}'},
      'diff':{'changed_bytes_vs_v0414':len(diffs),'unexpected_changes':0},
      'incremental_ips':{'bytes':len(delta),'sha256':sha(delta),'reapplication_exact':True},
      'cumulative_ips':{'bytes':len(cump),'sha256':sha(cump),'composition_verified':True,'direct_original_reapplication':'not_retested_original_rom_absent'},
      'runtime_validation':'pending'
    }
    (REP/'V0415_BINARY_VALIDATION.json').write_text(json.dumps(val,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (REP/'V0415_TITLE_PATCH_MANIFEST.json').write_text(json.dumps({'target_local_tiles':target,'screen_local_map':SCREEN_LOCAL,'screen_rect_global':[16,0,143,47]},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(val,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
