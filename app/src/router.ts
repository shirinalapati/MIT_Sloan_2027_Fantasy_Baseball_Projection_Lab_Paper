/**
 * Minimal hash router: "#/explorer?metric=sprint_speed&target=baserunning_rv".
 * Static hosting needs no rewrites. Page state lives in the hash query so every view is linkable.
 */
import { useEffect, useState } from 'react';

export interface Route {
  path: string;
  params: URLSearchParams;
}

const ROUTE_EVENT = 'fpl:routechange';

export function parseHash(hash: string): Route {
  const h = hash.replace(/^#/, '');
  const [p, q = ''] = h.split('?');
  const path = p && p.startsWith('/') ? p : `/${p ?? ''}`;
  return { path: path === '' ? '/' : path, params: new URLSearchParams(q) };
}

export function hrefFor(path: string, params?: Record<string, string | number | null | undefined>): string {
  const sp = new URLSearchParams();
  if (params) {
    for (const [k, v] of Object.entries(params)) if (v !== null && v !== undefined && v !== '') sp.set(k, String(v));
  }
  const qs = sp.toString();
  return `#${path}${qs ? `?${qs}` : ''}`;
}

export function currentRoute(): Route {
  return parseHash(typeof window === 'undefined' ? '' : window.location.hash);
}

export function useRoute(): Route {
  const [route, setRoute] = useState<Route>(currentRoute);
  useEffect(() => {
    const on = () => setRoute(currentRoute());
    window.addEventListener('hashchange', on);
    window.addEventListener(ROUTE_EVENT, on);
    return () => {
      window.removeEventListener('hashchange', on);
      window.removeEventListener(ROUTE_EVENT, on);
    };
  }, []);
  return route;
}

/**
 * Update query parameters of the current route without adding a history entry
 * (filters and pickers should not flood the back button).
 */
export function setParams(updates: Record<string, string | number | null | undefined>): void {
  const { path, params } = currentRoute();
  for (const [k, v] of Object.entries(updates)) {
    if (v === null || v === undefined || v === '') params.delete(k);
    else params.set(k, String(v));
  }
  const qs = params.toString();
  const hash = `#${path}${qs ? `?${qs}` : ''}`;
  if (hash === window.location.hash) return;
  window.history.replaceState(window.history.state, '', hash);
  window.dispatchEvent(new Event(ROUTE_EVENT));
}

export function navigate(path: string, params?: Record<string, string | number | null | undefined>): void {
  window.location.hash = hrefFor(path, params);
}
