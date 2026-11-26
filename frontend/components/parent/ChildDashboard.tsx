'use client';

import { copy } from '@/lib/copy';
import { printUrl, usePrintInfo, weekRange, type PrintDoc } from '@/lib/print';
import { useCoverage, usePastWeeks, type SubjectCoverage } from '@/lib/child';
import type { WeeklyPacketSummary } from '@/lib/api';
import { EmptyState, QueryState } from '@/components/parent/states';

const linkClass =
  'text-primary-700 inline-flex min-h-11 items-center underline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary-600';

function PastWeek({
  name,
  studentId,
  week,
}: {
  name: string;
  studentId: string;
  week: WeeklyPacketSummary;
}) {
  const info = usePrintInfo(studentId, week.packet_id);
  const range = weekRange(week.week_of) ?? week.week_of;
  const label: Record<PrintDoc, string> = {
    packet: copy.childPage.pages(name),
    guide: copy.childPage.guide,
    prep: copy.childPage.prep,
  };
  return (
    <li data-testid="past-week" className="rounded-md border border-neutral-200 bg-white p-4">
      <p className="text-foreground font-medium">{range}</p>
      {info.data?.title ? <p className="text-sm text-neutral-700">{info.data.title}</p> : null}
      {info.data ? (
        <ul
          aria-label={copy.childPage.documentsLabel(range)}
          className="mt-1 flex flex-wrap gap-x-5"
        >
          {info.data.documents.map((doc) => (
            <li key={doc}>
              <a
                href={printUrl(studentId, week.packet_id, doc)}
                target="_blank"
                rel="noopener noreferrer"
                aria-label={copy.childPage.docAria(label[doc], range)}
                className={linkClass}
              >
                {label[doc]}
              </a>
            </li>
          ))}
        </ul>
      ) : info.isLoading ? (
        <p className="mt-1 text-sm text-neutral-700">{copy.childPage.loadingDocs}</p>
      ) : null}
    </li>
  );
}

export function PastWeeks({ studentId, name }: { studentId: string; name: string }) {
  const query = usePastWeeks(studentId);
  return (
    <section aria-labelledby="past-weeks" className="mt-6 scroll-mt-4">
      <h2 id="past-weeks" className="text-foreground mb-3 text-xl font-semibold">
        {copy.childPage.pastWeeksTitle}
      </h2>
      <QueryState
        isLoading={query.isLoading}
        error={query.error}
        data={query.data}
        isEmpty={(weeks) => weeks.length === 0}
        onRetry={() => query.refetch()}
        empty={
          <div data-testid="past-weeks-empty">
            <EmptyState
              title={copy.childPage.pastWeeksEmpty}
              body={copy.childPage.pastWeeksEmptyBody}
            />
          </div>
        }
      >
        {(weeks) => (
          <ul className="space-y-3">
            {weeks.map((w) => (
              <PastWeek key={w.packet_id} name={name} studentId={studentId} week={w} />
            ))}
          </ul>
        )}
      </QueryState>
    </section>
  );
}

const SEGMENTS = [
  { key: 'solid', color: 'bg-sage-600' },
  { key: 'shaky', color: 'bg-secondary-400' },
  { key: 'to_come', color: 'bg-neutral-300' },
] as const;

function SubjectBar({ row }: { row: SubjectCoverage }) {
  const total = row.solid + row.shaky + row.to_come;
  const words = [
    copy.childPage.solid(row.solid),
    copy.childPage.shaky(row.shaky),
    copy.childPage.toCome(row.to_come),
  ].join(', ');
  return (
    <li
      data-testid="coverage-subject"
      className="rounded-md border border-neutral-200 bg-white p-4"
    >
      <p className="text-foreground font-medium">{row.subject}</p>
      <div aria-hidden="true" className="my-2 flex h-3 overflow-hidden rounded bg-neutral-200">
        {SEGMENTS.map((s) =>
          row[s.key] > 0 ? (
            <div
              key={s.key}
              className={s.color}
              style={{ width: `${(row[s.key] / total) * 100}%` }}
            />
          ) : null
        )}
      </div>
      <p className="text-sm text-neutral-700">{words}</p>
    </li>
  );
}

export function Coverage({ studentId }: { studentId: string }) {
  const query = useCoverage(studentId);
  return (
    <section aria-labelledby="coverage" className="mt-8 scroll-mt-4">
      <h2 id="coverage" className="text-foreground text-xl font-semibold">
        {copy.childPage.coverageTitle}
      </h2>
      <p className="mb-3 text-neutral-700">{copy.childPage.coverageIntro}</p>
      <QueryState
        isLoading={query.isLoading}
        error={query.error}
        data={query.data}
        isEmpty={(rows) => rows.length === 0}
        onRetry={() => query.refetch()}
        empty={
          <EmptyState
            title={copy.childPage.coverageEmpty}
            body={copy.childPage.coverageEmptyBody}
          />
        }
      >
        {(rows) => (
          <ul className="space-y-3">
            {rows.map((r) => (
              <SubjectBar key={r.subject} row={r} />
            ))}
          </ul>
        )}
      </QueryState>
    </section>
  );
}
