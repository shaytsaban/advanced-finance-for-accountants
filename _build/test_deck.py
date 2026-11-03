# Headless test: inject a script into a copy of the deck, read the JSON from data-test in the dumped DOM.
import json, os, re, subprocess, sys, tempfile, html as hh
H = os.path.dirname(os.path.abspath(__file__))
SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(H, '..', 'lectures', 'lecture-1', 'presentation.html')
CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
TEST = r'''
window.onerror=(m,u,l,c,e)=>{document.documentElement.setAttribute('data-err',m+' @'+l+':'+c+' '+(e&&e.stack||'').slice(0,500));};
(function(){
const D=window.__deckT,R={errors:[],overflow:[],small:[],mc:[],act:[],reveal:[],terms:[],chars:[],eqwide:[],abbr:{},bidi:[]};
window.addEventListener('error',e=>R.errors.push(e.message));
const st=document.createElement('style');st.textContent='*{transition:none!important;animation:none!important}';document.head.appendChild(st);
const stage=document.getElementById('stage');
const rel=e=>{const s=stage.getBoundingClientRect(),r=e.getBoundingClientRect(),k=s.width/1280;return{t:(r.top-s.top)/k,b:(r.bottom-s.top)/k,l:(r.left-s.left)/k,r:(r.right-s.left)/k};};
function solveWidgets(s){
 s.querySelectorAll('.numq').forEach(b=>{b.querySelector('input').value=b.dataset.a;b.querySelector('.chk').click();});
 s.querySelectorAll('.srow').forEach(r=>{r.querySelectorAll('.so')[+r.dataset.a].click();});
 s.querySelectorAll('.mc').forEach(m=>{m.classList.add('done');m.querySelectorAll('.o')[+m.dataset.a].classList.add('ok');});}
function measure(s,i,tag){const foot=s.querySelector('.ft');const limit=foot?720-36:716;let worst=0,who='',wl=0,wr=1280;
 s.querySelectorAll('*').forEach(e=>{const xw=e.closest('.xl-wrap');if(xw&&xw!==e)return;if(e.closest('.ft')||e.closest('.pd-num')||e.closest('.orb')||e.closest('svg')&&e.tagName!=='svg')return;const c=getComputedStyle(e);if(c.display==='none'||c.visibility==='hidden')return;const r=rel(e);if(r.b-r.t<1)return;if(r.b>worst){worst=r.b;who=e.tagName+'.'+(e.className.baseVal??e.className);}if(r.l<wl)wl=r.l;if(r.r>wr)wr=r.r;});
 if(worst>limit+.5||wl<-.5||wr>1280.5)R.overflow.push({i:i+1,id:s.id,tag,bottom:Math.round(worst),limit,who,l:Math.round(wl),r:Math.round(wr)});}
D.slides.forEach((s,i)=>{D.show(i);D.setAll(s,true);measure(s,i,'open');solveWidgets(s);measure(s,i,'solved');
 s.querySelectorAll('.eq').forEach(e=>{const box=e.closest('.card,.solw,.cout,.fm,td,.slide');const g=document.createRange();g.selectNodeContents(e);const a=g.getBoundingClientRect(),b=box.getBoundingClientRect();if(a.left<b.left-1||a.right>b.right+1)R.eqwide.push({id:s.id,t:e.textContent.slice(0,50)});});
 const tw=document.createTreeWalker(s,NodeFilter.SHOW_TEXT);let n;const seen={};while((n=tw.nextNode())){if(!n.nodeValue.trim())continue;const p=n.parentElement;if(p.closest('.ft,sup,sub,tspan'))continue;let fs=parseFloat(getComputedStyle(p).fontSize);const svg=p.closest('svg');if(svg){const vb=svg.viewBox.baseVal.width;fs*=svg.getBoundingClientRect().width/(stage.getBoundingClientRect().width/1280)/vb;if(fs<13.5)seen['svg '+fs.toFixed(1)]=n.nodeValue.slice(0,24);}else if(fs<16.5)seen[fs]=n.nodeValue.slice(0,24);}
 if(Object.keys(seen).length)R.small.push({id:s.id,seen});
 const txt=s.textContent;[['em','—'],['maqaf','־'],['en','–'],['ell','…'],['arrow','→'],['arrow2','⇒'],['q1','“'],['q2','”'],['cur','¤']].forEach(([k,c])=>{if(txt.includes(c))R.chars.push({id:s.id,k});});
 ['YTM','NPV','PV'].forEach(a=>{if(!(a in R.abbr)&&txt.includes(a)){const lk=[...s.querySelectorAll('.term')].some(t=>t.textContent.includes(a));R.abbr[a]=s.id+(lk?' linked':' NOT LINKED');}});
 // a bare minus before a number must stay on the left inside an LTR run
 s.querySelectorAll('.tbl2 td,.m').forEach(e=>{if(/\d\s*−\s*$/.test(e.textContent))R.bidi.push({id:s.id,t:e.textContent});});
 s.querySelectorAll('.mc').forEach(m=>{m.classList.remove('done');m.querySelectorAll('.o').forEach(o=>o.classList.remove('ok','bad'));});D.setAll(s,false);});

// bidi by measurement: inside an LTR run the first character must sit left of the last
R.bidiM={checked:0,bad:[]};D.slides.forEach((s,i)=>{D.show(i);D.setAll(s,true);s.querySelectorAll('.eq,.m,.n').forEach(e=>{const w=document.createTreeWalker(e,NodeFilter.SHOW_TEXT);const ts=[];let t;while(t=w.nextNode())if(t.nodeValue.trim())ts.push(t);if(!ts.length)return;const a=ts[0],b=ts[ts.length-1];const ia=a.nodeValue.search(/\S/),ib=b.nodeValue.length-1-b.nodeValue.split('').reverse().join('').search(/\S/);if(a===b&&ia>=ib)return;const r=document.createRange();r.setStart(a,ia);r.setEnd(a,ia+1);const x=r.getBoundingClientRect();r.setStart(b,ib);r.setEnd(b,ib+1);const y=r.getBoundingClientRect();if(x.width===0||y.width===0||e.closest('.frac')||e.querySelector('.frac')&&false)return;R.bidiM.checked++;if(x.left>y.left+0.5&&Math.abs(x.top-y.top)<4)R.bidiM.bad.push({id:s.id,t:e.textContent.slice(0,40)});});D.setAll(s,false);});
// reveals
D.slides.forEach((s,i)=>{const g=D.groups(s).length;D.show(i);let c=0;while(D.pending(s).length&&c<60){D.next();c++;}if(c!==g||D.cur()!==i)R.reveal.push({id:s.id,g,c});let b=0;while(D.groups(s).some(x=>x[0].classList.contains('show'))&&b<60){D.prev();b++;}if(b!==g||D.cur()!==i)R.reveal.push({id:s.id,back:b,g});});
D.show(0);let k=0;while(D.cur()<D.slides.length-1&&k<2000){D.next();k++;}R.walked=[k,D.cur()];
// mc
document.querySelectorAll('.mc').forEach(m=>{const a=+m.dataset.a,os=[...m.querySelectorAll('.o')],w=m.querySelector('.w');D.go(m.closest('.slide').id);const wrong=(a+1)%os.length;os[wrong].click();let ok=os[wrong].classList.contains('bad')&&os[a].classList.contains('ok')&&getComputedStyle(w).display!=='none';m.classList.remove('done');os.forEach(o=>o.classList.remove('ok','bad'));os[a].click();ok=ok&&os[a].classList.contains('ok')&&!os[wrong].classList.contains('bad');m.classList.remove('done');os.forEach(o=>o.classList.remove('ok','bad'));R.mc.push(ok?1:m.id);});
const A=(id,kind,ok,more)=>R.act.push({id,kind,ok:!!ok,...more});
const q=(s,r=document)=>r.querySelector(s),qq=(s,r=document)=>[...r.querySelectorAll(s)];const XLA=window.__XL;
// sorter
qq('.sorter').forEach(b=>{D.go(b.closest('.slide').id);q('.rst',b).click();const rows=qq('.srow',b),fb=q('.fbbar',b);let ok=true;rows.forEach(r=>{const a=+r.dataset.a,so=qq('.so',r),w=(a+1)%so.length;so[w].click();ok=ok&&so[w].classList.contains('bad')&&fb.classList.contains('wrong')&&!r.classList.contains('solved');so[a].click();ok=ok&&r.classList.contains('solved')&&fb.classList.contains('good');});ok=ok&&q('.score',b).textContent===rows.length+' / '+rows.length;q('.rst',b).click();ok=ok&&q('.score',b).textContent==='0 / '+rows.length;A(b.id,'sorter',ok);});
// numq
qq('.numq').forEach(b=>{D.go(b.closest('.slide').id);const i=q('input',b),c=q('.chk',b),fb=q('.fbbar',b),a=+b.dataset.a;i.value=String(a+7);c.click();let ok=fb.classList.contains('wrong');i.value='abc';c.click();ok=ok&&fb.classList.contains('wrong');i.value=String(a);c.click();ok=ok&&fb.classList.contains('good')&&b.classList.contains('solved');i.value='';fb.className='fbbar';b.classList.remove('solved');A(b.id,'numq',ok);});
// draw: real pointer events on the first handle, then the API for the rest
qq('.draw').forEach(b=>{D.go(b.closest('.slide').id);const C=JSON.parse(b.dataset.cfg),svg=q('svg',b),fb=q('.fbbar',b);let ok=true,solved=0;
 const circ=()=>q('.hd[data-i="0"] circle',svg);const r=circ().getBoundingClientRect();const cx=r.left+r.width/2,cy=r.top+r.height/2;const k=svg.getBoundingClientRect().height/430;
 const pe=(t,x,y)=>new PointerEvent(t,{bubbles:true,clientX:x,clientY:y,pointerId:1,pointerType:'mouse'});circ().dispatchEvent(pe('pointerdown',cx,cy));svg.dispatchEvent(pe('pointermove',cx,cy+100*k));svg.dispatchEvent(pe('pointerup',cx,cy+100*k));
 const moved=parseFloat(circ().getAttribute('cy'));ok=ok&&Math.abs(moved-(30+(40-0)/(80)*(430-30-46))-100)<12;R.dragY=moved;
 C.tasks.forEach((T,i)=>{const w=T.pts.map(x=>x+2);b.__set(w);q('.chk',b).click();ok=ok&&fb.classList.contains('wrong');b.__set(T.pts);q('.chk',b).click();ok=ok&&fb.classList.contains('good');if(fb.classList.contains('good'))solved++;if(!q('.nxt',b).disabled)q('.nxt',b).click();measure(b.closest('.slide'),99,'draw');});A(b.id,'draw',ok&&solved===C.tasks.length,{solved});});
// embedded Excel: every sheet rejects wrong input, then accepts typed formulas; buttons work
qq('.xlq').forEach(b=>{D.go(b.closest('.slide').id);const C=JSON.parse(b.dataset.cfg),h=q('.sheet',b),api=h.__api,fb=()=>q('.xl-fb',b).textContent;let ok=true;const btn=x=>q(`[data-x="${x}"]`,b);
 const clear=()=>btn('reset').click();clear();
 btn('check').click();ok=ok&&q('.xl-no',b)!==null;
 if(!C.values){C.targets.forEach(a=>api.put(a,'12345'));btn('check').click();ok=ok&&q('.xl-no',b)!==null&&/ערך ולא נוסחה/.test(fb());measure(b.closest('.slide'),99,'xl-wrong');}
 else{C.targets.forEach(a=>api.put(a,'12345'));btn('check').click();ok=ok&&q('.xl-no',b)!==null;measure(b.closest('.slide'),99,'xl-wrong');}
 clear();
 if(C.hints){btn('hint').click();ok=ok&&!!q('.xl-tip',b);measure(b.closest('.slide'),99,'xl-hint');}
 if(C.remind){btn('remind').click();ok=ok&&!!q('.xl-tip',b);}
 btn('part').click();ok=ok&&C.partial.every(a=>api.raw(a)===C.solution[a]);clear();
 C.targets.forEach(a=>api.put(a,C.solution[a]));btn('check').click();ok=ok&&q('.xl-ok',b)!==null&&h.dataset.solved==='1';
 const errs=qq('td.e',b).length;ok=ok&&!errs;measure(b.closest('.slide'),99,'xl-solved');
 const svg=q('svg.xlc',b);if(svg)ok=ok&&svg.querySelectorAll('polyline').length>=1;
 btn('reset').click();btn('solve').click();ok=ok&&q('.xl-ok',b)!==null;measure(b.closest('.slide'),99,'xl-full');
 // typing through the keyboard path, in the first target cell
 clear();const t=C.targets[0];api.select(t);const sink=q('.xl-sink',b);sink.focus();sink.dispatchEvent(new KeyboardEvent('keydown',{key:'=',bubbles:true}));const inp=q('.xl-in',b);if(inp){inp.value=C.solution[t];inp.dispatchEvent(new Event('input',{bubbles:true}));inp.dispatchEvent(new KeyboardEvent('keydown',{key:'Enter',bubbles:true}));ok=ok&&api.raw(t)===C.solution[t];}else ok=false;
 // every trap: all other cells solved, the trap formula in its cell, and the specific message must appear
 const solveAll=()=>{clear();api.putMany(C.solution);};const strip=h=>{const d=document.createElement('div');d.innerHTML=h;return d.textContent;};
 let trapsOk=0,trapsN=0;const tf=[];Object.entries(C.traps||{}).forEach(([a,L])=>L.forEach(([f,m])=>{trapsN++;api.putMany({...C.solution,[a]:f});btn('check').click();const t=fb();if(t.includes(strip(m).slice(0,25))&&q('.xl-no',b))trapsOk++;else tf.push(a+' '+f+' => '+t.slice(0,80));}));
 ok=ok&&trapsOk===trapsN;
 // sign: a solution that starts with =-FN( must give the sign message without the minus
 let signOk=true;C.targets.forEach(a=>{const f=C.solution[a];if(/^=-[A-Z]+\(/.test(f)){api.putMany({...C.solution,[a]:'='+f.slice(2)});btn('check').click();if(!/הסימן הפוך|ההפניה|היוונתם|חילקתם|המינוס/.test(fb()))signOk=false;}});ok=ok&&signOk;
 // other correct spellings are accepted: brackets, relative instead of absolute references (one cell at a time), PV with negated arguments
 let altOk=true;const alts=[];const seenC={};C.targets.filter(a=>{const c=a.replace(/\d+/,'');if(seenC[c])return false;seenC[c]=1;return true;}).forEach(a=>{const f=C.solution[a];const L=['=('+f.slice(1)+')',f.replace(/\$/g,'')];const m=/^=-PV\(([^,]+),([^,]+),([^,]*),([^,)]+)\)$/.exec(f);if(m)L.push(`=PV(${m[1]},${m[2]},-(${m[3]}),-${m[4]})`);
  L.forEach(g=>{api.putMany({...C.solution,[a]:g});btn('check').click();if(!q('.xl-ok',b)){altOk=false;alts.push(a+' '+g+' => '+fb().slice(0,60));}});});ok=ok&&altOk;
 // step by step demo: every step writes its cells; at the end the sheet is the full solution and checks green; the deck's next key goes on with a started demo
 let stepOk=true;if(C.steps){clear();btn('step').click();for(let k=1;k<C.steps.length;k++){D.next();}stepOk=C.targets.every(a=>api.raw(a)===C.solution[a])&&/זה הפתרון המלא/.test(fb());measure(b.closest('.slide'),99,'xl-steps');btn('check').click();stepOk=stepOk&&!!q('.xl-ok',b);}
 ok=ok&&stepOk;
 // Excel feel: typing a formula colours its references; arrows point at a cell; F2 and double click open the cell for editing
 clear();let feel=true;const t0=C.targets[0],p0=XLA.parseAddr(t0);api.select(t0);const sk=q('.xl-sink',b);sk.focus();sk.dispatchEvent(new KeyboardEvent('keydown',{key:'=',bubbles:true}));
 let ci=q('.xl-in',b);const ref=Object.keys(C.data).find(a=>XLA.parseAddr(a).r>=(C.r0||1)-1);
 if(ci&&ref){ci.value='='+ref;ci.dispatchEvent(new Event('input',{bubbles:true}));const el=q(`td[data-a="${ref}"]`,b);feel=feel&&el&&el.dataset.rf==='1'&&/inset/.test(el.style.boxShadow)&&q('.xl-ed .xl-ov span',b)!==null;
  ci.value='=';ci.dispatchEvent(new Event('input',{bubbles:true}));ci.setSelectionRange(1,1);ci.dispatchEvent(new KeyboardEvent('keydown',{key:'ArrowUp',bubbles:true}));const up=XLA.addr(Math.max((C.r0||1)-1,p0.r-1),p0.c);feel=feel&&ci.value==='='+up;
  ci.dispatchEvent(new KeyboardEvent('keydown',{key:'Escape',bubbles:true}));}else feel=false;
 api.put(t0,C.solution[t0]);api.select(t0);sk.focus();sk.dispatchEvent(new KeyboardEvent('keydown',{key:'F2',bubbles:true}));ci=q('.xl-in',b);feel=feel&&ci&&ci.value===C.solution[t0];if(ci)ci.dispatchEvent(new KeyboardEvent('keydown',{key:'Escape',bubbles:true}));
 const tdc=q(`td[data-a="${t0}"]`,b);tdc.dispatchEvent(new MouseEvent('dblclick',{bubbles:true}));ci=q('.xl-in',b);feel=feel&&ci&&ci.value===C.solution[t0];if(ci)ci.dispatchEvent(new KeyboardEvent('keydown',{key:'Escape',bubbles:true}));
 ok=ok&&feel;
 clear();A(b.id,'xl',ok,{targets:C.targets.length,errs,traps:trapsOk+'/'+trapsN,tf:tf.slice(0,3),alts:alts.slice(0,3),signOk,stepOk,feel});});
// no question without a sheet: every multiple choice question sits inside a question-and-sheet slide
R.mcNoSheet=qq('.mc').filter(m=>!m.closest('.qx')).map(m=>m.id);
// exercises with hints
qq('.sv').forEach(b=>{D.go(b.closest('.slide').id);const ps=qq('.svp',b),fb=q('.fbbar',b);const fill=f=>ps.forEach(p=>{q('input',p).value=f(+p.dataset.a);});fill(a=>a+9);q('.chk',b).click();let ok=fb.classList.contains('wrong');q('.hnt',b).click();ok=ok&&/רמז/.test(fb.textContent);q('.rmd',b).click();ok=ok&&fb.textContent.length>5;q('.prt',b).click();ok=ok&&qq('.svs.on',b).length===1;q('.ful',b).click();ok=ok&&qq('.svs.on',b).length===qq('.svs',b).length;fill(a=>a);q('.chk',b).click();ok=ok&&fb.classList.contains('good');measure(b.closest('.slide'),99,'sv-full');q('.rst',b).click();ok=ok&&qq('.svs.on',b).length===0;A(b.id,'sv',ok);});
// a cartoon must not sit on other content
R.toon=[];D.slides.forEach((s,i)=>{const t=s.querySelector('.toon');if(!t)return;D.show(i);D.setAll(s,true);const T=t.getBoundingClientRect();s.querySelectorAll('.card,table,.band,.mc,.fbbar,.rl .sp,.rl .eq,.lead,.act,.steps').forEach(e=>{if(e.contains(t)||t.contains(e))return;const r=e.getBoundingClientRect();if(r.width&&r.left<T.right-2&&r.right>T.left+2&&r.top<T.bottom-2&&r.bottom>T.top+2)R.toon.push({id:s.id,on:e.className});});D.setAll(s,false);});
qq('[data-t]').forEach(t=>{if(!D.G[t.dataset.t])R.terms.push(t.dataset.t);});
R.unusedTerms=Object.keys(D.G).filter(k=>!document.querySelector('.slide [data-t="'+k+'"]'));
Object.keys(D.G).forEach(k=>{D.openTerm(k);if(document.getElementById('dp').textContent.length<8||document.getElementById('dex').textContent.length<8)R.terms.push('empty '+k);});D.closeOverlays();
R.go=qq('[data-go]').filter(g=>!document.getElementById(g.dataset.go)).map(g=>g.dataset.go);
R.count=D.slides.length;R.mcN=qq('.mc').length;R.actN=R.act.length;
document.documentElement.setAttribute('data-test',JSON.stringify(R));
})();
'''
html = open(SRC, encoding='utf8').read().replace('window.__deck={', 'window.__deckT={G,')
html = html.replace('</body>', '<script>' + TEST + '</script></body>')
d = tempfile.mkdtemp(dir=os.environ.get('TMPDIR'))
import atexit, shutil; atexit.register(shutil.rmtree, d, True)
p = os.path.join(d, 't.html'); open(p, 'w', encoding='utf8').write(html)
out = subprocess.run([CHROME, '--headless=new', '--disable-gpu', '--no-sandbox', f'--user-data-dir={d}/prof', '--window-size=1280,764', '--virtual-time-budget=60000', '--dump-dom', 'file://' + p], capture_output=True, text=True, timeout=900).stdout
m = re.search(r'<html[^>]*data-test="([^"]*)"', out)
if not m:
    print('NO RESULT', re.findall(r'data-err="([^"]*)"', out)[:1]); sys.exit(1)
R = json.loads(hh.unescape(m.group(1)))
print('slides', R['count'], 'mc', R['mcN'], 'walk', R['walked'], 'dragY', R.get('dragY'))
print('errors', R['errors'])
print('overflow', len(R['overflow']));[print('  ', o) for o in R['overflow']]
print('eq wider than box', R['eqwide'])
print('small text', len(R['small']));[print('  ', o) for o in R['small'][:30]]
print('chars', R['chars']); print('abbr', R['abbr']); print('bidi', R['bidi'])
print('bidi measured', R['bidiM']['checked'], 'reversed', R['bidiM']['bad'][:12])
print('reveal problems', R['reveal'])
bad = [x for x in R['mc'] if x != 1]
print('mc ok', len(R['mc']) - len(bad), 'bad', bad)
print('activities', R['actN'], 'failed', [a for a in R['act'] if not a['ok']])
print('traps', [(a['id'], a.get('traps')) for a in R['act'] if a['kind'] == 'xl'])
print('toon overlaps', R['toon'])
print('mc without a sheet', R['mcNoSheet'])
print('counts', {k: sum(1 for a in R['act'] if a['kind'] == k) for k in {a['kind'] for a in R['act']}})
print('terms', R['terms'], 'unused', R['unusedTerms'], 'bad go', R['go'])
