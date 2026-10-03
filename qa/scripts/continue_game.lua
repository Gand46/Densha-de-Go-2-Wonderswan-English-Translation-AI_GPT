local frame=0
local idx=tonumber(os.getenv('COURSE_IDX') or '0')
local mode=os.getenv('QA_MODE') or 'course'
local out=assert(os.getenv('OUTDIR'))
local maxframe=tonumber(os.getenv('MAXFRAME') or '30000')
local freeze=os.getenv('QA_FREEZE')=='1'
local poked=false
local function wr(p,d) local f=assert(io.open(p,'wb')); f:write(d); f:close() end
local function shot(tag) wr(out..'/'..string.format('f%06d_',frame)..tag..'.png',emu.takeScreenshot()) end
local function dump(tag)
 local t={}; for a=0,65535 do t[#t+1]=string.char(emu.read(a,emu.memType.wsMemory) or 0) end
 wr(out..'/'..tag..'.wram',table.concat(t))
end
local function window(f,len) return frame>=f and frame<f+len end
emu.addEventCallback(function()
 local inp={}
 if window(470,10) then inp.start=true end
 if mode=='options' then
  if window(540,10) then inp.right=true end
  if window(610,10) then inp.a=true end
  for f=1000,2200,300 do if window(f,10) then inp.down=true end end
 else
  if window(610,10) then inp.a=true end
  if idx>=3 and window(900,10) then inp.right=true end
  if idx%3>=1 and window(1100,10) then inp.down=true end
  if idx%3==2 and window(1300,10) then inp.down=true end
  if window(1500,10) then inp.a=true end
  if window(2600,10) or window(11600,10) then inp.start=true end
  if frame>=2850 and mode~='idle' then
   local cyc=(frame-2850)%600
   if cyc<80 then inp.right2=true end
   if cyc>=120 and cyc<130 or cyc>=150 and cyc<160 or cyc>=180 and cyc<190 or cyc>=210 and cyc<220 or cyc>=240 and cyc<250 then inp.down=true end
  end
 end
 emu.setInput(inp,0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()

 if freeze and frame>=2200 then emu.write(0x0218,99,emu.memType.wsMemory);emu.write(0x0219,0,emu.memType.wsMemory) end
end,emu.eventType.startFrame)
emu.addEventCallback(function()
 frame=frame+1
 if frame==1450 then
  local selected=emu.read(0x021A,emu.memType.wsMemory)
  wr(out..'/selection_verified.json',string.format('{"requested":%d,"observed":%d,"matches":%s,"memory_writes":false}',idx,selected,tostring(idx==selected)))
  shot("selection_verified")
  if selected~=idx then emu.stop(2) end
 end
 if frame==11500 or frame==11900 or frame==12500 or frame==420 or frame==500 or frame==820 or frame==1200 or frame==1550 or frame==1700 or frame==2250 or frame>=3000 and frame%1000==0 or mode=='options' and frame>=800 and frame%300==0 then shot(mode) end
 if frame==500 or frame==820 or frame==2250 or frame==44000 or frame==11500 or frame==11900 or frame==14000 then dump('f'..frame) end
 if frame==maxframe then
  shot('final');dump('final')
  wr(out..'/completed.json',string.format('{"completed":true,"frames":%d,"course":%d,"course_injected":%s,"time_freeze":%s,"mode":"%s"}\n',frame,idx,tostring(poked),tostring(freeze),mode))
  emu.stop(0)
 end
end,emu.eventType.endFrame)
