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
  },
  glossary: {
    gotIt: 'Got it',
    shaky: 'Shaky',
    lostIt: 'Lost it',
    missed: 'Missed',
  },
} as const;

export type Copy = typeof copy;
