import { Suspense, lazy, useEffect, useRef, useState } from 'react';
import { hrefFor, useRoute } from './router';
import { LogoMark, MenuIcon } from './components/Icons';
import { ThemeControl, useTheme } from './components/ThemeControl';
import Home from './pages/Home';
import { ISSUES_URL } from './lib/links';

const Explorer = lazy(() => import('./pages/Explorer'));
const FantasyPage = lazy(() => import('./pages/Fantasy'));
const Casebook = lazy(() => import('./pages/Casebook'));
const Models = lazy(() => import('./pages/Models'));
const ValueLab = lazy(() => import('./pages/ValueLab'));
const Methods = lazy(() => import('./pages/Methods'));

export const NAV = [
  { path: '/', label: 'Home' },
  { path: '/explorer', label: 'Metric Explorer' },
  { path: '/fantasy', label: 'Fantasy Linkage' },
  { path: '/casebook', label: 'Player Casebook' },
  { path: '/models', label: 'Model Comparison' },
  { path: '/value-lab', label: 'Value Lab' },
  { path: '/methods', label: 'Methods & Sources' },
] as const;


function NotFound() {
  return (
    <div className="page-head">
      <h1 id="page-title" tabIndex={-1}>
        Page not found
      </h1>
      <p>
        That address does not match a page in this lab. <a href={hrefFor('/')}>Go to the home page</a>.
      </p>
    </div>
  );
}

function Page({ path }: { path: string }) {
  switch (path) {
    case '/':
      return <Home />;
    case '/explorer':
      return <Explorer />;
    case '/fantasy':
      return <FantasyPage />;
    case '/casebook':
      return <Casebook />;
    case '/models':
      return <Models />;
    case '/value-lab':
      return <ValueLab />;
    case '/methods':
      return <Methods />;
    default:
      return <NotFound />;
  }
}

export default function App() {
  const route = useRoute();
  const [theme, setTheme] = useTheme();
  const [menuOpen, setMenuOpen] = useState(false);
  const firstPath = useRef(true);

  useEffect(() => {
    setMenuOpen(false);
    if (firstPath.current) {
      firstPath.current = false;
      return;
    }
    window.scrollTo(0, 0);
    // Move focus to the new page's heading once it renders (pages may be lazy-loaded).
    let tries = 0;
    const id = window.setInterval(() => {
      const h = document.getElementById('page-title');
      if (h || tries++ > 40) {
        window.clearInterval(id);
        h?.focus({ preventScroll: true });
      }
    }, 50);
    return () => window.clearInterval(id);
  }, [route.path]);

  return (
    <>
      <a className="skip-link" href="#main" onClick={(e) => {
        e.preventDefault();
        document.getElementById('main')?.focus();
      }}>
        Skip to main content
      </a>
      <header className="site-header">
        <div className="header-inner">
          <div className="brand-row">
            <a className="brand" href={hrefFor('/')}>
              <LogoMark />
              <span>
                <span className="brand-name">Fantasy Projection Lab</span>
                <span className="brand-sub">
                  Which public baseball metrics improve next-season forecasts, and does that reach your fantasy categories?
                </span>
              </span>
            </a>
            <div className="header-tools">
              <ThemeControl theme={theme} onChange={setTheme} className="theme-control-desktop" />
              <button
                type="button"
                className="btn menu-button"
                aria-expanded={menuOpen}
                aria-controls="main-nav"
                onClick={() => setMenuOpen((o) => !o)}
              >
                <MenuIcon />
                Menu
              </button>
            </div>
          </div>
          <nav id="main-nav" className={`main-nav${menuOpen ? ' open' : ''}`} aria-label="Main">
            <ul>
              {NAV.map((n) => (
                <li key={n.path}>
                  <a href={hrefFor(n.path)} aria-current={route.path === n.path ? 'page' : undefined} onClick={() => setMenuOpen(false)}>
                    {n.label}
                  </a>
                </li>
              ))}
            </ul>
            <ThemeControl theme={theme} onChange={setTheme} className="theme-control-mobile" />
          </nav>
        </div>
      </header>
      <main id="main" tabIndex={-1}>
        <Suspense
          fallback={
            <p className="loading" role="status">
              Loading page…
            </p>
          }
        >
          <Page path={route.path} />
        </Suspense>
      </main>
      <footer className="site-footer">
        <div className="footer-inner">
          <p>
            <strong>Fantasy Projection Lab</strong> · companion to Paper ID 18, MIT Sloan Sports Analytics Conference 2027 (Baseball track).
          </p>
          <p>
            Shows aggregate research results and a curated set of player examples. MLB Stats API and Baseball Savant data © MLB Advanced
            Media; Baseball-Reference WAR © Sports Reference. <a href={hrefFor('/methods')}>Methods, limits &amp; sources</a> ·{' '}
            <a href={ISSUES_URL} target="_blank" rel="noopener noreferrer">
              Feedback (GitHub Issues)
            </a>
          </p>
        </div>
      </footer>
    </>
  );
}
