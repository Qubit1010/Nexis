import { test, expect } from '@playwright/test';

test('example.com loads and has a title', async ({ page }) => {
  await page.goto('https://example.com');
  await expect(page).toHaveTitle(/Example Domain/);
});

test('example.com has a heading', async ({ page }) => {
  await page.goto('https://example.com');
  await expect(page.locator('h1')).toBeVisible();
});
