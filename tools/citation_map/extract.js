const fs=require('fs');const html=fs.readFileSync(require('path').join(__dirname,'..','..','index.html'),'utf8');
const m=html.match(/const D = \[([\s\S]*?)\n\];/);const D=eval('['+m[1]+'\n]');
const counts={},seen={};D.forEach(d=>{if(d.num)counts[d.num]=(counts[d.num]||0)+1});
const en=f=>f==null?'':typeof f==='object'?f.en:f;const fr=f=>f==null?'':typeof f==='object'?(f.fr||f.en):f;
function gid(n,d,inNums){ if(/^RE\d/.test(n))return 'US'+n;
 if(/^[A-Z]{2,3}\d/.test(n)&&!/^D\d/.test(n))return n;
 if(/^D\d/.test(n))return 'USD'+n.slice(1);
 if(/^(19|20)\d{9}$/.test(n))return 'US'+n+'A1';
 if(!inNums&&d.pt==='design')return 'USD'+n;
 return 'US'+n;}
const out=[];D.forEach((d,i)=>{let ref;if(d.num){seen[d.num]=(seen[d.num]||0)+1;ref=counts[d.num]>1?`${d.num}-${seen[d.num]}`:d.num;}else ref=en(d.t).toLowerCase().replace(/\(.*?\)/g,"").replace(/[^a-z0-9]+/g,"-").replace(/^-|-$/g,"").slice(0,40);
 const ids=[];if(d.num)ids.push(gid(d.num,d,false));(d.nums||[]).forEach(n=>{const g=gid(n,d,true);if(!ids.includes(g))ids.push(g)});
 out.push({i,ref,t:en(d.t),tf:fr(d.t),cat:d.cat,y:d.y,st:d.st,np:!!d.np,who:d.who,ids,img:(d.imgs&&d.imgs[0]&&(d.imgs[0].src||d.imgs[0]))||d.img||null});});
fs.writeFileSync('atlas.json',JSON.stringify(out,null,0));
console.log(out.length,out.filter(o=>o.ids.length).length,out.reduce((a,o)=>a+o.ids.length,0));
const all=out.flatMap(o=>o.ids);console.log(all.filter(x=>/^[A-Z]/.test(x)&&!x.startsWith('US')).slice(0,40).join(' '));
