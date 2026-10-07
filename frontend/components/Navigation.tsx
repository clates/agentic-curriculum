'use client';

import { useEffect, useState } from 'react';
import { usePathname } from 'next/navigation';

const NAV_LINKS = [
  { href: '/dashboard', label: 'Dashboard' },
  { href: '/students', label: 'Students' },
  { href: '/plans', label: 'Plans' },
  { href: '/progress', label: 'Progress Map' },
];

export function Navigation() {
  const pathname = usePathname();
  const [menuOpen, setMenuOpen] = useState(false);

  const isActive = (path: string) => {
    return pathname === path;
  };

  useEffect(() => {
    if (!menuOpen) return;
    const onKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') setMenuOpen(false);
    };
    document.addEventListener('keydown', onKeyDown);
    return () => document.removeEventListener('keydown', onKeyDown);
  }, [menuOpen]);

  return (
    <nav className="border-b border-neutral-200 bg-white shadow-sm">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="flex h-16 items-center justify-between">
          <div className="flex items-center space-x-8">
            <a
              href="/dashboard"
              className="text-primary-600 hover:text-primary-700 text-2xl font-semibold"
            >
              CurricuLearn
            </a>
            <div className="hidden space-x-6 md:flex">
              {NAV_LINKS.map((link) => (
                <a
                  key={link.href}
                  href={link.href}
                  aria-current={isActive(link.href) ? 'page' : undefined}
                  className={`${
                    isActive(link.href)
                      ? 'text-foreground font-medium'
                      : 'hover:text-foreground text-neutral-500'
                  } transition-colors`}
                >
                  {link.label}
                </a>
              ))}
            </div>
          </div>
          <div className="flex items-center space-x-3">
            <button
              type="button"
              aria-label="Open navigation"
              aria-expanded={menuOpen}
              aria-controls="mobile-nav-panel"
              onClick={() => setMenuOpen((open) => !open)}
              className="hover:text-foreground focus-visible:ring-primary-500 inline-flex h-10 w-10 items-center justify-center rounded-md text-neutral-600 hover:bg-neutral-100 focus:outline-none focus-visible:ring-2 md:hidden"
            >
              <svg
                className="h-6 w-6"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                strokeWidth={2}
                aria-hidden="true"
              >
                {menuOpen ? (
                  <path strokeLinecap="round" strokeLinejoin="round" d="M6 6l12 12M6 18L18 6" />
                ) : (
                  <path strokeLinecap="round" strokeLinejoin="round" d="M4 6h16M4 12h16M4 18h16" />
                )}
              </svg>
            </button>
            <div className="bg-primary-200 h-8 w-8 rounded-full"></div>
          </div>
        </div>
      </div>
      {menuOpen && (
        <div id="mobile-nav-panel" className="border-t border-neutral-200 md:hidden">
          <div className="mx-auto flex max-w-7xl flex-col px-4 py-2 sm:px-6">
            {NAV_LINKS.map((link) => (
              <a
                key={link.href}
                href={link.href}
                aria-current={isActive(link.href) ? 'page' : undefined}
                onClick={() => setMenuOpen(false)}
                className={`${
                  isActive(link.href)
                    ? 'text-foreground bg-neutral-50 font-medium'
                    : 'hover:text-foreground text-neutral-500 hover:bg-neutral-50'
                } rounded-md px-3 py-3 transition-colors`}
              >
                {link.label}
              </a>
            ))}
          </div>
        </div>
      )}
    </nav>
  );
}
