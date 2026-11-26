import Link from 'next/link';
import { copy } from '@/lib/copy';
import type { ChildCard as Card } from '@/lib/thisWeek';
import { primaryButton } from './states';

const linkClass =
  'text-primary-700 inline-flex min-h-11 items-center underline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary-600';

function weekLabel(iso: string): string {
  const d = new Date(`${iso}T12:00:00`);
  return `${copy.thisWeek.weekOf} ${d.toLocaleDateString('en-US', { month: 'long', day: 'numeric' })}`;
}

function textFor(card: Card) {
  const a = copy.thisWeek.actions;
  if (card.next_action === 'pick' && card.options_expired) return a.pickAgain;
  return a[card.next_action];
}

/** One child, one next step. The action is driven by the week's loop state. */
export function ChildCard({ card }: { card: Card }) {
  const text = textFor(card);
  const href = `/week/${card.next_action.replace('_', '-')}/${card.student_id}`;
  return (
    <li
      data-testid="child-card"
      data-next-action={card.next_action}
      className="rounded-md border border-neutral-200 bg-white p-5"
    >
      <p className="text-sm text-neutral-700">
        <span className="font-medium">{card.first_name}</span> · {weekLabel(card.week_start)}
      </p>
      <h2 className="text-foreground mt-1 text-xl font-semibold">{text.title(card.first_name)}</h2>
      <p className="mt-1 text-neutral-700">{text.body}</p>
      {card.needs_attention ? (
        <p className="mt-3 rounded bg-secondary-100 p-3 text-sm text-neutral-900">
          {copy.thisWeek.attention}
        </p>
      ) : null}
      {text.button ? (
        <Link href={href} className={`${primaryButton} mt-4 w-full`}>
          {text.button}
        </Link>
      ) : null}
      <p className="mt-3 flex flex-wrap gap-x-5">
        <Link href={`/children/${card.student_id}#past-weeks`} className={linkClass}>
          {copy.thisWeek.pastWeeks}
        </Link>
        <Link href={`/children/${card.student_id}#coverage`} className={linkClass}>
          {copy.thisWeek.howItsGoing}
        </Link>
      </p>
    </li>
  );
}
