'use client';

import Link from 'next/link';
import { use } from 'react';
import { copy } from '@/lib/copy';
import { useThisWeek } from '@/lib/thisWeek';
import { EmptyState, QueryState, primaryButton } from '@/components/parent/states';
import { PrintWeek } from '@/components/parent/PrintWeek';

export default function PrintPage({ params }: { params: Promise<{ studentId: string }> }) {
  const { studentId } = use(params);
  const query = useThisWeek();
  const unknown = (
    <EmptyState
      title={copy.print.unknownChild}
      body=""
      action={
        <Link href="/week" className={primaryButton}>
          {copy.print.back}
        </Link>
      }
    />
  );

  return (
    <QueryState
      isLoading={query.isLoading}
      error={query.error}
      data={query.data}
      onRetry={() => query.refetch()}
      empty={unknown}
    >
      {(cards) => {
        const card = cards.find((k) => k.student_id === studentId);
        return card ? <PrintWeek card={card} /> : unknown;
      }}
    </QueryState>
  );
}
