import { beforeEach, describe, expect, it } from 'vitest';
import { render, screen, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import App from '../../src/App';
import { clearDataCache } from '../../src/data/load';
import { installDataFetch } from '../helpers/data';

beforeEach(() => {
  clearDataCache();
  installDataFetch();
});

describe('Fantasy Value Lab', () => {
  it('computes team AVG/ERA/WHIP from components and updates when inputs change', async () => {
    window.location.hash = '#/value-lab';
    const user = userEvent.setup();
    render(<App />);
    expect(await screen.findByText('Illustrative / unvalidated scenario: not a research finding', {}, { timeout: 15000 })).toBeInTheDocument();
    const hitting = (await screen.findByRole('heading', { name: 'Hitting categories' })).closest('.card') as HTMLElement;
    const pitching = screen.getByRole('heading', { name: 'Pitching categories' }).closest('.card') as HTMLElement;
    expect(within(hitting).getByText('.267')).toBeInTheDocument(); // 368 H / 1,380 AB
    expect(within(hitting).getByText('368 H ÷ 1,380 AB')).toBeInTheDocument();
    expect(within(pitching).getByText('3.74')).toBeInTheDocument(); // 9 × 166 / 399
    expect(within(pitching).getByText('1.190')).toBeInTheDocument(); // 475 / 399
    // the averaging shortcut is explained, not used
    expect(screen.getByText(/Averaging the hitters' own AVGs would give \.261/)).toBeInTheDocument();

    const hitterC = screen.getAllByRole('group', { name: 'Hitter C' })[0];
    const ab = within(hitterC).getByRole('spinbutton', { name: 'At-bats' });
    await user.clear(ab);
    await user.type(ab, '600');
    expect(within(hitting).getByText('.219')).toBeInTheDocument(); // 368 / 1,680
  });

  it('points mode uses the verified weights from scoring.json when present', async () => {
    window.location.hash = '#/value-lab';
    const user = userEvent.setup();
    render(<App />);
    await screen.findByText('Illustrative / unvalidated scenario: not a research finding', {}, { timeout: 15000 });
    await user.click(await screen.findByRole('radio', { name: 'Points' }));
    expect(await screen.findByText('Default weights from scoring.json')).toBeInTheDocument();
    expect(screen.getAllByText(/Yahoo default Head-to-Head Points/).length).toBeGreaterThan(0);
    const table = screen.getByRole('table', { name: 'Points by player' });
    const rowA = within(table).getByRole('row', { name: /Hitter A/ });
    expect(rowA).toHaveTextContent('1239.7');
    const rowP = within(table).getByRole('row', { name: /Pitcher A/ });
    expect(rowP).toHaveTextContent('761.7');
  });
});
