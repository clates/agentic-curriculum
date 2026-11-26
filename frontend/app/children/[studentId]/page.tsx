'use client';

import Link from 'next/link';
import { use } from 'react';
import { copy } from '@/lib/copy';
import { isNotFound, useChildName } from '@/lib/child';
import {
  BackLink,
  EmptyState,
  LoadingState,
  ErrorState,
  primaryButton,
} from '@/components/parent/states';
import { Coverage, PastWeeks } from '@/components/parent/ChildDashboard';

export default function ChildPage({ params }: { params: Promise<{ studentId: string }> }) {
  const { studentId } = use(params);
  const child = useChildName(studentId);

  if (child.isLoading) return <LoadingState />;
  if (isNotFound(child.error)) {
    return (
      <EmptyState
        title={copy.childPage.unknownChild}
        body=""
        action={
          <Link href="/week" className={primaryButton}>
            {copy.childPage.back}
          </Link>
        }
      />
    );
  }
  if (child.error || child.data == null) return <ErrorState onRetry={() => child.refetch()} />;

  return (
    <>
      <BackLink label={copy.childPage.back} />
      <h1 className="text-foreground text-2xl font-semibold">{child.data}</h1>
      <PastWeeks studentId={studentId} name={child.data} />
      <Coverage studentId={studentId} />
    </>
  );
}
