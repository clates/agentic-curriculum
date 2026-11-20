'use client';

import Link from 'next/link';
import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { parseMetadata, studentsApi } from '@/lib/api';
import { copy } from '@/lib/copy';
import { PARENT_QUERY } from '@/lib/parentQuery';
import { useProgressSummary } from '@/lib/progress';
import { Choice } from '@/components/parent/Choice';
import { ProgressView } from '@/components/parent/ProgressView';
import { EmptyState, QueryState, primaryButton } from '@/components/parent/states';

const p = copy.progress;

function ChildProgress({ studentId, name }: { studentId: string; name: string }) {
  const summary = useProgressSummary(studentId);
  const nothing = (s: { solid: unknown[]; shaky: unknown[]; needs_work: unknown[] }) =>
    s.solid.length + s.shaky.length + s.needs_work.length === 0;
  return (
    <QueryState
      isLoading={summary.isLoading}
      error={summary.error}
      data={summary.data}
      isEmpty={nothing}
      onRetry={() => summary.refetch()}
      empty={<EmptyState title={p.nothingTitle(name)} body={p.nothingBody} />}
    >
      {(data) => <ProgressView name={name} summary={data} />}
    </QueryState>
  );
}

export default function HowItsGoingPage() {
  const kids = useQuery({
    queryKey: ['students'],
    queryFn: studentsApi.listStudents,
    ...PARENT_QUERY,
  });
  const [picked, setPicked] = useState<string | null>(null);

  return (
    <>
      <h1 className="text-foreground text-2xl font-semibold">{p.title}</h1>
      <p className="mb-4 text-neutral-700">{p.intro}</p>
      <QueryState
        isLoading={kids.isLoading}
        error={kids.error}
        data={kids.data}
        isEmpty={(list) => list.length === 0}
        onRetry={() => kids.refetch()}
        empty={
          <EmptyState
            title={p.emptyTitle}
            body={p.emptyBody}
            action={
              <Link href="/students" className={primaryButton}>
                {p.emptyAction}
              </Link>
            }
          />
        }
      >
        {(list) => {
          const people = list.map((s) => ({
            id: s.student_id,
            name: (parseMetadata(s.metadata_blob)?.name ?? '').split(' ')[0] || s.student_id,
          }));
          const current = people.find((x) => x.id === picked) ?? people[0];
          return (
            <div className="space-y-4">
              {people.length > 1 ? (
                <fieldset>
                  <legend className="sr-only">{p.pickChild}</legend>
                  <div className="grid grid-cols-2 gap-2">
                    {people.map((x) => (
                      <Choice
                        key={x.id}
                        name="child"
                        checked={x.id === current.id}
                        onChange={() => setPicked(x.id)}
                        label={x.name}
                      />
                    ))}
                  </div>
                </fieldset>
              ) : null}
              <ChildProgress key={current.id} studentId={current.id} name={current.name} />
            </div>
          );
        }}
      </QueryState>
    </>
  );
}
