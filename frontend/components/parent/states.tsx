'use client';

import type { ReactNode } from 'react';
import { copy } from '@/lib/copy';

const primaryButton =
  'inline-flex min-h-11 items-center justify-center rounded-md bg-primary-600 px-6 py-3 font-medium text-white hover:bg-primary-700 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary-600';

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

export { primaryButton };

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
  if (data === undefined || data === null || (isEmpty && isEmpty(data))) return <>{empty}</>;
  return <>{children(data)}</>;
}
