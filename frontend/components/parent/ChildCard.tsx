import Link from 'next/link';
import { copy } from '@/lib/copy';
import type { ChildCard as Card } from '@/lib/thisWeek';
import { primaryButton } from './states';

function weekLabel(iso: string): string {
  const d = new Date(`${iso}T12:00:00`);
  return `${copy.thisWeek.weekOf} ${d.toLocaleDateString('en-US', { month: 'long', day: 'numeric' })}`;
}

/** A week that is "writing" but flagged: the work failed on our side. Say so, ask for nothing. */
function isStuckWriting(card: Card) {
  return card.needs_attention && card.next_action === 'writing';
}

function textFor(card: Card) {
  const a = copy.thisWeek.actions;
  if (isStuckWriting(card)) return { ...copy.thisWeek.problem, button: null };
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
      data-needs-attention={card.needs_attention ? 'true' : undefined}
      className="rounded-md border border-neutral-200 bg-white p-5"
    >
      <p className="text-sm text-neutral-700">
        <span className="font-medium">{card.first_name}</span> · {weekLabel(card.week_start)}
      </p>
      <h2 className="text-foreground mt-1 text-xl font-semibold">{text.title(card.first_name)}</h2>
      <p className="mt-1 text-neutral-700">{text.body}</p>
      {card.needs_attention && !isStuckWriting(card) ? (
        <p className="mt-3 rounded bg-secondary-100 p-3 text-sm text-neutral-900">
          {copy.thisWeek.attention}
        </p>
      ) : null}
      {text.button ? (
        <Link href={href} className={`${primaryButton} mt-4 w-full`}>
          {text.button}
        </Link>
      ) : null}
    </li>
  );
}
