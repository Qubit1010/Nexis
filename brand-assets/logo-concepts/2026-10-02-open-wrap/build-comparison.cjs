const fs = require('node:fs');
const path = require('node:path');
const {pathToFileURL} = require('node:url');
const {chromium} = require('playwright');
const sharp = require('sharp');
const root = __dirname;
const kit = '../../nexuspoint-wrapped-nexus-brand-kit-2026-10-02';
const variants = [
  {id:'01-open-wrap', title:'01 / Open Wrap', note:'Closest to the current logo. Slimmer sides, angled ends, more breathing room.'},
  {id:'02-soft-fold', title:'02 / Soft Fold', note:'Rounded shoulders and flowing folds soften the outer silhouette.'},
  {id:'03-split-flow', title:'03 / Split Flow', note:'Shorter side strokes and wider seams give the wrap a more open shape.'},
  {id:'04-tapered-nexus', title:'04 / Tapered Nexus', note:'Swept, pointed ends create a sharper sense of movement toward the centre.'}
];
const css = `
@font-face{font-family:Conthrax;src:url('${kit}/fonts/portfolio-local-use/conthrax-400.woff2') format('woff2');font-weight:400}
@font-face{font-family:Inter;src:url('${kit}/fonts/InterVariable.woff2') format('woff2');font-weight:100 900}
*{box-sizing:border-box}body{margin:0;background:#000;color:#fff;font:400 18px/1.45 Inter,Arial,sans-serif}
.sheet{width:1800px;padding:52px 52px 36px;background:#000}header{height:158px;display:flex;align-items:flex-start;justify-content:space-between;gap:40px}
.eyebrow{font-size:13px;letter-spacing:.2em;color:#02A1E1;margin:0 0 14px}.heading{font:400 30px/1.3 Conthrax,Inter,sans-serif;margin:0 0 14px}.intro{font-size:17px;color:#aaa;margin:0}
.baseline{width:450px;padding-top:5px}.baseline p{font-size:12px;color:#aaa;letter-spacing:.16em;margin:0 0 10px}.baseline img{display:block;width:410px;height:110px;object-fit:contain}
.grid{display:grid;grid-template-columns:repeat(2,830px);gap:30px 36px}.card{height:426px;border-top:1px solid #292929;padding-top:20px;overflow:hidden}
.card h2{font:400 22px/1.35 Conthrax,Inter,sans-serif;margin:0 0 10px}.lockup{width:830px;height:290px;background:#000;display:flex;justify-content:center;align-items:center;gap:6px;overflow:hidden}
.symbol{width:280px;height:280px;object-fit:contain;flex:none}.wordmark{width:480px;height:82px;object-fit:contain;flex:none}
.note{font-size:16px;line-height:1.5;color:#bdbdbd;max-width:780px;margin:12px 0 0}.foot{font-size:13px;letter-spacing:.03em;color:#777;margin:25px 0 0}
`;
const html = `<!doctype html><html lang='en'><head><meta charset='utf-8'><title>Wrapped Nexus, open shape variations</title><style>${css}</style></head><body><main class='sheet'><header><div><p class='eyebrow'>NEXUSPOINT / LOGO REFINEMENTS</p><h1 class='heading'>Wrapped Nexus, opened up.</h1><p class='intro'>Same N, centre point and wordmark. Four ways to soften the boxed outline.</p></div><div class='baseline'><p>CURRENT LOGO / REFERENCE</p><img src='${kit}/logos/nexuspoint-primary-transparent-white.svg' alt='Current Wrapped Nexus logo'></div></header><div class='grid'>${variants.map(v=>`<section class='card'><h2>${v.title}</h2><div class='lockup' id='${v.id}'><img class='symbol' src='${v.id}-symbol.png' alt='${v.title} symbol'><img class='wordmark' src='${kit}/logos/nexuspoint-wordmark-white.svg' alt='NexusPoint existing wordmark'></div><p class='note'>${v.note}</p></section>`).join('')}</div><p class='foot'>Concept previews. Existing wordmark outlines preserved. Headings use your actual Conthrax font.</p></main></body></html>`;
fs.writeFileSync(path.join(root,'logo-comparison.html'),html);
(async()=>{
 const browser=await chromium.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:true,args:['--allow-file-access-from-files']});
 try{
  const page=await browser.newPage({viewport:{width:1800,height:1180},deviceScaleFactor:1});
  const errors=[];page.on('pageerror',e=>errors.push(e.message));page.on('requestfailed',r=>errors.push(r.url()));
  await page.goto(pathToFileURL(path.join(root,'logo-comparison.html')).href);
  await page.evaluate(()=>document.fonts.ready);
  const missing=await page.locator('img').evaluateAll(items=>items.filter(i=>!i.complete||!i.naturalWidth).map(i=>i.src));
  if(missing.length)errors.push(...missing);
  if(!await page.evaluate(()=>document.fonts.check('400 22px Conthrax')))errors.push('Conthrax failed to load');
  await page.addStyleTag({content:'.lockup.exporting{position:fixed;left:0;top:0;z-index:1000}'});
  const exports=[];
  for(const v of variants){
   const element=page.locator('[id="'+v.id+'"]');await element.evaluate(el=>el.classList.add('exporting'));
   const filename=v.id+'-lockup.png';await element.screenshot({path:path.join(root,filename)});
   const meta=await sharp(path.join(root,filename)).metadata();
   if(meta.width!==830||meta.height!==290)errors.push(filename+': dimensions incorrect');
   exports.push({filename,width:meta.width,height:meta.height});
   await element.evaluate(el=>el.classList.remove('exporting'));
  }
  await page.locator('.sheet').screenshot({path:path.join(root,'logo-comparison.png')});
  const report={date:'2026-10-02',method:'Built-in imagegen concept symbols, native existing SVG wordmark, actual Conthrax headings',exports,errors};
  fs.writeFileSync(path.join(root,'validation-report.json'),JSON.stringify(report,null,2)+'\n');
  console.log(JSON.stringify(report,null,2));if(errors.length)process.exitCode=1;
 }finally{await browser.close()}
})().catch(e=>{console.error(e);process.exitCode=1});

