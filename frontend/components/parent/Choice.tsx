'use client';

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
      className={`flex min-h-14 cursor-pointer flex-col justify-center rounded-md border-2 px-4 py-3 has-[:focus-visible]:outline-2 has-[:focus-visible]:outline-offset-2 has-[:focus-visible]:outline-primary-600 ${
        checked ? 'border-primary-600 bg-primary-50' : 'border-neutral-200 bg-white'
      }`}
    >
      <input type="radio" name={name} checked={checked} onChange={onChange} className="sr-only" />
      <span className="text-foreground text-lg font-medium">{label}</span>
      {hint ? <span className="text-sm text-neutral-700">{hint}</span> : null}
    </label>
  );
}
