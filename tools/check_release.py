#!/usr/bin/env python3
"""Check exact reproduction and all frozen patch roundtrips without writing a ROM."""
from pathlib import Path
import argparse,json,sys
from build import ROOT,build,sha,require
from ws_patch_tools import ips,bps
p=argparse.ArgumentParser(description=__doc__);p.add_argument('rom',type=Path);a=p.parse_args()
try:
 original=a.rom.read_bytes();meta,baseline,result,changes=build(original)
 records=[]
 for label,source in [('CUMULATIVE',original),(f"from_v{meta['previous_rom_version']}_INCREMENTAL",baseline)]:
  for ext,lib in [('bps',bps),('ips',ips)]:
   name=f"Densha_de_Go_2_EN_v{meta['rom_version']}_{label}.{ext}";patch=(ROOT/'patches'/name).read_bytes()
   require(lib.create(source,result)==patch,f'{name}: rebuilt patch differs')
   require(lib.apply(source,patch)==result,f'{name}: roundtrip differs');records.append(name)
 bad=bytearray(original);bad[0]^=1
 try:build(bytes(bad))
 except ValueError:pass
 else:raise ValueError('Invalid source accepted')
 patch=(ROOT/'patches'/f"Densha_de_Go_2_EN_v{meta['rom_version']}_CUMULATIVE.bps").read_bytes();badpatch=bytearray(patch);badpatch[20]^=1
 for source,patchbytes in [(baseline,patch),(original,bytes(badpatch)),(original,patch[:-5])]:
  try:bps.apply(source,patchbytes)
  except ValueError:pass
  else:raise ValueError('Invalid BPS input accepted')
 print(json.dumps({'passed':True,'rom_sha256':sha(result),'patches_exact':records,'negative_input_guards_passed':True,'rom_written':False},indent=2))
except (ValueError,OSError,KeyError) as e:
 print(f'Verification failed: {e}',file=sys.stderr);sys.exit(1)
