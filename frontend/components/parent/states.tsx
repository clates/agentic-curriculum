'use client';

import Link from 'next/link';
import type { ReactNode } from 'react';
import { copy } from '@/lib/copy';

export const primaryButton =
  'inline-flex min-h-11 items-center justify-center rounded-md bg-primary-600 px-6 py-3 font-medium text-white hover:bg-primary-700 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary-600';

export const secondaryButton =
  'inline-flex min-h-11 items-center justify-center rounded-md border-2 border-primary-600 bg-white px-6 py-3 font-medium text-primary-700 hover:bg-primary-50 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary-600';

/** The quiet link back to This week, above a screen's heading. */
export function BackLink({ label }: { label: string }) {
  return (
    <Link href="/week" className="text-primary-700 mb-3 inline-block py-2 underline">
      {label}
    </Link>
  );
}

/** Shown once something is sent or confirmed, with the way back to This week. */
export function DonePanel({
  title,
  body,
  back,
  className = '',
}: {
  title: string;
  body: string;
  back: string;
  className?: string;
}) {
  return (
    <div
      role="status"
      className={`${className} rounded-md border border-sage-300 bg-white p-6 text-center`}
    >
      <h2 className="text-foreground text-xl font-semibold">{title}</h2>
      <p className="mt-2 text-neutral-700">{body}</p>
      <Link href="/week" className={`${primaryButton} mt-4`}>
        {back}
      </Link>
    </div>
  );
}

/** Shown while data loads. Announces itself politely to screen readers. */
export function LoadingState({ label = copy.states.loadingLabel }: { label?: string }) {
  return (
    <div role="status" aria-live="polite" className="animate-pulse space-y-4 py-4">
      <span className="sr-only">{label}</span>
      <div className="h-8 w-40 rounded bg-neutral-200" aria-hidden="true" />
      <div className="h-32 rounded-md bg-neutral-200" aria-hidden="true" />
      <div className="h-32 rounded-md bg-neutral-200" aria-hidden="true" />
    </div>
  );
}

/** Shown when there is nothing to show yet. Always says what to do next. */
export function EmptyState({
  title,
  body,
  action,
}: {
  title: string;
  body: string;
  action?: ReactNode;
}) {
  return (
    <div className="rounded-md border border-neutral-200 bg-white p-6 text-center">
      <h2 className="text-foreground text-lg font-semibold">{title}</h2>
      <p className="mt-2 text-neutral-700">{body}</p>
      {action ? <div className="mt-4 flex justify-center">{action}</div> : null}
    </div>
  );
}

/** Shown when loading failed. Plain words, never a raw error; always a way to retry. */
export function ErrorState({
  title = copy.states.errorTitle,
  body = copy.states.errorBody,
  onRetry,
}: {
  title?: string;
  body?: string;
  onRetry?: () => void;
}) {
  return (
    <div role="alert" className="rounded-md border border-primary-200 bg-white p-6 text-center">
      <h2 className="text-foreground text-lg font-semibold">{title}</h2>
      <p className="mt-2 text-neutral-700">{body}</p>
      {onRetry ? (
        <div className="mt-4 flex justify-center">
          <button type="button" onClick={onRetry} className={primaryButton}>
            {copy.states.retry}
          </button>
        </div>
      ) : null}
    </div>
  );
}

/**
 * One place that turns a data query into the right state, so every screen gets loading, empty and
 * error handling the same way.
 */
export function QueryState<T>({
  isLoading,
  error,
  data,
  isEmpty,
  empty,
  onRetry,
  children,
}: {
  isLoading: boolean;
  error: unknown;
  data: T | undefined;
  isEmpty?: (data: T) => boolean;
  empty: ReactNode;
  onRetry?: () => void;
  children: (data: T) => ReactNode;
}) {
  if (isLoading) return <LoadingState />;
  if (error) return <ErrorState onRetry={onRetry} />;
  if (data == null || isEmpty?.(data)) return <>{empty}</>;
  return <>{children(data)}</>;
}
