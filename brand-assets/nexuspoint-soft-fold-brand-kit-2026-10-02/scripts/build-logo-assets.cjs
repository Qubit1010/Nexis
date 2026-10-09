/* Export the newly reconstructed native SVGs, never edit the source raster.
 * Usage: NODE_PATH=<path to installed sharp> node scripts/build-logo-assets.cjs
 */
const fs = require('node:fs');
const path = require('node:path');
const sharp = require('sharp');
const kit = path.dirname(__dirname);
const logos = path.join(kit, 'logos');
const png = path.join(logos, 'png');
const fav = path.join(logos, 'favicons');
const geometry=JSON.parse(fs.readFileSync(path.join(logos,'geometry-and-method.json'),'utf8'));
fs.mkdirSync(png, {recursive:true});
fs.mkdirSync(fav, {recursive:true});

async function main() {
  const files = fs.readdirSync(logos).filter(x => x.endsWith('.svg'));
  for (const name of files) {
    const size = name.includes('symbol') ? 1200 : name.includes('stacked') ? 1600 : 2400;
    await sharp(path.join(logos, name), {density:300})
      .resize({width:size})
      .png()
      .toFile(path.join(png, name.replace('.svg', '.png')));
  }
  const buffers=[];
  for(const size of [16,32,48,64,128,180,192,256,512]) {
    const file=path.join(fav, `nexuspoint-${size}.png`);
    const buf=await sharp(path.join(logos, 'nexuspoint-favicon.svg'), {density:300})
      .resize(size,size)
      .png()
      .toBuffer();
    fs.writeFileSync(file,buf);
    if([16,32,48,64,256].includes(size)) buffers.push({size,buf});
  }
  // PNG-in-ICO is supported by modern browsers/Windows. Native PNGs are also supplied.
  const head=Buffer.alloc(6+16*buffers.length);
  head.writeUInt16LE(0,0);head.writeUInt16LE(1,2);head.writeUInt16LE(buffers.length,4);
  let offset=head.length;
  buffers.forEach(({size,buf},i)=>{
    const p=6+i*16;
    head[p]=size===256?0:size;head[p+1]=size===256?0:size;
    head[p+2]=0;head[p+3]=0;
    head.writeUInt16LE(1,p+4);head.writeUInt16LE(32,p+6);
    head.writeUInt32LE(buf.length,p+8);head.writeUInt32LE(offset,p+12);
    offset+=buf.length;
  });
  fs.writeFileSync(path.join(fav,'favicon.ico'),Buffer.concat([head,...buffers.map(x=>x.buf)]));
  // Source-scale exports support the contour-fidelity check in the Python builder.
  await sharp(path.join(logos,'nexuspoint-symbol-transparent-white.svg')).resize(geometry.icon_bounds_source[2],geometry.icon_bounds_source[3]).png().toFile(path.join(png,'nexuspoint-symbol-native-scale-qa.png'));
  await sharp(path.join(logos,'nexuspoint-wordmark-white.svg')).resize(879,138).png().toFile(path.join(png,'nexuspoint-wordmark-native-scale-qa.png'));
  const sizes=[16,32,64];
  const images=sizes.map((size,i)=>{
    const x=25+i*190;
    const encoded=fs.readFileSync(path.join(fav,`nexuspoint-${size}.png`)).toString('base64');
    return `<text x="${x}" y="26" fill="white" font-family="sans-serif" font-size="16">${size} px enlarged</text><image x="${x}" y="50" width="144" height="144" style="image-rendering:pixelated" href="data:image/png;base64,${encoded}"/>`;
  }).join('');
  const review=`<svg xmlns="http://www.w3.org/2000/svg" width="600" height="220"><rect width="600" height="220" fill="#101010"/>${images}</svg>`;
  await sharp(Buffer.from(review)).png().toFile(path.join(png,'favicon-size-review.png'));
  console.log(`Exported ${files.length} SVG assets to PNG, 9 favicon PNG sizes, and multi-resolution ICO.`);
}
main().catch(e=>{console.error(e);process.exit(1)});
