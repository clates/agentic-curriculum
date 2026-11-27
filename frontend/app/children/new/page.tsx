'use client';

import { Suspense } from 'react';
import { useSearchParams } from 'next/navigation';
import { copy } from '@/lib/copy';
import { MAX_CHILDREN } from '@/lib/childLimits';
import { ChildForm } from '@/components/parent/ChildForm';
import { useChildCount } from '@/components/parent/useChildGate';
import { BackLink, LoadingState } from '@/components/parent/states';

/** Opened from Children (`?from=students`), the way back and the way on lead there; else This week. */
function AddChild() {
  const fromStudents = useSearchParams().get('from') === 'students';
  const back = fromStudents
    ? { href: '/students', label: copy.nav.children }
    : { href: '/week', label: copy.nav.thisWeek };
  const { count, isLoading } = useChildCount();
  const full = (count ?? 0) >= MAX_CHILDREN;

  return (
    <>
      <BackLink label={back.label} href={back.href} />
      <h1 className="text-foreground text-2xl font-semibold">{copy.childForm.addTitle}</h1>
      {isLoading ? (
        <LoadingState />
      ) : full ? (
        <p className="mt-2 text-neutral-700">{copy.childForm.tooMany}</p>
      ) : (
        <>
          <p className="mt-2 text-neutral-700">{copy.childForm.addIntro}</p>
          <ChildForm doneHref={back.href} />
        </>
      )}
    </>
  );
}

export default function AddChildPage() {
  return (
    <Suspense fallback={<LoadingState />}>
      <AddChild />
    </Suspense>
  );
}
