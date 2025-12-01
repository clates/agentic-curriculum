'use client';

import { usePathname } from 'next/navigation';

export function Navigation() {
  const pathname = usePathname();

  const isActive = (path: string) => {
    return pathname === path;
  };

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
              <a
                href="/dashboard"
                className={`${
                  isActive('/dashboard')
                    ? 'text-foreground font-medium'
                    : 'hover:text-foreground text-neutral-500'
                } transition-colors`}
              >
                Dashboard
              </a>
              <a
                href="/students"
                className={`${
                  isActive('/students')
                    ? 'text-foreground font-medium'
                    : 'hover:text-foreground text-neutral-500'
                } transition-colors`}
              >
                Students
              </a>
              <a
                href="/plans"
                className={`${
                  isActive('/plans')
                    ? 'text-foreground font-medium'
                    : 'hover:text-foreground text-neutral-500'
                } transition-colors`}
              >
                Plans
              </a>
              <a href="#" className="hover:text-foreground text-neutral-500 transition-colors">
                Settings
              </a>
            </div>
          </div>
          <div className="flex items-center">
            <div className="bg-primary-200 h-8 w-8 rounded-full"></div>
          </div>
        </div>
      </div>
    </nav>
  );
}
