'use client';

import { useState } from 'react';
import { Badge, Button, Card } from '@/components/ui';
import {
  errorMessage,
  useFeedForward,
  useLoopAction,
  useLoopOverview,
  useRetryJob,
  useSeedDemo,
  type LoopAction,
  type LoopChild,
  type LoopStep,
} from '@/lib/loop';

const STEP_STYLE: Record<LoopStep['state'], string> = {
  done: 'border-sage-500 bg-sage-100 text-sage-700',
  current: 'border-primary-600 bg-primary-50 text-primary-700 font-semibold',
  expired: 'border-secondary-500 bg-secondary-100 text-secondary-700',
  todo: 'border-neutral-300 bg-white text-neutral-600',
};

function Stepper({ steps }: { steps: LoopStep[] }) {
  return (
    <ol aria-label="Loop steps" className="grid grid-cols-2 gap-2 sm:grid-cols-6">
      {steps.map((s) => (
        <li
          key={s.key}
          data-step={s.key}
          data-state={s.state}
          className={`rounded-md border px-2 py-2 text-sm ${STEP_STYLE[s.state]}`}
        >
          <div>{s.label}</div>
          <div className="text-xs">
            {s.actor === 'parent' ? 'parent' : 'system'} · {s.state}
          </div>
        </li>
      ))}
    </ol>
  );
}

function ActionButton({
  action,
  busy,
  onRun,
}: {
  action: LoopAction;
  busy: boolean;
  onRun: () => void;
}) {
  return (
    <Button
      size="sm"
      variant={action.id === 'reset_weeks' ? 'ghost' : 'secondary'}
      disabled={!action.enabled || busy}
      title={action.enabled ? undefined : action.why_not}
      onClick={onRun}
    >
      {action.label}
    </Button>
  );
}

function FeedForward({ studentId }: { studentId: string }) {
  const [open, setOpen] = useState(false);
  const q = useFeedForward(studentId, open);
  return (
    <div>
      <Button size="sm" variant="ghost" onClick={() => setOpen((v) => !v)} aria-expanded={open}>
        {open ? 'Hide feed forward' : 'Preview feed forward'}
      </Button>
      {open && q.isLoading && <p className="mt-2 text-sm text-neutral-700">Working it out…</p>}
      {open && q.data && (
        <div className="mt-2 text-sm text-neutral-800" data-testid="feed-forward">
          <p>
            Week of {q.data.week_start}, grade {q.data.grade}. Known: {q.data.known.mastered}{' '}
            mastered, {q.data.known.developing} developing, {q.data.known.rated} rated.
          </p>
          {q.data.skills.length === 0 ? (
            <p>Nothing to pick from yet.</p>
          ) : (
            <ul className="mt-1 space-y-1">
              {q.data.skills.map((s) => (
                <li key={s.standard_id}>
                  <Badge variant="subject">{s.reason}</Badge> {s.standard_id} · {s.subject} ·{' '}
                  {s.description}
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
    </div>
  );
}

function ChildCard({ child }: { child: LoopChild }) {
  const act = useLoopAction(child.student_id);
  const retry = useRetryJob();
  const [week, setWeek] = useState('');
  const [confirmReset, setConfirmReset] = useState(false);
  const busy = act.isPending || retry.isPending;
  const plan = child.plan;
  const run = (action: string, extra: { option?: string; week?: string } = {}) =>
    act.mutate({ action, ...extra });

  return (
    <Card data-testid="loop-child" data-student={child.student_id} className="space-y-4">
      <div className="flex flex-wrap items-baseline justify-between gap-2">
        <h2 className="min-w-0 text-xl font-semibold text-neutral-900">
          {child.name}
          {child.grade != null && <span className="text-neutral-700"> · grade {child.grade}</span>}
        </h2>
        <p className="text-sm text-neutral-700">
          {plan ? (
            <>
              Week of {plan.week_start} · <strong>{plan.status}</strong>
            </>
          ) : (
            'No week yet'
          )}
        </p>
      </div>

      {plan?.needs_attention && (
        <p
          data-testid="loop-attention"
          className="rounded-md border border-secondary-500 bg-secondary-100 px-3 py-2 text-sm font-medium text-neutral-900"
        >
          Needs attention: {plan.attention_reason ?? 'unspecified'}
        </p>
      )}

      <Stepper steps={child.steps} />

      <div className="flex flex-wrap items-center gap-2">
        {child.actions
          .filter((a) => a.id !== 'pick' && a.id !== 'reset_weeks' && a.id !== 'new_week')
          .map((a) => (
            <ActionButton key={a.id} action={a} busy={busy} onRun={() => run(a.id)} />
          ))}
        <label className="flex items-center gap-1 text-sm text-neutral-800">
          <span>New week starting</span>
          <input
            type="date"
            value={week}
            onChange={(e) => setWeek(e.target.value)}
            className="rounded-sm border border-neutral-300 px-2 py-1"
          />
        </label>
        <ActionButton
          action={child.actions.find((a) => a.id === 'new_week')!}
          busy={busy}
          onRun={() => run('new_week', { week })}
        />
      </div>

      {plan && plan.outlines.length > 0 && (
        <ul className="grid gap-3 sm:grid-cols-3" aria-label="The three ideas">
          {plan.outlines.map((o) => {
            const picked = plan.picked_option === o.option_id;
            return (
              <li
                key={o.option_id}
                data-testid="loop-idea"
                className={`rounded-md border p-3 text-sm ${picked ? 'border-primary-600 bg-primary-50' : 'border-neutral-300'}`}
              >
                <p className="font-semibold text-neutral-900">
                  {o.option_id.toUpperCase()} · {o.title}
                </p>
                <p className="text-neutral-800">{o.hook}</p>
                <p className="text-neutral-700">
                  {o.topic} · {o.skills} {o.skills === 1 ? 'skill' : 'skills'}
                </p>
                {picked ? (
                  <Badge variant="success">picked</Badge>
                ) : (
                  <Button
                    size="sm"
                    variant="secondary"
                    className="mt-2"
                    disabled={!child.actions.find((a) => a.id === 'pick')?.enabled || busy}
                    onClick={() => run('pick', { option: o.option_id })}
                  >
                    Pick {o.option_id.toUpperCase()}
                  </Button>
                )}
              </li>
            );
          })}
        </ul>
      )}

      {plan && plan.jobs.length > 0 && (
        <ul className="space-y-1 text-sm text-neutral-800" aria-label="Jobs for this week">
          {plan.jobs.map((j) => (
            <li key={j.id} data-testid="loop-job" data-state={j.state}>
              <Badge variant={j.state === 'dead' ? 'warning' : 'default'}>{j.state}</Badge> #{j.id}{' '}
              {j.kind} · attempt {j.attempts}/{j.max_attempts}
              {j.last_error ? ` · ${j.last_error}` : ''}
              {j.hint && (
                <p data-testid="loop-hint" className="mt-1 font-medium text-neutral-900">
                  {j.hint}
                </p>
              )}
              {j.state === 'dead' && (
                <Button
                  size="sm"
                  variant="ghost"
                  className="ml-2"
                  onClick={() => retry.mutate(j.id)}
                >
                  Retry
                </Button>
              )}
            </li>
          ))}
        </ul>
      )}

      <FeedForward studentId={child.student_id} />

      {act.isError && (
        <p role="alert" className="text-sm font-medium text-primary-700">
          {errorMessage(act.error)}
        </p>
      )}
      {act.isPending && (
        <p className="text-sm text-neutral-700">Working… ideas can take a moment.</p>
      )}

      <div className="border-t border-neutral-200 pt-3">
        {confirmReset ? (
          <span className="flex flex-wrap items-center gap-2 text-sm text-neutral-800">
            Delete every week and job for {child.name}? The child stays.
            <Button
              size="sm"
              variant="secondary"
              onClick={() => {
                run('reset_weeks');
                setConfirmReset(false);
              }}
            >
              Yes, reset
            </Button>
            <Button size="sm" variant="ghost" onClick={() => setConfirmReset(false)}>
              Cancel
            </Button>
          </span>
        ) : (
          <ActionButton
            action={child.actions.find((a) => a.id === 'reset_weeks')!}
            busy={busy}
            onRun={() => setConfirmReset(true)}
          />
        )}
      </div>
    </Card>
  );
}

export function LoopConsole() {
  const overview = useLoopOverview();
  const seed = useSeedDemo();
  const data = overview.data;
  const hasDemo = data?.children.some((c) => c.student_id === 'demo_child');

  return (
    <main className="mx-auto max-w-5xl space-y-6 px-4 py-8 [overflow-wrap:anywhere]">
      <header className="space-y-2">
        <h1 className="text-3xl font-semibold text-neutral-900">Loop console</h1>
        <p className="max-w-prose text-neutral-800">
          Push any child’s week one step at a time. Each button runs the same code the weekly loop
          uses, so it can only do what the loop could do. Steps marked parent are normally the
          parent’s.
        </p>
        {data && (
          <p className="text-sm text-neutral-800" data-testid="queue-line">
            Scheduler {data.loop_switch ? 'on' : 'off'} · queued {data.queue.counts.queued ?? 0} ·
            running {data.queue.running} · dead {data.queue.counts.dead ?? 0}
          </p>
        )}
        {data?.queue.worker_may_be_down && (
          <p role="alert" className="font-medium text-primary-700">
            Work is waiting and nothing is running. The worker may be down.
          </p>
        )}
      </header>

      {overview.isLoading && <p className="text-neutral-700">Loading…</p>}
      {overview.isError && (
        <p role="alert" className="font-medium text-primary-700">
          Could not load the loop. {errorMessage(overview.error)}
        </p>
      )}

      {data?.children.map((c) => (
        <ChildCard key={c.student_id} child={c} />
      ))}

      {data && !hasDemo && (
        <Button variant="secondary" onClick={() => seed.mutate()} disabled={seed.isPending}>
          Add a demo child
        </Button>
      )}

      {data && data.queue.dead.length > 0 && (
        <section aria-labelledby="dead-heading" className="space-y-2">
          <h2 id="dead-heading" className="text-xl font-semibold text-neutral-900">
            Jobs that gave up
          </h2>
          <ul className="space-y-1 text-sm text-neutral-800">
            {data.queue.dead.map((d) => (
              <li key={d.id}>
                #{d.id} {d.kind} · {d.attempts} {d.attempts === 1 ? 'attempt' : 'attempts'} ·{' '}
                {d.last_error}
                {d.hint && <span className="block font-medium text-neutral-900">{d.hint}</span>}
              </li>
            ))}
          </ul>
        </section>
      )}
    </main>
  );
}
