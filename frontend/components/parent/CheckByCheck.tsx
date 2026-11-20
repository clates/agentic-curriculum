'use client';

import Link from 'next/link';
import { useState } from 'react';
import { copy } from '@/lib/copy';
import {
  useSendCheckResults,
  type CheckResult,
  type PrepCheck,
  type Workload,
} from '@/lib/checkIn';
import { Choice } from './Choice';
import { ErrorState, primaryButton } from './states';

const t = copy.byCheck;
const c = copy.checkIn;
const RESULTS: CheckResult[] = ['got_it', 'shaky', 'missed'];
const WORKLOADS: { value: Workload; label: string }[] = [
  { value: 2, label: c.workload.tooLittle },
  { value: 0, label: c.workload.justRight },
  { value: -2, label: c.workload.tooMuch },
];
const secondary =
  'inline-flex min-h-11 items-center justify-center rounded-md border-2 border-neutral-700 bg-white px-5 py-2 font-medium text-neutral-900';

/** Optional per-check cards. Partial answers are fine; nothing answered falls back to the quick rating. */
export function CheckByCheck({
  studentId,
  packetId,
  firstName,
  checks,
}: {
  studentId: string;
  packetId: string;
  firstName: string;
  checks: PrepCheck[];
}) {
  const [index, setIndex] = useState(0);
  const [results, setResults] = useState<Record<string, CheckResult>>({});
  const [workload, setWorkload] = useState<Workload | null>(null);
  const send = useSendCheckResults();
  const quickHref = `/week/check-in/${studentId}`;
  const answered = Object.keys(results).length;
  const reviewing = index >= checks.length;

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

  if (reviewing) {
    return (
      <div className="space-y-5">
        <h2 className="text-foreground text-xl font-semibold">{t.reviewTitle}</h2>
        <p className="text-neutral-700">
          {answered === 0 ? t.answeredNone : t.answered(answered, checks.length)}
        </p>
        {answered > 0 ? <p className="text-neutral-700">{t.skippedNote}</p> : null}
        <fieldset>
          <legend className="text-foreground mb-2 text-lg font-semibold">
            {c.workloadQuestion}
          </legend>
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
        {answered === 0 ? (
          <p className="text-neutral-900">{t.needOne}</p>
        ) : (
          <button
            type="button"
            disabled={send.isPending}
            onClick={() =>
              send.mutate({ studentId, packetId, results, workload: workload ?? undefined })
            }
            className={`${primaryButton} w-full`}
          >
            {send.isPending ? c.sending : c.send}
          </button>
        )}
        <div className="flex flex-wrap gap-3">
          <button type="button" className={secondary} onClick={() => setIndex(checks.length - 1)}>
            {t.goBackAdd}
          </button>
          {answered === 0 ? (
            <Link href={quickHref} className={primaryButton}>
              {t.useQuick}
            </Link>
          ) : null}
        </div>
      </div>
    );
  }

  const check = checks[index];
  const choose = (r: CheckResult) => {
    setResults((prev) => ({ ...prev, [check.check_id]: r }));
    setIndex(index + 1);
  };

  return (
    <div className="space-y-4">
      <p className="text-sm text-neutral-700" aria-live="polite">
        {t.progress(index + 1, checks.length)} · {check.day}
      </p>
      <div className="rounded-md border border-neutral-200 bg-white p-5">
        <h2 className="text-sm font-semibold text-neutral-700">{t.ask}</h2>
        <p className="text-foreground mt-1 text-lg">{check.prompt}</p>
        <h3 className="mt-4 text-sm font-semibold text-neutral-700">{t.goodAnswer}</h3>
        <p className="text-foreground mt-1">{check.pass_criteria}</p>
      </div>
      <div
        className="grid grid-cols-3 gap-2"
        role="group"
        aria-label={t.progress(index + 1, checks.length)}
      >
        {RESULTS.map((r) => (
          <button
            key={r}
            type="button"
            onClick={() => choose(r)}
            aria-pressed={results[check.check_id] === r}
            className={`min-h-14 rounded-md border-2 px-2 text-lg font-medium ${
              results[check.check_id] === r
                ? 'border-primary-600 bg-primary-50'
                : 'border-neutral-200 bg-white'
            }`}
          >
            {t.result[r]}
          </button>
        ))}
      </div>
      <div className="flex items-center justify-between">
        <button
          type="button"
          className={secondary}
          disabled={index === 0}
          onClick={() => setIndex(index - 1)}
        >
          {t.back}
        </button>
        <button type="button" className={secondary} onClick={() => setIndex(index + 1)}>
          {t.skip}
        </button>
      </div>
      <p className="text-center">
        <Link href={quickHref} className="text-primary-700 inline-block py-2 underline">
          {t.useQuick}
        </Link>
      </p>
    </div>
  );
}
