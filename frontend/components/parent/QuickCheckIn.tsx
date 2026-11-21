'use client';

import Link from 'next/link';
import { useState } from 'react';
import { copy } from '@/lib/copy';
import { useSendQuickCheckIn, type QuickRating, type Workload } from '@/lib/checkIn';
import { ErrorState, primaryButton } from './states';
import { Choice } from './Choice';

const c = copy.checkIn;
const RATINGS: QuickRating[] = ['smooth', 'mixed', 'rough'];
const WORKLOADS: { value: Workload; label: string }[] = [
  { value: 2, label: c.workload.tooLittle },
  { value: 0, label: c.workload.justRight },
  { value: -2, label: c.workload.tooMuch },
];

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
    return (
      <div role="status" className="rounded-md border border-sage-300 bg-white p-6 text-center">
        <h2 className="text-foreground text-xl font-semibold">{c.doneTitle}</h2>
        <p className="mt-2 text-neutral-700">{c.doneBody(firstName)}</p>
        <Link href="/week" className={`${primaryButton} mt-4`}>
          {c.back}
        </Link>
      </div>
    );
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
      <fieldset>
        <legend className="text-foreground mb-2 text-lg font-semibold">{c.workloadQuestion}</legend>
        <div className="grid grid-cols-3 gap-2">
          {WORKLOADS.map((w) => (
            <Choice
              key={w.value}
              name="workload"
              checked={workload === w.value}
              onChange={() => setWorkload(w.value)}
              label={w.label}
            />
          ))}
        </div>
      </fieldset>
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
