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
  progress: {
    title: 'How it\u2019s going',
    intro: 'A plain look at what each child has down and what comes next.',
    pickChild: 'Choose a child',
    emptyTitle: 'No children yet',
    emptyBody: 'Add a child and their progress will show up here.',
    emptyAction: 'Add a child',
    nothingTitle: (name: string) => `Nothing to show for ${name} yet`,
    nothingBody: 'After your first Friday check-in, you will see how things are going here.',
    hasDown: (name: string) => `What ${name} has down`,
    hasDownEmpty: 'Nothing here yet. It fills in as skills click.',
    workingOn: 'What we are working on',
    workingOnEmpty: 'Nothing is being worked on right now.',
    comingUp: 'Coming up',
    comingUpEmpty: 'Nothing is due for a second look.',
    lastFour: 'The last four weeks',
    lastFourEmpty: 'No check-ins in the last four weeks.',
    checked: (n: number) => `${n} ${n === 1 ? 'skill' : 'skills'} checked`,
    wentWell: 'Went well',
    stillShaky: 'Still shaky',
    needsMore: 'Needs more practice',
    tagShaky: 'Still shaky',
    tagNeedsWork: 'Needs more practice',
  },
  glossary: {
    gotIt: 'Got it',
    shaky: 'Shaky',
    lostIt: 'Lost it',
    missed: 'Missed',
  },
} as const;

export type Copy = typeof copy;
