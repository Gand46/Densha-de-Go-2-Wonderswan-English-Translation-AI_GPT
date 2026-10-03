local f=0
local out=assert(os.getenv('OUTDIR'))
local function wr(p,d)local q=assert(io.open(p,'wb'));q:write(d);q:close()end
local function dump(n)
 wr(out..'/'..n..'.png',emu.takeScreenshot());local t={};for a=0,65535 do t[#t+1]=string.char(emu.read(a,emu.memType.wsMemory) or 0) end;wr(out..'/'..n..'.wram',table.concat(t))
end
local steps={{470,'start'},{540,'right'},{610,'a'},{900,'left'},{1050,'right'},{1200,'right'},{1350,'right'},{1500,'right'},{1650,'down'},{1800,'right'},{1950,'right'},{2100,'down'},{2250,'right'},{2400,'right'},{2550,'down'},{2700,'right'},{2850,'right'}}
emu.addEventCallback(function()local inp={};for _,s in ipairs(steps) do if f>=s[1] and f<s[1]+10 then inp[s[2]]=true end end;emu.setInput(inp,0)end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 f=f+1
 if f==820 or f>=980 and (f-980)%150==0 then dump('f'..f) end
 if f==3000 then wr(out..'/complete.txt','SCRIPTED_NATURAL frames=3000');emu.stop(0) end
end,emu.eventType.endFrame)
