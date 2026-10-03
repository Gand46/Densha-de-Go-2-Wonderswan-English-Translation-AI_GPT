local frame=0
local out=assert(os.getenv('OUTDIR'))
local maxframe=tonumber(os.getenv('MAXFRAME') or '7000')
local idx=tonumber(os.getenv('COURSE_IDX') or '5')
local events={};local seen={};local interesting={}
local injected=false
local targets={[0x3d92e1]=true,[0x3d93ab]=true,[0x3d855c]=true,[0x3d866f]=true,[0x3d8759]=true,[0x3d8881]=true,[0x3d8a62]=true,[0x3d8b56]=true,[0x3d8c9f]=true,[0x3d8dd2]=true}
local function wr(name,data)local f=assert(io.open(out..'/'..name,'wb'));f:write(data);f:close()end
local function win(f,n)return frame>=f and frame<f+n end
emu.addMemoryCallback(function()
 if not injected and frame>=3000 and frame<3010 then
  local a=0x05a2
  assert(emu.read(0x135,emu.memType.wsMemory)==0x0d,'Route precondition failed')
  assert(emu.read(a,emu.memType.wsMemory)==0 and emu.read(a+1,emu.memType.wsMemory)==0,'Object slot occupied')
  local ptr=emu.read(0x100,emu.memType.wsMemory)+256*emu.read(0x101,emu.memType.wsMemory)
  emu.write(a,0,emu.memType.wsMemory);emu.write(a+1,5,emu.memType.wsMemory)
  emu.write(a+2,0x50,emu.memType.wsMemory);emu.write(a+4,0x30,emu.memType.wsMemory)
  emu.write(a+6,7,emu.memType.wsMemory)
  emu.write(a+10,0x25,emu.memType.wsMemory)
  emu.write(a+14,ptr%256,emu.memType.wsMemory);emu.write(a+15,math.floor(ptr/256),emu.memType.wsMemory)
  injected=true
  events[#events+1]=string.format('POKE\t%d\t05A2\tupdate=07 flags=05 counter=0025 ptr=%04X',frame,ptr)
 end
end,emu.callbackType.exec,0xF62E0,0xF62E0,emu.cpuType.ws)
for _,v in ipairs({0xF7915,0xF794C,0xF660B,0xF6636,0xF668A,0xF69CC}) do
 emu.addMemoryCallback(function()
  if #events<150 then events[#events+1]=string.format('PC\t%d\t%05X\t0378=%02X\t0379=%02X\t013F=%04X\t0218=%04X',frame,v,emu.read(0x378,emu.memType.wsMemory),emu.read(0x379,emu.memType.wsMemory),emu.read(0x13f,emu.memType.wsMemory)+256*emu.read(0x140,emu.memType.wsMemory),emu.read(0x218,emu.memType.wsMemory)+256*emu.read(0x219,emu.memType.wsMemory)) end
 end,emu.callbackType.exec,v,v,emu.cpuType.ws)
end
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
 if frame==3000 or frame==3020 or frame==3050 or frame==3100 or frame==3200 or frame==3500 then wr(string.format('f%05d.png',frame),emu.takeScreenshot()) end
 if frame==3020 then
  local a=0x5a2;events[#events+1]=string.format('OBJECT\t%d\t%02X %02X counter=%02X%02X ptr=%02X%02X',frame,emu.read(a,emu.memType.wsMemory),emu.read(a+1,emu.memType.wsMemory),emu.read(a+11,emu.memType.wsMemory),emu.read(a+10,emu.memType.wsMemory),emu.read(a+15,emu.memType.wsMemory),emu.read(a+14,emu.memType.wsMemory))
 end
 if frame==maxframe then wr('trace.tsv',table.concat(events,'\n')..'\n');wr('completed.json','{"completed":'..tostring(injected)..',"method":"SYNTHETIC_OBJECT_INJECTION","course":'..idx..'}');emu.stop(injected and 0 or 2)end
end,emu.eventType.endFrame)
