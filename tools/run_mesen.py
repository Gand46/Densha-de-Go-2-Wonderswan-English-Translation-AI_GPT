#!/usr/bin/env python3
"""Bounded Linux Mesen QA; framebuffer screenshots remain unmodified."""
from pathlib import Path
import argparse,os,sys,subprocess,time,json,hashlib,shutil
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--name',required=True);p.add_argument('--mesen',type=Path,required=True);p.add_argument('--rom',type=Path,default=ROOT/'build/Densha_de_Go_2_EN_v0.4.17.ws');p.add_argument('--mode',choices=['course','options','idle'],default='course');p.add_argument('--index',type=int,choices=range(6),default=0);p.add_argument('--frames',type=int,default=18000);p.add_argument('--freeze',action='store_true');p.add_argument('--lua',type=Path);a=p.parse_args()
if a.mode=='options':a.frames=3000;a.index=0;a.freeze=False
if sys.platform!='linux':p.error('Emulator runner validated on Linux only; ROM builder is portable.')
if Path(a.name).name!=a.name:p.error('name must be a single new directory name')
out=ROOT/'qa/generated'/a.name
if out.exists():p.error('Output exists. Choose another name to preserve evidence.')
out.mkdir(parents=True)
mesen=a.mesen.resolve()
if not mesen.is_file():p.error('Mesen executable not found; supply --mesen PATH')
mesen.chmod(mesen.stat().st_mode|0o755)
settings=mesen.with_name('settings.json')
if not settings.exists():settings.write_text('{}\n')
env=os.environ.copy();env.update(OUTDIR=str(out),COURSE_IDX=str(a.index),QA_MODE=a.mode,MAXFRAME=str(a.frames),QA_FREEZE='1' if a.freeze else '0')
lib=Path('/usr/lib/x86_64-linux-gnu/libstdc++.so.6')
if not lib.exists() and shutil.which('g++'):lib=Path(subprocess.check_output(['g++','-print-file-name=libstdc++.so.6'],text=True).strip())
if lib.exists():env['LD_PRELOAD']=str(lib)
lua=(a.lua or ROOT/'qa/scripts'/('options_sweep.lua' if a.mode=='options' else 'natural_course.lua')).resolve();rom=a.rom.resolve()
cmd=[str(mesen),'--testRunner','--timeout=85','--enableStdout','--doNotSaveSettings','--debug.scriptWindow.allowIoOsAccess=true',str(lua),str(rom)]
start=time.monotonic()
try:
 r=subprocess.run(cmd,env=env,cwd=mesen.parent,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=90);code=r.returncode;log=r.stdout
except subprocess.TimeoutExpired as e:code=124;log=e.stdout or b''
(out/'run.log').write_bytes(log)
detail=json.loads((out/'completed.json').read_text()) if (out/'completed.json').exists() else {}
completed=detail.get('completed',False) or (out/'complete.txt').exists()
access=detail.get('method') or detail.get('access_method') or ('WRAM_SUBSTATE_INJECTION' if (out/'assisted_transition.json').exists() else 'WRAM_POKE+FREEZE' if detail.get('course_injected') and a.freeze else 'WRAM_POKE' if detail.get('course_injected') else 'FREEZE' if a.freeze else 'SCRIPTED_NATURAL')
rep={'exit_code':code,'completed':completed,'seconds':round(time.monotonic()-start,3),'rom_sha256':hashlib.sha256(rom.read_bytes()).hexdigest(),'lua_sha256':hashlib.sha256(lua.read_bytes()).hexdigest(),'access_method':access,'parameters':vars(a),'command':cmd}
(out/'execution.json').write_text(json.dumps(rep,indent=2,default=str));print(json.dumps(rep,default=str));sys.exit(0 if code==0 and completed else 1)
