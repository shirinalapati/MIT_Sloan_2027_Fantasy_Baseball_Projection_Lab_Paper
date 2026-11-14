import { expect, test, type Page } from '@playwright/test';
import { mkdirSync } from 'node:fs';
import path from 'node:path';

const SHOTS = path.resolve(process.cwd(), 'screenshots');
mkdirSync(SHOTS, { recursive: true });

const SCREENS = [
  { name: 'home', url: '/#/', h1: 'Fantasy Projection Lab', ready: 'Headline contrasts across three evaluation designs' },
  { name: 'explorer', url: '/#/explorer?metric=sprint_speed&target=baserunning_rv', h1: 'Metric → Target Explorer', ready: 'Same metric, different targets' },
  { name: 'fantasy', url: '/#/fantasy?kind=target_forecast_added&target=fip&outcome=ERA', h1: 'Fantasy Linkage Explorer', ready: 'Who is in the fantasy pools' },
  { name: 'casebook', url: '/#/casebook?contrast=pitching_fip:stuff_plus', h1: 'Player Casebook', ready: 'Decile effects: Stuff+ → FIP' },
  { name: 'models', url: '/#/models?target=pitching_fip', h1: 'Model Comparison', ready: 'What the models are' },
  { name: 'value-lab', url: '/#/value-lab', h1: 'Fantasy Value Lab', ready: 'Team 5×5 line' },
  { name: 'methods', url: '/#/methods', h1: 'Methods, Limits & Sources', ready: 'Provenance' },
] as const;

const NAV = [
  ['Home', 'Fantasy Projection Lab'],
  ['Metric Explorer', 'Metric → Target Explorer'],
  ['Fantasy Linkage', 'Fantasy Linkage Explorer'],
  ['Player Casebook', 'Player Casebook'],
  ['Model Comparison', 'Model Comparison'],
  ['Value Lab', 'Fantasy Value Lab'],
  ['Methods & Sources', 'Methods, Limits & Sources'],
] as const;

/** Collect console errors, uncaught exceptions, failed requests and HTTP errors. */
function watch(page: Page) {
  const problems: string[] = [];
  page.on('console', (m) => {
    if (m.type() === 'error') problems.push(`console: ${m.text()}`);
  });
  page.on('pageerror', (e) => problems.push(`pageerror: ${e.message}`));
  page.on('requestfailed', (r) => problems.push(`requestfailed: ${r.url()}`));
  page.on('response', (r) => {
    if (r.status() >= 400) problems.push(`http ${r.status()}: ${r.url()}`);
  });
  return problems;
}

async function openScreen(page: Page, s: (typeof SCREENS)[number]) {
  await page.goto(s.url);
  await expect(page.getByRole('heading', { level: 1, name: s.h1 })).toBeVisible();
  await expect(page.getByRole('heading', { name: s.ready }).first()).toBeVisible();
  await page.waitForLoadState('networkidle');
}

test('the app loads every screen with no console errors or failed requests', async ({ page }) => {
  const problems = watch(page);
  for (const s of SCREENS) await openScreen(page, s);
  expect(problems).toEqual([]);
});

test('every nav tab works (desktop)', async ({ page }) => {
  const problems = watch(page);
  await page.setViewportSize({ width: 1440, height: 900 });
  await page.goto('/#/');
  const nav = page.getByRole('navigation', { name: 'Main' });
  for (const [label, h1] of NAV) {
    await nav.getByRole('link', { name: label }).click();
    await expect(page.getByRole('heading', { level: 1, name: h1 })).toBeVisible();
    await expect(nav.getByRole('link', { name: label })).toHaveAttribute('aria-current', 'page');
  }
  expect(problems).toEqual([]);
});

test('every nav tab works (mobile menu) and no page scrolls horizontally', async ({ page }) => {
  const problems = watch(page);
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto('/#/');
  for (const [label, h1] of NAV) {
    await page.getByRole('button', { name: 'Menu' }).click();
    await page.getByRole('navigation', { name: 'Main' }).getByRole('link', { name: label }).click();
    await expect(page.getByRole('heading', { level: 1, name: h1 })).toBeVisible();
    await page.waitForLoadState('networkidle');
    const overflow = await page.evaluate(() => document.documentElement.scrollWidth - window.innerWidth);
    expect(overflow, `horizontal overflow on ${label}`).toBeLessThanOrEqual(0);
  }
  expect(problems).toEqual([]);
});

test('no horizontal page scroll at 360 px on any screen', async ({ page }) => {
  await page.setViewportSize({ width: 360, height: 780 });
  for (const s of SCREENS) {
    await openScreen(page, s);
    const overflow = await page.evaluate(() => document.documentElement.scrollWidth - window.innerWidth);
    expect(overflow, `horizontal overflow on ${s.name}`).toBeLessThanOrEqual(0);
  }
});

test('explorer: search and target filters operate, known values appear', async ({ page }) => {
  const problems = watch(page);
  await page.goto('/#/explorer?metric=ev&target=pitching_fip');
  await expect(page.locator('article .card-head [data-verdict]')).toHaveAttribute('data-verdict', 'Not evaluated');
  const box = page.getByRole('combobox', { name: /Metric/ });
  await box.click();
  await box.fill('sprint');
  await page.getByRole('option', { name: /Statcast sprint speed/ }).click();
  await page.getByRole('radio', { name: 'Baserunning' }).check();
  const card = page.locator('article').first();
  await expect(card.getByRole('heading', { level: 2 })).toHaveText('Statcast sprint speed → Next-season baserunning run-value rate');
  await expect(card.locator('.card-head [data-verdict]')).toHaveAttribute('data-verdict', 'Projection');
  await expect(card.getByText('−4.28%').first()).toBeVisible();
  await page.getByRole('radio', { name: 'wOBA' }).check();
  await expect(card.locator('.card-head [data-verdict]')).toHaveAttribute('data-verdict', 'Diagnostic');
  await expect(card.getByText('+0.08%').first()).toBeVisible();
  // candidate table verdict filter
  await page.getByRole('radio', { name: /^Projection \(\d+\)$/ }).check();
  await expect(page.getByText(/^Showing \d+ of 62 candidates for wOBA\.$/)).toBeVisible();
  expect(problems).toEqual([]);
});

test('models: FIP selection policy lift shows −7.50%', async ({ page }) => {
  await page.goto('/#/models?target=pitching_fip');
  await expect(page.getByRole('img', { name: /^ADM vs B0 \(selection policy lift\): −7\.50%/ })).toBeVisible();
  await page.getByRole('radio', { name: 'LightGBM' }).check();
  await expect(page.getByText('Only B0, ADM and KS were refit with this estimator.')).toBeVisible();
});

test('casebook and fantasy filters operate', async ({ page }) => {
  const problems = watch(page);
  await page.goto('/#/casebook?contrast=pitching_fip:stuff_plus');
  await expect(page.locator('p[role="status"]')).toContainText('Showing 60 of 420 cases');
  await page.getByRole('radio', { name: 'Largest forecast decreases' }).check();
  await expect(page.locator('p[role="status"]')).toContainText('Showing 20 of 420 cases');
  await page.getByLabel('Search player').fill('zzzz');
  await expect(page.getByText('No cases match these filters.')).toBeVisible();

  await page.goto('/#/fantasy?kind=target_forecast_added&target=woba&outcome=HR');
  await expect(page.locator('article .card-head [data-verdict]').first()).toHaveAttribute('data-verdict', 'no detectable gain');
  await page.getByRole('button', { name: /^FIP → ERA:/ }).click();
  await expect(page.locator('article .card-head [data-verdict]').first()).toHaveAttribute('data-verdict', 'adds information');
  expect(problems).toEqual([]);
});

test('value lab recomputes from components', async ({ page }) => {
  await page.goto('/#/value-lab');
  const hitting = page.locator('.card', { has: page.getByRole('heading', { name: 'Hitting categories' }) });
  await expect(hitting.getByText('.267')).toBeVisible();
  const c = page.getByRole('group', { name: 'Hitter C' });
  await c.getByRole('spinbutton', { name: 'At-bats' }).fill('600');
  await expect(hitting.getByText('.219')).toBeVisible();
});

for (const theme of ['light', 'dark'] as const) {
  test(`screenshots (${theme})`, async ({ browser }) => {
    for (const vp of [
      { tag: 'desktop', width: 1440, height: 900 },
      { tag: 'mobile', width: 390, height: 844 },
    ]) {
      const context = await browser.newContext({ viewport: { width: vp.width, height: vp.height }, colorScheme: theme });
      const page = await context.newPage();
      const problems = watch(page);
      for (const s of SCREENS) {
        if (theme === 'dark' && vp.tag === 'mobile' && !['explorer', 'fantasy', 'value-lab'].includes(s.name)) continue;
        await openScreen(page, s);
        const file = `${s.name}-${vp.tag}${theme === 'dark' ? '-dark' : ''}.png`;
        await page.screenshot({ path: path.join(SHOTS, file), fullPage: true });
      }
      if (theme === 'light') {
        await page.goto('/#/value-lab');
        await page.getByRole('radio', { name: 'Points' }).check();
        await expect(page.getByRole('heading', { name: 'Points', exact: true })).toBeVisible();
        await page.screenshot({ path: path.join(SHOTS, `value-lab-points-${vp.tag}.png`), fullPage: true });
      }
      expect(problems).toEqual([]);
      await context.close();
    }
  });
}
