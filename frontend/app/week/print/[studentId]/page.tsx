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
  const back = (
    <Link href="/week" className={primaryButton}>
      {copy.print.back}
    </Link>
  );

  return (
    <QueryState
      isLoading={query.isLoading}
      error={query.error}
      data={query.data}
      onRetry={() => query.refetch()}
      empty={<EmptyState title={copy.print.unknownChild} body="" action={back} />}
    >
      {(cards) => {
        const card = cards.find((k) => k.student_id === studentId);
        if (!card) return <EmptyState title={copy.print.unknownChild} body="" action={back} />;
        return <PrintWeek card={card} />;
      }}
    </QueryState>
  );
}
