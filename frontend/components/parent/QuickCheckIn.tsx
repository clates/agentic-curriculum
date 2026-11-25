'use client';

import { useState } from 'react';
import { copy } from '@/lib/copy';
import { useSendQuickCheckIn, type QuickRating, type Workload } from '@/lib/checkIn';
import { DonePanel, ErrorState, primaryButton } from './states';
import { Choice, WorkloadChoice } from './Choice';

const c = copy.checkIn;
const RATINGS: QuickRating[] = ['smooth', 'mixed', 'rough'];

/** Quick Friday rating: tap how it went, tap how much work it was, Send. */
export function QuickCheckIn({
  studentId,
  packetId,
  firstName,
}: {
  studentId: string;
  packetId: string;
  firstName: string;
}) {
  const [rating, setRating] = useState<QuickRating | null>(null);
  const [workload, setWorkload] = useState<Workload | null>(null);
  const send = useSendQuickCheckIn();

  if (send.isSuccess) {
    return <DonePanel title={c.doneTitle} body={c.doneBody(firstName)} back={c.back} />;
  }

  return (
    <form
      onSubmit={(e) => {
        e.preventDefault();
        if (!rating) return;
        send.mutate({ studentId, packetId, rating, workload: workload ?? undefined });
      }}
      className="space-y-6"
    >
      <fieldset className="space-y-2">
        <legend className="text-foreground mb-2 text-lg font-semibold">{c.overallQuestion}</legend>
        {RATINGS.map((r) => (
          <Choice
            key={r}
            name="overall"
            checked={rating === r}
            onChange={() => setRating(r)}
            label={c.overall[r].label}
            hint={c.overall[r].hint}
          />
        ))}
      </fieldset>
      <WorkloadChoice value={workload} onChange={setWorkload} />
      {send.isError ? <ErrorState title={c.sendErrorTitle} body={c.sendErrorBody} /> : null}
      <div className="sticky bottom-20 md:static">
        <button
          type="submit"
          disabled={!rating || send.isPending}
          className={`${primaryButton} w-full disabled:bg-neutral-700 disabled:opacity-100`}
        >
          {send.isPending ? c.sending : c.send}
        </button>
      </div>
    </form>
  );
}
