'use client';

import { copy } from '@/lib/copy';
import type { Workload } from '@/lib/checkIn';

/** A big tap target that behaves as a radio button (keyboard and screen reader friendly). */
export function Choice({
  name,
  checked,
  onChange,
  label,
  hint,
}: {
  name: string;
  checked: boolean;
  onChange: () => void;
  label: string;
  hint?: string;
}) {
  return (
    <label
      className={`flex min-h-14 min-w-0 cursor-pointer flex-col justify-center rounded-md border-2 px-4 py-3 has-[:focus-visible]:outline-2 has-[:focus-visible]:outline-offset-2 has-[:focus-visible]:outline-primary-600 ${
        checked ? 'border-primary-600 bg-primary-50' : 'border-neutral-200 bg-white'
      }`}
    >
      <input type="radio" name={name} checked={checked} onChange={onChange} className="sr-only" />
      <span className="text-foreground text-lg font-medium [overflow-wrap:anywhere]">{label}</span>
      {hint ? <span className="text-sm text-neutral-700">{hint}</span> : null}
    </label>
  );
}

const c = copy.checkIn;
const WORKLOADS: { value: Workload; label: string }[] = [
  { value: 2, label: c.workload.tooLittle },
  { value: 0, label: c.workload.justRight },
  { value: -2, label: c.workload.tooMuch },
];

/** "How much work was it?" as three choices in a row, shared by both check-in screens. */
export function WorkloadChoice({
  value,
  onChange,
}: {
  value: Workload | null;
  onChange: (w: Workload) => void;
}) {
  return (
    <fieldset>
      <legend className="text-foreground mb-2 text-lg font-semibold">{c.workloadQuestion}</legend>
      <div className="grid grid-cols-3 gap-2">
        {WORKLOADS.map((w) => (
          <Choice
            key={w.value}
            name="workload"
            checked={value === w.value}
            onChange={() => onChange(w.value)}
            label={w.label}
          />
        ))}
      </div>
    </fieldset>
  );
}
