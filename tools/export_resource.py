#!/usr/bin/env python3
"""Export a known compressed graphics resource for an editable development override."""
from pathlib import Path
import argparse,json
from codec import dec_stream
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser(description=__doc__);p.add_argument('rom',type=Path);p.add_argument('offset',type=lambda s:int(s,0));p.add_argument('output',type=Path);a=p.parse_args()
known={int(r['stream'],16) for r in json.loads((ROOT/'translations/GLOBAL_RESOURCE_INVENTORY.json').read_text(encoding='utf-8'))['resources'] if 'stream' in r}
if a.offset not in known:p.error('Offset not present in compressed resource inventory')
raw,used=dec_stream(a.rom.read_bytes(),a.offset)
if a.output.exists():p.error('Output exists; choose a new filename')
a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_bytes(raw)
print(json.dumps({'offset':hex(a.offset),'raw_bytes':len(raw),'compressed_bytes':used,'output':str(a.output)}))
