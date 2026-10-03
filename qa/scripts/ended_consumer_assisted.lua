local frame=0;local out=assert(os.getenv('OUTDIR'));local before=nil
local function wr(name,data)local f=assert(io.open(out..'/'..name,'wb'));f:write(data);f:close()end
emu.addEventCallback(function()local inp={} if frame>=470 and frame<480 then inp.start=true end;if frame>=610 and frame<620 then inp.a=true end;emu.setInput(inp,0)end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 if frame==900 then
  local state=emu.read(0x135,emu.memType.wsMemory);local sub=emu.read(0x395,emu.memType.wsMemory)
  assert(state==0x10 and sub==1,'Expected selector state before assisted transition')
  before=sub;emu.write(0x395,0x88,emu.memType.wsMemory)
  wr('assisted_transition.json','{"method":"WRAM_SUBSTATE_INJECTION","address":"0x0395","before":1,"after":136,"dispatcher":"F000:2FD2 -> F000:2DF0 -> F000:373A -> F000:3A53","natural_completion":false}')
 end
end,emu.eventType.startFrame)
emu.addMemoryCallback(function()
 local s=emu.getState()
 if s['cart.selectedBanks3']%64==61 and s['cpu.bx']==0x61c0 then wr('ended_load.json',string.format('{"frame":%d,"stream":"0x3D61C0","destination":%d}',frame,s['cpu.di'])) end
end,emu.callbackType.exec,0xEC186,0xEC186,emu.cpuType.ws)
emu.addEventCallback(function()
 frame=frame+1
 if frame==950 or frame==1000 or frame==1050 or frame==1100 then wr('f'..frame..'.png',emu.takeScreenshot()) end
 if frame==1000 then local t={};for a=0,65535 do t[#t+1]=string.char(emu.read(a,emu.memType.wsMemory)) end;wr('ended.wram',table.concat(t)) end
 if frame==1100 then wr('completed.json','{"completed":true,"frames":1100,"assisted":true,"natural_completion":false}');emu.stop(0) end
end,emu.eventType.endFrame)
