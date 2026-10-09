/* Actual portfolio-font typesetting over an imagegen background; native outlined logo. */
const fs=require("node:fs");
const path=require("node:path");
const {pathToFileURL}=require("node:url");
const {chromium}=require("playwright");
const sharp=require("sharp");
const root=__dirname;
const kit=path.resolve(root,"../nexuspoint-wrapped-nexus-brand-kit-2026-10-02");
const fonts="../nexuspoint-wrapped-nexus-brand-kit-2026-10-02/fonts/";
const variants=[
 {id:"conthrax",family:"Conthrax",label:"01 · Conthrax",note:"Recommended: broad, restrained technology lettering.",case:"upper"},
 {id:"ethnocentric",family:"Ethnocentric",label:"02 · Ethnocentric",note:"Closest to the portfolio hero, with the strongest geometric character.",case:"upper"},
 {id:"nasalization",family:"Nasalization",label:"03 · Nasalization",note:"Lighter and more approachable, with rounded technical forms.",case:"normal"},
 {id:"mokoto",family:"Mokoto",label:"04 · Mokoto",note:"More graphic and experimental. Compare readability at phone size.",case:"upper"},
 {id:"gambetta",family:"Gambetta",label:"05 · Gambetta Light Italic",note:"An editorial alternative with a softer personal tone.",case:"normal",italic:true}
];
const faces=variants.map(v=>'@font-face{font-family:"'+v.family+'";src:url("'+fonts+'portfolio-local-use/'+(v.id==="gambetta"?"gambetta-300-italic":v.id+"-400")+'.woff2") format("woff2");font-weight:'+(v.italic?300:400)+';font-style:'+(v.italic?"italic":"normal")+';font-display:block}').join("\n");
const logo=fs.readFileSync(path.join(kit,"logos/nexuspoint-primary-transparent-white.svg"),"utf8");
const css=[
faces,
'@font-face{font-family:Inter;src:url("'+fonts+'InterVariable.woff2") format("woff2");font-weight:100 900}',
'*{box-sizing:border-box}body{margin:0;padding:32px;background:#202020;color:#fff;font:400 16px/1.5 Inter,Arial,sans-serif}main{max-width:1584px;margin:auto}h1{font-size:30px;letter-spacing:-.03em;line-height:1.2;margin:0 0 10px}header{margin-bottom:24px}header p{color:#ccc;margin:0 0 12px}header a{color:#02A1E1}.variant{margin:0 0 24px;background:#000;border:1px solid #424242}.label{padding:14px 20px;display:flex;justify-content:space-between;align-items:center;gap:24px;font-size:14px;background:#101010}.label h2{font-size:16px;margin:0;font-weight:500}.label p{font-size:13px;margin:0;color:#aaa}.label a{color:#02A1E1;white-space:nowrap}.preview{width:100%;aspect-ratio:4;overflow:hidden;position:relative}.banner{width:1584px;height:396px;position:absolute;top:0;left:0;transform-origin:0 0;background:#000;overflow:hidden;color:#fff}.backdrop{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;object-position:center}.logo{position:absolute;left:1120px;top:24px;width:336px;height:91px}.logo svg{display:block;width:100%;height:auto}.copy{position:absolute;left:516px;top:144px;width:942px}.name{font-size:62px;line-height:1.15;white-space:nowrap;margin:0 0 15px;font-weight:400;letter-spacing:.01em;text-transform:none}.role{font:400 19px/1.4 Nasalization,Inter,sans-serif;color:#02A1E1;letter-spacing:.15em;margin:0 0 18px}.tagline{font:500 29px/1.25 Inter,sans-serif;margin:0;letter-spacing:-.02em;white-space:nowrap}.tagline span{color:#02A1E1}.url{position:absolute;right:128px;bottom:34px;font:400 17px/1.4 Nasalization,Inter,sans-serif;letter-spacing:.12em}.url:after{content:"";display:block;width:100px;height:1px;background:#02A1E1;margin-top:7px}.upper .name{text-transform:uppercase}.italic .name{font-weight:300;font-style:italic}.credits{font-size:12px;color:#aaa;max-width:85ch;margin:30px 0 0}'
,'main{max-width:1586px}'
].join("\n");
const sections=variants.map(v=>'<section class="variant" id="'+v.id+'"><div class="label"><div><h2>'+v.label+'</h2><p>'+v.note+'</p></div><a href="LinkedIn-Banner-'+v.family+'.png" download>Download PNG</a></div><div class="preview"><div class="banner '+(v.case==="upper"?"upper":"")+' '+(v.italic?"italic":"")+'" data-font="'+v.family+'" data-id="'+v.id+'"><img class="backdrop" src="background-master.png" alt=""><div class="logo">'+logo+'</div><div class="copy"><h1 class="name" style="font-family:'+v.family+'">Aleem Ul Hassan</h1><p class="role">AI SYSTEMS &amp; AUTOMATION</p><p class="tagline">Automate the work. <span>Own the system.</span></p></div><div class="url">aleemuh.com</div></div></div></section>').join("\n");
async function ready(){
 await document.fonts.ready;
 for(const el of document.querySelectorAll(".name")){
  const st=getComputedStyle(el), family=st.fontFamily;
  await document.fonts.load((st.fontStyle==="italic"?"italic 300 ":"400 ")+"62px "+family);
  let size=62;el.style.fontSize=size+"px";
  while(el.scrollWidth>el.parentElement.clientWidth && size>30){size-=.5;el.style.fontSize=size+"px";}
 }
 const scale=()=>{for(const p of document.querySelectorAll(".preview")){p.firstElementChild.style.transform="scale("+p.clientWidth/1584+")"}};
 scale();window.addEventListener("resize",scale);
 return true;
}
const html='<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Aleem LinkedIn banner, portfolio font variations</title><style>'+css+'</style></head><body><main><header><h1>Portfolio fonts, compared.</h1><p>The same LinkedIn layout in five actual portfolio font families. Conthrax is the recommended starting point; Ethnocentric matches the portfolio hero most closely.</p><p><a href="../nexuspoint-wrapped-nexus-brand-kit-2026-10-02/fonts/portfolio-local-use/README.md">Portfolio font folder</a></p></header>'+sections+'<p class="credits">Native typesetting uses the exact downloaded WOFF2 files. The logo uses supplied outlines; the background was created with imagegen. These local preview sources use portfolio font files, so share the PNG exports rather than distributing the underlying fonts. Gambetta by Indian Type Foundry.</p></main><script>window.bannerReady=('+ready.toString()+')();</script></body></html>';
fs.writeFileSync(path.join(root,"font-comparison.html"),html);
(async()=>{
 const browser=await chromium.launch({executablePath:"C:/Program Files/Google/Chrome/Application/chrome.exe",headless:true,args:["--allow-file-access-from-files","--disable-gpu"]});
 try{
  const page=await browser.newPage({viewport:{width:1650,height:900},deviceScaleFactor:1});
  const errors=[];page.on("pageerror",e=>errors.push(e.message));page.on("requestfailed",r=>errors.push(r.url()));
  await page.goto(pathToFileURL(path.join(root,"font-comparison.html")).href);
  await page.evaluate(()=>window.bannerReady);
  await page.addStyleTag({content:'.banner.exporting{position:fixed!important;left:0!important;top:0!important;transform:none!important;z-index:10000}'});
  const reports=[];
  for(const v of variants){
   const selector='.banner[data-id="'+v.id+'"]';
   await page.locator(selector).evaluate(el=>el.classList.add("exporting"));
   const metrics=await page.locator(selector).evaluate(el=>{
    const name=el.querySelector(".name"),container=name.parentElement,style=getComputedStyle(name);
    const bounds=el.getBoundingClientRect();
    return {family:el.dataset.font,declaredFamily:style.fontFamily,fontSize:style.fontSize,fontStyle:style.fontStyle,nameScrollWidth:name.scrollWidth,availableWidth:container.clientWidth,width:bounds.width,height:bounds.height,fontReady:document.fonts.check(style.fontStyle+" "+style.fontWeight+" "+style.fontSize+" "+style.fontFamily),loadedFonts:[...document.fonts].filter(f=>f.status==="loaded").map(f=>f.family),missingImages:[...el.querySelectorAll("img")].filter(i=>!i.complete||!i.naturalWidth).length};
   });
   if(!metrics.fontReady || metrics.missingImages || metrics.nameScrollWidth>metrics.availableWidth || Math.abs(metrics.width-1584)>1 || Math.abs(metrics.height-396)>1)errors.push(v.family+": render validation failed");
   const output=path.join(root,"LinkedIn-Banner-"+v.family+".png");
   await page.locator(selector).screenshot({path:output});
   const actual=await sharp(output).metadata();
   metrics.exportWidth=actual.width;metrics.exportHeight=actual.height;
   if(actual.width!==1584 || actual.height!==396)errors.push(v.family+": incorrect PNG dimensions");
   await page.locator(selector).evaluate(el=>el.classList.remove("exporting"));
   reports.push(metrics);
  }
  await page.screenshot({path:path.join(root,"font-comparison.png"),fullPage:true});
  const report={date:"2026-10-02",method:"Actual local portfolio webfonts rendered in Chrome, native SVG logo, imagegen background",recommended:"Conthrax",dimensions:[1584,396],variants:reports,errors};
  fs.writeFileSync(path.join(root,"validation-report.json"),JSON.stringify(report,null,2)+"\n");
  console.log(JSON.stringify(report,null,2));
  if(errors.length)process.exitCode=1;
 }finally{await browser.close()}
})().catch(e=>{console.error(e);process.exitCode=1});
