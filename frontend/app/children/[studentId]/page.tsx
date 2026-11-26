'use client';

import Link from 'next/link';
import { use, useEffect, useRef } from 'react';
import { useIsFetching, useQueryClient } from '@tanstack/react-query';
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

/**
 * The sections render only after the data loads, so the browser's own jump to `#coverage` or
 * `#past-weeks` finds nothing. Jump once the page is shown and nothing is still loading (so the
 * layout above the section has settled), unless the parent has already moved the page themselves.
 */
function useScrollToHashWhen(shown: boolean) {
  const client = useQueryClient();
  const fetching = useIsFetching();
  const done = useRef(false);
  const userMoved = useRef(false);
  useEffect(() => {
    const moved = () => {
      userMoved.current = true;
    };
    const events = ['wheel', 'touchmove', 'keydown', 'mousedown'] as const;
    events.forEach((e) => window.addEventListener(e, moved, { passive: true }));
    return () => events.forEach((e) => window.removeEventListener(e, moved));
  }, []);
  useEffect(() => {
    // Re-check the client: a section's queries may have started after this render.
    if (!shown || done.current || fetching > 0 || client.isFetching() > 0) return;
    done.current = true;
    const id = decodeURIComponent(window.location.hash.slice(1));
    if (!id || userMoved.current) return;
    document.getElementById(id)?.scrollIntoView();
  }, [shown, fetching, client]);
}

export default function ChildPage({ params }: { params: Promise<{ studentId: string }> }) {
  const { studentId } = use(params);
  const child = useChildName(studentId);
  useScrollToHashWhen(child.data != null);

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
