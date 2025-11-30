'use client';

import { usePathname } from 'next/navigation';

export function Navigation() {
  const pathname = usePathname();

  const isActive = (path: string) => {
    return pathname === path;
  };

  return (
    <nav className="bg-white border-b border-neutral-200 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <div className="flex items-center space-x-8">
            <a href="/dashboard" className="text-2xl font-semibold text-primary-600 hover:text-primary-700">
              CurricuLearn
            </a>
            <div className="hidden md:flex space-x-6">
              <a
                href="/dashboard"
                className={`${
                  isActive('/dashboard')
                    ? 'text-foreground font-medium'
                    : 'text-neutral-500 hover:text-foreground'
                } transition-colors`}
              >
                Dashboard
              </a>
              <a
                href="/students"
                className={`${
                  isActive('/students')
                    ? 'text-foreground font-medium'
                    : 'text-neutral-500 hover:text-foreground'
                } transition-colors`}
              >
                Students
              </a>
              <a
                href="/plans"
                className={`${
                  isActive('/plans')
                    ? 'text-foreground font-medium'
                    : 'text-neutral-500 hover:text-foreground'
                } transition-colors`}
              >
                Plans
              </a>
              <a
                href="#"
                className="text-neutral-500 hover:text-foreground transition-colors"
              >
                Settings
              </a>
            </div>
          </div>
          <div className="flex items-center">
            <div className="w-8 h-8 bg-primary-200 rounded-full"></div>
          </div>
        </div>
      </div>
    </nav>
  );
}
