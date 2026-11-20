'use client';

import Link from 'next/link';
import { useQuery } from '@tanstack/react-query';
import { studentsApi, parseMetadata } from '@/lib/api';
import { PARENT_QUERY } from '@/lib/parentQuery';
import { copy } from '@/lib/copy';
import { EmptyState, QueryState, primaryButton } from '@/components/parent/states';

export default function ThisWeekPage() {
  const query = useQuery({
    queryKey: ['students'],
    queryFn: studentsApi.listStudents,
    ...PARENT_QUERY,
  });

  return (
    <>
      <h1 className="text-foreground text-2xl font-semibold">{copy.thisWeek.title}</h1>
      <p className="mb-4 text-neutral-700">{copy.thisWeek.intro}</p>
      <QueryState
        isLoading={query.isLoading}
        error={query.error}
        data={query.data}
        isEmpty={(kids) => kids.length === 0}
        onRetry={() => query.refetch()}
        empty={
          <EmptyState
            title={copy.thisWeek.emptyTitle}
            body={copy.thisWeek.emptyBody}
            action={
              <Link href="/students" className={primaryButton}>
                {copy.thisWeek.emptyAction}
              </Link>
            }
          />
        }
      >
        {(kids) => (
          <ul className="space-y-3">
            {kids.map((kid) => (
              <li
                key={kid.student_id}
                className="rounded-md border border-neutral-200 bg-white p-4"
              >
                {parseMetadata(kid.metadata_blob)?.name ?? ''}
              </li>
            ))}
          </ul>
        )}
      </QueryState>
    </>
  );
}
