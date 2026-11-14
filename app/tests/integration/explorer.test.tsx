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

async function resultCard() {
  const heading = await screen.findByRole('heading', { level: 2, name: /→/ }, T);
  return heading.closest('article') as HTMLElement;
}

describe('Metric → Target Explorer', () => {
  it('sprint speed × baserunning renders Projection and the published numbers', async () => {
    window.location.hash = '#/explorer?metric=sprint_speed&target=baserunning_rv';
    render(<App />);
    const card = await resultCard();
    expect(within(card).getByRole('heading', { level: 2 })).toHaveTextContent('Statcast sprint speed → Next-season baserunning run-value rate');
    expect(card.querySelector('.card-head [data-verdict]')).toHaveAttribute('data-verdict', 'Projection');
    expect(within(card).getAllByText('−4.28%').length).toBeGreaterThan(0);
    expect(within(card).getByText('95% CI [−5.15, −3.02]')).toBeInTheDocument();
    expect(within(card).getByText('7 of 7')).toBeInTheDocument();
    expect(within(card).getByText('Statistical finding.')).toBeInTheDocument();
    expect(within(card).getByText('0.92')).toBeInTheDocument(); // reliability r
    // metadata block
    expect(within(card).getByText('sloan2027/tables/table7_reason_codes_208.csv')).toBeInTheDocument();
    expect(within(card).getByText(/Evidence tier: Historical research evidence/)).toBeInTheDocument();
  });

  it('switching the target shows the same metric failing for wOBA, and "Not evaluated" for FIP', async () => {
    window.location.hash = '#/explorer?metric=sprint_speed&target=baserunning_rv';
    const user = userEvent.setup();
    render(<App />);
    await resultCard();
    await user.click(screen.getByRole('radio', { name: 'wOBA' }));
    let card = await resultCard();
    expect(card.querySelector('.card-head [data-verdict]')).toHaveAttribute('data-verdict', 'Diagnostic');
    expect(within(card).getAllByText('+0.08%').length).toBeGreaterThan(0);
    expect(within(card).getByText(/label is human-specified/)).toBeInTheDocument();

    await user.click(screen.getByRole('radio', { name: 'FIP' }));
    card = await resultCard();
    expect(card.querySelector('.card-head [data-verdict]')).toHaveAttribute('data-verdict', 'Not evaluated');
    expect(within(card).getByText(/No verdict exists for this pair/)).toBeInTheDocument();
    expect(within(card).queryByText('Projection')).toBeNull();
  });

  it('the metric search filters the catalog and selects a metric', async () => {
    window.location.hash = '#/explorer?metric=sprint_speed&target=pitching_fip';
    const user = userEvent.setup();
    render(<App />);
    await resultCard();
    const box = screen.getByRole('combobox', { name: /Metric/ });
    await user.click(box);
    await user.type(box, 'pitch-quality');
    const option = await screen.findByRole('option', { name: /Pitch-quality score/ });
    await user.click(option);
    const card = await resultCard();
    expect(within(card).getByRole('heading', { level: 2 })).toHaveTextContent(/Pitch-quality score.*→ Next-season FIP/);
    expect(card.querySelector('.card-head [data-verdict]')).toHaveAttribute('data-verdict', 'Projection');
    expect(window.location.hash).toContain('metric=stuff_plus');
  });

  it('lists the metric across all six targets, with "Not evaluated" rows', async () => {
    window.location.hash = '#/explorer?metric=sprint_speed&target=baserunning_rv';
    render(<App />);
    await resultCard();
    const across = screen.getByRole('heading', { name: 'Same metric, different targets' }).closest('section') as HTMLElement;
    expect(within(across).getAllByText('Not evaluated').length).toBeGreaterThanOrEqual(2);
    expect(within(across).getByRole('img', { name: /Next-season baserunning run-value rate: Projection: −4\.28%/ })).toBeTruthy();
  });
});
