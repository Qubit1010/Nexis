import { chromium } from '@playwright/test';
import path from 'path';
import fs from 'fs';

const url = process.argv[2];

if (!url) {
  console.error('Usage: npx ts-node scripts/screenshot.ts <url>');
  process.exit(1);
}

(async () => {
  const outputDir = path.join(__dirname, '..', 'output', 'screenshots');
  fs.mkdirSync(outputDir, { recursive: true });

  const filename = `${new URL(url).hostname}-${Date.now()}.png`;
  const outputPath = path.join(outputDir, filename);

  const browser = await chromium.launch();
  const page = await browser.newPage();

  await page.setViewportSize({ width: 1280, height: 900 });
  await page.goto(url, { waitUntil: 'networkidle' });
  await page.screenshot({ path: outputPath, fullPage: true });

  await browser.close();

  console.log(`Screenshot saved: ${outputPath}`);
})();
