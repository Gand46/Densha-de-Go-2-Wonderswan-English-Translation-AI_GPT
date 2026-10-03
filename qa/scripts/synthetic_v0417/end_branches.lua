local frame=0
local out=assert(os.getenv('OUTDIR'))
local mode=assert(os.getenv('END_CASE'))
local cases={low={0,1,0,0,0,0},middle={2,1,0,0,0,0},high_nonzero={3,1,0,0,0,0},high_zero_a={3,0,0,0,1,0},high_zero_b={3,0,0,0,0,0}}
local cfg=assert(cases[mode], 'Unknown END_CASE')
local events={}
local function wr(name,data) local f=assert(io.open(out..'/'..name,'wb'));f:write(data);f:close() end
local function byte(a) return emu.read(a,emu.memType.wsMemory) end
local function hit(name)
 local s=emu.getState()
 events[#events+1]=string.format('%d\t%s\t%04X:%04X\t078F=%02X\t077F=%02X\t0780=%02X\t0781=%02X\t019C=%02X%02X\tbank=%d\tbx=%04X\tdi=%04X',frame,name,s['cpu.cs'],s['cpu.ip'],byte(0x78f),byte(0x77f),byte(0x780),byte(0x781),byte(0x19d),byte(0x19c),s['cart.selectedBanks3'],s['cpu.bx'],s['cpu.di'])
end
emu.addEventCallback(function()
 local inp={}
 if frame>=470 and frame<480 then inp.start=true end
 if frame>=610 and frame<620 then inp.a=true end
 emu.setInput(inp,0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 if frame==900 then
  assert(byte(0x135)==0x10 and byte(0x395)==1,'Selector precondition failed')
  for i,a in ipairs({0x78f,0x77f,0x780,0x781,0x19c,0x19d}) do emu.write(a,cfg[i],emu.memType.wsMemory) end
  emu.write(0x395,0x88,emu.memType.wsMemory)
  hit('injection_'..mode)
 end
end,emu.eventType.startFrame)
for name,addr in pairs({entry=0xF373A,low_or_middle=0xF37EA,high_branch=0xF3773,score_a=0xF377A,score_b=0xF37AE,mid_call=0xF37F1,high_call=0xF37E0,ended_load=0xEC186}) do
 emu.addMemoryCallback(function()
  if frame>=900 and frame<1300 then hit(name) end
 end,emu.callbackType.exec,addr,addr,emu.cpuType.ws)
end
emu.addEventCallback(function()
 frame=frame+1
 if frame==950 or frame==1000 or frame==1150 or frame==1300 then wr(string.format('f%05d.png',frame),emu.takeScreenshot()) end
 if frame==1300 then
  wr('trace.tsv',table.concat(events,'\n')..'\n')
  wr('completed.json','{"completed":true,"method":"WRAM_SUBSTATE_AND_SCORE_INJECTION","natural_completion":false,"case":"'..mode..'"}')
  emu.stop(0)
 end
end,emu.eventType.endFrame)
