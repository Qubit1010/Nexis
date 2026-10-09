const fs=require('node:fs');
const path=require('node:path');
const {pathToFileURL}=require('node:url');
const sharp=require('sharp');
const {chromium}=require('playwright');
const folder=(process.argv.find(a=>a.startsWith('--directory='))||'--directory=card-variations').split('=')[1];
if(!/^[a-z0-9-]+$/.test(folder))throw Error('Invalid output directory');
const only=(process.argv.find(a=>a.startsWith('--only-prefix='))||'').split('=')[1];
const kit=path.dirname(__dirname),dir=path.join(kit,'applications',folder);
const manifest=JSON.parse(fs.readFileSync(path.join(dir,'design-manifest.json'),'utf8'));
const directions=manifest.directions;
const labels=directions.map(d=>d.name);
const prefixes=directions.map(d=>d.id.toLowerCase()+'-'+(d.slug||d.name.toLowerCase().replaceAll(' ','-')));
const isFolded=folder==='folded-edge-variations';
(async()=>{
 const reports=[];
 for(const file of fs.readdirSync(dir).filter(n=>n.endsWith('.svg')&&(!only||n.startsWith(only)))){
  const raw=fs.readFileSync(path.join(dir,file));
  const data=await sharp(raw,{density:144}).resize(1125,675).withMetadata({density:300}).png().toBuffer();
  fs.writeFileSync(path.join(dir,file.replace('.svg','.png')),data);
  reports.push({file:file.replace('.svg','.png'),width:1125,height:675,density:300});
 }
 const browser=await chromium.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:true});
 try{
  const page=await browser.newPage({viewport:{width:1536,height:960},deviceScaleFactor:1});
  let pdfCount=0;
  for(let i=0;i<prefixes.length;i++){
   const prefix=prefixes[i];
   if(only&&!prefix.startsWith(only))continue;
   const svg=n=>fs.readFileSync(path.join(dir,prefix+'-'+n+'.svg'),'utf8');
   await page.setContent('<!doctype html><html><head><style>@page{size:3.75in 2.25in;margin:0}html,body{margin:0;padding:0}.card{width:3.75in;height:2.25in;break-after:page;overflow:hidden}.card:last-child{break-after:auto}.card svg{display:block;width:100%;height:100%}</style></head><body><div class="card">'+svg('front')+'</div><div class="card">'+svg('back')+'</div></body></html>');
   const pdf=await page.pdf({width:'3.75in',height:'2.25in',preferCSSPageSize:true,printBackground:true,margin:{top:0,right:0,bottom:0,left:0}});
   fs.writeFileSync(path.join(dir,prefix+'-print.pdf'),pdf);
   pdfCount++;
  }
  const groups=prefixes.map((prefix,i)=>`<section class="direction" id="direction-${i+1}"><div class="heading"><h2><span>${directions[i].id}</span> ${labels[i]}</h2><p>Soft Fold · Conthrax · Nexus blue</p></div><div class="pair"><figure><figcaption>FRONT</figcaption><img src="${prefix}-front.png" alt="${labels[i]} front"></figure><figure><figcaption>BACK</figcaption><img src="${prefix}-back.png" alt="${labels[i]} back"></figure></div></section>`).join('');
  const html=`<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>NexusPoint card variations</title><style>@font-face{font-family:Inter;src:url('../../fonts/InterVariable.woff2')}*{box-sizing:border-box}body{margin:0;background:#E8ECEF;color:#071118;font-family:Inter,Arial,sans-serif}main{max-width:1536px;margin:auto;padding:45px 64px}header{padding:0 0 26px}header h1{font-size:32px;letter-spacing:-.04em;margin:0 0 10px}header p{font-size:15px;margin:0;color:#43535E}.direction{margin:0 0 40px;padding:25px 28px 28px;background:#F8F9FA;border:1px solid #CDD4D8;border-radius:12px}.heading{display:flex;justify-content:space-between;align-items:center;margin-bottom:22px}h2{font-size:23px;letter-spacing:-.025em;margin:0}h2 span{font-weight:450;color:#0079AA;margin-right:12px}.heading p{font-size:12px;color:#53616B;margin:0}.pair{display:grid;grid-template-columns:1fr 1fr;gap:25px}figure{margin:0}figcaption{font-size:10px;letter-spacing:.13em;font-weight:600;margin-bottom:10px;color:#53616B}img{display:block;width:100%;height:auto;box-shadow:0 6px 20px #07111818}.direction:last-child{margin-bottom:0}@media(max-width:900px){main{padding:26px 20px}.pair{grid-template-columns:1fr}.heading{display:block}.heading p{margin-top:8px}.direction{padding:22px}header h1{font-size:27px}}</style></head><body><main><header><h1>NexusPoint / Business card directions</h1><p>Three front-and-back designs. Every QR opens https://nexus-point.co/work.</p></header>${groups}</main></body></html>`;
  fs.writeFileSync(path.join(dir,'comparison.html'),isFolded?html.replace('NexusPoint / Business card directions','NexusPoint / Folded Edge refinements').replace('Three front-and-back designs. Every QR opens','More space below the divider. Every QR opens'):html);
  await page.goto(pathToFileURL(path.join(dir,'comparison.html')).href,{waitUntil:'load'});
  await page.evaluate(async()=>{await document.fonts.ready});
  const missing=await page.evaluate(()=>[...document.images].filter(i=>!i.complete||!i.naturalWidth).length);
  if(missing)throw Error('Missing card preview');
  await page.screenshot({path:path.join(dir,'comparison.png'),fullPage:true});
  for(let i=0;i<prefixes.length;i++)if(!only||prefixes[i].startsWith(only)){
   const suffix=folder==='card-variations'&&prefixes[i]==='03-folded-edge'?'-proof-spacing-fixed.png':'-proof.png';
   const proof=await page.locator('#direction-'+(i+1)).screenshot();
   fs.writeFileSync(path.join(dir,prefixes[i]+suffix),proof);
  }
  await page.setViewportSize({width:390,height:844});
  const width=await page.evaluate(()=>document.documentElement.scrollWidth);
  if(width>390)throw Error('Mobile comparison overflow: '+width);
  fs.writeFileSync(path.join(dir,'render-validation.json'),JSON.stringify({exports:reports,printPDFs:pdfCount,comparisonImages:only?2:4,missingImages:0,mobileViewport:390,mobileScrollWidth:width,status:'rendered; visual and QR checks pending'},null,2)+'\n');
  console.log(JSON.stringify({exports:reports.length,pdfs:pdfCount,comparison:'applications/'+folder+'/comparison.png',mobileWidth:width},null,2));
 }finally{await browser.close()}
})().catch(e=>{console.error(e);process.exitCode=1});
