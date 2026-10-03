local f=0;local out=assert(os.getenv('OUTDIR'));local rows={}
local function wr(n,d)local h=assert(io.open(out..'/'..n,'wb'));h:write(d);h:close()end
local steps={{470,'start'},{610,'a'},{850,'a'},{2000,'start'},{2400,'down'},{2550,'down'},{2700,'down'},{4000,'start'},{4500,'a'},{5000,'start'},{5500,'down'},{5800,'a'}}
emu.addEventCallback(function()local p={} for _,s in ipairs(steps)do if f>=s[1] and f<s[1]+10 then p[s[2]]=true end end;if f>=2250 and f<2330 then p.right2=true end;emu.setInput(p,0)end,emu.eventType.inputPolled)
local captures={[3900]=true,[4100]=true,[4400]=true,[4700]=true,[5100]=true,[5600]=true,[6100]=true}
emu.addEventCallback(function()
 f=f+1
 if captures[f] then
  wr('f'..f..'.png',emu.takeScreenshot());local t={};for a=0,65535 do t[#t+1]=string.char(emu.read(a,emu.memType.wsMemory))end;wr('f'..f..'.wram',table.concat(t))
  rows[#rows+1]=string.format('{"frame":%d,"state":%d,"substate":%d,"selection":%d,"timer":%d}',f,emu.read(0x135,emu.memType.wsMemory),emu.read(0x395,emu.memType.wsMemory),emu.read(0x220,emu.memType.wsMemory),emu.read16(0x218,emu.memType.wsMemory))
 end
 if f==6200 then wr('completed.json','{"completed":true,"frames":6200,"memory_writes":false,"samples":['..table.concat(rows,',')..']}');emu.stop(0)end
end,emu.eventType.endFrame)
