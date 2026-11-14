import AxeBuilder from '@axe-core/playwright';
import { expect, test } from '@playwright/test';

const PAGES = [
  ['home', '/#/', 'Headline contrasts across three evaluation designs'],
  ['explorer', '/#/explorer?metric=sprint_speed&target=baserunning_rv', 'Same metric, different targets'],
  ['explorer (not evaluated)', '/#/explorer?metric=sprint_speed&target=pitching_fip', 'Same metric, different targets'],
  ['fantasy', '/#/fantasy?kind=target_forecast_added&target=fip&outcome=ERA', 'Who is in the fantasy pools'],
  ['casebook', '/#/casebook?contrast=pitching_fip:stuff_plus', 'Decile effects: Stuff+ → FIP'],
  ['models', '/#/models?target=pitching_fip', 'What the models are'],
  ['value lab', '/#/value-lab', 'Team 5×5 line'],
  ['methods', '/#/methods', 'Provenance'],
] as const;

for (const scheme of ['light', 'dark'] as const) {
  test(`axe: no serious or critical WCAG A/AA violations (${scheme})`, async ({ browser }) => {
    const context = await browser.newContext({ colorScheme: scheme, viewport: { width: 1280, height: 900 } });
    const page = await context.newPage();
    const report: string[] = [];
    for (const [name, url, ready] of PAGES) {
      await page.goto(url);
      await expect(page.getByRole('heading', { name: ready }).first()).toBeVisible();
      await page.waitForLoadState('networkidle');
      const results = await new AxeBuilder({ page }).withTags(['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa']).analyze();
      for (const v of results.violations) {
        if (v.impact === 'serious' || v.impact === 'critical') {
          report.push(`${name}: [${v.impact}] ${v.id} — ${v.help} (${v.nodes.length} node(s)): ${v.nodes.slice(0, 3).map((n) => n.target.join(' ')).join(' | ')}`);
        }
      }
    }
    expect(report, report.join('\n')).toEqual([]);
    await context.close();
  });
}

test('keyboard only: metric search, target radios and matrix cells work without a mouse', async ({ page }) => {
  await page.goto('/#/explorer?metric=ev&target=hitting_woba');
  await expect(page.locator('article .card-head [data-verdict]')).toHaveAttribute('data-verdict', 'Projection');
  const box = page.getByRole('combobox', { name: /Metric/ });
  await box.focus();
  await page.keyboard.type('sprint speed');
  // the first match is highlighted as you type; arrows move through the list
  await page.keyboard.press('ArrowDown');
  await expect(page.getByRole('option', { name: /Year-over-year sprint speed change/ })).toHaveAttribute('aria-selected', 'true');
  await page.keyboard.press('ArrowUp');
  await expect(page.getByRole('option', { name: /^Statcast sprint speed/ })).toHaveAttribute('aria-selected', 'true');
  await page.keyboard.press('Enter');
  await expect(page.locator('article h2')).toHaveText('Statcast sprint speed → Next-season wOBA');
  // move through the target radio group with arrow keys
  await page.getByRole('radio', { name: 'wOBA' }).focus();
  await page.keyboard.press('ArrowRight'); // FIP
  await expect(page.locator('article .card-head [data-verdict]')).toHaveAttribute('data-verdict', 'Not evaluated');
  await page.keyboard.press('ArrowRight'); // Baserunning
  await expect(page.locator('article .card-head [data-verdict]')).toHaveAttribute('data-verdict', 'Projection');
  // focus is visible on the focused control
  const outline = await page.evaluate(() => getComputedStyle(document.activeElement as Element, null).outlineStyle);
  expect(['auto', 'solid']).toContain(outline === 'none' ? 'none' : outline);

  await page.goto('/#/fantasy?kind=target_forecast_added&target=woba&outcome=HR');
  const cell = page.getByRole('button', { name: /^FIP → WHIP:/ });
  await cell.focus();
  await page.keyboard.press('Enter');
  await expect(page.locator('article h2').first()).toHaveText('FIP forecast → Walks + hits per inning (WHIP)');
});
