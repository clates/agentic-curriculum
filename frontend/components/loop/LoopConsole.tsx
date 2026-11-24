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
  useWeekReview,
  type LoopAction,
  type LoopChild,
  type LoopIdea,
  type LoopStep,
  type WeekReview,
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
      className="disabled:border-neutral-300 disabled:bg-neutral-100 disabled:text-neutral-600 disabled:opacity-100"
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

function IdeaDetails({ idea }: { idea: LoopIdea }) {
  const subjects = Array.from(new Set(idea.skills.map((s) => s.subject).filter(Boolean)));
  return (
    <div className="space-y-1 text-neutral-700">
      <p>
        {idea.topic}
        {idea.effort ? ` · ${idea.effort}` : ''}
      </p>
      {idea.activities && <p className="text-neutral-800">{idea.activities}</p>}
      <details>
        <summary className="cursor-pointer text-neutral-800">
          {idea.skills.length} {idea.skills.length === 1 ? 'skill' : 'skills'}
          {subjects.length > 0 ? `: ${subjects.join(', ')}` : ''}
        </summary>
        <ul className="mt-1 space-y-1" data-testid="idea-skills">
          {idea.skills.map((s) => (
            <li key={s.id}>
              <span className="font-medium text-neutral-900">{s.subject || s.id}</span>
              {s.description ? ` · ${s.description}` : ''}
            </li>
          ))}
        </ul>
        {idea.skill_names.length > 0 && (
          <p className="mt-1">As the parent sees it: {idea.skill_names.join('; ')}</p>
        )}
      </details>
    </div>
  );
}

function level(grade: number | null) {
  if (grade == null) return '—';
  return grade <= 0 ? 'K' : grade.toFixed(1).replace(/\.0$/, '');
}

function minutes(seconds: number | null) {
  if (seconds == null) return '—';
  const m = Math.floor(seconds / 60);
  return `${m}m ${Math.round(seconds % 60)}s`;
}

function ReviewPanel({ review }: { review: WeekReview }) {
  const warns = review.flags.filter((f) => f.level === 'warn');
  const gradeLabel = review.grade === 0 ? 'kindergarten' : `grade ${review.grade}`;
  const tooHard = (g: number | null, slack: number) => g != null && g > review.grade + slack;
  return (
    <div className="space-y-4 rounded-md border border-neutral-300 p-3" data-testid="week-review">
      <div className="flex flex-wrap items-baseline justify-between gap-2">
        <h4 className="text-lg font-semibold text-neutral-900">{review.title}</h4>
        <Badge variant={warns.length ? 'warning' : 'success'} data-testid="review-verdict">
          {review.verdict}
        </Badge>
      </div>

      <div className="flex flex-wrap gap-2">
        {review.documents.map((d) => (
          <a
            key={d.doc}
            href={d.url}
            target="_blank"
            rel="noopener noreferrer"
            className="rounded-sm border-2 border-primary-500 px-3 py-1 text-sm font-medium text-primary-700 hover:bg-primary-50"
          >
            Open {d.label.toLowerCase()}
          </a>
        ))}
      </div>

      {review.flags.length > 0 && (
        <section aria-label="Things to check">
          <h5 className="font-semibold text-neutral-900">Things to check</h5>
          <ul className="mt-1 space-y-1 text-sm" data-testid="review-flags">
            {review.flags.map((f, i) => (
              <li key={i} data-level={f.level} className="flex gap-2">
                <Badge variant={f.level === 'warn' ? 'warning' : 'default'}>
                  {f.level === 'warn' ? 'fix' : 'look'}
                </Badge>
                <span className="text-neutral-800">{f.message}</span>
              </li>
            ))}
          </ul>
        </section>
      )}

      <section aria-label="Day by day">
        <h5 className="font-semibold text-neutral-900">Day by day</h5>
        <p className="text-xs text-neutral-700">
          Reading levels are estimates (Flesch-Kincaid). The child is {gradeLabel}; a day is about{' '}
          {review.word_budget} words for that grade.
        </p>
        <div className="mt-1 overflow-x-auto">
          <table className="w-full min-w-[640px] text-left text-sm" data-testid="review-days">
            <thead className="text-neutral-700">
              <tr>
                <th className="py-1 pr-2 font-medium">Day</th>
                <th className="py-1 pr-2 font-medium">Lesson</th>
                <th className="py-1 pr-2 font-medium">Skills</th>
                <th className="py-1 pr-2 font-medium">Worksheets</th>
                <th className="py-1 pr-2 font-medium">Words</th>
                <th className="py-1 pr-2 font-medium">Passage level</th>
                <th className="py-1 font-medium">Question level</th>
              </tr>
            </thead>
            <tbody className="text-neutral-800">
              {review.days.map((d) => (
                <tr key={d.day} className="border-t border-neutral-200 align-top">
                  <td className="py-1 pr-2 whitespace-nowrap">{d.day.slice(0, 3)}</td>
                  <td className="py-1 pr-2">{d.title}</td>
                  <td className="py-1 pr-2">
                    {d.skills.map((s) => s.subject || s.id).join(', ') || '—'}
                  </td>
                  <td className="py-1 pr-2">{d.kinds.join(', ')}</td>
                  <td
                    className={`py-1 pr-2 ${d.words > review.word_budget * 1.2 ? 'font-semibold text-primary-700' : ''}`}
                  >
                    {d.words}
                  </td>
                  <td
                    className={`py-1 pr-2 ${tooHard(d.passage_grade, 1) ? 'font-semibold text-primary-700' : ''}`}
                  >
                    {level(d.passage_grade)}
                  </td>
                  <td
                    className={`py-1 ${tooHard(d.prompt_grade, 1.5) ? 'font-semibold text-primary-700' : ''}`}
                  >
                    {level(d.prompt_grade)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <section aria-label="Skills">
        <h5 className="font-semibold text-neutral-900">
          Skills ({review.subjects.join(', ') || 'none'})
        </h5>
        <ul className="mt-1 space-y-1 text-sm text-neutral-800" data-testid="review-skills">
          {review.skills.map((s) => (
            <li key={s.id}>
              <span className="font-medium text-neutral-900">{s.subject || s.id}</span> ·{' '}
              {s.days.length
                ? `taught ${s.days.map((d) => d.slice(0, 3)).join(', ')}`
                : 'not taught'}
              {s.description ? ` · ${s.description}` : ''}
            </li>
          ))}
        </ul>
        <p className="mt-1 text-sm text-neutral-700">
          {review.prep_checks} prep checks for the parent.
        </p>
      </section>

      {review.run && (
        <p className="text-sm text-neutral-700" data-testid="review-run">
          Written by {review.run.model ?? 'unknown model'} in {minutes(review.run.wall_s)} for $
          {(review.run.cost_usd ?? 0).toFixed(3)}
          {review.run.repairs ? ` after ${review.run.repairs} rewrite(s)` : ', no rewrites'} ·{' '}
          {review.run.status ?? 'unknown'}
          {review.run.prompt_version ? ` · prompt ${review.run.prompt_version}` : ''}
        </p>
      )}
    </div>
  );
}

function WeekReviewLoader({ studentId, planId }: { studentId: string; planId: string }) {
  const q = useWeekReview(studentId, planId);
  if (q.isLoading) return <p className="text-sm text-neutral-700">Checking the week…</p>;
  if (q.isError)
    return (
      <p role="alert" className="text-sm font-medium text-primary-700">
        {errorMessage(q.error)}
      </p>
    );
  return q.data ? <ReviewPanel review={q.data} /> : null;
}

function RecentWeeks({ child }: { child: LoopChild }) {
  const [open, setOpen] = useState<string | null>(null);
  if (!child.weeks?.length) return null;
  return (
    <section aria-label={`Weeks for ${child.name}`} className="space-y-2">
      <h3 className="font-semibold text-neutral-900">Weeks</h3>
      <ul className="space-y-2 text-sm" data-testid="loop-weeks">
        {child.weeks.map((w) => (
          <li key={w.plan_id} data-plan={w.plan_id} className="space-y-2">
            <div className="flex flex-wrap items-center gap-2 text-neutral-800">
              <span className="font-medium text-neutral-900">Week of {w.week_start}</span>
              <Badge variant="default">{w.status}</Badge>
              {w.picked_title && <span>· {w.picked_title}</span>}
              {w.packet_id ? (
                <Button
                  size="sm"
                  variant="secondary"
                  aria-expanded={open === w.plan_id}
                  onClick={() => setOpen(open === w.plan_id ? null : w.plan_id)}
                >
                  {open === w.plan_id ? 'Hide review' : 'Review this week'}
                </Button>
              ) : (
                <span className="text-neutral-700">· not written yet</span>
              )}
            </div>
            {open === w.plan_id && (
              <WeekReviewLoader studentId={child.student_id} planId={w.plan_id} />
            )}
          </li>
        ))}
      </ul>
    </section>
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
          {child.grade != null && (
            <span className="text-neutral-700">
              {' '}
              · {child.grade === 0 ? 'kindergarten' : `grade ${child.grade}`}
            </span>
          )}
          {child.demo && (
            <Badge variant="default" className="ml-2 align-middle">
              made-up child
            </Badge>
          )}
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
                <IdeaDetails idea={o} />
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

      <RecentWeeks child={child} />

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
                #{d.id} {d.kind} · {d.attempts} attempts · {d.last_error}
              </li>
            ))}
          </ul>
        </section>
      )}
    </main>
  );
}
