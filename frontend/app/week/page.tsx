'use client';

import { useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { copy } from '@/lib/copy';
import { useThisWeek } from '@/lib/thisWeek';
import { useMe } from '@/lib/useMe';
import { MAX_CHILDREN } from '@/lib/childLimits';
import { ChildCard } from '@/components/parent/ChildCard';
import { EmptyState, QueryState, primaryButton, secondaryButton } from '@/components/parent/states';

export default function ThisWeekPage() {
  const query = useThisWeek();
  const { data: me, isLoading: meLoading } = useMe();
  const router = useRouter();
  // Login on and no children yet: this is a new family, so start with the welcome page.
  const firstRun = Boolean(me?.auth_required) && query.data?.length === 0;
  useEffect(() => {
    if (firstRun) router.replace('/welcome');
  }, [firstRun, router]);
  // Until we know whether to redirect, and while the redirect is pending, keep the loading state
  // up rather than flash "No children yet".
  const loading = query.isLoading || meLoading || firstRun;

  return (
    <>
      <h1 className="text-foreground text-2xl font-semibold">{copy.thisWeek.title}</h1>
      <p className="mb-4 text-neutral-700">{copy.thisWeek.intro}</p>
      <QueryState
        isLoading={loading}
        error={query.error}
        data={query.data}
        isEmpty={(cards) => cards.length === 0}
        onRetry={() => query.refetch()}
        empty={
          <EmptyState
            title={copy.thisWeek.emptyTitle}
            body={copy.thisWeek.emptyBody}
            action={
              <Link href="/students" className={primaryButton}>
                {copy.thisWeek.emptyAction}
              </Link>
            }
          />
        }
      >
        {(cards) => (
          <>
            <ul className="space-y-4">
              {cards.map((card) => (
                <ChildCard key={card.student_id} card={card} />
              ))}
            </ul>
            {me?.auth_required && cards.length < MAX_CHILDREN ? (
              <Link href="/children/new" className={`${secondaryButton} mt-6`}>
                {copy.childForm.addButton}
              </Link>
            ) : null}
          </>
        )}
      </QueryState>
    </>
  );
}
