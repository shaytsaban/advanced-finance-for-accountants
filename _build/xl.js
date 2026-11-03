/* ===== mini Excel: a small spreadsheet that behaves like Hebrew (right-to-left) Excel ===== */
const esc=t=>String(t).replace(/[&<>]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;'}[c]));
const XL=(function(){
const colName=i=>{let s='';i++;while(i>0){const m=(i-1)%26;s=String.fromCharCode(65+m)+s;i=Math.floor((i-1)/26);}return s;};
const colIdx=L=>{let n=0;for(const ch of L)n=n*26+(ch.charCodeAt(0)-64);return n-1;};
const addr=(r,c)=>colName(c)+(r+1);
const parseAddr=a=>{const m=/^\$?([A-Z]+)\$?(\d+)$/.exec(a);return m?{r:+m[2]-1,c:colIdx(m[1])}:null;};
const ERR=e=>({err:e});const isErr=v=>v&&typeof v==='object'&&'err' in v;
const NUMRX=/^\s*-?(\d+(\.\d*)?|\.\d+)\s*%?\s*$/;

/* ---------- tokenizer and parser ---------- */
function tokenize(s){const T=[];let i=0;
 while(i<s.length){const ch=s[i];
  if(/\s/.test(ch)){i++;continue;}
  let m;
  if((m=/^(\d+(\.\d*)?|\.\d+)/.exec(s.slice(i)))){T.push({t:'num',v:parseFloat(m[1])});i+=m[1].length;continue;}
  if((m=/^(\$?[A-Za-z]{1,2}\$?\d+)(:\$?[A-Za-z]{1,2}\$?\d+)?/.exec(s.slice(i)))&&!/^[A-Za-z]+\(/.test(s.slice(i))){
   T.push(m[2]?{t:'range',a:m[1].toUpperCase(),b:m[2].slice(1).toUpperCase()}:{t:'ref',a:m[1].toUpperCase()});i+=m[0].length;continue;}
  if((m=/^([A-Za-z]+)\s*\(/.exec(s.slice(i)))){T.push({t:'fn',v:m[1].toUpperCase()});i+=m[0].length;continue;}
  if((m=/^(>=|<=|<>)/.exec(s.slice(i)))){T.push({t:'op',v:m[1]});i+=2;continue;}
  if('+-*/^%(),;<>='.includes(ch)){T.push({t:'op',v:ch===';'?',':ch});i++;continue;}
  if(ch==='"'){const j=s.indexOf('"',i+1);if(j<0)throw 'str';T.push({t:'str',v:s.slice(i+1,j)});i=j+1;continue;}
  throw 'bad';}
 return T;}
function parse(T){let p=0;const peek=()=>T[p],eat=v=>{if(T[p]&&T[p].t==='op'&&T[p].v===v){p++;return true;}return false;};
 function expr(){let n=add();for(const o of ['>=','<=','<>','>','<','=']){if(eat(o))return {k:'cmp',o,a:n,b:add()};}return n;}
 function add(){let n=term();for(;;){if(eat('+'))n={k:'+',a:n,b:term()};else if(eat('-'))n={k:'-',a:n,b:term()};else return n;}}
 function term(){let n=pow();for(;;){if(eat('*'))n={k:'*',a:n,b:pow()};else if(eat('/'))n={k:'/',a:n,b:pow()};else return n;}}
 function pow(){let n=unary();while(eat('^'))n={k:'^',a:n,b:unary()};return n;}
 function unary(){if(eat('-'))return {k:'neg',a:unary()};if(eat('+'))return unary();return post();}
 function post(){let n=prim();while(eat('%'))n={k:'pct',a:n};return n;}
 function prim(){const t=peek();if(!t)throw 'end';
  if(t.t==='num'){p++;return {k:'num',v:t.v};}
  if(t.t==='str'){p++;return {k:'str',v:t.v};}
  if(t.t==='ref'){p++;return {k:'ref',a:t.a};}
  if(t.t==='range'){p++;return {k:'range',a:t.a,b:t.b};}
  if(t.t==='fn'){p++;const args=[];if(!eat(')')){do{const nx=peek();if(nx&&nx.t==='op'&&(nx.v===','||nx.v===')'))args.push({k:'miss'});else args.push(expr());}while(eat(','));if(!eat(')'))throw 'paren';}return {k:'fn',f:t.v,args};}
  if(eat('(')){const n=expr();if(!eat(')'))throw 'paren';return n;}
  throw 'tok';}
 const n=expr();if(p<T.length)throw 'trail';return n;}


/* ---------- finance functions, with Excel's argument order and sign convention (money paid out is negative) ---------- */
const FIN=(function(){
 const E=e=>({err:e});
 const t01=t=>t?1:0;
 function PV(r,n,p,f,t){p=p||0;f=f||0;t=t01(t);if(r===0)return -(f+p*n);const q=Math.pow(1+r,n);return -(f+p*(1+r*t)*(q-1)/r)/q;}
 function FV(r,n,p,v,t){p=p||0;v=v||0;t=t01(t);if(r===0)return -(v+p*n);const q=Math.pow(1+r,n);return -(v*q+p*(1+r*t)*(q-1)/r);}
 function PMT(r,n,v,f,t){f=f||0;t=t01(t);if(n===0)return E('#NUM!');if(r===0)return -(v+f)/n;const q=Math.pow(1+r,n);return -(f+v*q)*r/((1+r*t)*(q-1));}
 function NPER(r,p,v,f,t){f=f||0;t=t01(t);if(r===0){if(p===0)return E('#NUM!');return -(v+f)/p;}const a=p*(1+r*t)-f*r,b=p*(1+r*t)+v*r;if(a/b<=0||r<=-1)return E('#NUM!');return Math.log(a/b)/Math.log(1+r);}
 /* a root by Newton steps, falling back to bisection on a bracket; returns null when there is no root */
 function root(F,g){let x=g;for(let i=0;i<300;i++){const fx=F(x);if(!isFinite(fx))break;const h=1e-7*Math.max(1,Math.abs(x)),d=(F(x+h)-F(x-h))/(2*h);if(!isFinite(d)||d===0)break;let nx=x-fx/d;if(nx<=-1)nx=(x-1)/2;if(Math.abs(nx-x)<1e-15*Math.max(1,Math.abs(x))){x=nx;return polish(F,x);}x=nx;}
  const xs=[-0.999999,-0.99,-0.9,-0.5,-0.2,-0.1,-0.05,0,0.01,0.02,0.05,0.1,0.2,0.5,1,2,5,10,100,1000];let lo=null,hi=null;
  for(let i=0;i+1<xs.length;i++){const a=F(xs[i]),b=F(xs[i+1]);if(isFinite(a)&&isFinite(b)&&a*b<=0){lo=xs[i];hi=xs[i+1];break;}}
  if(lo===null)return null;let flo=F(lo);for(let i=0;i<300;i++){const m=(lo+hi)/2,fm=F(m);if(fm===0||hi-lo<1e-16)return m;if(flo*fm<0)hi=m;else{lo=m;flo=fm;}}return (lo+hi)/2;}
 function polish(F,x){for(let i=0;i<3;i++){const h=1e-8*Math.max(1,Math.abs(x)),d=(F(x+h)-F(x-h))/(2*h);if(!d)break;const nx=x-F(x)/d;if(!isFinite(nx))break;x=nx;}return x;}
 function RATE(n,p,v,f,t,g){p=p||0;f=f||0;t=t01(t);const F=r=>Math.abs(r)<1e-12?v+p*n+f:v*Math.pow(1+r,n)+p*(1+r*t)*(Math.pow(1+r,n)-1)/r+f;const x=root(F,g==null?0.1:g);return x===null?E('#NUM!'):x;}
 function NPV(r,vals){if(r===-1)return E('#DIV/0!');let s=0;vals.forEach((v,i)=>{s+=v/Math.pow(1+r,i+1);});return s;}
 function IRR(vals,g){if(!vals.some(v=>v>0)||!vals.some(v=>v<0))return E('#NUM!');const F=r=>vals.reduce((s,v,i)=>s+v/Math.pow(1+r,i),0);const x=root(F,g==null?0.1:g);return x===null?E('#NUM!'):x;}
 function XNPV(r,vals,dates){if(vals.length!==dates.length||!vals.length)return E('#NUM!');const d0=dates[0];let s=0;for(let i=0;i<vals.length;i++){if(dates[i]<d0)return E('#NUM!');s+=vals[i]/Math.pow(1+r,(dates[i]-d0)/365);}return s;}
 function XIRR(vals,dates,g){if(vals.length!==dates.length||!vals.some(v=>v>0)||!vals.some(v=>v<0))return E('#NUM!');const d0=dates[0];const F=r=>vals.reduce((s,v,i)=>s+v/Math.pow(1+r,(dates[i]-d0)/365),0);const x=root(F,g==null?0.1:g);return x===null?E('#NUM!'):x;}
 /* Excel date serial: days since 30.12.1899 */
 function DATE(y,m,d){y=Math.trunc(y);if(y<1900)y+=1900;return Math.round((Date.UTC(y,Math.trunc(m)-1,Math.trunc(d))-Date.UTC(1899,11,30))/864e5);}
 function ROUND(x,d){d=Math.trunc(d||0);const k=Math.pow(10,d);const y=Math.abs(x)*k;const r=Math.round(y+1e-9*Math.max(1,y));return Math.sign(x)*r/k;}
 return {PV,FV,PMT,NPER,RATE,NPV,IRR,XNPV,XIRR,DATE,ROUND};})();

/* ---------- a sheet ---------- */
function Sheet(rows,cols){this.rows=rows;this.cols=cols;this.raw={};this.fmt={};this.val={};}
Sheet.prototype.set=function(a,raw){if(raw===''||raw==null)delete this.raw[a];else this.raw[a]=String(raw);};
Sheet.prototype.recalc=function(){const S=this,memo={},busy={};
 function cellv(a){if(a in memo)return memo[a];const pa=parseAddr(a);if(!pa||pa.r>=S.rows||pa.c>=S.cols&&pa.c>25)return ERR('#REF!');
  if(busy[a])return ERR('#CIRC!');busy[a]=1;let v;const raw=S.raw[a];
  if(raw==null)v=null;else if(raw[0]==='='){try{v=ev(parse(tokenize(raw.slice(1))));if(v==null)v=0;}catch(e){v=ERR(e==='bad'||e==='tok'?'#NAME?':'#ERROR!');}}
  else if(NUMRX.test(raw)){const pc=raw.includes('%');v=parseFloat(raw.replace('%',''))/(pc?100:1);}
  else v=raw;
  busy[a]=0;memo[a]=v;return v;}
 function rng(a,b){const A=parseAddr(a),B=parseAddr(b);const out=[];for(let r=Math.min(A.r,B.r);r<=Math.max(A.r,B.r);r++)for(let c=Math.min(A.c,B.c);c<=Math.max(A.c,B.c);c++)out.push(cellv(addr(r,c)));return out;}
 function num(v){if(isErr(v))return v;if(v==null)return 0;if(typeof v==='number')return v;return ERR('#VALUE!');}
 function ev(n){switch(n.k){
  case 'num':return n.v; case 'str':return n.v;
  case 'ref':return cellv(n.a.replace(/\$/g,''));
  case 'range':return ERR('#VALUE!');
  case 'neg':{const a=num(ev(n.a));return isErr(a)?a:-a;}
  case 'pct':{const a=num(ev(n.a));return isErr(a)?a:a/100;}
  case 'cmp':{const a=num(ev(n.a)),b=num(ev(n.b));if(isErr(a))return a;if(isErr(b))return b;return {'>=':a>=b,'<=':a<=b,'<>':a!==b,'>':a>b,'<':a<b,'=':a===b}[n.o];}
  case 'miss':return null;
  case 'fn':{const F=n.f,A=n.args;
   /* finance and math functions: scalar arguments, or a list of numbers from ranges */
   const sc=i=>{const x=A[i];if(!x||x.k==='miss')return undefined;if(x.k==='range')return ERR('#VALUE!');const v=ev(x);if(v===true)return 1;if(v===false)return 0;return num(v);};
   const list=(i,e)=>{const out=[];for(let j=i;j<(e==null?A.length:e);j++){const x=A[j];if(x.k==='miss')continue;if(x.k==='range'){for(const v of rng(x.a.replace(/\$/g,''),x.b.replace(/\$/g,''))){if(isErr(v))return v;if(typeof v==='number')out.push(v);}}else{const v=ev(x);if(isErr(v))return v;if(typeof v==='number')out.push(v);else if(v!=null&&v!==''&&typeof v!=='boolean')return ERR('#VALUE!');}}return out;};
   const SIG={PV:[3,5],FV:[3,5],PMT:[3,5],NPER:[3,5],RATE:[3,6],ROUND:[2,2],POWER:[2,2],SQRT:[1,1],LN:[1,1],EXP:[1,1],DATE:[3,3],EFFECT:[2,2],NOMINAL:[2,2]};
   if(SIG[F]){const [lo,hi]=SIG[F];if(A.length<lo||A.length>hi)return ERR('#N/A');const v=[];for(let i=0;i<A.length;i++){const x=sc(i);if(isErr(x))return x;v.push(x);}
    for(let i=0;i<lo;i++)if(v[i]===undefined)v[i]=0;   /* an empty argument counts as 0, as in Excel */
    let r;switch(F){case 'PV':r=FIN.PV(v[0],v[1],v[2],v[3],v[4]);break;case 'FV':r=FIN.FV(v[0],v[1],v[2],v[3],v[4]);break;case 'PMT':r=FIN.PMT(v[0],v[1],v[2],v[3],v[4]);break;
     case 'NPER':r=FIN.NPER(v[0],v[1],v[2],v[3],v[4]);break;case 'RATE':r=FIN.RATE(v[0],v[1],v[2],v[3],v[4],v[5]);break;case 'ROUND':r=FIN.ROUND(v[0],v[1]);break;
     case 'POWER':r=Math.pow(v[0],v[1]);break;case 'SQRT':r=v[0]<0?ERR('#NUM!'):Math.sqrt(v[0]);break;case 'LN':r=v[0]<=0?ERR('#NUM!'):Math.log(v[0]);break;case 'EXP':r=Math.exp(v[0]);break;
     case 'DATE':r=FIN.DATE(v[0],v[1],v[2]);break;case 'EFFECT':r=v[1]<1||v[0]<=0?ERR('#NUM!'):Math.pow(1+v[0]/Math.trunc(v[1]),Math.trunc(v[1]))-1;break;case 'NOMINAL':r=v[1]<1||v[0]<=0?ERR('#NUM!'):Math.trunc(v[1])*(Math.pow(1+v[0],1/Math.trunc(v[1]))-1);break;}
    if(typeof r==='number'&&!isFinite(r))return ERR('#NUM!');return r;}
   if(F==='NPV'){if(A.length<2)return ERR('#N/A');const r=sc(0);if(isErr(r))return r;const L=list(1);if(isErr(L))return L;return FIN.NPV(r||0,L);}
   if(F==='IRR'){if(!A.length||A.length>2)return ERR('#N/A');const L=list(0,1);if(isErr(L))return L;const g=A[1]?sc(1):undefined;if(isErr(g))return g;return FIN.IRR(L,g);}
   if(F==='XNPV'||F==='XIRR'){const x=F==='XNPV';if(A.length<(x?3:2)||A.length>3)return ERR('#N/A');const L=list(x?1:0,x?2:1),D=list(x?2:1,x?3:2);if(isErr(L))return L;if(isErr(D))return D;
    if(x){const r=sc(0);if(isErr(r))return r;return FIN.XNPV(r||0,L,D);}const g=A[2]?sc(2):undefined;return FIN.XIRR(L,D,g);}
   if(F==='SUMPRODUCT'){const ls=A.map(x=>x.k==='range'?rng(x.a.replace(/\$/g,''),x.b.replace(/\$/g,'')):[ev(x)]);if(ls.some(l=>l.length!==ls[0].length))return ERR('#VALUE!');let s=0;for(let i=0;i<ls[0].length;i++){let p=1;for(const l of ls){const v=l[i];if(isErr(v))return v;p*=typeof v==='number'?v:0;}s+=p;}return s;}
   if(n.f==='IF'){if(n.args.length<2)return ERR('#N/A');const c=ev(n.args[0]);if(isErr(c))return c;return c?ev(n.args[1]):(n.args[2]?ev(n.args[2]):false);}
   if(n.f==='ABS'){const a=num(ev(n.args[0]));return isErr(a)?a:Math.abs(a);}
   const vals=[];for(const x of n.args){if(x.k==='range')vals.push(...rng(x.a.replace(/\$/g,''),x.b.replace(/\$/g,'')).map(v=>({v,inRange:true})));else vals.push({v:ev(x),inRange:false});}
   const e=vals.find(o=>isErr(o.v));if(e&&n.f!=='COUNTA'&&n.f!=='COUNT')return e.v;
   const nums=vals.filter(o=>typeof o.v==='number'||(!o.inRange&&o.v==null)).map(o=>o.v||0);
   switch(n.f){case 'SUM':return nums.reduce((s,x)=>s+x,0);
    case 'AVERAGE':return nums.length?nums.reduce((s,x)=>s+x,0)/nums.length:ERR('#DIV/0!');
    case 'MIN':return nums.length?Math.min(...nums):0; case 'MAX':return nums.length?Math.max(...nums):0;
    case 'COUNT':return vals.filter(o=>typeof o.v==='number').length;
    case 'COUNTA':return vals.filter(o=>o.v!=null&&o.v!=='').length;
    default:return ERR('#NAME?');}}
  default:{const a=num(ev(n.a)),b=num(ev(n.b));if(isErr(a))return a;if(isErr(b))return b;
   if(n.k==='+')return a+b;if(n.k==='-')return a-b;if(n.k==='*')return a*b;if(n.k==='/')return b===0?ERR('#DIV/0!'):a/b;if(n.k==='^')return Math.pow(a,b);}}}
 for(let r=0;r<S.rows;r++)for(let c=0;c<S.cols;c++)cellv(addr(r,c));
 Object.keys(S.raw).forEach(cellv);this.val=memo;};

/* shift every relative reference in a formula by (dr,dc), the way Excel does when a formula is dragged or pasted */
function shift(raw,dr,dc){if(!raw||raw[0]!=='=')return raw;
 return '='+raw.slice(1).replace(/("[^"]*")|(\$?)([A-Za-z]{1,2})(\$?)(\d+)(?![\d(A-Za-z])/g,(m,str,d1,L,d2,R)=>{if(str)return str;
  let c=colIdx(L.toUpperCase()),r=+R-1;if(!d1)c+=dc;if(!d2)r+=dr;if(c<0||r<0)return '#REF!';return d1+colName(c)+d2+(r+1);});}

const fmtNum=(v,f)=>{if(f==='gen')f='';const fd=/^(pct|num)(\d)$/.exec(f||'');if(fd){const d=+fd[2];const x=fd[1]==='pct'?v*100:v;const t=x.toLocaleString('en-US',{minimumFractionDigits:d,maximumFractionDigits:d}).replace('-','−');return fd[1]==='pct'?t+'%':t;}
 if(f==='pct'){const x=Math.round(v*100*100)/100;return x+'%';}
 if(Math.abs(v)>=1e11)return v.toExponential(4);const x=Math.round(v*1e6)/1e6;
 return x.toLocaleString('en-US',{maximumFractionDigits:2}).replace('-','−');};
function display(S,a){const v=S.val[a];if(v==null)return {t:'',n:false};if(isErr(v))return {t:v.err,n:false,e:true};
 if(typeof v==='number'){const raw=S.raw[a]||'';const f=S.fmt[a]||(raw[0]!=='='&&raw.includes('%')?'pct':'');return {t:fmtNum(v,f),n:true};}
 return {t:String(v),n:false};}

/* ---------- the widget ---------- */
let CLIP=null;
function mount(host,cfg){
 const R=cfg.rows,C=cfg.cols,R0=(cfg.r0||1)-1;const S=new Sheet(R,C);
 /* a template built click by click (the first exercise): the label cells of each group appear on the deck's next key */
 const BL=cfg.build||[];let bk=0;
 const baseNow=()=>{const d={...cfg.data};BL.slice(0,bk).forEach(st=>st.cells.forEach(a=>{d[a]=cfg.bdata[a];}));return d;};
 let base=baseNow();
 const load=()=>{base=baseNow();S.raw={};S.fmt={...(cfg.fmt||{})};Object.entries(base).forEach(([a,v])=>S.set(a,v));S.recalc();};load();
 const W=cfg.widths||[];
 host.classList.add('xl');
 host.innerHTML=`<div class="xl-top"><div class="xl-name" title="תיבת השם">A1</div><div class="xl-fx">fx</div><input class="xl-bar" dir="auto" spellcheck="false" autocomplete="off"></div>
  <div class="xl-tools">${cfg.tools===false?'':`<button data-x="formulas" title="הצגת נוסחאות">נוסחאות</button>`}${cfg.targets?`<button data-x="check" class="xl-go">✔ בדיקה</button>${cfg.steps?'<button data-x="step" class="xl-st">▶ צעד אחר צעד</button>':''}${cfg.hints?'<button data-x="hint">💡 רמז</button>':''}${cfg.remind?'<button data-x="remind">📐 תזכורת נוסחה</button>':''}${cfg.partial?'<button data-x="part">פתרון חלקי</button>':''}<button data-x="solve">פתרון מלא</button>`:''}<button data-x="reset">איפוס</button><span class="xl-msg"></span></div>
  <div class="xl-wrap"${cfg.maxh?` style="max-height:${cfg.maxh}px"`:''}><table class="xl-g" tabindex="0"><thead><tr><th class="xl-c0"></th>${Array.from({length:C},(_,c)=>`<th style="width:${W[c]||92}px">${colName(c)}</th>`).join('')}</tr></thead><tbody>${Array.from({length:R-R0},(_,k)=>k+R0).map(r=>`<tr><th class="xl-rn">${r+1}</th>${Array.from({length:C},(_,c)=>`<td data-a="${addr(r,c)}"></td>`).join('')}</tr>`).join('')}</tbody></table></div>
  ${cfg.targets?'<div class="xl-fb"></div>':''}`;
 const g=host.querySelector('.xl-g'),bar=host.querySelector('.xl-bar'),nameB=host.querySelector('.xl-name'),msg=host.querySelector('.xl-msg'),fb=host.querySelector('.xl-fb');
 /* hidden text sink: catches typing from on-screen keyboards and IMEs that send input events without a usable key */
 const sink=document.createElement('textarea');sink.className='xl-sink';sink.setAttribute('aria-hidden','true');sink.tabIndex=-1;sink.spellcheck=false;host.appendChild(sink);
 const focusG=()=>sink.focus({preventScroll:true});
 sink.addEventListener('input',()=>{const v=sink.value;sink.value='';if(!editing&&v)startEdit(v.trim()===''?'':v,false);});
 const td=a=>g.querySelector(`td[data-a="${a}"]`);
 const setFb=h=>{if(!fb)return;fb.innerHTML=h;if(cfg.onFb)cfg.onFb();};
 let sel={r:R0,c:0},sel2={r:R0,c:0},editing=null,showF=false,marks={},hintN=0;
 const inSel=(r,c)=>r>=Math.min(sel.r,sel2.r)&&r<=Math.max(sel.r,sel2.r)&&c>=Math.min(sel.c,sel2.c)&&c<=Math.max(sel.c,sel2.c);
 const selName=()=>sel.r===sel2.r&&sel.c===sel2.c?addr(sel.r,sel.c):addr(Math.min(sel.r,sel2.r),Math.min(sel.c,sel2.c))+':'+addr(Math.max(sel.r,sel2.r),Math.max(sel.c,sel2.c));
 function render(){S.recalc();
  g.querySelectorAll('td').forEach(el=>{const a=el.dataset.a;if(editing&&editing.a===a)return;const p=parseAddr(a);if(el.dataset.rf){el.style.boxShadow='';el.style.backgroundColor='';delete el.dataset.rf;}
   const raw=S.raw[a];let d=display(S,a);if(showF&&raw&&raw[0]==='=')d={t:raw,n:false,f:true};
   el.className=(d.n?'n':'')+(d.f?' f':'')+(d.e?' e':'')+(inSel(p.r,p.c)?' sel':'')+(p.r===sel.r&&p.c===sel.c?' act':'')+(cfg.inputs&&cfg.inputs.includes(a)?' in':'')+(cfg.targets&&cfg.targets.includes(a)?' tg':'')+(marks[a]?' '+marks[a]:'')+(cfg.headRows&&cfg.headRows.includes(p.r+1)?' hd':'');
   /* freeze the table's header row in a scrolling sheet, like Freeze Panes */
   if(cfg.maxh&&cfg.headRows&&cfg.headRows.length&&p.r+1===cfg.headRows[0]){el.classList.add('frz');el.style.top=g.tHead.offsetHeight+'px';const rn=el.parentElement.firstElementChild;rn.classList.add('frz');rn.style.top=el.style.top;}
   el.innerHTML=(d.n||d.f?`<span dir="ltr">${esc(d.t)}</span>`:esc(d.t))+(p.r===Math.max(sel.r,sel2.r)&&p.c===Math.max(sel.c,sel2.c)&&!editing?'<i class="xl-fh"></i>':'');});
  const ae=td(addr(sel.r,sel.c));if(ae&&cfg.maxh)keepVisible(ae);
  g.querySelectorAll('th.hs').forEach(x=>x.classList.remove('hs'));const hr=g.tHead.rows[0].cells;for(let c=Math.min(sel.c,sel2.c);c<=Math.max(sel.c,sel2.c);c++)hr[c+1].classList.add('hs');
  g.querySelectorAll('tbody th.xl-rn').forEach(th=>{const r=+th.textContent-1;if(r>=Math.min(sel.r,sel2.r)&&r<=Math.max(sel.r,sel2.r))th.classList.add('hs');});
  nameB.textContent=selName();if(!editing||editing.where!=='bar')bar.value=S.raw[addr(sel.r,sel.c)]||'';
  if(cfg.onSelect)cfg.onSelect(selName());}
 /* ---------- editing, as in Excel: Enter mode (typing) and Edit mode (F2 or double click); references are coloured while a formula is written ---------- */
 const RC=['#1a73e8','#d93025','#8e24aa','#188038','#e37400','#00838f','#c2185b'];
 const REFRX=/("[^"]*")|(\$?[A-Za-z]{1,2}\$?\d+(?::\$?[A-Za-z]{1,2}\$?\d+)?)(?![\d(A-Za-z])/g;
 function refsOf(v){const out=[],col={};if(!v||v[0]!=='=')return out;let m;REFRX.lastIndex=0;
  while((m=REFRX.exec(v))){if(m[1])continue;const t=m[2],k=t.replace(/\$/g,'').toUpperCase();if(m.index>0&&/[A-Za-z_]/.test(v[m.index-1]))continue;
   if(!(k in col))col[k]=RC[Object.keys(col).length%RC.length];out.push({i:m.index,t,k,c:col[k]});}return out;}
 const tint=c=>c+'1f';
 function paintRefs(){g.querySelectorAll('td[data-rf]').forEach(el=>{el.style.boxShadow='';el.style.backgroundColor='';el.classList.remove('ptr');delete el.dataset.rf;});
  const inp=curInput();if(!inp)return;const done={};
  refsOf(inp.value).forEach(f=>{if(done[f.k])return;done[f.k]=1;const [a,b]=f.k.split(':'),A=parseAddr(a),B=parseAddr(b||a);if(!A||!B)return;
   const r0=Math.min(A.r,B.r),r1=Math.max(A.r,B.r),c0=Math.min(A.c,B.c),c1=Math.max(A.c,B.c);
   for(let r=r0;r<=r1;r++)for(let c=c0;c<=c1;c++){const el=td(addr(r,c));if(!el||(editing&&editing.a===addr(r,c)))continue;
    /* the sheet runs right to left: the lowest column is on the right edge */
    const sh=[];if(r===r0)sh.push(`inset 0 2px 0 ${f.c}`);if(r===r1)sh.push(`inset 0 -2px 0 ${f.c}`);if(c===c0)sh.push(`inset -2px 0 0 ${f.c}`);if(c===c1)sh.push(`inset 2px 0 0 ${f.c}`);
    el.style.boxShadow=sh.join(',');el.style.backgroundColor=tint(f.c);el.dataset.rf='1';}
   if(editing&&editing.ptr&&editing.ptr.start===f.i){const el=td(addr(r0,c0));if(el)el.classList.add('ptr');}});}
 /* the coloured text: an overlay that shows the same characters as the input, which is drawn transparent */
 function colourise(inp,ov){const v=inp.value,fs=refsOf(v);
  if(!fs.length||inp.scrollWidth>inp.clientWidth+1){ov.innerHTML='';inp.classList.remove('xl-clr');return;}
  let h='',k=0;fs.forEach(f=>{h+=esc(v.slice(k,f.i))+`<span style="color:${f.c}">${esc(f.t)}</span>`;k=f.i+f.t.length;});h+=esc(v.slice(k));
  ov.innerHTML=h;ov.style.direction=getComputedStyle(inp).direction;inp.classList.add('xl-clr');}
 const barOv=document.createElement('div');barOv.className='xl-ov xl-bov';bar.parentNode.insertBefore(barOv,bar);
 function sync(){const inp=curInput();if(!inp)return;if(inp!==bar)bar.value=inp.value;else{const el=td(editing.a).querySelector('input');if(el)el.value=bar.value;}
  const ci=td(editing.a).querySelector('input');if(ci){fitEditor(ci);colourise(ci,ci.previousSibling);}Object.assign(barOv.style,{left:bar.offsetLeft+'px',top:bar.offsetTop+'px',width:bar.offsetWidth+'px',height:bar.offsetHeight+'px'});colourise(bar,barOv);barOv.scrollLeft=bar.scrollLeft;paintRefs();}
 const meas=document.createElement('canvas').getContext('2d');
 function fitEditor(inp){meas.font=getComputedStyle(inp).font;const w=Math.ceil(meas.measureText(inp.value).width)+18;const box=inp.parentNode;box.style.width=Math.max(box.parentNode.clientWidth,w)+'px';}
 /* scroll the sheet so the cell is below the frozen headers and above the bottom edge; positions are measured against the scroll area (the stage is scaled) */
 function keepVisible(el){const w=host.querySelector('.xl-wrap'),wr=w.getBoundingClientRect(),k=wr.height/w.offsetHeight||1,r=el.getBoundingClientRect();
  const fr=g.querySelector('td.frz'),hb=g.tHead.offsetHeight+(fr&&fr!==el&&!fr.parentElement.contains(el)?fr.offsetHeight:0);
  const top=(r.top-wr.top)/k+w.scrollTop,bot=(r.bottom-wr.top)/k+w.scrollTop;
  if(top<w.scrollTop+hb)w.scrollTop=Math.max(0,top-hb);else if(bot>w.scrollTop+w.clientHeight)w.scrollTop=bot-w.clientHeight;}
 function startEdit(initial,keep,mode){const a=addr(sel.r,sel.c);sel2={...sel};editing={a,where:'cell',orig:S.raw[a]||'',mode:mode||(keep?'edit':'enter'),ptr:null};const el=td(a);
  el.className+=' ed';el.innerHTML=`<div class="xl-ed"><div class="xl-ov" aria-hidden="true"></div><input class="xl-in" dir="auto" spellcheck="false" autocomplete="off"></div>`;const inp=el.querySelector('input');inp.value=keep?(S.raw[a]||''):initial;
  inp.focus({preventScroll:true});inp.setSelectionRange(inp.value.length,inp.value.length);
  inp.oninput=()=>{if(editing){editing.ptr=null;}sync();};inp.onkeydown=keyEdit;inp.onkeyup=inp.onclick=()=>sync();sync();modeTip();}
 function modeTip(){if(editing)toastX(editing.mode==='edit'?'מצב עריכה (F2): החצים מזיזים את הסמן':'מצב הזנה: אחרי אופרטור, החצים בוחרים תא');}
 function curInput(){return editing?(editing.where==='bar'?bar:td(editing.a).querySelector('input')):null;}
 function endEdit(){editing=null;barOv.innerHTML='';bar.classList.remove('xl-clr');g.querySelectorAll('td[data-rf]').forEach(el=>{el.style.boxShadow='';el.style.backgroundColor='';el.classList.remove('ptr');delete el.dataset.rf;});}
 function pctEntry(a,v){if(!/^pct/.test(S.fmt[a]||'')||!/^-?(\d+(\.\d*)?|\.\d+)$/.test(v))return v;const x=parseFloat(v);return Math.abs(x)>=1?v+'%':v;}
 function commit(dr,dc){if(!editing)return;const v=pctEntry(editing.a,curInput().value.trim());S.set(editing.a,v);endEdit();move(dr,dc);render();focusG();if(cfg.onChange)cfg.onChange();}
 function cancel(){endEdit();render();focusG();}
 function move(dr,dc){sel={r:Math.max(R0,Math.min(R-1,sel.r+dr)),c:Math.max(0,Math.min(C-1,sel.c+dc))};sel2={...sel};}
 const NAV={ArrowDown:[1,0],ArrowUp:[-1,0],ArrowLeft:[0,1],ArrowRight:[0,-1]};
 const refTxt=(A,B)=>!B||(A.r===B.r&&A.c===B.c)?addr(A.r,A.c):addr(Math.min(A.r,B.r),Math.min(A.c,B.c))+':'+addr(Math.max(A.r,B.r),Math.max(A.c,B.c));
 /* point mode: put or replace the reference that the arrows, a click or a drag point at */
 function pointTo(anchor,cur){const inp=curInput(),p=editing.ptr,t=refTxt(anchor,cur);let st;
  if(p){st=p.start;inp.value=inp.value.slice(0,st)+t+inp.value.slice(st+p.len);}else{st=inp.selectionStart;inp.value=inp.value.slice(0,st)+t+inp.value.slice(inp.selectionEnd);}
  editing.ptr={start:st,len:t.length,anchor,cur};inp.setSelectionRange(st+t.length,st+t.length);inp.focus({preventScroll:true});sync();}
 function keyEdit(e){e.stopPropagation();
  if(e.key==='Enter'){e.preventDefault();commit(e.shiftKey?-1:1,0);return;}
  if(e.key==='Tab'){e.preventDefault();commit(0,e.shiftKey?-1:1);return;}
  if(e.key==='Escape'){e.preventDefault();cancel();return;}
  if(e.key==='F2'){e.preventDefault();editing.mode=editing.mode==='edit'?'enter':'edit';editing.ptr=null;modeTip();return;}
  if(NAV[e.key]&&editing.mode==='enter'){e.preventDefault();const d=NAV[e.key],p=editing.ptr;
   const base=p?p.cur:parseAddr(editing.a),nx={r:Math.max(R0,Math.min(R-1,base.r+d[0])),c:Math.max(0,Math.min(C-1,base.c+d[1]))};
   if(p){pointTo(e.shiftKey?p.anchor:nx,nx);return;}
   if(pointable()){pointTo(nx,nx);return;}
   commit(d[0],d[1]);return;}
  if(e.key==='F4'){e.preventDefault();const inp=e.target,v=inp.value,p=inp.selectionStart,rx=/\$?[A-Za-z]{1,2}\$?\d+/g;let m,hit=null;
   while((m=rx.exec(v)))if(m.index<=p&&p<=m.index+m[0].length)hit=m;
   if(hit){const q=/^(\$?)([A-Za-z]{1,2})(\$?)(\d+)$/.exec(hit[0]),st=(q[1]?2:0)+(q[3]?1:0),nx={0:3,3:1,1:2,2:0}[st];
    const nr=(nx&2?'$':'')+q[2]+(nx&1?'$':'')+q[4];inp.value=v.slice(0,hit.index)+nr+v.slice(hit.index+hit[0].length);
    const np=hit.index+nr.length;inp.setSelectionRange(np,np);if(editing.ptr&&editing.ptr.start===hit.index)editing.ptr.len=nr.length;sync();}}}
 const pointable=()=>{const inp=curInput();if(!inp)return false;if(editing.ptr)return true;const v=inp.value.slice(0,inp.selectionStart).trimEnd();return v[0]==='='&&/[=+\-*/^(,:;<>&]$/.test(v);};
 function insertRef(a){const p=parseAddr(a);pointTo(p,p);toastX(`נוספה הפניה לתא ${a}`);}
 function toastX(t){msg.textContent=t;clearTimeout(toastX.t);toastX.t=setTimeout(()=>{if(msg.textContent===t)msg.textContent='';},1800);}
 /* pointer: select, drag a range, insert a reference while writing a formula, or drag the fill handle */
 let drag=null;
 g.addEventListener('pointerdown',e=>{const cell=e.target.closest('td');
  if(e.target.classList.contains('xl-fh')){e.preventDefault();drag={k:'fill',b:blk(),to:null};try{g.setPointerCapture(e.pointerId);}catch(_){}return;}
  if(!cell)return;const p=parseAddr(cell.dataset.a);
  if(editing&&editing.a===cell.dataset.a)return;
  if(editing&&pointable()){e.preventDefault();insertRef(cell.dataset.a);drag={k:'ptr',a:p};try{g.setPointerCapture(e.pointerId);}catch(_){}return;}
  if(editing)commit(0,0);
  e.preventDefault();sel={...p};sel2={...p};drag={k:'sel'};try{g.setPointerCapture(e.pointerId);}catch(_){}render();focusG();});
 g.addEventListener('pointermove',e=>{if(!drag)return;
  /* dragging past the top or bottom edge of a scrolling sheet scrolls it, as in Excel */
  let y=e.clientY;const w=host.querySelector('.xl-wrap'),wr=w.getBoundingClientRect(),k=wr.height/w.offsetHeight||1,top=wr.top+(g.tHead.offsetHeight+((g.querySelector('td.frz')||{}).offsetHeight||0))*k;
  if(w.scrollHeight>w.clientHeight){if(y>wr.bottom-6){w.scrollTop+=24;y=wr.bottom-8;}else if(y<top+4&&w.scrollTop>0){w.scrollTop-=24;y=top+6;}}
  const el=document.elementFromPoint(e.clientX,y);const cell=el&&el.closest&&el.closest('td');if(!cell||!g.contains(cell))return;const p=parseAddr(cell.dataset.a);
  if(drag.k==='sel'){sel2=p;render();}
  else if(drag.k==='ptr'){if(editing&&editing.ptr&&(p.r!==editing.ptr.cur.r||p.c!==editing.ptr.cur.c))pointTo(drag.a,p);}
  else{const b=drag.b;const dv=p.r>b.r1?p.r-b.r1:p.r<b.r0?b.r0-p.r:0,dh=p.c>b.c1?p.c-b.c1:p.c<b.c0?b.c0-p.c:0;
   const to=!dv&&!dh?null:dv>=dh?{r0:Math.min(b.r0,p.r),r1:Math.max(b.r1,p.r),c0:b.c0,c1:b.c1,v:1}:{r0:b.r0,r1:b.r1,c0:Math.min(b.c0,p.c),c1:Math.max(b.c1,p.c),v:0};drag.to=to;
   g.querySelectorAll('td.fillp').forEach(x=>x.classList.remove('fillp'));
   if(to)for(let r=to.r0;r<=to.r1;r++)for(let c=to.c0;c<=to.c1;c++)td(addr(r,c)).classList.add('fillp');}});
 g.addEventListener('pointerup',e=>{if(!drag)return;const d=drag;drag=null;try{g.releasePointerCapture(e.pointerId);}catch(_){}
  if(d.k==='fill'){g.querySelectorAll('td.fillp').forEach(x=>x.classList.remove('fillp'));if(d.to)fill(d.b,d.to);}});
 /* fill a selected block (one cell or several) down/up or sideways, repeating the block like Excel */
 function blk(){return{r0:Math.min(sel.r,sel2.r),r1:Math.max(sel.r,sel2.r),c0:Math.min(sel.c,sel2.c),c1:Math.max(sel.c,sel2.c)};}
 const md=(a,n)=>((a%n)+n)%n;
 const plainNum=x=>x!=null&&x!==''&&String(x)[0]!=='='&&NUMRX.test(String(x));
 function fill(b,to){const h=b.r1-b.r0+1,w=b.c1-b.c0+1;
  const series={};if(to.v&&h>1)for(let c=b.c0;c<=b.c1;c++){const vs=[];for(let r=b.r0;r<=b.r1;r++)vs.push(S.raw[addr(r,c)]);if(vs.every(plainNum)){const n=vs.map(x=>parseFloat(x));series[c]={a:n[0],st:(n[n.length-1]-n[0])/(n.length-1),pc:vs.every(x=>String(x).includes('%'))};}}
  if(!to.v&&w>1)for(let r=b.r0;r<=b.r1;r++){const vs=[];for(let c=b.c0;c<=b.c1;c++)vs.push(S.raw[addr(r,c)]);if(vs.every(plainNum)){const n=vs.map(x=>parseFloat(x));series['r'+r]={a:n[0],st:(n[n.length-1]-n[0])/(n.length-1),pc:vs.every(x=>String(x).includes('%'))};}}
  for(let r=to.r0;r<=to.r1;r++)for(let c=to.c0;c<=to.c1;c++){if(r>=b.r0&&r<=b.r1&&c>=b.c0&&c<=b.c1)continue;
   const sr=to.v?b.r0+md(r-b.r0,h):r,sc=to.v?c:b.c0+md(c-b.c0,w);const src=addr(sr,sc),raw=S.raw[src],a=addr(r,c);
   const se=to.v?series[c]:series['r'+r];if(se){const k=to.v?r-b.r0:c-b.c0;S.set(a,String(Math.round((se.a+se.st*k)*1e9)/1e9)+(se.pc?'%':''));if(S.fmt[src])S.fmt[a]=S.fmt[src];continue;}
   S.set(a,raw==null?'':shift(raw,r-sr,c-sc));if(S.fmt[src])S.fmt[a]=S.fmt[src];else delete S.fmt[a];}
  sel={r:to.r0,c:to.c0};sel2={r:to.r1,c:to.c1};render();toastX('הנוסחה שוכפלה, וההפניות התעדכנו בכל תא');if(cfg.onChange)cfg.onChange();}
 g.addEventListener('dblclick',e=>{/* pointer capture sends the event to the table: find the cell under the pointer */const tgt=document.elementFromPoint(e.clientX,e.clientY)||e.target;if(tgt.classList.contains('xl-fh')){const b=blk();
   let last=b.r1;for(let r=b.r1+1;r<R;r++){const nb=[b.c0-1,b.c1+1].some(c=>c>=0&&c<C&&S.raw[addr(r,c)]!=null);if(nb)last=r;else break;}
   if(last>b.r1)fill(b,{r0:b.r0,r1:last,c0:b.c0,c1:b.c1,v:1});return;}
  const cell=(tgt.closest&&tgt.closest('td'))||e.target.closest('td');if(!cell||!g.contains(cell))return;if(editing&&editing.a===cell.dataset.a)return;sel=parseAddr(cell.dataset.a);sel2={...sel};startEdit('',true,'edit');});
 const gKey=e=>{if(editing)return;const k=e.key;
  const mod=e.ctrlKey||e.metaKey;
  if(mod&&(k==='c'||k==='C'||k==='ג')){e.preventDefault();e.stopPropagation();CLIP={raw:S.raw[addr(sel.r,sel.c)],r:sel.r,c:sel.c,fmt:S.fmt[addr(sel.r,sel.c)]};toastX('הועתק. סמנו תא או טווח, והדביקו ב-Ctrl+V');return;}
  if(mod&&(k==='v'||k==='V'||k==='ה')){e.preventDefault();e.stopPropagation();if(!CLIP||CLIP.raw==null)return;
   for(let r=Math.min(sel.r,sel2.r);r<=Math.max(sel.r,sel2.r);r++)for(let c=Math.min(sel.c,sel2.c);c<=Math.max(sel.c,sel2.c);c++){S.set(addr(r,c),shift(CLIP.raw,r-CLIP.r,c-CLIP.c));if(CLIP.fmt)S.fmt[addr(r,c)]=CLIP.fmt;}
   render();if(cfg.onChange)cfg.onChange();return;}
  if(mod&&(k==='`'||k===';')){e.preventDefault();e.stopPropagation();toggleF();return;}
  const nav={ArrowDown:[1,0],ArrowUp:[-1,0],ArrowLeft:[0,1],ArrowRight:[0,-1],Enter:[e.shiftKey?-1:1,0],Tab:[0,e.shiftKey?-1:1]};
  if(nav[k]){e.preventDefault();e.stopPropagation();if(e.shiftKey&&k.startsWith('Arrow')){sel2={r:Math.max(R0,Math.min(R-1,sel2.r+nav[k][0])),c:Math.max(0,Math.min(C-1,sel2.c+nav[k][1]))};}else move(...nav[k]);render();return;}
  if(k==='F2'){e.preventDefault();e.stopPropagation();startEdit('',true,'edit');return;}
  if(k==='Delete'||k==='Backspace'){e.preventDefault();e.stopPropagation();for(let r=Math.min(sel.r,sel2.r);r<=Math.max(sel.r,sel2.r);r++)for(let c=Math.min(sel.c,sel2.c);c<=Math.max(sel.c,sel2.c);c++)S.set(addr(r,c),'');render();if(cfg.onChange)cfg.onChange();return;}
  if(k===' '||k.length===1&&!mod){e.preventDefault();e.stopPropagation();startEdit(k===' '?'':k,false);return;}
  if(k==='Escape'||k==='PageDown'||k==='PageUp'||k==='Home'||k==='End')e.stopPropagation();};
 g.addEventListener('keydown',gKey);sink.addEventListener('keydown',gKey);
 bar.addEventListener('focus',()=>{if(!editing){editing={a:addr(sel.r,sel.c),where:'bar',orig:S.raw[addr(sel.r,sel.c)]||'',mode:'edit',ptr:null};}});
 bar.addEventListener('input',()=>{if(editing){editing.ptr=null;sync();}});bar.addEventListener('scroll',()=>{barOv.scrollLeft=bar.scrollLeft;});
 bar.addEventListener('keydown',keyEdit);
 bar.addEventListener('blur',()=>{if(editing&&editing.where==='bar')setTimeout(()=>{if(editing&&editing.where==='bar'&&document.activeElement!==bar)commit(0,0);},120);});
 function toggleF(){showF=!showF;host.querySelector('[data-x="formulas"]')&&host.querySelector('[data-x="formulas"]').classList.toggle('on',showF);render();}
 host.querySelector('.xl-tools').addEventListener('click',e=>{const b=e.target.closest('button');if(!b)return;const x=b.dataset.x;
  if(x==='pct'){for(let r=Math.min(sel.r,sel2.r);r<=Math.max(sel.r,sel2.r);r++)for(let c=Math.min(sel.c,sel2.c);c<=Math.max(sel.c,sel2.c);c++){const a=addr(r,c);S.fmt[a]=/^pct/.test(S.fmt[a]||'')?'':'pct';}render();}
  if(x==='formulas')toggleF();
  if(x==='hint'&&fb){const i=hintN%cfg.hints.length;hintN++;setFb(`<div class="xl-tip"><b>רמז ${i+1} מתוך ${cfg.hints.length}:</b> ${cfg.hints[i]}</div>`);}
  if(x==='remind'&&fb){setFb(`<div class="xl-tip">${cfg.remind}</div>`);}
  if(x==='part'){cfg.partial.forEach(a=>{S.set(a,cfg.solution[a]);});render();if(fb)setFb('<div class="xl-tip">השורה הראשונה מולאה. המשיכו מכאן: גררו את ידית המילוי או כתבו לבד.</div>');if(cfg.onChange)cfg.onChange();}
  if(x==='reset'){load();marks={};hintN=0;stepK=0;{const b=host.querySelector('[data-x="step"]');if(b)b.textContent='▶ צעד אחר צעד';}if(fb)setFb('');sel={r:R0,c:0};sel2={...sel};render();if(cfg.onChange)cfg.onChange();}
  if(x==='solve'){Object.entries(cfg.solution).forEach(([a,v])=>S.set(a,v));Object.assign(S.fmt,cfg.solFmt||{});render();check(true);if(cfg.onChange)cfg.onChange();}
  if(x==='check')check(false);
  if(x==='step')stepNext();});
 /* step by step demonstration: each step writes its formulas into the sheet and explains them; the lecturer can go on with the deck's next key */
 function buildTo(k,note){bk=Math.max(0,Math.min(BL.length,k));const keep={};Object.keys(S.raw).forEach(a=>{if(!(a in cfg.data)&&!(cfg.bdata&&a in cfg.bdata))keep[a]=S.raw[a];});load();Object.entries(keep).forEach(([a,v])=>S.set(a,v));
  marks={};if(note&&bk>0)BL[bk-1].cells.forEach(a=>marks[a]='bld');render();
  if(note&&bk>0)setFb(`<div class="xl-step"><b>בניית התבנית, שלב ${bk} מתוך ${BL.length}:</b> ${BL[bk-1].note}${bk===BL.length?' <b>התבנית מוכנה. עכשיו ממלאים.</b>':''}</div>`);else if(!note)setFb('');}
 let stepK=0;
 function stepNext(){if(!cfg.steps)return;if(bk<BL.length)buildTo(BL.length,false);if(stepK>=cfg.steps.length){stepK=0;load();}const st=cfg.steps[stepK];if(editing)cancel();
  Object.entries(st.cells).forEach(([a,f])=>S.set(a,f));marks={};Object.keys(st.cells).forEach(a=>marks[a]='stp');
  const ks=Object.keys(st.cells);sel=parseAddr(st.sel||ks[0]);sel2=parseAddr(st.sel2||st.sel||ks[0]);render();
  stepK++;const last=stepK===cfg.steps.length;
  if(fb)setFb(`<div class="xl-step"><b>צעד ${stepK} מתוך ${cfg.steps.length}:</b> ${st.note}${last?' <b>זה הפתרון המלא.</b>':''}</div>`);
  const b=host.querySelector('[data-x="step"]');if(b)b.textContent=last?'↺ מההתחלה':'▶ הצעד הבא';if(cfg.onChange)cfg.onChange();}
 /* checking: the value must match, the cell must hold a formula with references (unless the solution has none: =14*12 converts years to months), and no number from the table may be typed in */
 const needOf=a=>cfg.need?(typeof cfg.need==='object'?cfg.need[a]:cfg.need):null;
 function check(silent){const sol=new Sheet(R,C);Object.entries({...cfg.data,...(cfg.bdata||{})}).forEach(([a,v])=>sol.set(a,v));Object.entries(cfg.solution).forEach(([a,v])=>sol.set(a,v));sol.recalc();
  S.recalc();marks={};const notes=[];let ok=0;
  cfg.targets.forEach(a=>{const raw=S.raw[a]||'',want=sol.val[a],got=S.val[a];const sf=cfg.solution[a]||'';
   const lits=s=>(s.replace(/\$?[A-Za-z]{1,2}\$?\d+/g,' ').match(/\d+(\.\d+)?/g)||[]).map(Number);
   const allowed=new Set([...lits(sf),...(cfg.allow||[0,1])]);let why='';
   const tol=w=>cfg.tol!=null?cfg.tol:Math.max(1e-6,1e-9*Math.abs(w));const near=(x,w)=>typeof x==='number'&&typeof w==='number'&&Math.abs(x-w)<=tol(w);
   if(cfg.vin&&cfg.vin.includes(a)){const pc=/^pct/.test(cfg.fmt&&cfg.fmt[a]||'');let w='';
    if(!raw)w='ריק: הזינו את הנתון מהשאלה';else if(isErr(got))w=`שגיאה ${got.err}`;
    else if(!near(got,want))w=pc&&near(got/100,want)?'זה אחוז: כתבו אותו עם סימן האחוז, למשל 5%':pc&&near(got*100,want)?'האחוז קטן פי 100 מהנדרש. כתבו את האחוז כפי שהוא בשאלה, למשל 5%':'הערך אינו תואם את הנתון בשאלה. קראו שוב את השאלה';
    if(w){marks[a]='bad';notes.push(`<b>${a}:</b> ${w}`);}else{marks[a]='ok';ok++;}return;}
   const nf=x=>String(x).toUpperCase().replace(/\s+/g,'').replace(/;/g,',');const exact=((cfg.traps&&cfg.traps[a])||[]).find(([f])=>nf(f)===nf(raw));
   if(exact&&!(typeof want==='number'&&near(got,want)))why=exact[1];
   else if(!raw)why='ריק';else if(raw[0]!=='='&&cfg.values){if(!near(got,want))why='המספר אינו נכון. חשבו שוב לפי ההסבר';}else if(raw[0]!=='=')why='הוקלד ערך ולא נוסחה. נוסחה מתחילה בסימן =';
   else if(isErr(got))why=`שגיאה ${got.err}: בדקו את הכתיב ואת הסוגריים`;
   else if(raw[0]==='='&&!/[A-Za-z]{1,2}\d/.test(raw.replace(/\$/g,'').replace(/[A-Z]+\(/g,''))&&/[A-Za-z]{1,2}\d/.test(sf.replace(/\$/g,'').replace(/[A-Z]+\(/g,''))&&!cfg.values)why='אין בנוסחה הפניה לתאים. השתמשו בכתובות התאים במקום במספרים';
   else if(raw[0]==='='&&!cfg.values&&lits(raw).some(x=>!allowed.has(x)))why='הוקלד בנוסחה מספר. כשהנתון קיים בטבלה, מפנים לתא שלו';
   else if(needOf(a)&&!new RegExp(needOf(a),'i').test(raw))why=(/^קבעו/.test(cfg.needMsg||'')?'קיבוע: ':'עבודה יעילה: ')+(cfg.needMsg||'יש פונקציה מתאימה לפעולה הזו');
   else if(typeof want==='number'&&!near(got,want)){why=cfg.wrongMsg||'התוצאה אינה נכונה. בדקו את סדר הפעולות ואת התאים שבחרתם';
    /* a known mistake gets its own explanation: the trap formula is evaluated on the solved sheet and compared with the student's value */
    const tr=(cfg.traps&&cfg.traps[a])||[];for(const [f,m] of tr){const T=new Sheet(R,C);Object.entries({...cfg.data,...(cfg.bdata||{})}).forEach(([k,v])=>T.set(k,v));Object.entries(cfg.solution).forEach(([k,v])=>T.set(k,v));T.set(a,f);T.recalc();if(near(got,T.val[a])){why=m;break;}}
    if(why===(cfg.wrongMsg||'התוצאה אינה נכונה. בדקו את סדר הפעולות ואת התאים שבחרתם')&&near(-got,want)&&want!==0)why=cfg.signMsg||'הסימן הפוך. פונקציות המימון באקסל מחזירות תשלום כמספר שלילי. הוסיפו מינוס לפני הפונקציה, או הפכו את סימן התזרים';}
   if(why){marks[a]='bad';notes.push(`<b>${a}:</b> ${why}`);}else{marks[a]='ok';ok++;}});
  render();const all=ok===cfg.targets.length;
  if(fb)setFb(all?`<div class="xl-ok">✔ כל ${ok} התאים נכונים${silent?' (פתרון לדוגמה)':''}.${cfg.done?' '+cfg.done:''}</div>`:`<div class="xl-no">נכונים ${ok} מתוך ${cfg.targets.length}.</div><div class="xl-notes">${notes.slice(0,2).join('<br>')}${notes.length>2?' ועוד '+(notes.length-2)+' תאים.':''}</div>`);
  if(all&&!silent)host.dataset.solved='1';if(cfg.onChange)cfg.onChange();}
 render();
 return {sheet:S,render,select:(a)=>{sel=parseAddr(a);sel2={...sel};render();},put:(a,v)=>{S.set(a,v);render();if(cfg.onChange)cfg.onChange();},stepNext:()=>stepNext(),buildPending:()=>bk<BL.length,buildNext:()=>buildTo(bk+1,true),buildBack:()=>buildTo(bk-1,true),buildAll:()=>{if(bk<BL.length)buildTo(BL.length,false);},buildBackAll:()=>buildTo(0,false),buildCount:()=>BL.length,built:()=>bk,stepActive:()=>!!cfg.steps&&stepK>0&&stepK<cfg.steps.length,stepCount:()=>stepK,putMany:o=>{Object.entries(o).forEach(([a,v])=>S.set(a,v));render();if(cfg.onChange)cfg.onChange();},get:a=>S.val[a],raw:a=>S.raw[a],check,reset:()=>host.querySelector('[data-x="reset"]').click(),showFormulas:v=>{if(showF!==!!v)toggleF();},
  fmtSel:fn=>{for(let r=Math.min(sel.r,sel2.r);r<=Math.max(sel.r,sel2.r);r++)for(let c=Math.min(sel.c,sel2.c);c<=Math.max(sel.c,sel2.c);c++){const a=addr(r,c),f=fn(S.fmt[a]||'',S.val[a],display(S,a).t);if(f)S.fmt[a]=f;else delete S.fmt[a];}render();},
  fmtAt:a=>S.fmt[a]||'',active:()=>addr(sel.r,sel.c),onSel:fn=>{cfg.onSelect=fn;}};}
const api={mount,shift,Sheet,addr,parseAddr,colName,tokenize,parse,FIN};if(typeof window!=='undefined')window.__XL=api;return api;
})();
