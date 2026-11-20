'use client';

import Link from 'next/link';
import { use } from 'react';
import { copy } from '@/lib/copy';
import { useThisWeek } from '@/lib/thisWeek';
import { EmptyState, QueryState, primaryButton } from '@/components/parent/states';
import { QuickCheckIn } from '@/components/parent/QuickCheckIn';

export default function CheckInPage({ params }: { params: Promise<{ studentId: string }> }) {
  const { studentId } = use(params);
  const query = useThisWeek();
  const back = (
    <Link href="/week" className={primaryButton}>
      {copy.checkIn.back}
    </Link>
  );

  return (
    <QueryState
      isLoading={query.isLoading}
      error={query.error}
      data={query.data}
      onRetry={() => query.refetch()}
      empty={<EmptyState title={copy.checkIn.unknownChild} body="" action={back} />}
    >
      {(cards) => {
        const card = cards.find((k) => k.student_id === studentId);
        if (!card) {
          return <EmptyState title={copy.checkIn.unknownChild} body="" action={back} />;
        }
        return (
          <>
            <Link href="/week" className="text-primary-700 mb-3 inline-block py-2 underline">
              {copy.checkIn.back}
            </Link>
            <h1 className="text-foreground mb-4 text-2xl font-semibold">
              {copy.checkIn.title(card.first_name)}
            </h1>
            {card.feedback_packet_id ? (
              <QuickCheckIn
                studentId={card.student_id}
                packetId={card.feedback_packet_id}
                firstName={card.first_name}
              />
            ) : (
              <EmptyState
                title={copy.checkIn.nothingTitle}
                body={copy.checkIn.nothingBody}
                action={back}
              />
            )}
          </>
        );
      }}
    </QueryState>
  );
}
