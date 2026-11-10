// Trusted mouse and keyboard input through the DevTools protocol (pointer capture and double click behave as with a real mouse).
// Run: node tests/real_input.js <deck.html>
const {spawn}=require('child_process'),fs=require('fs'),os=require('os'),path=require('path');
const CHROME='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const dir=fs.mkdtempSync(path.join(process.env.TMPDIR||os.tmpdir(),'ri'));
const ch=spawn(CHROME,['--headless=new','--disable-gpu','--no-sandbox','--remote-debugging-port=0',`--user-data-dir=${dir}`,'--window-size=1280,764','about:blank'],{stdio:['ignore','ignore','pipe']});
const done=(c)=>{try{ch.kill();}catch(e){}setTimeout(()=>{try{fs.rmSync(dir,{recursive:true,force:true});}catch(e){}process.exit(c);},800);};
let buf='';ch.stderr.on('data',async d=>{buf+=d;const m=/ws:\/\/[^\s]+/.exec(buf);if(!m||run.started)return;run.started=1;run(m[0]).catch(e=>{console.log('ERR',e);done(1);});});
async function run(bws){
 const list=await (await fetch(bws.replace('ws://','http://').replace(/\/devtools.*/,'/json/list'))).json();
 const ws=new WebSocket(list.find(t=>t.type==='page').webSocketDebuggerUrl);await new Promise(r=>ws.onopen=r);
 let id=0;const pend={};ws.onmessage=e=>{const m=JSON.parse(e.data);if(m.id&&pend[m.id]){pend[m.id](m);delete pend[m.id];}};
 const cmd=(method,params={})=>new Promise(r=>{const i=++id;pend[i]=r;ws.send(JSON.stringify({id:i,method,params}));});
 const ev=async x=>(await cmd('Runtime.evaluate',{expression:x,returnByValue:true,awaitPromise:true})).result.result.value;
 await cmd('Page.enable');await cmd('Page.navigate',{url:'file://'+path.resolve(process.argv[2])});await new Promise(r=>setTimeout(r,2500));
 await ev(`document.head.insertAdjacentHTML('beforeend','<style>*{transition:none!important;animation:none!important}</style>');window.__deck.go('q-1');1`);
 const at=async a=>ev(`(()=>{const r=document.querySelector('#q-1 td[data-a="${a}"]').getBoundingClientRect();return [r.left+r.width/2,r.top+r.height/2];})()`);
 const mouse=async(type,[x,y],clickCount=1)=>cmd('Input.dispatchMouseEvent',{type,x,y,button:'left',buttons:type==='mouseReleased'?0:1,clickCount});
 const click=async(p,n=1)=>{for(let k=1;k<=n;k++){await mouse('mousePressed',p,k);await mouse('mouseReleased',p,k);}};
 const key=async(k,code,text)=>{await cmd('Input.dispatchKeyEvent',{type:'keyDown',key:k,code:code||k,windowsVirtualKeyCode:{Enter:13,F2:113,Escape:27,ArrowRight:39,ArrowLeft:37}[k]||0,text});await cmd('Input.dispatchKeyEvent',{type:'keyUp',key:k,code:code||k});};
 const type=async t=>{for(const c of t)await cmd('Input.insertText',{text:c});};
 const R={};
 // 1. type a formula with point mode: = , right arrow, +, right arrow twice, Enter
 await click(await at('D16'));await type('=');await key('ArrowRight');await type('+');await key('ArrowRight');await key('ArrowRight');
 R.colored=await ev(`[...document.querySelectorAll('#q-1 td[data-rf]')].map(x=>x.dataset.a).join(',')`);R.typed=await ev(`document.querySelector('#q-1 .xl-in').value`);
 await key('Enter');R.raw=await ev(`document.querySelector('#q-1 .sheet').__api.raw('D16')`);
 // 2. a real double click opens the cell for editing, with the formula and its references coloured
 await click(await at('D16'),2);R.dbl=await ev(`(()=>{const i=document.querySelector('#q-1 .xl-in');return i?[i.closest('td').dataset.a,i.value,[...document.querySelectorAll('#q-1 td[data-rf]')].map(x=>x.dataset.a).join(',')]:null;})()`);
 await key('Escape');
 // 3. F2 on the selected cell opens it in edit mode, and the left arrow moves the caret, not the selection
 await key('F2');await key('ArrowLeft');R.f2=await ev(`(()=>{const i=document.querySelector('#q-1 .xl-in');return i?[i.closest('td').dataset.a,i.value,i.selectionStart]:null;})()`);await key('Escape');
 // 4. the fill handle: drag from B16 down to B21
 await ev(`(()=>{const a=document.querySelector('#q-1 .sheet').__api;a.put('B16','=$D$9*$D$10');a.select('B16');return 1;})()`);
 const fh=await ev(`(()=>{const r=document.querySelector('#q-1 .xl-fh').getBoundingClientRect();return [r.left+r.width/2,r.top+r.height/2];})()`),b21=await at('B21');
 R.before=await ev('(()=>{const e=document.elementFromPoint('+fh[0]+','+fh[1]+');return e&&(e.tagName+"."+e.className);})()');
 await ev(`window.__pl=[];['pointerdown','pointermove','pointerup','dblclick'].forEach(t=>document.addEventListener(t,e=>window.__pl.push(t+':'+(e.target.className||e.target.tagName)),true));1`);
 await mouse('mousePressed',fh);const wb=await ev(`document.querySelector('#q-1 .xl-wrap').getBoundingClientRect().bottom`);for(let k=1;k<=14;k++)await cmd('Input.dispatchMouseEvent',{type:'mouseMoved',x:fh[0]+3,y:Math.min(wb+20,fh[1]+30*k),button:'left',buttons:1});
 R.scrolled=await ev(`document.querySelector('#q-1 .xl-wrap').scrollTop`);await mouse('mouseReleased',[fh[0]+3,wb+20]);
 R.fill=await ev(`document.querySelector('#q-1 .sheet').__api.raw('B21')`)||null;R.last=await ev(`document.querySelector('#q-1 .xl-name').textContent`);R.fh=fh;R.b21=b21;R.pl=await ev('window.__pl.join(" ")');R.name=await ev(`document.querySelector('#q-1 .xl-name').textContent`);R.under=await ev('(()=>{const e=document.elementFromPoint('+fh[0]+','+fh[1]+');return e&&(e.tagName+"."+e.className);})()');
 // 5. editing a written formula (Shay, 2026-11-10): F2, a real click just before the B of B16 in the coloured text, then type $
 await click(await at('D16'));await key('F2');
 const bpos=await ev(`(()=>{const sp=[...document.querySelectorAll('#q-1 td.ed .xl-ov span')].find(s=>s.textContent==='B16');if(!sp)return null;const r=sp.getBoundingClientRect();return [r.left+1.5,r.top+r.height/2];})()`);
 if(bpos){await click(bpos);await type('$');}
 R.dollar=await ev(`(()=>{const i=document.querySelector('#q-1 td.ed .xl-in');return i?i.value:null;})()`);await key('Escape');
 // 6. Enter mode: type a formula, click inside it, and the left arrow moves the caret instead of pointing at a cell
 await click(await at('E16'));await type('=C16+B16');const mid=await ev(`(()=>{const sp=[...document.querySelectorAll('#q-1 td.ed .xl-ov span')].find(s=>s.textContent==='C16');if(!sp)return null;const r=sp.getBoundingClientRect();return [r.right-1,r.top+r.height/2];})()`);
 if(mid){await click(mid);await key('ArrowLeft');await type('9');}
 R.enterClick=await ev(`(()=>{const i=document.querySelector('#q-1 td.ed .xl-in');return i?i.value:null;})()`);await key('Escape');
 console.log(JSON.stringify(R));
 const ok=R.typed==='=C16+B16'&&R.colored==='C16,B16'.split(',').sort().join(',')||R.colored.split(',').sort().join(',')==='B16,C16';
 const pass=R.typed==='=C16+B16'&&R.colored.split(',').sort().join(',')==='B16,C16'&&R.raw==='=C16+B16'&&R.dbl&&R.dbl[0]==='D16'&&R.dbl[1]==='=C16+B16'&&R.dbl[2].split(',').sort().join(',')==='B16,C16'&&R.f2&&R.f2[0]==='D16'&&R.f2[2]===R.f2[1].length-1&&R.fill==='=$D$9*$D$10'&&R.dollar==='=C16+$B16'&&R.enterClick==='=C196+B16';
 console.log(pass?'REAL INPUT: PASS':'REAL INPUT: FAIL');done(pass?0:1);}
setTimeout(()=>{console.log('timeout');done(1);},120000);
