/* Render the portable application examples. Uses local Playwright and Chrome. */
const fs = require("node:fs");
const path = require("node:path");
const { pathToFileURL } = require("node:url");
const { chromium } = require("playwright");
const kit = path.resolve(__dirname, "..");
const qa = path.join(kit, "qa", "templates");
fs.mkdirSync(qa, { recursive: true });

(async () => {
  const browser = await chromium.launch({
    executablePath: process.env.CHROME_EXECUTABLE || "C:/Program Files/Google/Chrome/Application/chrome.exe",
    headless: true,
    args: ["--allow-file-access-from-files", "--disable-gpu"]
  });
  const errors = [];
  const reports = [];
  const page = await browser.newPage();
  page.on("pageerror", e => errors.push(String(e)));
  page.on("requestfailed", r => errors.push(r.url() + ": " + r.failure()?.errorText));
  for (const target of [
    {file:"social-cover.svg", width:1584, height:396},
    {file:"proposal-cover.svg", width:794, height:1123},
    {file:"email-signature.html", width:1050, height:530},
    {file:"components.html", width:1440, height:1020},
    {file:"components.html", width:390, height:844, mobile:true}
  ]) {
    await page.setViewportSize({width:target.width, height:target.height});
    if(target.file.endsWith(".svg")) {
      const art=fs.readFileSync(path.join(kit, "templates", target.file),"utf8");
      await page.setContent('<!doctype html><html><head><style>html,body{margin:0;padding:0}svg{display:block}</style></head><body>'+art+'</body></html>');
    } else {
      await page.goto(pathToFileURL(path.join(kit, "templates", target.file)).href);
    }
    await page.evaluate(() => document.fonts.ready);
    const metrics = await page.evaluate(() => ({
      scrollWidth:document.documentElement.scrollWidth,
      viewport:window.innerWidth,
      images:[...document.images].map(i=>({source:i.getAttribute("src"), complete:i.complete, width:i.naturalWidth})),
      fonts:document.fonts.status
    }));
    if (metrics.scrollWidth > metrics.viewport + 1) errors.push(target.file + ": horizontal overflow");
    if (metrics.images.some(i=>!i.complete || i.width===0)) errors.push(target.file + ": missing image");
    const name=target.file.replace(/\.[^.]+$/,"") + (target.mobile?"-mobile":"");
    const screenshot=path.join(qa,name+".png");
    await page.screenshot({path:screenshot,fullPage:!target.file.endsWith(".svg")});
    if (target.file==="social-cover.svg") fs.copyFileSync(screenshot,path.join(kit,"templates","social-cover.png"));
    if (target.file==="proposal-cover.svg") {
      await page.addStyleTag({content:"@page{size:A4;margin:0}html,body{margin:0;padding:0;width:210mm;height:297mm;overflow:hidden}svg{display:block;width:210mm;height:297mm}"});
      await page.pdf({path:path.join(kit,"templates","proposal-cover.pdf"),format:"A4",printBackground:true,margin:{top:0,right:0,bottom:0,left:0},preferCSSPageSize:true});
    }
    reports.push({file:target.file,mobile:!!target.mobile,...metrics,screenshot:path.relative(kit,screenshot).replaceAll("\\","/")});
  }
  await browser.close();
  fs.writeFileSync(path.join(qa,"validation-report.json"),JSON.stringify({date:"2026-10-02",reports,errors},null,2)+"\n");
  console.log(JSON.stringify({renders:reports.length,errors},null,2));
  if(errors.length)process.exitCode=1;
})().catch(e=>{console.error(e);process.exitCode=1});
