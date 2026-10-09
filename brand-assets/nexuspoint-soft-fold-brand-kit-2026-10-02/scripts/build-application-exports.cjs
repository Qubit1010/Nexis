const fs=require('node:fs');
const path=require('node:path');
const sharp=require('sharp');
const {chromium}=require('playwright');
const kit=path.dirname(__dirname),out=path.join(kit,'applications');
(async()=>{
 const reports=[];
 for(const file of fs.readdirSync(out).filter(f=>f.endsWith('.svg'))){
  const raw=fs.readFileSync(path.join(out,file),'utf8');
  const w=Number(raw.match(/<svg[^>]+width="([\d.]+)"/)[1]);
  const h=Number(raw.match(/<svg[^>]+height="([\d.]+)"/)[1]);
  const png=path.join(out,file.replace('.svg','.png'));
  const size=file==='portfolio-qr.svg'?370:w;
  const pngBuffer=await sharp(Buffer.from(raw),{density:144}).resize({width:size}).withMetadata({density:file.startsWith('Business-Card')?300:96}).png().toBuffer();
  fs.writeFileSync(png,pngBuffer);
  const meta=await sharp(png).metadata();
  if(file!=='portfolio-qr.svg' && (meta.width!==w || meta.height!==h))throw Error('Incorrect export dimensions: '+file);
  reports.push({file: path.basename(png),width:meta.width,height:meta.height,density:meta.density});
 }
 const front=fs.readFileSync(path.join(out,'Business-Card-Soft-Fold-Front.svg'),'utf8');
 const back=fs.readFileSync(path.join(out,'Business-Card-Soft-Fold-Back.svg'),'utf8');
 const browser=await chromium.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:true});
 try{
  const page=await browser.newPage();
  await page.setContent('<!doctype html><html><head><style>@page{size:3.75in 2.25in;margin:0}html,body{margin:0;padding:0}.card{width:3.75in;height:2.25in;overflow:hidden;break-after:page}.card:last-child{break-after:auto}.card svg{display:block;width:100%;height:100%}</style></head><body><div class="card">'+front+'</div><div class="card">'+back+'</div></body></html>');
  await page.pdf({path:path.join(out,'Business-Card-Soft-Fold-Print.pdf'),width:'3.75in',height:'2.25in',preferCSSPageSize:true,printBackground:true,margin:{top:0,right:0,bottom:0,left:0}});
 }finally{await browser.close()}
 function embed(name,x,y,w,h){const data=fs.readFileSync(path.join(out,name)).toString('base64');return `<image href="data:image/png;base64,${data}" x="${x}" y="${y}" width="${w}" height="${h}"/>`}
 const proof='<svg xmlns="http://www.w3.org/2000/svg" width="1254" height="1400"><rect width="1254" height="1400" fill="#101010"/>'+embed('Business-Card-Soft-Fold-Front.png',65,50,1124,674.4)+embed('Business-Card-Soft-Fold-Back.png',65,740,1124,674.4)+'</svg>';
 // Keep both card faces fully inside the proof canvas.
 const proofBuffer=await sharp(Buffer.from(proof.replace('height="1400"','height="1465"').replace('height="1400"','height="1465"'))).png().toBuffer();
 const locked=fs.existsSync(path.join(out,'business-card-selection.json'));
 fs.writeFileSync(path.join(out,locked?'Business-Card-Soft-Fold-Final-Proof.png':'Business-Card-Soft-Fold-Proof-v2.png'),proofBuffer);
 fs.writeFileSync(path.join(kit,'qa/application-export-validation.json'),JSON.stringify({date:'2026-10-02',exports:reports,cardPDF:'Business-Card-Soft-Fold-Print.pdf',status:'rendered; visual and QR review required'},null,2)+'\n');
 console.log(JSON.stringify({exports:reports,pdf:'Business-Card-Soft-Fold-Print.pdf'},null,2));
})().catch(e=>{console.error(e);process.exitCode=1});
