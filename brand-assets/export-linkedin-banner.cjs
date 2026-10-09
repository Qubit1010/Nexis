/* Production export only: centre crop the generated master and resize to LinkedIn's recommended 4:1 canvas. */
const fs=require("node:fs");
const path=require("node:path");
const sharp=require("sharp");
(async()=>{
 const root=__dirname;
 const master=path.join(root,"LinkedIn-Banner-Aleem-Wrapped-Nexus-Master.png");
 const output=path.join(root,"LinkedIn-Banner-Aleem-Wrapped-Nexus.png");
 if(!fs.existsSync(master))fs.copyFileSync(output,master);
 const meta=await sharp(master).metadata();
 const cropHeight=Math.round(meta.width/4);
 const cropTop=Math.round((meta.height-cropHeight)/2);
 await sharp(master).extract({left:0,top:cropTop,width:meta.width,height:cropHeight}).resize(1584,396,{kernel:"lanczos3"}).png().toFile(output);
 const final=await sharp(output).metadata();
 const report={creativeTool:"Built-in imagegen",master:path.basename(master),masterPixels:[meta.width,meta.height],export:path.basename(output),pixels:[final.width,final.height],exportProcess:"Centre crop and resize only; no logo, typography or background retouching",crop:{left:0,top:cropTop,width:meta.width,height:cropHeight},platformSource:"https://www.linkedin.com/help/linkedin/answer/a568217",bytes:fs.statSync(output).size};
 fs.writeFileSync(path.join(root,"LinkedIn-Banner-Aleem-Wrapped-Nexus.validation.json"),JSON.stringify(report,null,2)+"\n");
 console.log(JSON.stringify(report,null,2));
})().catch(e=>{console.error(e);process.exitCode=1});
