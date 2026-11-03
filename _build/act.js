/* ===== lesson activities: one clear task, immediate feedback ===== */
(function(){
const n=s=>`<span class="n">${s}</span>`;
const fm=(x,d=0)=>(x<0?'−':'')+Math.abs(x).toLocaleString('en-US',{minimumFractionDigits:d,maximumFractionDigits:d});
const cfg=b=>JSON.parse(b.dataset.cfg);const cfg0=cfg;
const say=(el,ok,html)=>{el.className='fbbar '+(ok===true?'good':ok===false?'wrong':'');el.innerHTML=html;};
const num=s=>{s=String(s).replace(/[,\s]/g,'').replace('−','-');return s===''?NaN:Number(s);};

/* ---------- shared chart drawing, same look as the static charts ---------- */
const fg=x=>(x<0?'−':'')+Math.abs(x).toLocaleString('en-US',{maximumFractionDigits:2});
function frame(c){const W=c.W||640,H=c.H||400,ml=Math.max(58,14+Math.max(...c.yt.map(t=>fg(t).length))*9.5),mr=18,mt=30,mb=46,X=v=>ml+(v-c.x0)/(c.x1-c.x0)*(W-ml-mr),Y=v=>mt+(c.y1-v)/(c.y1-c.y0)*(H-mt-mb);
 const tx=(x,y,t,o={})=>{const he=/[֐-׿]/.test(t);let a=o.a||'middle';if(he)a={start:'end',end:'start',middle:'middle'}[a];return `<text x="${x}" y="${y}" font-size="${o.fs||16}" text-anchor="${a}" fill="${o.fill||'#5d6a86'}" font-weight="${o.w||500}"${he?' direction="rtl"':''}>${t}</text>`;};
 let p=`<rect x="${ml}" y="${mt}" width="${W-ml-mr}" height="${H-mt-mb}" fill="#fff"/>`;
 c.yt.forEach(t=>{p+=`<line x1="${ml}" y1="${Y(t)}" x2="${W-mr}" y2="${Y(t)}" stroke="${t===0?'#1b2d55':'#e8e2d4'}" stroke-width="${t===0?2.2:1}"/>`+tx(ml-7,Y(t)+5,fg(t),{a:'end'});});
 c.xt.forEach(t=>{p+=`<line x1="${X(t)}" y1="${mt}" x2="${X(t)}" y2="${H-mb}" stroke="#f0ebe0"/>`+tx(X(t),H-mb+19,fg(t));});
 if(c.xl)p+=tx((ml+W-mr)/2,H-5,c.xl,{w:700,fill:'#2a3858'});
 if(c.yl)p+=tx(8,mt-11,c.yl,{a:'start',w:700,fill:'#2a3858',fs:15});
 return {W,H,X,Y,tx,p,ml,mr,mt,mb,id:c.id};}
const line=(f,pts,col,w,dash)=>`<polyline points="${pts.map(([a,b])=>f.X(a)+','+f.Y(Math.max(Math.min(b,1e6),-1e6))).join(' ')}" fill="none" stroke="${col}" stroke-width="${w||4}" stroke-linejoin="round"${dash?` stroke-dasharray="${dash}"`:''} clip-path="url(#clp${f.id})"/>`;
const clip=f=>`<clipPath id="clp${f.id}"><rect x="${f.ml}" y="${f.mt}" width="${f.W-f.ml-f.mr}" height="${f.H-f.mt-f.mb}"/></clipPath>`;

/* ---------- sorter: each row has one right answer ---------- */
$$('.sorter').forEach(b=>{const rows=$$('.srow',b),fb=$('.fbbar',b),sc=$('.score',b);
 const upd=()=>{const d=rows.filter(r=>r.classList.contains('solved')).length;sc.textContent=d+' / '+rows.length;if(d===rows.length)say(fb,true,'כל השורות נכונות. '+fb.innerHTML);};
 rows.forEach(r=>{const a=+r.dataset.a;$$('.so',r).forEach(o=>o.addEventListener('click',()=>{if(r.classList.contains('solved'))return;const i=+o.dataset.i;
  if(i===a){o.classList.add('ok');r.classList.add('solved');$$('.so',r).forEach(x=>x.classList.remove('bad'));say(fb,true,'<b>נכון.</b> '+r.dataset.w);upd();}
  else{o.classList.add('bad');say(fb,false,'<b>לא.</b> קראו שוב את השורה, ונסו אפשרות אחרת.');}}));});
 $('.rst',b).addEventListener('click',()=>{rows.forEach(r=>{r.classList.remove('solved');$$('.so',r).forEach(x=>x.classList.remove('ok','bad'));});say(fb,null,'בחרו תשובה בכל שורה.');sc.textContent='0 / '+rows.length;});});

/* ---------- numeric question ---------- */
$$('.numq').forEach(b=>{const a=+b.dataset.a,t=+b.dataset.tol,i=$('input',b),fb=$('.fbbar',b);
 const check=()=>{const v=num(i.value);if(!Number.isFinite(v)){say(fb,false,'הקלידו מספר.');return;}
  if(Math.abs(v-a)<=t){b.classList.add('solved');say(fb,true,'<b>נכון.</b> '+b.dataset.w);}else{b.classList.remove('solved');say(fb,false,'<b>לא.</b> '+b.dataset.h);}};
 $('.chk',b).addEventListener('click',check);i.addEventListener('keydown',e=>{if(e.key==='Enter')check();});});

/* ---------- live Excel inside a question, with a chart drawn from the student's own cells ---------- */
const nCell=a=>{const m=/^([A-Z]+)(\d+)$/.exec(a);return {L:m[1],r:+m[2]};};
const rangeCells=(a,b)=>{const A=nCell(a),B=nCell(b),o=[];for(let r=A.r;r<=B.r;r++)o.push(A.L+r);return o;};
$$('.xlq').forEach(b=>{const cfg=cfg0(b),host=$('.sheet',b),svg=$('svg.xlc',b);let api;
 const nice=(lo,hi,n)=>{const span=hi-lo||Math.abs(hi)||1,raw=span/n,mag=Math.pow(10,Math.floor(Math.log10(raw))),st=[1,2,2.5,5,10].map(m=>m*mag).find(s=>s>=raw);const a=Math.floor(lo/st)*st,b=Math.ceil(hi/st)*st,t=[];for(let v=a;v<=b+st/2;v+=st)t.push(+v.toFixed(8));return t;};
 const draw=()=>{if(!svg)return;const c=cfg.chart,xs=rangeCells(...c.x).map(a=>api.get(a));
  // the chart follows the sheet: axes widen to the prices and results the student types
  const ser=c.series.map(se=>rangeCells(...se.y).map(a=>api.get(a)));const nx=xs.filter(v=>typeof v==='number');const ny=[].concat(...ser.map((ys,k)=>ys.filter((v,i)=>typeof v==='number'&&typeof xs[i]==='number')));
  let x0=c.x0,x1=c.x1,y0=c.y0,y1=c.y1,xt=c.xt,yt=c.yt;
  if(nx.length>1){x0=Math.min(...nx);x1=Math.max(...nx);if(x0===x1){x0-=1;x1+=1;}const ux=[...new Set(nx)].sort((a,b)=>a-b);xt=ux.length<=7?ux:nice(x0,x1,5).filter(v=>v>=x0&&v<=x1);}
  if(ny.length){const lo=Math.min(0,...ny,c.y0),hi=Math.max(0,...ny,c.y1);yt=nice(lo,hi,5);y0=yt[0];y1=yt[yt.length-1];}
  const f=frame({id:b.id,x0,x1,y0,y1,xt,yt,W:c.W||470,H:c.H||330,xl:c.xl,yl:c.yl});let p=f.p+clip(f);
  const single=c.series.length===1;
  c.series.forEach((se,k)=>{const ys=ser[k];const pts=[];xs.forEach((x,i)=>{if(typeof x==='number'&&typeof ys[i]==='number')pts.push([x,ys[i]]);});pts.sort((a,b)=>a[0]-b[0]);
   if(pts.length>1)p+=line(f,pts,se.c,4);pts.forEach(([x,y])=>{p+=`<circle cx="${f.X(x)}" cy="${f.Y(y)}" r="5.5" fill="${se.c}"/>`;if(single&&pts.length<=7){const X=f.X(x),an=X>f.W-f.mr-40?'end':X<f.ml+40?'start':'middle';p+=f.tx(X+(an==='start'?6:an==='end'?-6:0),f.Y(y)+(y<0?22:-11),fg(y),{fill:se.c,w:800,fs:15,a:an});}});
   if(pts.length&&!single){const [x,y]=pts[pts.length-1];p+=f.tx(f.X(x)-8,f.Y(y)+(se.dy||-10),se.lab,{a:'end',fill:se.c,w:800,fs:17});}});
  if(single&&c.series[0].lab)p+=f.tx(f.W-f.mr-4,f.mt+16,c.series[0].lab,{a:'end',fill:c.series[0].c,w:800,fs:16});
  svg.innerHTML=p;};
 cfg.onChange=draw;api=XL.mount(host,cfg);host.__api=api;const fbx=$('.xl-fb',host);if(fbx)$('.xlside',b).appendChild(fbx);draw();});

/* ---------- worked exercise with hints, reminder, partial and full solution ---------- */
$$('.sv').forEach(b=>{const parts=$$('.svp',b),fb=$('.fbbar',b),sol=$$('.svs',b);let h=0;const H=cfg0(b);
 $('.chk',b).addEventListener('click',()=>{let bad=0;parts.forEach(p=>{const i=$('input',p),v=num(i.value),ok=Number.isFinite(v)&&Math.abs(v-+p.dataset.a)<=+p.dataset.tol;i.classList.toggle('good',ok);i.classList.toggle('badc',!ok);if(!ok)bad++;});
  if(!bad){b.classList.add('solved');say(fb,true,'<b>נכון.</b> כל הסעיפים נכונים.');}else{b.classList.remove('solved');say(fb,false,`<b>${n(bad)} מתוך ${n(parts.length)} סעיפים עדיין שגויים.</b> נסו רמז.`);}});
 $('.hnt',b).addEventListener('click',()=>{say(fb,null,`<b>רמז ${n(h%H.hints.length+1)} מתוך ${n(H.hints.length)}:</b> ${H.hints[h%H.hints.length]}`);h++;});
 $('.rmd',b).addEventListener('click',()=>say(fb,null,H.remind));
 $('.prt',b).addEventListener('click',()=>{sol.forEach((s,i)=>s.classList.toggle('on',i===0));say(fb,null,'הסעיף הראשון פתור למטה. המשיכו לבד.');});
 $('.ful',b).addEventListener('click',()=>{sol.forEach(s=>s.classList.add('on'));say(fb,null,'הפתרון המלא מוצג למטה.');});
 $('.rst',b).addEventListener('click',()=>{parts.forEach(p=>{const i=$('input',p);i.value='';i.classList.remove('good','badc');});sol.forEach(s=>s.classList.remove('on'));b.classList.remove('solved');h=0;say(fb,null,'הקלידו את התשובות, ולחצו ״בדיקה״.');});});
/* ---------- draw the profit line by dragging three points ---------- */
$$('.draw').forEach(b=>{const C=cfg(b),svg=$('svg',b),fb=$('.fbbar',b),tt=$('.tasktxt',b),xs=C.xs;let k=0,v=[],done=false,drag=-1;
 const ch={id:'d',x0:C.x0,x1:C.x1,y0:C.y0,y1:C.y1,xt:C.xt,yt:C.yt,W:640,H:430,xl:'מחיר נכס הבסיס בפקיעה',yl:'רווח או הפסד'};
 function paint(){const f=frame(ch);let p=f.p+clip(f);const T=C.tasks[k];
  p+=line(f,xs.map((x,i)=>[x,v[i]]),done?'#25a65f':'#ff6a4d',4.5);
  p+=`<line x1="${f.X(T.K)}" y1="${f.mt}" x2="${f.X(T.K)}" y2="${f.H-f.mb}" stroke="#6d4df2" stroke-width="1.6" stroke-dasharray="5 5"/>`+f.tx(f.X(T.K),f.mt+16,'K',{fill:'#6d4df2',w:800});
  xs.forEach((x,i)=>{const cx=f.X(x),cy=f.Y(v[i]);p+=`<g class="hd" data-i="${i}"><rect x="${cx-24}" y="${f.mt}" width="48" height="${f.H-f.mt-f.mb}" fill="transparent"/><circle cx="${cx}" cy="${cy}" r="12" fill="${done?'#25a65f':'#1b2d55'}" stroke="#fff" stroke-width="3"/>`+f.tx(cx+(i===xs.length-1?-20:20),cy-14,fm(v[i]),{fill:'#16213a',w:800,fs:18})+`</g>`;});
  svg.innerHTML=p;}
 function load(i){k=i;done=false;v=xs.map(()=>0);const T=C.tasks[k];tt.innerHTML=`<b>משימה ${n(k+1)} מתוך ${n(C.tasks.length)}:</b> ${T.t}`;say(fb,null,'גררו כל נקודה אנכית לערך הרווח או ההפסד במחיר שמתחתיה, ולחצו ״בדיקה״.');$('.nxt',b).disabled=true;paint();}
 const toY=e=>{const m=svg.getScreenCTM().inverse(),q=new DOMPoint(e.clientX,e.clientY).matrixTransform(m),f=frame(ch);const val=C.y1-(q.y-f.mt)/(f.H-f.mt-f.mb)*(C.y1-C.y0);return Math.max(C.y0,Math.min(C.y1,Math.round(val/C.snap)*C.snap));};
 svg.addEventListener('pointerdown',e=>{const g=e.target.closest('.hd');if(!g||done)return;drag=+g.dataset.i;svg.setPointerCapture&&svg.setPointerCapture(e.pointerId);v[drag]=toY(e);paint();e.preventDefault();});
 svg.addEventListener('pointermove',e=>{if(drag<0)return;v[drag]=toY(e);paint();});
 const up=()=>{drag=-1;};svg.addEventListener('pointerup',up);svg.addEventListener('pointercancel',up);
 $('.chk',b).addEventListener('click',()=>{const T=C.tasks[k],bad=xs.filter((x,i)=>v[i]!==T.pts[i]);
  if(!bad.length){done=true;b.dataset.solved=(+b.dataset.solved||0)+1;paint();say(fb,true,'<b>נכון.</b> '+T.w);$('.nxt',b).disabled=false;}
  else say(fb,false,`<b>עדיין לא.</b> בדקו את הנקודה במחיר ${bad.map(x=>n(x)).join(' ובמחיר ')}. ${T.h}`);});
 $('.nxt',b).addEventListener('click',()=>{if(k<C.tasks.length-1)load(k+1);else{say(fb,true,'סיימתם את כל המשימות. ארבע הפוזיציות הן שתי צורות בלבד: קו ושיקופו ביחס לציר.');$('.nxt',b).disabled=true;}});
 $('.rst',b).addEventListener('click',()=>load(k));
 b.__set=a=>{v=a.slice();paint();};b.__task=()=>k;load(0);});

})();
