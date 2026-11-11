const {chromium}=require('playwright');const fs=require('fs');
(async()=>{
 const b=await chromium.launch({args:['--lang=nl-NL']});const ctx=await b.newContext({viewport:{width:1600,height:1000},deviceScaleFactor:2,colorScheme:'dark',locale:'nl-NL'});
 const p=await ctx.newPage();p.on('pageerror',e=>console.log('ERR',e.message));
 await p.goto('file://'+__dirname+'/app.html');await p.waitForTimeout(800);
 await p.evaluate(()=>{
  T.forEach(t=>{t.file={name:t.title+'.mp3',native:true,path:'/x'};t.key='MP3/'+t.artist+'/'+t.title+'.mp3'});
  T.forEach((t,i)=>{t.src=i%5===1?'r':i%3===0?'c':''});
  const KS=['8A','9A','8B','7A','10B','5A','4B','11A','6B','9B','12A','1B'];T.forEach((t,i)=>{t.tkey=i%7===3?'':KS[(i*5)%12];if(t.src==='c')t.nrg=estE(t)});
  $('#demo').textContent='Eigen bestanden gekoppeld · alleen op deze computer';$('#demo').classList.add('live');
  setStatus('Klaar: 69 nummers direct herkend. Klik op ▶ om te luisteren.');
  setSave('Bewaard: 69 nummers · 11 nov, 13:52');
  $('#refineStatus').textContent='Verfijnd: 69 van 69';
  $('#airDate').value='2026-11-17';$('#airTime').value='09:00';updateSlot();['#airDate','#airTime'].forEach(q=>{const i=$(q);const v=q==='#airDate'?'di 17-11-2026':'09:00';i.type='text';i.value=v;i.size=1;i.style.cssText='min-width:0;width:100%;font:14px var(--f-body);color:var(--ink);background:var(--bg);border:1px solid var(--line);border-radius:6px;padding:8px 10px';});
  buildChips();render();
 });
 const box=async sel=>p.evaluate(s=>{const r=document.querySelector(s).getBoundingClientRect();return{x:r.x+scrollX,y:r.y+scrollY,w:r.width,h:r.height}},sel);
 const meta={};
 // 1 overzicht
 await p.screenshot({path:'shots/overzicht.png'});
 meta.overzicht={W:1600,H:1000,marks:{
  1:await box('#drop'),2:await box('#sec-bewaren'),3:await box('#sec-indelen'),4:await box('#sec-filters'),5:await box('#sec-catalogus'),6:await box('#sec-uur')}};
 // 2 balken bovenaan
 const top=await box('#drop');const ind=await box('#sec-indelen');
 const clipBars={x:0,y:top.y-12,width:1600,height:ind.y+ind.h-top.y+24};
 await p.screenshot({path:'shots/balken.png',clip:clipBars});
 meta.balken={clip:clipBars,marks:{1:await box('#pickDir'),2:await box('#saveCat'),3:await box('#expCsv'),4:await box('#expJson'),5:await box('#impList'),6:await box('#refine')}};
 // 3 filters met Oldies + Ochtend
 await p.evaluate(()=>{state.genre.add('Oldies');buildChips();render()});
 const f=await box('#sec-filters');const clipF={x:f.x-10,y:f.y-10,width:f.w+20,height:f.h+20};
 await p.screenshot({path:'shots/filters.png',clip:clipF,fullPage:true});
 meta.filters={clip:clipF,marks:{1:await box('#q'),2:await box('#fDaypart'),3:await box('#fMood'),4:await box('#fGenre'),5:await box('#fDecade'),6:await box('#fCal'),7:await box('#fTheme'),8:await box('#fDur'),9:await box('#fNrg'),10:await box('#hideRecent'),11:await box('#harm')}};
 meta.filters.groups=await p.evaluate(()=>[...document.querySelectorAll('#sec-filters p.label')].map(e=>e.getBoundingClientRect().y+scrollY));
 await p.evaluate(()=>{state.genre.clear();buildChips();render()});
 // 4 catalogus met speler
 await p.evaluate(()=>{state.daypart.clear();buildChips();state.playing=T.findIndex(t=>t.title==='Lovely Day');$('#pTitle').textContent='Lovely Day';$('#pArtist').textContent='Bill Withers · 1977';$('#pCur').textContent='1:12';$('#pDur').textContent='4:14';$('#pSeek').value=283;$('#pp').textContent='❚❚';$('#player').hidden=false;render();
   document.querySelector('#audio').__defineGetter__('paused',()=>false);render();});
 const c=await box('#sec-catalogus');const clipC={x:c.x-10,y:c.y-10,width:c.w+20,height:Math.min(c.h,340)+20};
 await p.screenshot({path:'shots/catalogus.png',clip:clipC,fullPage:true});
 const row=await p.evaluate(()=>{const r=document.querySelector('#rows tr').getBoundingClientRect();return{x:r.x+scrollX,y:r.y+scrollY,w:r.width,h:r.height}});
 const cell=async (i)=>p.evaluate(i=>{const r=document.querySelector('#rows tr').children[i].getBoundingClientRect();return{x:r.x+scrollX,y:r.y+scrollY,w:r.width,h:r.height}},i);
 meta.catalogus={clip:clipC,marks:{1:await box('#rows tr .play'),2:await p.evaluate(()=>{const r=document.querySelector('thead th[data-sort="year"]').getBoundingClientRect();return{x:r.x,y:r.y+scrollY,w:r.width,h:r.height}}),3:await cell(3),4:await cell(4),5:await cell(5),6:await cell(6),7:await cell(7),8:await cell(8),9:await box('#rows tr [data-edit]'),10:await box('#rows tr [data-id]')}};
 // 5 speler
 const pl=await p.evaluate(()=>{const r=document.querySelector('#player').getBoundingClientRect();return{x:r.x,y:r.y,w:r.width,h:r.height}});
 await p.screenshot({path:'shots/speler.png',clip:{x:0,y:pl.y,width:1600,height:pl.h}});
 meta.speler={clip:{x:0,y:pl.y,width:1600,height:pl.h},marks:{1:await p.evaluate(()=>{const r=document.querySelector('#pp').getBoundingClientRect();return{x:r.x,y:r.y,w:r.width,h:r.height}}),2:await p.evaluate(()=>{const r=document.querySelector('.seek').getBoundingClientRect();return{x:r.x,y:r.y,w:r.width,h:r.height}}),3:await p.evaluate(()=>{const r=document.querySelector('.cues').getBoundingClientRect();return{x:r.x,y:r.y,w:r.width,h:r.height}})}};
 await p.evaluate(()=>{$('#player').hidden=true;state.playing=null;render()});
 // 6 programma-uur
 await p.evaluate(()=>{state.run=[7,0,32,16,23,30,8];state.talk=12;state.run.forEach((id,i)=>{T[id].tkey=['8A','9A','9B','10B','10A','11A','11B'][i];T[id].nrg=[3,4,5,6,7,8,9][i]});state.shape='op';$('#shape').value='op';render()});
 await p.evaluate(()=>{document.querySelector('#sec-uur').style.position='static';document.querySelector('#run').style.maxHeight='none'});const u=await box('#sec-uur');const clipU={x:u.x-10,y:u.y-10,width:u.w+20,height:u.h+20};
 await p.screenshot({path:'shots/uur.png',clip:clipU,fullPage:true});
 meta.uur={clip:clipU,marks:{1:await box('#airDate'),2:await box('.clock'),3:await box('#curveBox'),4:await box('#shape'),5:await box('#talk'),6:await box('#fill'),7:await box('#run'),8:await box('#zipMp3'),9:await box('#copy'),10:await box('#saveHour'),11:await box('#aired'),12:await box('#hours')}};
 // 7 bewerkvenster
 await p.evaluate(()=>openEditor(T.findIndex(t=>t.title==='Last Christmas')));await p.waitForTimeout(200);
 const ed=await p.evaluate(()=>{const r=document.querySelector('#ed').getBoundingClientRect();return{x:r.x,y:r.y,w:r.width,h:r.height}});
 await p.screenshot({path:'shots/bewerken.png',clip:{x:ed.x-24,y:ed.y-24,width:ed.w+48,height:ed.h+48}});
 meta.bewerken={clip:{x:ed.x-24,y:ed.y-24,width:ed.w+48,height:ed.h+48},marks:{}};
 const ov=await box('#sec-over');const clipO={x:ov.x-10,y:ov.y-10,width:ov.w+20,height:ov.h+20};await p.evaluate(()=>{const d=document.querySelector('#ed');if(d.open)d.close()});await p.screenshot({path:'shots/over.png',clip:clipO,fullPage:true});meta.over={clip:clipO,marks:{}};
 fs.writeFileSync('shots/meta.json',JSON.stringify(meta,null,1));
 await b.close();console.log('klaar');
})();
