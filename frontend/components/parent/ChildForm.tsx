'use client';

import { useState, type FormEvent } from 'react';
import { useRouter } from 'next/navigation';
import { useQueryClient } from '@tanstack/react-query';
import { isAxiosError } from 'axios';
import { apiClient } from '@/lib/api';
import { copy } from '@/lib/copy';
import { primaryButton } from '@/components/parent/states';

const field =
  'mt-1 block min-h-11 w-full rounded-md border border-neutral-400 bg-white px-3 py-2 text-base focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary-600';
const MAX_INTERESTS = 8;
const MAX_INTEREST_LENGTH = 40;
const GRADES = [0, 1, 2, 3, 4, 5, 6, 7, 8];

/** "a, b ,, c" -> ["a", "b", "c"]: trimmed, blanks dropped. The server checks the limits. */
export const splitInterests = (text: string) =>
  text
    .split(',')
    .map((item) => item.trim())
    .filter(Boolean);

function GradeSelect(props: { label: string; value: number; onChange: (grade: number) => void }) {
  const id = `child-${props.label.replace(/\W+/g, '-').toLowerCase()}`;
  return (
    <div>
      <label htmlFor={id} className="text-foreground block font-medium">
        {props.label}
      </label>
      <select
        id={id}
        value={props.value}
        onChange={(e) => props.onChange(Number(e.target.value))}
        className={field}
      >
        {GRADES.map((grade) => (
          <option key={grade} value={grade}>
            {copy.childForm.gradeOption(grade)}
          </option>
        ))}
      </select>
    </div>
  );
}

/** Name, interests, two grades and notes. Saving starts the child's first week, then shows This week. */
export function ChildForm() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const [name, setName] = useState('');
  const [interests, setInterests] = useState('');
  const [mathGrade, setMathGrade] = useState(0);
  const [laGrade, setLaGrade] = useState(0);
  const [notes, setNotes] = useState('');
  const [saving, setSaving] = useState(false);
  const [problem, setProblem] = useState('');
  const [interestsProblem, setInterestsProblem] = useState('');

  async function submit(event: FormEvent) {
    event.preventDefault();
    if (saving) return;
    const items = splitInterests(interests);
    const tooLong = items.some((item) => item.length > MAX_INTEREST_LENGTH);
    if (items.length > MAX_INTERESTS || tooLong) {
      setInterestsProblem(
        items.length > MAX_INTERESTS
          ? copy.childForm.tooManyInterests
          : copy.childForm.interestTooLong
      );
      document.getElementById('child-interests')?.focus();
      return;
    }
    setInterestsProblem('');
    setSaving(true);
    setProblem('');
    try {
      await apiClient.post('/children', {
        name: name.trim(),
        interests: items,
        math_grade: mathGrade,
        la_grade: laGrade,
        notes: notes.trim(),
      });
      await queryClient.invalidateQueries({ queryKey: ['this-week'] });
      await queryClient.invalidateQueries({ queryKey: ['students'] });
      router.push('/week');
    } catch (error) {
      const tooMany = isAxiosError(error) && error.response?.status === 409;
      setProblem(tooMany ? copy.childForm.tooMany : copy.childForm.failed);
      setSaving(false);
    }
  }

  return (
    <form onSubmit={submit} className="mt-6 space-y-4" noValidate>
      <div>
        <label htmlFor="child-name" className="text-foreground block font-medium">
          {copy.childForm.name}
        </label>
        <input
          id="child-name"
          type="text"
          required
          maxLength={40}
          autoComplete="off"
          value={name}
          onChange={(e) => setName(e.target.value)}
          className={field}
        />
      </div>
      <div>
        <label htmlFor="child-interests" className="text-foreground block font-medium">
          {copy.childForm.interests}
        </label>
        <p id="child-interests-hint" className="text-sm text-neutral-700">
          {copy.childForm.interestsHint}
        </p>
        <input
          id="child-interests"
          type="text"
          aria-describedby={
            interestsProblem ? 'child-interests-hint child-interests-error' : 'child-interests-hint'
          }
          aria-invalid={interestsProblem ? true : undefined}
          value={interests}
          onChange={(e) => {
            setInterests(e.target.value);
            setInterestsProblem('');
          }}
          className={interestsProblem ? `${field} border-2 border-neutral-900` : field}
        />
        {interestsProblem ? (
          <p id="child-interests-error" className="mt-1 text-neutral-900">
            {interestsProblem}
          </p>
        ) : null}
      </div>
      <GradeSelect label={copy.childForm.mathGrade} value={mathGrade} onChange={setMathGrade} />
      <GradeSelect label={copy.childForm.laGrade} value={laGrade} onChange={setLaGrade} />
      <div>
        <label htmlFor="child-notes" className="text-foreground block font-medium">
          {copy.childForm.notes}
        </label>
        <textarea
          id="child-notes"
          rows={3}
          maxLength={500}
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
          className={field}
        />
      </div>
      <p className="text-neutral-700">{copy.childForm.calibrate}</p>
      <p className="text-neutral-700">{copy.childForm.aiNote}</p>
      <div role="alert" className="min-h-6 text-neutral-900">
        {problem}
      </div>
      <button
        type="submit"
        disabled={saving || !name.trim()}
        className={`${primaryButton} w-full disabled:cursor-not-allowed disabled:opacity-60`}
      >
        {saving ? copy.childForm.submitting : copy.childForm.submit}
      </button>
    </form>
  );
}
