'use client';

import { copy } from '@/lib/copy';
import { ChildForm } from '@/components/parent/ChildForm';
import { MAX_CHILDREN, useChildCount } from '@/components/parent/useChildGate';
import { BackLink, LoadingState } from '@/components/parent/states';

export default function AddChildPage() {
  const { count, isLoading } = useChildCount();
  const full = (count ?? 0) >= MAX_CHILDREN;

  return (
    <>
      <BackLink label={copy.nav.thisWeek} />
      <h1 className="text-foreground text-2xl font-semibold">{copy.childForm.addTitle}</h1>
      {isLoading ? (
        <LoadingState />
      ) : full ? (
        <p className="mt-2 text-neutral-700">{copy.childForm.tooMany}</p>
      ) : (
        <>
          <p className="mt-2 text-neutral-700">{copy.childForm.addIntro}</p>
          <ChildForm />
        </>
      )}
    </>
  );
}
