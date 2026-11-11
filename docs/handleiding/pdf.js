const {chromium}=require('playwright');
(async()=>{const b=await chromium.launch();const p=await b.newPage();
 await p.goto('file://'+__dirname+'/cover.html');await p.waitForTimeout(500);
 await p.pdf({path:'cover.pdf',width:'210mm',height:'297mm',printBackground:true,margin:{top:0,right:0,bottom:0,left:0},pageRanges:'1'});
 await p.goto('file://'+__dirname+'/body.html');await p.waitForTimeout(800);
 await p.pdf({path:'body.pdf',format:'A4',printBackground:true,preferCSSPageSize:true,displayHeaderFooter:true,
  headerTemplate:'<span></span>',
  footerTemplate:'<div style="width:100%;font:7pt Helvetica,Arial,sans-serif;color:#8A94A6;padding:0 15mm;display:flex;justify-content:space-between"><span>CURIOUS XXL · Handleiding · © 2026 Han Koopman · Niet verspreiden zonder toestemming</span><span><span class="pageNumber"></span></span></div>'});
 await b.close();})();
