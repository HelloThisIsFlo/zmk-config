const fs=require('fs');
const html=fs.readFileSync(__dirname+'/D10.html','utf8');
const src=html.split('// BEGIN outcome')[1].split('// END outcome')[0];
const wsrc=html.split('// BEGIN word')[1].split('// END word')[0];
const {PAIRS,outcome,typedWord}=new Function(src+wsrc+';return {PAIRS,outcome,typedWord};')();
const E={ok:'✅',bad:'❌',wait:'⏸',tie:'⚖️'};
const cases=[['MT',true,5,'❌'],['MT',true,10,'⏸'],['MT',true,11,'✅'],['MT',true,110,'⚖️'],['MT',true,111,'❌'],['MT',false,5,'✅'],['PC',false,25,'❌'],['PC',false,26,'⚖️'],['PC',false,27,'✅'],['PC',true,115,'⚖️'],['PC',false,126,'⚖️']];
let fail=0;
for(const [p,on,d,exp] of cases){const got=E[outcome(p,on,d).verdict]; const ok=got===exp; if(!ok)fail++; console.log(ok?'PASS':'FAIL',p,on?'on':'off',d,got,exp);}
// rendered word
const WORD={PC:'kept',MT:'column'};
const words=[['PC',true,15,'kept'],['PC',false,15,'kepc'],['PC',false,30,'kept'],['MT',true,7,'columt'],['MT',false,7,'column']];
for(const [p,on,d,exp] of words){const got=typedWord(WORD[p],on,d).text; const ok=got===exp; if(!ok)fail++; console.log(ok?'PASS':'FAIL','word',p,on?'on':'off',d,got,exp);}
// band summary
function bands(p,on){let r=[],st=0,c=x=>outcome(p,on,x).verdict;for(let d=1;d<=131;d++){if(d===131||c(d)!==c(st)){r.push(E[c(st)]+' '+st+(d-1>st?'-'+(d-1):''));st=d;}}return r.join(' · ');}
for(const p of ['MT','PC'])for(const on of [true,false])console.log(p,on?'ON ':'OFF',bands(p,on));
process.exit(fail?1:0);
