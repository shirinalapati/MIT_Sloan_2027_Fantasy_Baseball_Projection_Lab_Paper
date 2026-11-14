import { beforeEach, describe, expect, it } from 'vitest';
import { render, screen } from '@testing-library/react';
import App from '../../src/App';
import { clearDataCache } from '../../src/data/load';
import { installDataFetch } from '../helpers/data';

beforeEach(() => {
  clearDataCache();
  installDataFetch();
});

describe('Model Comparison', () => {
  it('FIP: "ADM vs B0 (selection policy lift)" shows ΔRMSE ≈ −7.498% (rendered −7.50%)', async () => {
    window.location.hash = '#/models?target=pitching_fip';
    render(<App />);
    const row = await screen.findByRole('img', { name: /^ADM vs B0 \(selection policy lift\): −7\.50%/ }, { timeout: 15000 });
    expect(row).toBeInTheDocument();
    expect(row.getAttribute('aria-label')).toContain('[−9.38, −5.48]');
    expect(screen.getByText(/The nested-admitted set \(ADM\) was more accurate than the history baseline \(B0\) \(−7\.50%/)).toBeInTheDocument();
    expect(screen.getByText('Directional / exploratory')).toBeInTheDocument();
  });
});
