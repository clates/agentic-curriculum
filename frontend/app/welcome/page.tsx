'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { copy } from '@/lib/copy';
import { ChildForm } from '@/components/parent/ChildForm';
import { useChildCount } from '@/components/parent/useChildGate';
import { LoadingState } from '@/components/parent/states';

export default function WelcomePage() {
  const router = useRouter();
  const { count, isLoading } = useChildCount();
  const hasChildren = (count ?? 0) > 0;

  useEffect(() => {
    if (hasChildren) router.replace('/week');
  }, [hasChildren, router]);

  return (
    <div className="bg-background min-h-screen">
      <main id="main" className="mx-auto max-w-sm px-4 py-12 [overflow-wrap:anywhere]">
        <p className="text-primary-700 text-xl font-semibold">{copy.app.name}</p>
        <h1 className="text-foreground mt-6 text-2xl font-semibold">{copy.welcome.title}</h1>
        {isLoading || hasChildren ? (
          <LoadingState />
        ) : (
          <>
            <p className="mt-2 text-neutral-700">{copy.welcome.intro}</p>
            <p className="mt-2 text-neutral-700">{copy.welcome.intro2}</p>
            <ChildForm />
          </>
        )}
      </main>
    </div>
  );
}
