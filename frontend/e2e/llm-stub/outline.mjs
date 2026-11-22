/**
 * Outline replies for the static LLM stub (M6.3). Kept in its own file so streams that edit
 * server.mjs for other prompts do not collide with it.
 *
 * The backend's outline prompt carries a machine-readable line, `OPTIONS_JSON: {...}`, with the
 * three options and the standard ids each must cover; the reply echoes those ids, so the gate in
 * src/outline_generator.py passes. The child's first name comes from `First name: <name>`.
 *
 * Scenarios ride in the student's parent notes, like the other stub scenarios, and apply to the
 * FIRST outline call for that student only (later calls are normal):
 *   e2e-stub:outline=repair     the first reply fails the gate once; the repair call succeeds
 *   e2e-stub:outline=fail-once  the first call and all four repairs fail the gate (the backend
 *                               answers 502); the next call from the parent succeeds
 *   e2e-stub:outline=slow       the first reply is delayed 2.5 s (a visible loading state)
 *
 * A bad reply carries `e2e_stub` (with how many more bad replies to give) so the repair call,
 * which has no student in it, can be recognised and answered from what it was shown.
 */

const TITLES = [
  ['Number Detectives', 'Garden Scientists', 'Story Builders'],
  ['Kitchen Math Lab', 'Backyard Explorers', 'Comic Makers'],
  ['Puzzle Week', 'Weather Watchers', 'Letter Writers'],
];
const FIRST_CALL_SCENARIOS = new Set(['repair', 'fail-once', 'slow']);
const LETTERS = ['a', 'b', 'c'];

const callsPerStudent = new Map();

export const isOutlinePrompt = (prompt) => prompt.includes('OPTIONS_JSON: ');
export const isStubRepair = (prompt) =>
  prompt.includes('You repair invalid JSON') && prompt.includes('e2e_stub');

function parseOptions(prompt) {
  const line = /^OPTIONS_JSON: (.+)$/m.exec(prompt)?.[1];
  if (!line) throw new Error('outline prompt had no OPTIONS_JSON line');
  return JSON.parse(line);
}

function validReply(prompt, callNumber) {
  const options = parseOptions(prompt);
  const name = /^First name: (.+)$/m.exec(prompt)?.[1]?.trim() ?? 'your child';
  const titles = TITLES[callNumber % TITLES.length];
  return JSON.stringify({
    options: LETTERS.map((letter, i) => {
      const spec = options[letter];
      const subjects = [...new Set(spec.standards.map((s) => s.subject.toLowerCase()))];
      return {
        option_id: letter,
        title: titles[i],
        hook: `${name} ${['eases into', 'builds on', 'stretches with'][i]} ${subjects[0]} through ${titles[i].toLowerCase()}.`,
        activities: `${titles[i]}: short hands-on tasks each day that keep ${name} busy and curious.`,
        skills: subjects.map((s) => `Growing ${s} skills`),
        effort: ['About 15 minutes a day', 'About 25 minutes a day', 'About 35 minutes a day'][i],
        standard_ids: spec.standards.map((s) => s.id),
      };
    }),
  });
}

function badReply(promptForRepair, garbageLeft) {
  // Wrong shape on purpose: no options, plus what the repair call needs to answer later.
  return JSON.stringify({
    options: [],
    e2e_stub: { garbage_left: garbageLeft, prompt: promptForRepair },
  });
}

/** -> { record, raw, delayMs } for an outline prompt or a repair of one of our bad replies. */
export function outlineResponse(prompt, student, scenario) {
  if (isStubRepair(prompt)) {
    const shown = /Invalid output:\n([\s\S]*)$/.exec(prompt)?.[1] ?? '';
    const stub = JSON.parse(shown).e2e_stub;
    if (stub.garbage_left > 0) {
      return {
        record: { kind: 'outline-repair', student, scenario: 'still-bad' },
        raw: badReply(stub.prompt, stub.garbage_left - 1),
        delayMs: 0,
      };
    }
    return {
      record: { kind: 'outline-repair', student, scenario: 'repaired' },
      raw: validReply(stub.prompt, 0),
      delayMs: 0,
    };
  }
  const key = student ?? 'anonymous';
  const n = callsPerStudent.get(key) ?? 0;
  callsPerStudent.set(key, n + 1);
  const active = n === 0 && FIRST_CALL_SCENARIOS.has(scenario) ? scenario : null;
  const record = { kind: 'outline', student, scenario: active, call: n + 1 };
  if (active === 'repair') return { record, raw: badReply(prompt, 0), delayMs: 0 };
  if (active === 'fail-once') return { record, raw: badReply(prompt, 4), delayMs: 0 };
  return { record, raw: validReply(prompt, n), delayMs: active === 'slow' ? 2500 : 0 };
}
