import { beforeEach, describe, expect, it } from 'vitest';
import { render, screen, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import App from '../../src/App';
import { clearDataCache } from '../../src/data/load';
import { installDataFetch } from '../helpers/data';

const T = { timeout: 15000 };

beforeEach(() => {
  clearDataCache();
  installDataFetch();
});

async function card() {
  const h = await screen.findByRole('heading', { level: 2, name: /→/ }, T);
  return h.closest('article') as HTMLElement;
}

describe('Fantasy Linkage Explorer', () => {
  it('FIP forecast → ERA (primary linkage) adds information; wOBA → HR shows a null as prominently', async () => {
    window.location.hash = '#/fantasy?kind=target_forecast_added&target=fip&outcome=ERA';
    const user = userEvent.setup();
    render(<App />);
    let c = await card();
    expect(within(c).getByRole('heading', { level: 2 })).toHaveTextContent('FIP forecast → Earned run average (ERA)');
    expect(c.querySelector('.card-head [data-verdict]')).toHaveAttribute('data-verdict', 'adds information');
    expect(within(c).getAllByText('−1.17%').length).toBeGreaterThan(0);
    expect(within(c).getByText(/Primary pre-specified linkage/)).toBeInTheDocument();
    expect(within(c).getByText(/association only/i, { selector: 'strong' })).toBeInTheDocument();
    expect(within(c).getByText(/2026 \(exploratory\): one season/)).toBeInTheDocument();

    await user.click(screen.getByRole('radio', { name: 'wOBA' }));
    await user.click(screen.getByRole('radio', { name: 'HR' }));
    c = await card();
    expect(c.querySelector('.card-head [data-verdict]')).toHaveAttribute('data-verdict', 'no detectable gain');
    expect(within(c).getAllByText(/^Across 2021–2025 \(pooled\), adding the wOBA forecast.*The interval includes zero: no detectable gain\.$/)).toHaveLength(1);
    expect(within(c).queryByText(/adds information about/)).toBeNull();
  });

  it('the overview matrix lists every result, including harmful ones, and selecting a cell opens it', async () => {
    window.location.hash = '#/fantasy?kind=admitted_vs_history_target_forecast&target=woba&outcome=HR';
    const user = userEvent.setup();
    render(<App />);
    await card();
    const harmful = screen.getByRole('button', { name: /Hitter bWAR → AVG: .*Harmful/ });
    await user.click(harmful);
    const c = await card();
    expect(c.querySelector('.card-head [data-verdict]')).toHaveAttribute('data-verdict', 'harmful');
    expect(within(c).getAllByText(/^Across 2021–2025 \(pooled\).*less accurate \(harmful\)\.$/)).toHaveLength(1);
  });
});
