const fs=require('fs');
const html=fs.readFileSync(__dirname+'/D7.html','utf8');
const src=html.split('// BEGIN outcome')[1].split('// END outcome')[0];
const {PAIRS,outcome}=new Function(src+';return {PAIRS,outcome};')();
const E={ok:'✅',bad:'❌',wait:'⏸',tie:'⚖️'};
const cases=[['MT',true,5,'❌'],['MT',true,10,'⏸'],['MT',true,11,'✅'],['MT',true,110,'⚖️'],['MT',true,111,'❌'],['MT',false,5,'✅'],['PC',false,25,'❌'],['PC',false,26,'⚖️'],['PC',false,27,'✅'],['PC',true,115,'⚖️'],['PC',false,126,'⚖️']];
let fail=0;
for(const [p,on,d,exp] of cases){const got=E[outcome(PAIRS[p],on,d).verdict]; const ok=got===exp; if(!ok)fail++; console.log(ok?'PASS':'FAIL',p,on?'on':'off',d,got,exp);}
// band summary
function bands(p,on){let r=[],st=0,c=x=>outcome(PAIRS[p],on,x).verdict;for(let d=1;d<=131;d++){if(d===131||c(d)!==c(st)){r.push(E[c(st)]+' '+st+(d-1>st?'-'+(d-1):''));st=d;}}return r.join(' · ');}
for(const p of ['MT','PC'])for(const on of [true,false])console.log(p,on?'ON ':'OFF',bands(p,on));
process.exit(fail?1:0);
