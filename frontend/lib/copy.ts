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
  glossary: {
    gotIt: 'Got it',
    shaky: 'Shaky',
    lostIt: 'Lost it',
    missed: 'Missed',
  },
} as const;

export type Copy = typeof copy;
