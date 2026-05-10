import { test, expect } from '@playwright/test';

const URL = 'https://aleemuh001.framer.ai/contact';

test.describe('Portfolio Contact Form', () => {
  test('page loads with correct heading and form fields', async ({ page }) => {
    await page.goto(URL, { waitUntil: 'networkidle' });

    await expect(page.getByText("Let's get in touch")).toBeVisible();
    await expect(page.getByPlaceholder('Name')).toBeVisible();
    await expect(page.getByPlaceholder('Email Address')).toBeVisible();
    await expect(page.getByPlaceholder('Message')).toBeVisible();
    await expect(page.getByRole('button', { name: 'Send Message' })).toBeVisible();
  });

  test('fills out contact form with valid data', async ({ page }) => {
    await page.goto(URL, { waitUntil: 'networkidle' });

    await page.getByPlaceholder('Name').fill('Test User');
    await page.getByPlaceholder('Email Address').fill('test@example.com');
    await page.getByPlaceholder('Message').fill('This is a test message from Playwright automation.');

    // Verify all fields are filled correctly before submitting
    await expect(page.getByPlaceholder('Name')).toHaveValue('Test User');
    await expect(page.getByPlaceholder('Email Address')).toHaveValue('test@example.com');
    await expect(page.getByPlaceholder('Message')).toHaveValue('This is a test message from Playwright automation.');
  });

  test('submits form and shows confirmation', async ({ page }) => {
    await page.goto(URL, { waitUntil: 'networkidle' });

    await page.getByPlaceholder('Name').fill('Aleem Test');
    await page.getByPlaceholder('Email Address').fill('hassanaleem86@gmail.com');
    await page.getByPlaceholder('Message').fill('Playwright automation test submission — ignore this message.');

    await page.getByRole('button', { name: 'Send Message' }).click();

    // Button turns green and reads "Thank you" on successful submission
    await expect(page.getByRole('button', { name: 'Thank you' })).toBeVisible({ timeout: 10000 });
    await page.screenshot({ path: 'output/screenshots/contact-form-submitted.png', fullPage: false });
  });

  test('send button is enabled after filling form', async ({ page }) => {
    await page.goto(URL, { waitUntil: 'networkidle' });

    await page.getByPlaceholder('Name').fill('Test User');
    await page.getByPlaceholder('Email Address').fill('test@example.com');
    await page.getByPlaceholder('Message').fill('Checking button state after filling form.');

    await expect(page.getByRole('button', { name: 'Send Message' })).toBeEnabled();
  });

  test('social links are visible in footer', async ({ page }) => {
    await page.goto(URL, { waitUntil: 'networkidle' });

    const footer = page.getByRole('contentinfo');
    await expect(footer.getByRole('link', { name: /linkedin/i }).first()).toBeVisible();
    await expect(footer.getByRole('link', { name: /instagram/i }).first()).toBeVisible();
    await expect(footer.getByRole('link', { name: /facebook/i }).first()).toBeVisible();
  });
});
