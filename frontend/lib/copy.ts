/**
 * The parent-facing copy glossary. Every word a parent reads on the new screens lives here (or is
 * checked by `npm run lint:copy`), in plain language: no technical terms, no standard ids.
 *
 * Banned words are listed in `lib/bannedWords.ts`; the lint reads this file and every parent
 * screen, and a browser test also checks the text that actually renders.
 */
export const copy = {
  app: { name: 'CurricuLearn' },
  nav: {
    label: 'Main',
    thisWeek: 'This week',
    progress: 'How it’s going',
    children: 'Children',
  },
  states: {
    loadingLabel: 'Loading',
    loadingMessage: 'Just a moment…',
    errorTitle: 'We couldn’t load this',
    errorBody: 'Something went wrong on our side. Your information is safe. Please try again.',
    offlineBody: 'We can’t reach the server right now. Check your connection and try again.',
    retry: 'Try again',
  },
  thisWeek: {
    title: 'This week',
    intro: 'One next step for each child.',
    emptyTitle: 'No children yet',
    emptyBody: 'Add your first child and we will help you plan their week.',
    emptyAction: 'Add a child',
    attention: 'We\u2019re taking a closer look at this one. You don\u2019t need to do anything.',
    weekOf: 'Week of',
    actions: {
      check_in: {
        title: (name: string) => `How was ${name}\u2019s week?`,
        body: 'A quick check-in helps us plan what comes next.',
        button: 'Check in',
      },
      writing: {
        title: (name: string) => `Writing ${name}\u2019s next week`,
        body: 'This takes a few minutes. We\u2019ll let you know when it\u2019s ready.',
        button: null,
      },
      pick: {
        title: (name: string) => `Pick ${name}\u2019s next week`,
        body: 'Three ideas are ready for you.',
        button: 'See the ideas',
      },
      pickAgain: {
        title: (name: string) => `Pick ${name}\u2019s next week`,
        body: 'Those ideas ran out of time. We\u2019ll write fresh ones.',
        button: 'Get fresh ideas',
      },
      print: {
        title: (name: string) => `${name}\u2019s week is ready`,
        body: 'Print it and you\u2019re set for Monday.',
        button: 'Print it',
      },
      done: {
        title: (name: string) => `${name} is all set`,
        body: 'Nothing to do right now.',
        button: null,
      },
    },
  },
  checkIn: {
    title: (name: string) => `How was ${name}\u2019s week?`,
    back: 'Back to this week',
    overallQuestion: 'How did the week go overall?',
    overall: {
      smooth: { label: 'Got it', hint: 'Most things clicked' },
      mixed: { label: 'Shaky', hint: 'Some parts were tricky' },
      rough: { label: 'Lost it', hint: 'Most of it was a struggle' },
    },
    workloadQuestion: 'How much work was it?',
    workload: { tooLittle: 'Too little', justRight: 'Just right', tooMuch: 'Too much' },
    send: 'Send',
    sending: 'Sending\u2026',
    doneTitle: 'Thank you!',
    doneBody: (name: string) => `We\u2019ll start on ${name}\u2019s next week.`,
    sendErrorTitle: 'We couldn\u2019t send that',
    sendErrorBody: 'Nothing was lost. Please try again.',
    nothingTitle: 'Nothing to check in on yet',
    nothingBody: 'Once a week has been printed, you can tell us how it went.',
    unknownChild: 'We couldn\u2019t find that child',
  },
  byCheck: {
    useQuick: 'Use the quick rating instead',
    useChecks: 'Check each skill instead',
    progress: (n: number, total: number) => `Check ${n} of ${total}`,
    ask: 'What to ask or do',
    goodAnswer: 'A good answer sounds like',
    skip: 'Skip this one',
    back: 'Back',
    reviewTitle: 'Ready to send?',
    answered: (n: number, total: number) => `You answered ${n} of ${total} checks.`,
    answeredNone: 'You haven\u2019t answered any checks yet.',
    skippedNote: 'Skipped ones are fine. We only count what you answer.',
    needOne: 'Answer at least one check, or use the quick rating instead.',
    goBackAdd: 'Go back and answer more',
    loadingChecks: 'Loading the checks',
    noChecksTitle: 'No checks for this week',
    noChecksBody: 'This week doesn\u2019t have a check list. The quick rating works just as well.',
    result: { got_it: 'Got it', shaky: 'Shaky', missed: 'Missed' },
  },
  glossary: {
    gotIt: 'Got it',
    shaky: 'Shaky',
    lostIt: 'Lost it',
    missed: 'Missed',
  },
} as const;

export type Copy = typeof copy;
