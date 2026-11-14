import { beforeEach, describe, expect, it } from 'vitest';
import { render, screen, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import App, { NAV } from '../../src/App';
import { clearDataCache } from '../../src/data/load';
import { installDataFetch } from '../helpers/data';

beforeEach(() => {
  clearDataCache();
  installDataFetch();
  window.location.hash = '#/';
});

describe('app shell', () => {
  it('every nav link opens its page', async () => {
    const user = userEvent.setup();
    render(<App />);
    await screen.findByRole('heading', { level: 1, name: 'Fantasy Projection Lab' }, { timeout: 15000 });
    const nav = screen.getByRole('navigation', { name: 'Main' });
    const expected: Record<string, RegExp> = {
      '/': /Fantasy Projection Lab/,
      '/explorer': /Metric → Target Explorer/,
      '/fantasy': /Fantasy Linkage Explorer/,
      '/casebook': /Player Casebook/,
      '/models': /Model Comparison/,
      '/value-lab': /Fantasy Value Lab/,
      '/methods': /Methods, Limits & Sources/,
    };
    for (const item of NAV) {
      await user.click(within(nav).getByRole('link', { name: item.label }));
      expect(await screen.findByRole('heading', { level: 1, name: expected[item.path] }, { timeout: 15000 })).toBeInTheDocument();
      expect(within(nav).getByRole('link', { name: item.label })).toHaveAttribute('aria-current', 'page');
    }
  });

  it('the theme control sets and clears a manual theme', async () => {
    const user = userEvent.setup();
    render(<App />);
    await screen.findByRole('heading', { level: 1, name: 'Fantasy Projection Lab' }, { timeout: 15000 });
    const dark = screen.getAllByRole('radio', { name: 'Dark' })[0];
    await user.click(dark);
    expect(document.documentElement).toHaveAttribute('data-theme', 'dark');
    await user.click(screen.getAllByRole('radio', { name: 'System' })[0]);
    expect(document.documentElement).not.toHaveAttribute('data-theme');
  });

  it('the Methods page renders the study notes verbatim and the provenance table', async () => {
    window.location.hash = '#/methods';
    render(<App />);
    expect(
      await screen.findByText(/a metric that explains player performance does not necessarily improve a future projection/, {}, { timeout: 15000 }),
    ).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: 'What changed after stronger validation' })).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: /Four different things called/ })).toBeInTheDocument();
    expect(screen.getByText('2e0bd681239f14a8a2ffdfe270ffa781a191a1c6698732fc49e9438dcddeb613')).toBeInTheDocument();
    expect(screen.getByRole('link', { name: 'GitHub Issues' })).toHaveAttribute(
      'href',
      'https://github.com/shirinalapati/MIT_Sloan_2027_Fantasy_Baseball_Projection_Lab_Paper/issues',
    );
  });
});
