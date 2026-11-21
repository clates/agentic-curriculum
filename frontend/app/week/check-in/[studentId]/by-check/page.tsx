'use client';

import Link from 'next/link';
import { use } from 'react';
import { copy } from '@/lib/copy';
import { usePrepChecks } from '@/lib/checkIn';
import { useThisWeek } from '@/lib/thisWeek';
import { EmptyState, ErrorState, LoadingState, primaryButton } from '@/components/parent/states';
import { CheckByCheck } from '@/components/parent/CheckByCheck';

export default function CheckByCheckPage({ params }: { params: Promise<{ studentId: string }> }) {
  const { studentId } = use(params);
  const week = useThisWeek();
  const card = week.data?.find((k) => k.student_id === studentId);
  const checks = usePrepChecks(studentId, card?.feedback_packet_id);

  const quick = (
    <Link href={`/week/check-in/${studentId}`} className={primaryButton}>
      {copy.byCheck.useQuick}
    </Link>
  );

  if (week.isLoading || (card?.feedback_packet_id && checks.isLoading)) return <LoadingState />;
  if (week.error) return <ErrorState onRetry={() => week.refetch()} />;
  if (checks.error) return <ErrorState onRetry={() => checks.refetch()} />;
  if (!card) {
    return (
      <EmptyState
        title={copy.checkIn.unknownChild}
        body=""
        action={
          <Link href="/week" className={primaryButton}>
            {copy.checkIn.back}
          </Link>
        }
      />
    );
  }
  if (!card.feedback_packet_id || !checks.data || checks.data.length === 0) {
    return (
      <EmptyState
        title={copy.byCheck.noChecksTitle}
        body={copy.byCheck.noChecksBody}
        action={quick}
      />
    );
  }
  return (
    <>
      <Link
        href={`/week/check-in/${studentId}`}
        className="text-primary-700 mb-3 inline-block py-2 underline"
      >
        {copy.checkIn.back}
      </Link>
      <h1 className="text-foreground mb-4 text-2xl font-semibold">
        {copy.checkIn.title(card.first_name)}
      </h1>
      <CheckByCheck
        studentId={card.student_id}
        packetId={card.feedback_packet_id}
        firstName={card.first_name}
        checks={checks.data}
      />
    </>
  );
}
