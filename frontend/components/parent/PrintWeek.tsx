'use client';

import Link from 'next/link';
import { useRef } from 'react';
import { copy } from '@/lib/copy';
import type { ChildCard } from '@/lib/thisWeek';
import {
  deadlineInfo,
  printUrl,
  useMarkPrinted,
  usePrintInfo,
  weekRange,
  type PrintDoc,
} from '@/lib/print';
import {
  BackLink,
  DonePanel,
  EmptyState,
  ErrorState,
  LoadingState,
  primaryButton,
  secondaryButton,
} from './states';

const c = copy.print;

function docText(doc: PrintDoc, name: string): { title: string; body: string } {
  if (doc === 'packet') return { title: c.docs.packet.title(name), body: c.docs.packet.body };
  return c.docs[doc];
}

/** The print screen for one child's finished week: open each document to print, then confirm. */
export function PrintWeek({ card }: { card: ChildCard }) {
  const name = card.first_name;
  const printed = card.next_action === 'done';
  const ready = card.next_action === 'print';
  const info = usePrintInfo(card.student_id, ready || printed ? card.packet_id : null);
  const mark = useMarkPrinted();
  const inFlight = useRef(false);

  if (!ready && !printed) {
    const reason =
      card.next_action === 'check_in' || card.next_action === 'pick'
        ? c.notReady[card.next_action](name)
        : c.notReady.writing(name);
    return (
      <>
        <BackLink label={c.back} />
        <EmptyState
          title={c.notReadyTitle}
          body={reason}
          action={
            <Link href="/week" className={primaryButton}>
              {c.back}
            </Link>
          }
        />
      </>
    );
  }

  const range = weekRange(card.week_start);
  const deadline = ready ? deadlineInfo(card.print_deadline) : null;
  const justMarked = mark.isSuccess;

  const confirm = () => {
    if (inFlight.current) return; // a fast double tap is one request
    inFlight.current = true;
    mark.mutate(
      { studentId: card.student_id, planId: card.plan_id },
      {
        onSettled: () => {
          inFlight.current = false;
        },
      }
    );
  };

  return (
    <>
      <BackLink label={c.back} />
      <h1 className="text-foreground mb-2 text-2xl font-semibold">{c.title(name)}</h1>
      {info.data ? (
        <p className="text-foreground text-lg font-medium" data-testid="week-title">
          {info.data.title}
        </p>
      ) : null}
      {range ? <p className="text-neutral-700">{c.covers(range)}</p> : null}
      {deadline ? (
        <p
          data-testid="deadline"
          className={
            deadline.passed
              ? 'mt-2 rounded bg-secondary-100 p-3 text-sm text-neutral-900'
              : 'text-neutral-700'
          }
        >
          {deadline.passed ? c.deadlinePassed(deadline.text) : c.printBy(deadline.text)}
        </p>
      ) : null}

      {printed && !justMarked ? (
        <div role="status" className="mt-4 rounded-md border border-sage-300 bg-white p-4">
          <p className="text-foreground font-semibold">{c.alreadyTitle}</p>
          <p className="mt-1 text-neutral-700">{c.alreadyBody}</p>
        </div>
      ) : null}

      <div className="mt-4">
        {info.isLoading || (info.isFetching && !info.data && !info.error) ? (
          <LoadingState label={c.loadingDocs} />
        ) : info.error || !info.data ? (
          <ErrorState title={c.docsErrorTitle} onRetry={() => info.refetch()} />
        ) : (
          <>
            <p className="text-neutral-700">
              {info.data.structured ? c.intro(name) : c.introLegacy(name)}
            </p>
            <ol aria-label={c.documentsLabel} className="mt-4 space-y-3">
              {info.data.documents.map((doc, i) => {
                const text = docText(doc, name);
                return (
                  <li
                    key={doc}
                    data-testid={`doc-${doc}`}
                    className="rounded-md border border-neutral-200 bg-white p-5"
                  >
                    <h2 className="text-foreground text-lg font-semibold">
                      {i + 1}. {text.title}
                    </h2>
                    <p className="mt-1 text-neutral-700">{text.body}</p>
                    <a
                      href={printUrl(card.student_id, card.packet_id as string, doc)}
                      target="_blank"
                      rel="noopener"
                      className={`${primaryButton} mt-4 w-full`}
                    >
                      {c.openToPrint}
                      <span className="sr-only">
                        {' '}
                        {text.title} {c.newTab}
                      </span>
                    </a>
                  </li>
                );
              })}
            </ol>
            {!info.data.structured ? (
              <p className="mt-3 text-sm text-neutral-700">{c.legacyNote}</p>
            ) : null}

            {justMarked ? (
              <DonePanel
                title={c.doneTitle}
                body={c.doneBody(name)}
                back={c.back}
                className="mt-6"
              />
            ) : ready ? (
              <div className="mt-6 space-y-2">
                {mark.isError ? (
                  <ErrorState
                    title={c.confirmErrorTitle}
                    body={c.confirmErrorBody}
                    onRetry={confirm}
                  />
                ) : null}
                <p className="text-sm text-neutral-700">{c.confirmHint}</p>
                <button
                  type="button"
                  onClick={confirm}
                  disabled={mark.isPending}
                  className={`${secondaryButton} w-full disabled:border-neutral-700 disabled:text-neutral-700`}
                >
                  {mark.isPending ? c.confirming : c.confirm}
                </button>
              </div>
            ) : null}
          </>
        )}
      </div>
    </>
  );
}
