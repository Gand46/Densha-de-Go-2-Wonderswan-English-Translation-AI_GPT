#!/usr/bin/env python3
"""Apply the frozen cumulative BPS to the exact Japanese ROM."""
from pathlib import Path
import argparse,hashlib,json,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'vendor'))
from ws_patch_tools import bps
p=argparse.ArgumentParser(description=__doc__);p.add_argument('original',type=Path);p.add_argument('output',type=Path);a=p.parse_args()
try:
 meta=json.loads((ROOT/'project.json').read_text(encoding='utf-8'));source=a.original.read_bytes()
 if hashlib.sha256(source).hexdigest()!=meta['original_sha256']:raise ValueError('Wrong original ROM SHA-256')
 if a.output.resolve()==a.original.resolve() or a.output.exists():raise ValueError('Choose a new output path; original and existing files are preserved')
 patch=ROOT/'patches'/f"Densha_de_Go_2_EN_v{meta['rom_version']}_CUMULATIVE.bps"
 result=bps.apply(source,patch.read_bytes())
 if hashlib.sha256(result).hexdigest()!=meta['target_sha256']:raise ValueError('Patched ROM SHA-256 mismatch')
 a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_bytes(result);print(f'Saved: {a.output}\nSHA-256: {meta["target_sha256"]}')
except (OSError,ValueError,KeyError) as error:
 print(f'Patch failed: {error}',file=sys.stderr);sys.exit(1)
