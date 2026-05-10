import { chromium } from '@playwright/test';

const url = process.argv[2];
const selector = process.argv[3] || 'body';

if (!url) {
  console.error('Usage: npx ts-node scripts/scrape.ts <url> [css-selector]');
  process.exit(1);
}

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();

  await page.goto(url, { waitUntil: 'domcontentloaded' });

  const text = await page.locator(selector).innerText().catch(() => {
    console.error(`Selector "${selector}" not found on page.`);
    process.exit(1);
  });

  await browser.close();

  console.log(text);
})();
