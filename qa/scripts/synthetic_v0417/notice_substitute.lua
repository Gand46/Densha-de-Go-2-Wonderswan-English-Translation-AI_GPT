local frame=0
local out=assert(os.getenv('OUTDIR'))
local maxframe=tonumber(os.getenv('MAXFRAME') or '7000')
local idx=tonumber(os.getenv('COURSE_IDX') or '5')
local replacement=tonumber(assert(os.getenv('NOTICE_DESCRIPTOR')),16)
assert(replacement>=0x8000 and replacement<=0x9000,'Descriptor out of expected bank 3D notice range')
local substituted=false
local original_descriptor=0x8dd0
local events={};local seen={};local interesting={}
local targets={[0x3d92e1]=true,[0x3d93ab]=true,[0x3d855c]=true,[0x3d866f]=true,[0x3d8759]=true,[0x3d8881]=true,[0x3d8a62]=true,[0x3d8b56]=true,[0x3d8c9f]=true,[0x3d8dd2]=true}
local function wr(name,data)local f=assert(io.open(out..'/'..name,'wb'));f:write(data);f:close()end
local function win(f,n)return frame>=f and frame<f+n end
local function word(a)return emu.read(a,emu.memType.wsMemory)+256*emu.read(a+1,emu.memType.wsMemory)end
emu.addMemoryCallback(function()
 if not substituted and frame>=6500 and frame<6650 and word(0xa14)==original_descriptor then
  assert(emu.read(0xa12,emu.memType.wsMemory)==0xfd and emu.read(0xa13,emu.memType.wsMemory)==0x00,'Bank selector guard failed')
  assert(word(0xa18)==0x2580,'Destination guard failed')
  emu.write(0xa14,replacement%256,emu.memType.wsMemory)
  emu.write(0xa15,math.floor(replacement/256),emu.memType.wsMemory)
  substituted=true
  events[#events+1]=string.format('POKE\t%d\t0A14\t%04X\t%04X\tbank=3D\tdest=2580',frame,original_descriptor,replacement)
 end
end,emu.callbackType.exec,0xEC074,0xEC074,emu.cpuType.ws)
emu.addEventCallback(function()
 local inp={}
 if win(470,10) then inp.start=true end
 if win(610,10) then inp.a=true end
 if idx>=3 and win(900,10) then inp.right=true end
 if idx%3>=1 and win(1100,10) then inp.down=true end
 if idx%3==2 and win(1300,10) then inp.down=true end
 if win(1500,10) then inp.a=true end
 if win(2600,10) then inp.start=true end
 if frame>=2850 then
  local cyc=(frame-2850)%600
  if cyc<80 then inp.right2=true end
  if cyc>=120 and cyc<130 or cyc>=150 and cyc<160 or cyc>=180 and cyc<190 or cyc>=210 and cyc<220 or cyc>=240 and cyc<250 then inp.down=true end
 end
 emu.setInput(inp,0)
end,emu.eventType.inputPolled)
emu.addMemoryCallback(function()
 local s=emu.getState();local bank=s['cart.selectedBanks3']%64;local bx=s['cpu.bx'];local key=bank*65536+bx
 if bank==61 or bank==2 then
  local k=tostring(key)
  if not seen[k] then
   seen[k]=true;events[#events+1]=string.format('%d\t%06X\t%04X\t%04X\t%04X\t%02X\t%02X',frame,key,s['cpu.di'],s['cpu.cs'],s['cpu.ip'],emu.read(0x135,emu.memType.wsMemory),emu.read(0x395,emu.memType.wsMemory))
   if targets[key] then
    interesting[#interesting+1]={frame=frame,key=key}
    local ss=s['cpu.ss'];local sp=s['cpu.sp'];local a=(ss*16+sp)%65536;local stack={}
    for i=0,23 do stack[#stack+1]=string.format('%02X',emu.read((a+i)%65536,emu.memType.wsMemory)) end
    events[#events+1]=string.format('STACK\t%06X\tSS=%04X SP=%04X\t%s',key,ss,sp,table.concat(stack,' '))
    local q={};for i=0,47 do q[#q+1]=string.format('%02X',emu.read(0xa00+i,emu.memType.wsMemory))end
    events[#events+1]=string.format('QUEUE\t%06X\t%s',key,table.concat(q,' '))
   end
  end
 end
end,emu.callbackType.exec,0xEC186,0xEC186,emu.cpuType.ws)
emu.addEventCallback(function()
 frame=frame+1
 for _,a in ipairs(interesting) do
  if frame==a.frame+5 or frame==a.frame+30 or frame==a.frame+80 then wr(string.format('target_%06X_f%05d.png',a.key,frame),emu.takeScreenshot()) end
 end
 if frame==1450 then
  local selected=emu.read(0x21a,emu.memType.wsMemory)
  assert(selected==idx,'selection mismatch')
 end
 if frame==1450 or frame==1600 or frame==2200 or frame==2600 or frame==3000 or frame==4000 or frame==5000 or frame==6000 or frame==7000 then wr(string.format('f%05d.png',frame),emu.takeScreenshot()) end
 if frame==6600 or frame==6650 or frame==6700 then wr(string.format('notice_f%05d.png',frame),emu.takeScreenshot()) end
 if frame==maxframe then
  wr('trace.tsv',table.concat(events,'\n')..'\n')
  wr('completed.json','{"completed":'..tostring(substituted)..',"method":"WRAM_POINTER_INJECTION","natural_completion":false,"original_descriptor":"8DD0","replacement_descriptor":"'..string.format('%04X',replacement)..'","course":'..idx..'}')
  emu.stop(substituted and 0 or 2)
 end
end,emu.eventType.endFrame)
