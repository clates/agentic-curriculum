'use client';

import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useEffect, useRef, useState } from 'react';
import { copy } from '@/lib/copy';
import {
  serverMessage,
  useFreshIdeas,
  usePickIdea,
  type Idea,
  type OptionId,
  type WeekPlan,
} from '@/lib/pick';
import { EmptyState, ErrorState, primaryButton } from './states';

const c = copy.pick;
const secondaryButton =
  'inline-flex min-h-11 items-center justify-center rounded-md border-2 border-primary-600 bg-white px-6 py-3 font-medium text-primary-700 hover:bg-primary-50 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary-600';

export function BackLink() {
  return (
    <Link href="/week" className="text-primary-700 mb-3 inline-block py-2 underline">
      {c.back}
    </Link>
  );
}

function Working({ title, body }: { title: string; body: string }) {
  return (
    <div role="status" className="rounded-md border border-neutral-200 bg-white p-6 text-center">
      <h2 className="text-foreground text-lg font-semibold">{title}</h2>
      <p className="mt-2 text-neutral-700">{body}</p>
    </div>
  );
}

/** One idea as a big radio card: topic, title, hook and the effort. */
function IdeaCard({
  idea,
  checked,
  onChange,
}: {
  idea: Idea;
  checked: boolean;
  onChange: () => void;
}) {
  return (
    <label
      data-testid="idea-card"
      data-option={idea.option_id}
      className={`block min-w-0 cursor-pointer rounded-md border-2 p-4 has-[:focus-visible]:outline-2 has-[:focus-visible]:outline-offset-2 has-[:focus-visible]:outline-primary-600 ${
        checked ? 'border-primary-600 bg-primary-50' : 'border-neutral-200 bg-white'
      }`}
    >
      <input
        type="radio"
        name="idea"
        value={idea.option_id}
        checked={checked}
        onChange={onChange}
        className="sr-only"
      />
      {idea.topic ? (
        <span className="block text-sm font-medium text-neutral-700">{idea.topic}</span>
      ) : null}
      <span className="text-foreground mt-1 block text-xl font-semibold [overflow-wrap:anywhere]">
        {idea.title}
      </span>
      <span className="mt-1 block text-neutral-900 [overflow-wrap:anywhere]">{idea.hook}</span>
      {idea.effort ? (
        <span className="mt-2 block text-sm text-neutral-700">{idea.effort}</span>
      ) : null}
    </label>
  );
}

function FreshIdeas({ plan, variant }: { plan: WeekPlan; variant: 'primary' | 'secondary' }) {
  const fresh = useFreshIdeas(plan.student_id);
  const lock = useRef(false);
  const ask = () => {
    if (lock.current) return;
    lock.current = true;
    fresh.mutate(plan.plan_id, { onSettled: () => (lock.current = false) });
  };
  const { code, message } = serverMessage(fresh.error);

  if (fresh.isPending) return <Working title={c.writingFresh} body={c.writingFreshBody} />;
  if (plan.regenerations_left <= 0 || code === 'limit_reached') {
    return (
      <p className="mt-4 rounded-md bg-neutral-100 p-4 text-neutral-900" data-testid="fresh-limit">
        <span className="font-medium">{c.limitTitle}.</span> {c.limitBody}
      </p>
    );
  }
  return (
    <div className="space-y-3">
      {fresh.isError ? (
        <ErrorState title={c.freshErrorTitle} body={message ?? c.freshErrorBody} onRetry={ask} />
      ) : null}
      {!fresh.isError ? (
        <>
          <button
            type="button"
            onClick={ask}
            className={`${variant === 'primary' ? primaryButton : secondaryButton} w-full`}
          >
            {variant === 'primary' ? c.getFresh : c.fresh}
          </button>
          {variant === 'secondary' ? (
            <p className="text-center text-sm text-neutral-700">
              {c.freshLeft(plan.regenerations_left)}
            </p>
          ) : null}
        </>
      ) : null}
    </div>
  );
}

function Choose({ plan, ideas }: { plan: WeekPlan; ideas: Idea[] }) {
  const router = useRouter();
  const pick = usePickIdea(plan.student_id);
  const lock = useRef(false);
  const [selected, setSelected] = useState<OptionId>(ideas[0].option_id);
  const [confirming, setConfirming] = useState(false);
  const confirmHeading = useRef<HTMLHeadingElement>(null);
  const idea = ideas.find((i) => i.option_id === selected) ?? ideas[0];

  useEffect(() => {
    if (confirming) confirmHeading.current?.focus();
  }, [confirming]);

  const confirm = () => {
    if (lock.current) return; // a second tap while the first is in flight does nothing
    lock.current = true;
    pick.mutate(
      { option: selected, planId: plan.plan_id },
      {
        onSuccess: () => router.push('/week'),
        onError: () => (lock.current = false),
      }
    );
  };

  if (confirming) {
    const { message } = serverMessage(pick.error);
    return (
      <section aria-labelledby="confirm-title" className="space-y-4">
        <div className="rounded-md border-2 border-primary-600 bg-primary-50 p-5">
          <h2
            id="confirm-title"
            ref={confirmHeading}
            tabIndex={-1}
            className="text-foreground text-xl font-semibold outline-none [overflow-wrap:anywhere]"
          >
            {c.confirmTitle(idea.title)}
          </h2>
          <p className="mt-2 text-neutral-900">{idea.hook}</p>
          {idea.activities ? (
            <>
              <h3 className="text-foreground mt-4 text-sm font-semibold">{c.willDo}</h3>
              <p className="text-neutral-900">{idea.activities}</p>
            </>
          ) : null}
          {idea.skills.length > 0 ? (
            <>
              <h3 className="text-foreground mt-4 text-sm font-semibold">{c.covers}</h3>
              <ul className="list-disc pl-5 text-neutral-900">
                {idea.skills.map((s) => (
                  <li key={s}>{s}</li>
                ))}
              </ul>
            </>
          ) : null}
          {idea.effort ? <p className="mt-3 text-sm text-neutral-700">{idea.effort}</p> : null}
        </div>
        <p className="text-neutral-900">{c.confirmBody(plan.first_name)}</p>
        {pick.isError ? (
          <ErrorState title={c.chooseErrorTitle} body={message ?? c.chooseErrorBody} />
        ) : null}
        <button
          type="button"
          onClick={confirm}
          disabled={pick.isPending || pick.isSuccess}
          className={`${primaryButton} w-full disabled:bg-neutral-700 disabled:opacity-100`}
        >
          {pick.isPending || pick.isSuccess ? c.choosing : c.confirmYes}
        </button>
        <button
          type="button"
          onClick={() => setConfirming(false)}
          disabled={pick.isPending || pick.isSuccess}
          className={`${secondaryButton} w-full disabled:opacity-60`}
        >
          {c.confirmBack}
        </button>
      </section>
    );
  }

  return (
    <div className="space-y-6">
      <fieldset className="space-y-3">
        <legend className="text-foreground mb-2 text-lg font-semibold">
          {c.question(plan.first_name)}
        </legend>
        <p className="text-neutral-700">{c.sameSkills}</p>
        {ideas.map((i) => (
          <IdeaCard
            key={i.option_id}
            idea={i}
            checked={selected === i.option_id}
            onChange={() => setSelected(i.option_id)}
          />
        ))}
      </fieldset>
      <div className="sticky bottom-20 md:static">
        <button
          type="button"
          onClick={() => setConfirming(true)}
          className={`${primaryButton} w-full`}
        >
          {c.useThis}
        </button>
      </div>
      <FreshIdeas plan={plan} variant="secondary" />
    </div>
  );
}

/** What the pick screen shows for a child's plan, by where the week is. */
export function PickIdeas({ plan }: { plan: WeekPlan }) {
  const ideas = plan.outlines ?? [];
  const pickedTitle = ideas.find((i) => i.option_id === plan.picked_option)?.title ?? null;
  const back = (
    <Link href="/week" className={primaryButton}>
      {c.back}
    </Link>
  );

  let body;
  if (plan.status === 'awaiting_pick' && ideas.length > 0) {
    body = <Choose plan={plan} ideas={ideas} />;
  } else if (plan.status === 'expired') {
    body = (
      <div className="space-y-4">
        <p className="text-neutral-900">{c.expiredBody}</p>
        <FreshIdeas plan={plan} variant="primary" />
      </div>
    );
  } else if (plan.status === 'authoring' || plan.status === 'ready' || plan.status === 'printed') {
    body = (
      <EmptyState
        title={c.alreadyTitle(plan.first_name)}
        body={c.alreadyBody(pickedTitle)}
        action={back}
      />
    );
  } else if (plan.status === 'awaiting_feedback') {
    body = (
      <EmptyState
        title={c.notYetTitle}
        body={c.notYetBody}
        action={
          <Link href={`/week/check-in/${plan.student_id}`} className={primaryButton}>
            {c.checkIn}
          </Link>
        }
      />
    );
  } else {
    body = <Working title={c.writingTitle} body={c.writingBody} />;
  }

  return (
    <>
      <BackLink />
      <h1 className="text-foreground mb-4 text-2xl font-semibold">{c.title(plan.first_name)}</h1>
      {body}
    </>
  );
}
