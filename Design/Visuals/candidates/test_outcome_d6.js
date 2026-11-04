const fs=require('fs');
const html=fs.readFileSync(__dirname+'/D6.html','utf8');
const src=html.split('// BEGIN outcome')[1].split('// END outcome')[0];
const {PAIRS,outcome}=new Function(src+';return {PAIRS,outcome};')();
const E={ok:'✅',bad:'❌',wait:'⏸',tie:'⚖️'};
const cases=[['MT',true,5,'❌'],['MT',true,10,'⏸'],['MT',true,11,'✅'],['MT',true,110,'⚖️'],['MT',true,111,'❌'],['MT',false,5,'✅'],['PC',false,25,'❌'],['PC',false,26,'⚖️'],['PC',false,27,'✅'],['PC',true,115,'⚖️'],['PC',false,126,'⚖️']];
let fail=0;
for(const [p,on,d,exp] of cases){const got=E[outcome(p,on,d).verdict]; const ok=got===exp; if(!ok)fail++; console.log(ok?'PASS':'FAIL',p,on?'on':'off',d,got,exp);}
// scene schedule: typed times and gate for P→C (aTyped = p, bTyped = c, gate = p + 10)
const sch=html.split('/* ===== SCHEDULE')[1].split('/* ===== VIEW')[0];
const schedule=new Function(src+'/*'+sch+';return schedule;')();
const S=[[false,7,7,7,17],[false,15,15,15,25],[false,30,16,30,26],[true,7,11,11,21],[true,15,15,26,25],[true,30,16,41,26]];
for(const [on,d,pT,cT,g] of S){const s=schedule('PC',on,d); const ok=s.aTyped===pT&&s.bTyped===cT&&s.gate===g; if(!ok)fail++;
  console.log(ok?'PASS':'FAIL','schedule PC',on?'on':'off',d,'p',s.aTyped,'c',s.bTyped,'gate',s.gate,'(want',pT,cT,g+')');}
// band summary
function bands(p,on){let r=[],st=0,c=x=>outcome(p,on,x).verdict;for(let d=1;d<=131;d++){if(d===131||c(d)!==c(st)){r.push(E[c(st)]+' '+st+(d-1>st?'-'+(d-1):''));st=d;}}return r.join(' · ');}
for(const p of ['MT','PC'])for(const on of [true,false])console.log(p,on?'ON ':'OFF',bands(p,on));
process.exit(fail?1:0);
