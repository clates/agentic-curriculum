import { APIRequestContext, expect } from '@playwright/test';
import { STUB_BASE_URL } from '../llm-stub/config';

/** One call recorded by the static LLM/ntfy stub (see e2e/llm-stub/server.mjs). */
export interface StubCall {
  id: number;
  at: string;
  kind: 'scaffold' | 'day' | 'ntfy' | 'bad-auth' | 'unrecognised';
  student?: string | null;
  subject?: string | null;
  grade?: string | null;
  day?: string;
  scenario?: string | null;
  title?: string | null;
  priority?: string | null;
  message?: string;
  note?: string;
}

export async function stubCalls(
  request: APIRequestContext,
  filter: { student?: string; kind?: StubCall['kind'] } = {}
): Promise<StubCall[]> {
  const qs = new URLSearchParams();
  if (filter.student) qs.set('student', filter.student);
  if (filter.kind) qs.set('kind', filter.kind);
  const res = await request.get(`${STUB_BASE_URL}/__requests?${qs}`);
  if (!res.ok()) throw new Error(`stub /__requests failed: ${res.status()}`);
  return (await res.json()).requests as StubCall[];
}

/** Calls that mean the stub (or the backend's env pinning) is misbehaving. Must always be empty. */
export async function stubProblems(request: APIRequestContext): Promise<StubCall[]> {
  const all = await stubCalls(request);
  return all.filter((c) => c.kind === 'unrecognised' || c.kind === 'bad-auth');
}

/** ntfy pushes are sent from a background task, so wait for the one we expect. */
export async function waitForNtfy(
  request: APIRequestContext,
  titleIncludes: string
): Promise<StubCall> {
  let found: StubCall | undefined;
  await expect
    .poll(
      async () => {
        found = (await stubCalls(request, { kind: 'ntfy' })).find((c) =>
          (c.title ?? '').includes(titleIncludes)
        );
        return !!found;
      },
      { timeout: 30_000, message: `no ntfy push with title containing "${titleIncludes}"` }
    )
    .toBe(true);
  return found!;
}
