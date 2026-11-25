'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useState, type ReactNode } from 'react';
import { apiClient } from '@/lib/api';
import { copy } from '@/lib/copy';
import { useMe } from '@/lib/useMe';

const TABS = [
  { href: '/week', label: copy.nav.thisWeek, icon: 'M5 4h14v16H5zM5 9h14M9 2v4M15 2v4' },
  {
    href: '/how-its-going',
    label: copy.nav.progress,
    icon: 'M4 19V9m6 10V5m6 14v-7m4 7H2',
  },
  {
    href: '/students',
    label: copy.nav.children,
    icon: 'M16 11a4 4 0 10-8 0 4 4 0 008 0zM4 21a8 8 0 0116 0',
  },
];

/** Phone-first shell: a title bar, the page, and a thumb-reachable tab bar (top links on desktop). */
export function ParentShell({ children }: { children: ReactNode }) {
  const pathname = usePathname();
  const [leaving, setLeaving] = useState(false);
  // Sign-out only shows when a login is in use. The Admin link shows to anyone allowed to admin:
  // with login off that is the operator, who is the only user.
  const { data: me } = useMe();
  const signedIn = Boolean(me?.auth_required && me.user);
  const isAdmin = Boolean(me?.permissions.includes('admin'));

  async function signOut() {
    setLeaving(true);
    try {
      await apiClient.post('/auth/logout');
    } finally {
      window.location.assign('/login');
    }
  }
  const isActive = (href: string) => pathname === href || pathname.startsWith(`${href}/`);

  return (
    <div className="bg-background min-h-screen">
      <header className="border-b border-neutral-200 bg-white">
        <div className="mx-auto flex h-14 max-w-3xl items-center justify-between px-4">
          <span className="text-primary-700 text-xl font-semibold">{copy.app.name}</span>
          <nav aria-label={copy.nav.label} className="hidden gap-6 md:flex">
            {TABS.map((tab) => (
              <Link
                key={tab.href}
                href={tab.href}
                aria-current={isActive(tab.href) ? 'page' : undefined}
                className={`py-2 ${isActive(tab.href) ? 'text-foreground font-medium underline' : 'text-neutral-700'}`}
              >
                {tab.label}
              </Link>
            ))}
          </nav>
          <div className="flex items-center gap-2">
            {isAdmin ? (
              <Link
                href="/admin"
                className="flex min-h-11 items-center px-2 text-sm text-neutral-700 underline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary-600"
              >
                {copy.admin.link}
              </Link>
            ) : null}
            {signedIn ? (
              <button
                type="button"
                onClick={signOut}
                disabled={leaving}
                className="min-h-11 px-2 text-sm text-neutral-700 underline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary-600"
              >
                {leaving ? copy.login.signingOut : copy.login.signOut}
              </button>
            ) : null}
          </div>
        </div>
      </header>
      <main
        id="main"
        className="mx-auto max-w-3xl px-4 py-6 pb-28 [overflow-wrap:anywhere] md:pb-10"
      >
        {children}
      </main>
      <nav
        aria-label={copy.nav.label}
        data-testid="tab-bar"
        className="fixed inset-x-0 bottom-0 z-20 border-t border-neutral-200 bg-white pb-[env(safe-area-inset-bottom)] md:hidden"
      >
        <ul className="mx-auto flex max-w-3xl">
          {TABS.map((tab) => (
            <li key={tab.href} className="min-w-0 flex-1">
              <Link
                href={tab.href}
                aria-current={isActive(tab.href) ? 'page' : undefined}
                className={`flex min-h-14 flex-col items-center justify-center gap-1 px-1 py-2 text-center text-xs ${
                  isActive(tab.href) ? 'text-primary-700 font-semibold' : 'text-neutral-700'
                }`}
              >
                <svg
                  className="h-6 w-6"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                  strokeWidth={2}
                  aria-hidden="true"
                >
                  <path strokeLinecap="round" strokeLinejoin="round" d={tab.icon} />
                </svg>
                {tab.label}
              </Link>
            </li>
          ))}
        </ul>
      </nav>
    </div>
  );
}
