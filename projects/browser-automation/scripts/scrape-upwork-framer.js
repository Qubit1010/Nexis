const { chromium } = require('playwright-extra');
const StealthPlugin = require('puppeteer-extra-plugin-stealth');
const { execSync } = require('child_process');

chromium.use(StealthPlugin());

const SEARCH_URL =
  'https://www.upwork.com/nx/search/jobs/?nav_dir=pop&per_page=50&q=framer&sort=recency&is_sts_vector_search_result=null';

(async () => {
  const browser = await chromium.launch({
    headless: false,
    args: ['--disable-blink-features=AutomationControlled'],
  });

  const ctx = await browser.newContext({
    userAgent:
      'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    viewport: { width: 1366, height: 768 },
    locale: 'en-US',
    timezoneId: 'Asia/Karachi',
  });

  const page = await ctx.newPage();

  console.log('Navigating to Upwork search...');
  await page.goto(SEARCH_URL, { waitUntil: 'domcontentloaded', timeout: 30000 });

  // Wait for Cloudflare challenge to clear or job tiles to appear
  console.log('Waiting for page to resolve...');
  try {
    await page.waitForSelector('[data-test="job-tile"], article[data-ev-label], div.job-tile', {
      timeout: 20000,
    });
  } catch {
    console.log('Primary selectors not found, trying fallback wait...');
    await page.waitForTimeout(5000);
  }

  const pageTitle = await page.title();
  console.log('Page title:', pageTitle);

  if (pageTitle.includes('Just a moment')) {
    console.error('Cloudflare challenge not cleared. Please run in headed mode and solve manually.');
    await browser.close();
    process.exit(1);
  }

  // Scroll to trigger lazy-loaded jobs
  await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight / 2));
  await page.waitForTimeout(1500);

  console.log('Scraping jobs...');

  const jobs = await page.evaluate(() => {
    // Upwork renders job tiles as articles or divs with data-test="job-tile"
    const tiles =
      document.querySelectorAll('[data-test="job-tile"]').length > 0
        ? document.querySelectorAll('[data-test="job-tile"]')
        : document.querySelectorAll('article');

    return Array.from(tiles).map((tile) => {
      const titleEl =
        tile.querySelector('[data-test="job-tile-title"] a') ||
        tile.querySelector('h2 a') ||
        tile.querySelector('h3 a') ||
        tile.querySelector('a[href*="/jobs/"]');

      const title = titleEl ? titleEl.innerText.trim() : '';
      const link = titleEl ? 'https://www.upwork.com' + titleEl.getAttribute('href') : '';

      const descEl =
        tile.querySelector('[data-test="job-description-text"]') ||
        tile.querySelector('.job-description') ||
        tile.querySelector('p');
      const description = descEl ? descEl.innerText.trim() : '';

      const budgetEl =
        tile.querySelector('[data-test="budget"]') ||
        tile.querySelector('[data-test="is-fixed-price"]') ||
        tile.querySelector('[data-test="hourly-rate"]') ||
        tile.querySelector('.js-budget');
      const budget = budgetEl ? budgetEl.innerText.trim() : '';

      const skillEls = tile.querySelectorAll('[data-test="token"] span, .skill-badge, .o-tag');
      const skills = Array.from(skillEls)
        .map((s) => s.innerText.trim())
        .filter(Boolean)
        .join(', ');

      const postedEl =
        tile.querySelector('[data-test="job-pubilshed-date"]') ||
        tile.querySelector('time') ||
        tile.querySelector('[data-test="posted-on"]');
      const posted = postedEl ? postedEl.innerText.trim() : '';

      const typeEl =
        tile.querySelector('[data-test="job-type"]') ||
        tile.querySelector('[data-test="employment-type"]');
      const jobType = typeEl ? typeEl.innerText.trim() : '';

      const levelEl = tile.querySelector('[data-test="contractor-tier"]');
      const level = levelEl ? levelEl.innerText.trim() : '';

      const proposalsEl = tile.querySelector('[data-test="proposals"]');
      const proposals = proposalsEl ? proposalsEl.innerText.trim() : '';

      return { title, link, budget, jobType, level, skills, posted, proposals, description: description.slice(0, 300) };
    });
  });

  console.log(`Found ${jobs.length} jobs.`);

  if (jobs.length === 0) {
    console.log('No jobs found — taking debug screenshot...');
    await page.screenshot({ path: 'output/screenshots/upwork-debug.png', fullPage: true });
    await browser.close();
    process.exit(1);
  }

  // Print as JSON for the gws pipe
  console.log('JOBS_JSON:' + JSON.stringify(jobs));

  await browser.close();
})().catch((err) => {
  console.error('Scraper error:', err.message);
  process.exit(1);
});
