local frame=0
local out=assert(os.getenv('OUTDIR'))
local function wr(p,d) local f=assert(io.open(out..'/'..p,'wb'));f:write(d);f:close() end
local events={{470,'start'},{610,'a'},{900,'right'},{1100,'down'},{1300,'down'},{1500,'left'},{1700,'up'},{1900,'up'}}
local log={}
emu.addEventCallback(function() local inp={} for _,v in ipairs(events) do if frame>=v[1] and frame<v[1]+10 then inp[v[2]]=true end end emu.setInput(inp,0) end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1
 if frame==820 or frame==1000 or frame==1200 or frame==1400 or frame==1600 or frame==1800 or frame==2000 then
  local idx=emu.read(0x21a,emu.memType.wsMemory)
  wr(string.format('f%04d_selector%d.png',frame,idx),emu.takeScreenshot())
  log[#log+1]=string.format('{"frame":%d,"selector_index":%d,"state":%d,"substate":%d}',frame,idx,emu.read(0x135,emu.memType.wsMemory),emu.read(0x395,emu.memType.wsMemory))
 end
 if frame==2100 then wr('completed.json','{"completed":true,"access":"BUTTONS_ONLY_NO_MEMORY_WRITES","samples":['..table.concat(log,',')..']}');emu.stop(0) end
end,emu.eventType.endFrame)
