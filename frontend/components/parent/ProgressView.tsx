import { copy } from '@/lib/copy';
import type { ProgressSummary, SkillItem } from '@/lib/progress';

const p = copy.progress;

function Section({
  title,
  empty,
  items,
  tag,
}: {
  title: string;
  empty: string;
  items: (SkillItem & { tag?: string })[];
  tag?: string;
}) {
  return (
    <section className="rounded-md border border-neutral-200 bg-white p-5">
      <h2 className="text-foreground text-lg font-semibold">{title}</h2>
      {items.length === 0 ? (
        <p className="mt-2 text-neutral-700">{empty}</p>
      ) : (
        <ul className="mt-3 space-y-3">
          {items.map((item, i) => (
            <li key={`${item.skill}-${i}`}>
              <p className="text-foreground">{item.skill}</p>
              <p className="text-sm text-neutral-700">
                {[item.subject, item.tag ?? tag, item.why].filter(Boolean).join(' · ')}
              </p>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}

/** One child's progress in three plain groups, plus the last four weeks. No ids, no jargon. */
export function ProgressView({ name, summary }: { name: string; summary: ProgressSummary }) {
  const working = [
    ...summary.shaky.map((s) => ({ ...s, tag: p.tagShaky })),
    ...summary.needs_work.map((s) => ({ ...s, tag: p.tagNeedsWork })),
  ];
  const four = summary.last_four_weeks;
  return (
    <div className="space-y-4">
      <p className="text-foreground text-lg" data-testid="progress-sentence">
        {summary.summary}
      </p>
      <Section title={p.hasDown(name)} empty={p.hasDownEmpty} items={summary.solid} />
      <Section title={p.workingOn} empty={p.workingOnEmpty} items={working} />
      <Section title={p.comingUp} empty={p.comingUpEmpty} items={summary.due_for_review} />
      <section className="rounded-md border border-neutral-200 bg-white p-5">
        <h2 className="text-foreground text-lg font-semibold">{p.lastFour}</h2>
        {four.skills_checked === 0 ? (
          <p className="mt-2 text-neutral-700">{p.lastFourEmpty}</p>
        ) : (
          <>
            <p className="mt-1 text-neutral-700">{p.checked(four.skills_checked)}</p>
            <dl className="mt-3 grid grid-cols-3 gap-2 text-center">
              {[
                [p.wentWell, four.went_well.length],
                [p.stillShaky, four.still_shaky.length],
                [p.needsMore, four.needs_work.length],
              ].map(([label, n]) => (
                <div key={label as string} className="rounded-md bg-neutral-50 p-2">
                  <dd className="text-foreground text-2xl font-semibold">{n as number}</dd>
                  <dt className="text-sm text-neutral-700">{label as string}</dt>
                </div>
              ))}
            </dl>
          </>
        )}
      </section>
    </div>
  );
}
