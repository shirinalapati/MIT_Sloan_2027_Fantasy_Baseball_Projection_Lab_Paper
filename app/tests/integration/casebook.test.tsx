import { beforeEach, describe, expect, it } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import App from '../../src/App';
import { clearDataCache } from '../../src/data/load';
import { installDataFetch } from '../helpers/data';

beforeEach(() => {
  clearDataCache();
  installDataFetch();
});

describe('Player Casebook', () => {
  it('shows the selection note and filters by selection type and player', async () => {
    window.location.hash = '#/casebook?contrast=pitching_fip:stuff_plus';
    const user = userEvent.setup();
    render(<App />);
    expect(await screen.findByText(/the 20 largest forecast increases, the 20 largest decreases/, {}, { timeout: 15000 })).toBeInTheDocument();
    const status = () => screen.getByText(/Showing/, { selector: 'span' }).closest('p') as HTMLElement;
    expect(status()).toHaveTextContent('Showing 60 of 420 cases');
    await user.click(screen.getByRole('radio', { name: 'Largest forecast decreases' }));
    expect(status()).toHaveTextContent('Showing 20 of 420 cases');
    expect(status()).toHaveTextContent(/\d+ improved/);
    expect(status()).toHaveTextContent(/\d+ worsened/);
    await user.click(screen.getByRole('radio', { name: 'Worsened' }));
    expect(status()).toHaveTextContent(/0 improved/);
    // decile chart for the contrast
    expect(screen.getByRole('img', { name: /Share improved by cohort for Stuff\+ → FIP/ })).toBeInTheDocument();
  });
});
