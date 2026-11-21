'use client';

import Link from 'next/link';
import { copy } from '@/lib/copy';
import { useThisWeek } from '@/lib/thisWeek';
import { ChildCard } from '@/components/parent/ChildCard';
import { EmptyState, QueryState, primaryButton } from '@/components/parent/states';

export default function ThisWeekPage() {
  const query = useThisWeek();

  return (
    <>
      <h1 className="text-foreground text-2xl font-semibold">{copy.thisWeek.title}</h1>
      <p className="mb-4 text-neutral-700">{copy.thisWeek.intro}</p>
      <QueryState
        isLoading={query.isLoading}
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
          <ul className="space-y-4">
            {cards.map((card) => (
              <ChildCard key={card.student_id} card={card} />
            ))}
          </ul>
        )}
      </QueryState>
    </>
  );
}
