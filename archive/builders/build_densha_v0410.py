#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
import csv, hashlib, json, sys, zipfile
import numpy as np
from PIL import Image, ImageDraw

ROOT=Path('/mnt/data')
BASE=ROOT/'Densha_de_Go_2_EN_v0.4.9_package'/'Densha_de_Go_2_EN_v0.4.9.ws'
OUT=ROOT/'Densha_de_Go_2_EN_v0.4.10.ws'
DELTA=ROOT/'Densha_de_Go_2_EN_v0.4.10_from_v0.4.9.ips'
CUM_BASE=ROOT/'Densha_de_Go_2_EN_v0.4.9_package'/'Densha_de_Go_2_EN_v0.4.9.ips'
CUM=ROOT/'Densha_de_Go_2_EN_v0.4.10.ips'
WORK=ROOT/'densha_v0410_work'
PREV=WORK/'previews'; REP=WORK/'reports'; RUNTIME=WORK/'runtime'
for d in (WORK,PREV,REP,RUNTIME): d.mkdir(parents=True,exist_ok=True)

sys.path.insert(0,str(Path(__file__).parent))
from build_densha_v045 import dec_stream, compress_ws, tiles_arrays, arrays_to_data

ATLAS_OFF=0x028537
# exact atlas blocks proven by Mesen evaluation-screen tilemap consumer
BLOCKS=[
    {'name':'seconds_unit','jp':'秒','en':'SEC','top':28,'cols':2,'font':'3x5'},
    {'name':'none_value','jp':'なし','en':'NONE','top':42,'cols':3,'font':'5x7'},
    {'name':'total_minus','jp':'合計マイナス','en':'TOTAL LOSS','top':72,'cols':8,'font':'5x7'},
    {'name':'overrun','jp':'オーバーラン','en':'OVERRUN','top':88,'cols':9,'font':'5x7'},
    {'name':'time_left','jp':'持ち時間','en':'TIME LEFT','top':118,'cols':6,'font':'5x7'},
    {'name':'station_reaccel','jp':'駅構内再加速','en':'RE-ACCEL','top':130,'cols':9,'font':'5x7'},
]

FONT5={
 'A':["01110","10001","10001","11111","10001","10001","10001"],
 'B':["11110","10001","10001","11110","10001","10001","11110"],
 'C':["01111","10000","10000","10000","10000","10000","01111"],
 'D':["11110","10001","10001","10001","10001","10001","11110"],
 'E':["11111","10000","10000","11110","10000","10000","11111"],
 'F':["11111","10000","10000","11110","10000","10000","10000"],
 'G':["01111","10000","10000","10111","10001","10001","01111"],
 'H':["10001","10001","10001","11111","10001","10001","10001"],
 'I':["11111","00100","00100","00100","00100","00100","11111"],
 'J':["00111","00010","00010","00010","10010","10010","01100"],
 'K':["10001","10010","10100","11000","10100","10010","10001"],
 'L':["10000","10000","10000","10000","10000","10000","11111"],
 'M':["10001","11011","10101","10101","10001","10001","10001"],
 'N':["10001","11001","10101","10011","10001","10001","10001"],
 'O':["01110","10001","10001","10001","10001","10001","01110"],
 'P':["11110","10001","10001","11110","10000","10000","10000"],
 'Q':["01110","10001","10001","10001","10101","10010","01101"],
 'R':["11110","10001","10001","11110","10100","10010","10001"],
 'S':["01111","10000","10000","01110","00001","00001","11110"],
 'T':["11111","00100","00100","00100","00100","00100","00100"],
 'U':["10001","10001","10001","10001","10001","10001","01110"],
 'V':["10001","10001","10001","10001","10001","01010","00100"],
 'W':["10001","10001","10001","10101","10101","10101","01010"],
 'X':["10001","10001","01010","00100","01010","10001","10001"],
 'Y':["10001","10001","01010","00100","00100","00100","00100"],
 'Z':["11111","00001","00010","00100","01000","10000","11111"],
 '-':["00000","00000","00000","11111","00000","00000","00000"],
 ' ':["000","000","000","000","000","000","000"],
}
FONT3={
 'A':["010","101","111","101","101"], 'B':["110","101","110","101","110"],
 'C':["011","100","100","100","011"], 'D':["110","101","101","101","110"],
 'E':["111","100","110","100","111"], 'F':["111","100","110","100","100"],
 'G':["011","100","101","101","011"], 'H':["101","101","111","101","101"],
 'I':["111","010","010","010","111"], 'J':["001","001","001","101","010"],
 'K':["101","101","110","101","101"], 'L':["100","100","100","100","111"],
 'M':["101","111","111","101","101"], 'N':["101","111","111","111","101"],
 'O':["111","101","101","101","111"], 'P':["110","101","110","100","100"],
 'Q':["111","101","101","111","001"], 'R':["110","101","110","101","101"],
 'S':["011","100","111","001","110"], 'T':["111","010","010","010","010"],
 'U':["101","101","101","101","111"], 'V':["101","101","101","101","010"],
 'W':["101","101","111","111","101"], 'X':["101","101","010","101","101"],
 'Y':["101","101","010","010","010"], 'Z':["111","001","010","100","111"],
 ' ':["00","00","00","00","00"], '-':["000","000","111","000","000"],
}
PALETTE=np.array([0,85,170,255],dtype=np.uint8)

def sha(b:bytes)->str: return hashlib.sha256(b).hexdigest()

def block_indices(top:int, cols:int)->list[int]:
    return list(range(top,top+cols))+list(range(top+cols,top+2*cols))

def canvas_from_indices(raw:bytes, top:int, cols:int)->np.ndarray:
    arrs=tiles_arrays(raw); c=np.zeros((16,cols*8),dtype=np.uint8)
    for row in range(2):
        for col in range(cols): c[row*8:(row+1)*8,col*8:(col+1)*8]=arrs[top+row*cols+col]
    return c

def text_canvas(text:str,width:int,fontkind:str,fg:int=3)->np.ndarray:
    font=FONT5 if fontkind=='5x7' else FONT3
    h=7 if fontkind=='5x7' else 5
    widths=[len(font.get(ch,font[' '])[0]) for ch in text]
    # 1px tracking. If a 5x7 line barely exceeds, reduce tracking to 0.
    spacing=1
    tw=sum(widths)+max(0,len(text)-1)*spacing
    if tw>width:
        spacing=0; tw=sum(widths)
    if tw>width: raise ValueError(f'{text} width {tw}>{width}')
    c=np.zeros((16,width),dtype=np.uint8)
    x=(width-tw)//2; y=(16-h)//2
    for ch,w in zip(text,widths):
        glyph=font.get(ch,font[' '])
        for gy,row in enumerate(glyph):
            for gx,v in enumerate(row):
                if v=='1': c[y+gy,x+gx]=fg
        x+=w+spacing
    return c

def put_canvas(raw:bytes,top:int,cols:int,c:np.ndarray)->bytes:
    arrs=tiles_arrays(raw)
    for row in range(2):
        for col in range(cols): arrs[top+row*cols+col]=c[row*8:(row+1)*8,col*8:(col+1)*8].copy()
    return arrays_to_data(arrs)

def render_canvas(c:np.ndarray,path:Path,scale:int=4)->None:
    img=Image.fromarray(PALETTE[c],mode='L')
    if scale!=1: img=img.resize((img.width*scale,img.height*scale),Image.Resampling.NEAREST)
    img.save(path)

def render_atlas(raw:bytes,path:Path,scale:int=3,labels:bool=False)->None:
    arrs=tiles_arrays(raw); cols=16; rows=(len(arrs)+15)//16
    labelh=7 if labels else 0
    img=Image.new('L',(cols*8,rows*(8+labelh)),0); draw=ImageDraw.Draw(img)
    for i,a in enumerate(arrs):
        x=(i%cols)*8; y=(i//cols)*(8+labelh); img.paste(Image.fromarray(PALETTE[a],mode='L'),(x,y))
        if labels: draw.text((x,y+8),str(i%100),fill=255)
    if scale!=1: img=img.resize((img.width*scale,img.height*scale),Image.Resampling.NEAREST)
    img.save(path)

def make_contact(before_raw:bytes,after_raw:bytes,path:Path)->None:
    rows=[]
    for b in BLOCKS:
        before=canvas_from_indices(before_raw,b['top'],b['cols'])
        after=canvas_from_indices(after_raw,b['top'],b['cols'])
        rows.append((f"{b['jp']} -> {b['en']}",before,after))
    scale=4; left=80*scale; right=80*scale; rowh=16*scale+25
    out=Image.new('RGB',(left+right+30,22+len(rows)*rowh),'white'); d=ImageDraw.Draw(out)
    d.text((6,4),'BEFORE (JP)',fill='black'); d.text((left+20,4),'AFTER (EN)',fill='black')
    y=22
    for label,bef,aft in rows:
        d.text((6,y),label,fill='black'); yy=y+13
        for x,c in ((6,bef),(left+20,aft)):
            im=Image.fromarray(PALETTE[c],mode='L').resize((c.shape[1]*scale,c.shape[0]*scale),Image.Resampling.NEAREST).convert('RGB')
            out.paste(im,(x,yy))
        y+=rowh
    out.save(path)

def ips_create(src:bytes,dst:bytes)->bytes:
    if len(src)!=len(dst): raise ValueError('same-size only')
    out=bytearray(b'PATCH'); i=0; n=len(src)
    while i<n:
        if src[i]==dst[i]: i+=1; continue
        start=i; buf=bytearray()
        while i<n and src[i]!=dst[i] and len(buf)<65535:
            buf.append(dst[i]); i+=1
        out+=start.to_bytes(3,'big')+len(buf).to_bytes(2,'big')+buf
    out+=b'EOF'; return bytes(out)

def ips_apply(src:bytes,patch:bytes)->bytes:
    if not patch.startswith(b'PATCH'): raise ValueError('bad IPS')
    out=bytearray(src); p=5
    while patch[p:p+3]!=b'EOF':
        off=int.from_bytes(patch[p:p+3],'big');p+=3; ln=int.from_bytes(patch[p:p+2],'big');p+=2
        if ln==0:
            rln=int.from_bytes(patch[p:p+2],'big');p+=2; val=patch[p];p+=1; out[off:off+rln]=bytes([val])*rln
        else:
            out[off:off+ln]=patch[p:p+ln];p+=ln
    return bytes(out)

def ips_write_map(patch:bytes)->dict[int,int]:
    m={}; p=5
    if not patch.startswith(b'PATCH'): raise ValueError('bad IPS')
    while patch[p:p+3]!=b'EOF':
        off=int.from_bytes(patch[p:p+3],'big');p+=3; ln=int.from_bytes(patch[p:p+2],'big');p+=2
        if ln==0:
            rln=int.from_bytes(patch[p:p+2],'big');p+=2; val=patch[p];p+=1
            for j in range(rln): m[off+j]=val
        else:
            for j,v in enumerate(patch[p:p+ln]): m[off+j]=v
            p+=ln
    return m

def map_to_ips(m:dict[int,int])->bytes:
    out=bytearray(b'PATCH'); keys=sorted(m); i=0
    while i<len(keys):
        start=keys[i]; vals=bytearray([m[start]]); prev=start; i+=1
        while i<len(keys) and keys[i]==prev+1 and len(vals)<65535:
            prev=keys[i]; vals.append(m[prev]); i+=1
        out+=start.to_bytes(3,'big')+len(vals).to_bytes(2,'big')+vals
    out+=b'EOF'; return bytes(out)

def main():
    base=BASE.read_bytes(); assert len(base)==4*1024*1024
    raw,cons=dec_stream(base,ATLAS_OFF)
    assert len(raw)==2816 and cons==1496, (len(raw),cons)
    before=raw; after=raw
    manifests=[]; all_target=set()
    for b in BLOCKS:
        c=text_canvas(b['en'],b['cols']*8,b['font'])
        after=put_canvas(after,b['top'],b['cols'],c)
        idxs=block_indices(b['top'],b['cols']); all_target.update(idxs)
        manifests.append({**b,'indices':f"{idxs[0]}-{idxs[-1]}",'pixels_foreground':int(np.sum(c==3))})
        render_canvas(canvas_from_indices(before,b['top'],b['cols']),PREV/f"before_{b['name']}.png",5)
        render_canvas(c,PREV/f"after_{b['name']}.png",5)
    # prove every non-target tile is byte-identical
    ba=tiles_arrays(before); aa=tiles_arrays(after)
    changed_tiles=[]
    for i,(x,y) in enumerate(zip(ba,aa)):
        if not np.array_equal(x,y): changed_tiles.append(i)
    assert set(changed_tiles)==all_target, (changed_tiles,sorted(all_target))
    packed=compress_ws(after)
    dec2,used2=dec_stream(packed,0)
    assert dec2==after and used2==len(packed)
    if len(packed)>cons: raise RuntimeError(f'new stream {len(packed)} exceeds allocation {cons}')
    rom=bytearray(base); rom[ATLAS_OFF:ATLAS_OFF+len(packed)]=packed
    rom[-2:]=b'\0\0'; chk=sum(rom[:-2])&0xFFFF; rom[-2:]=chk.to_bytes(2,'little')
    final=bytes(rom); OUT.write_bytes(final)
    # validate final stream
    fraw,fcons=dec_stream(final,ATLAS_OFF); assert fraw==after and fcons==len(packed)
    # changed bytes constrained
    diffs=[i for i,(a,b) in enumerate(zip(base,final)) if a!=b]
    unexpected=[i for i in diffs if not (ATLAS_OFF<=i<ATLAS_OFF+cons or i>=len(final)-2)]
    assert not unexpected, unexpected[:20]
    delta=ips_create(base,final); DELTA.write_bytes(delta); assert ips_apply(base,delta)==final
    # cumulative composition: v0.4.9 cumulative writes + exact v0.4.10 delta writes
    cm=ips_write_map(CUM_BASE.read_bytes())
    dm=ips_write_map(delta)
    cm.update(dm)
    cump=map_to_ips(cm); CUM.write_bytes(cump)
    # Composition semantic validation: all delta target bytes override cumulative correctly.
    cm2=ips_write_map(cump)
    assert all(cm2[k]==v for k,v in dm.items())
    # and all prior cumulative bytes not overridden remain unchanged
    oldm=ips_write_map(CUM_BASE.read_bytes())
    assert all(cm2[k]==v for k,v in oldm.items() if k not in dm)

    render_atlas(before,PREV/'028537_atlas_before.png',3,False)
    render_atlas(after,PREV/'028537_atlas_after.png',3,False)
    make_contact(before,after,PREV/'V0410_evaluation_labels_before_after.png')
    with (REP/'v0410_atlas_patch_manifest.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=['name','jp','en','top','cols','font','indices','pixels_foreground']);w.writeheader();w.writerows(manifests)
    val={
      'version':'0.4.10','base_version':'0.4.9','base_sha256':sha(base),'rom_sha256':sha(final),
      'rom_bytes':len(final),'ws_checksum_stored':f'0x{int.from_bytes(final[-2:],"little"):04X}','ws_checksum_calculated':f'0x{sum(final[:-2])&0xFFFF:04X}',
      'atlas':{'offset':'0x028537','decompressed_bytes':len(after),'old_compressed_bytes':cons,'new_compressed_bytes':len(packed),'free_bytes':cons-len(packed),'changed_tile_count':len(changed_tiles),'changed_tiles':changed_tiles,'non_target_tiles_byte_identical':True},
      'translations':[{k:b[k] for k in ('name','jp','en','top','cols')} for b in BLOCKS],
      'diff':{'changed_bytes_vs_v049':len(diffs),'unexpected_changes':0},
      'incremental_ips':{'bytes':len(delta),'sha256':sha(delta),'reapplication_exact':True},
      'cumulative_ips':{'bytes':len(cump),'sha256':sha(cump),'composition_from_v049_cumulative_plus_delta':True,'direct_original_reapplication':'not_retested_original_rom_absent'},
      'runtime_validation':'pending'
    }
    (REP/'V0410_BINARY_VALIDATION.json').write_text(json.dumps(val,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(val,ensure_ascii=False,indent=2))

if __name__=='__main__': main()
