/**
 * Outline replies for the static LLM stub (M6.3). Kept in its own file so streams that edit
 * server.mjs for other prompts do not collide with it.
 *
 * The backend's outline prompt carries a `SKILLS_JSON:` line (the skills every option shares)
 * and a "recent topics" line; the reply gives three topics that avoid the recent ones, so the
 * gate in src/outline_generator.py passes. The child's first name comes from `First name: <name>`.
 *
 * Scenarios ride in the student's parent notes, like the other stub scenarios, and apply to the
 * FIRST outline call for that student only (later calls are normal):
 *   e2e-stub:outline=repair     the first reply fails the gate once; the repair call succeeds
 *   e2e-stub:outline=fail-once  the first call and all four repairs fail the gate; the backend
 *                               falls back to topics from its curated list (still 3 options)
 *   e2e-stub:outline=provider-error  the first call is refused with HTTP 400 (the backend
 *                               answers 502); the next call from the parent succeeds
 *   e2e-stub:outline=slow       the first reply is delayed 2.5 s (a visible loading state)
 *
 * A bad reply carries `e2e_stub` (with how many more bad replies to give) so the repair call,
 * which has no student in it, can be recognised and answered from what it was shown.
 */

// Each set is three clearly different topics (the backend's distinctness gate checks this).
// A set is skipped when one of its topics was shown recently (the prompt lists them).
const SETS = [
  [
    { topic: 'Weather', title: 'Weather Watchers', hook: 'tracks the sky and predicts tomorrow.' },
    {
      topic: 'Sports reporting',
      title: 'Game Day Reporter',
      hook: 'reports live from the big game.',
    },
    {
      topic: 'Ocean animals',
      title: 'Deep Sea Animal Files',
      hook: 'dives down to meet sea creatures.',
    },
  ],
  [
    { topic: 'Space', title: 'Mission to Mars', hook: 'plans a trip to another planet.' },
    { topic: 'Baking', title: 'Bakery Boss', hook: 'runs a bakery and tests every recipe.' },
    { topic: 'Castles', title: 'Castle Under Siege', hook: 'defends a castle and its kingdom.' },
  ],
  [
    {
      topic: 'Detective cases',
      title: 'The Missing Map Case',
      hook: 'cracks a case by following clues.',
    },
    { topic: 'Music', title: 'Band Practice Week', hook: 'puts a band together for a show.' },
    { topic: 'Robots', title: 'Robot Workshop', hook: 'designs a robot and tests how it works.' },
  ],
  [
    {
      topic: 'Pirates',
      title: 'Pirate Treasure Hunt',
      hook: 'follows a treasure map to the prize.',
    },
    { topic: 'Farm life', title: 'Harvest Time Farm', hook: 'runs a farm from seed to harvest.' },
    { topic: 'Mountains', title: 'Summit Climb Diary', hook: 'plans a climb to the very top.' },
  ],
];
const FIRST_CALL_SCENARIOS = new Set(['repair', 'fail-once', 'slow', 'provider-error']);
const LETTERS = ['a', 'b', 'c'];

const callsPerStudent = new Map();

export const isOutlinePrompt = (prompt) => prompt.includes('SKILLS_JSON: ');
export const isStubRepair = (prompt) =>
  prompt.includes('You repair invalid JSON') && prompt.includes('e2e_stub');

function recentTopics(prompt) {
  const line = /Do not reuse these recent topics: (\[.*\])\./.exec(prompt)?.[1];
  try {
    return line ? JSON.parse(line).map((t) => String(t).toLowerCase()) : [];
  } catch {
    return [];
  }
}

function validReply(prompt, callNumber) {
  const name = /^First name: (.+)$/m.exec(prompt)?.[1]?.trim() ?? 'your child';
  const avoid = recentTopics(prompt);
  const clash = (set) => set.some((o) => avoid.some((a) => a.includes(o.topic.toLowerCase())));
  let set = SETS[callNumber % SETS.length];
  for (let k = 0; k < SETS.length; k++) {
    const candidate = SETS[(callNumber + k) % SETS.length];
    if (!clash(candidate)) {
      set = candidate;
      break;
    }
  }
  return JSON.stringify({
    options: LETTERS.map((letter, i) => ({
      option_id: letter,
      topic: set[i].topic,
      title: set[i].title,
      hook: `${name} ${set[i].hook}`,
      activities: `${set[i].title}: short hands-on tasks each day that keep ${name} busy and curious.`,
    })),
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
  if (active === 'provider-error') return { record, raw: '', delayMs: 0, httpStatus: 400 };
  if (active === 'fail-once') return { record, raw: badReply(prompt, 4), delayMs: 0 };
  return { record, raw: validReply(prompt, n), delayMs: active === 'slow' ? 2500 : 0 };
}
