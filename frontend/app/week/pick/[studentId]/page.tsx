'use client';

import Link from 'next/link';
import { use } from 'react';
import { copy } from '@/lib/copy';
import { serverMessage, useWeekPlan } from '@/lib/pick';
import { EmptyState, ErrorState, LoadingState, primaryButton } from '@/components/parent/states';
import { PickIdeas } from '@/components/parent/PickIdeas';

export default function PickPage({ params }: { params: Promise<{ studentId: string }> }) {
  const { studentId } = use(params);
  const query = useWeekPlan(studentId);

  if (query.isLoading) return <LoadingState />;
  if (query.error) {
    const { code } = serverMessage(query.error);
    if (code === 'unknown_child' || code === 'no_plan') {
      return (
        <EmptyState
          title={copy.pick.unknownChild}
          body=""
          action={
            <Link href="/week" className={primaryButton}>
              {copy.pick.back}
            </Link>
          }
        />
      );
    }
    return <ErrorState onRetry={() => query.refetch()} />;
  }
  if (!query.data) return <LoadingState />;
  return <PickIdeas plan={query.data} />;
}
