/**
 * The parent-facing copy glossary. Every word a parent reads on the new screens lives here (or is
 * checked by `npm run lint:copy`), in plain language: no technical terms, no standard ids.
 *
 * Banned words are listed in `lib/bannedWords.ts`; the lint reads this file and every parent
 * screen, and a browser test also checks the text that actually renders.
 */
export const copy = {
  // The product name, in one place: change it here and every screen and page title follows.
  app: { name: 'CurricuLearn' },
  nav: {
    label: 'Main',
    thisWeek: 'This week',
    progress: 'How it’s going',
    children: 'Children',
  },
  login: {
    title: 'Welcome back',
    intro: 'Sign in to see your week.',
    username: 'Username',
    password: 'Password',
    show: 'Show',
    hide: 'Hide',
    showLabel: 'Show password',
    hideLabel: 'Hide password',
    submit: 'Sign in',
    submitting: 'Signing in\u2026',
    wrong: 'That didn\u2019t match. Try again.',
    wait: (seconds: number) =>
      `Too many tries. Please wait ${seconds} ${seconds === 1 ? 'second' : 'seconds'}.`,
    couldNotReach:
      'We couldn\u2019t sign you in just now. Your information is safe. Please try again.',
    busy: 'Busy right now. Please try again in a moment.',
    retry: 'Try again',
    signOut: 'Sign out',
    signingOut: 'Signing out\u2026',
  },
  admin: {
    link: 'Admin',
    title: 'Admin',
    loopTitle: 'Loop console',
    loopBody: 'Drive your family\u2019s children through each step of the loop.',
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
  pick: {
    title: (name: string) => `Pick ${name}\u2019s next week`,
    back: 'Back to this week',
    question: (name: string) => `Which idea fits ${name}\u2019s next week?`,
    sameSkills: 'Every idea covers the same skills. Pick the topic they will enjoy.',
    willDo: 'What they\u2019ll do',
    covers: 'What it covers',
    useThis: 'Use this one',
    confirmTitle: (idea: string) => `Use \u201c${idea}\u201d?`,
    confirmBody: (name: string) =>
      `We\u2019ll start writing ${name}\u2019s week right away. Once we start, it can\u2019t be changed.`,
    confirmYes: 'Yes, use this one',
    confirmBack: 'Back to the ideas',
    choosing: 'Choosing\u2026',
    chooseErrorTitle: 'We couldn\u2019t save your choice',
    chooseErrorBody: 'Nothing was lost. Please try again.',
    fresh: 'Show me different ideas',
    freshLeft: (n: number) =>
      n === 1
        ? 'One more set available'
        : n === 2
          ? 'Two more sets available'
          : `${n} more sets available`,
    freshUsedUp: 'You\u2019ve used this week\u2019s fresh ideas.',
    expiredBody: 'Those ideas ran out of time. We can write fresh ones.',
    getFresh: 'Get fresh ideas',
    writingFresh: 'Writing fresh ideas\u2026',
    writingFreshBody: 'This can take a minute or two. Please keep this page open.',
    freshErrorTitle: 'We couldn\u2019t write new ideas',
    freshErrorBody: 'Nothing was lost. Please try again.',
    limitTitle: 'That\u2019s all the fresh ideas for this week',
    limitBody: 'We\u2019ll have new ones after your next check-in.',
    alreadyTitle: (name: string) => `${name}\u2019s next week is on its way`,
    alreadyBody: (idea: string | null) =>
      idea
        ? `You chose \u201c${idea}\u201d. We\u2019re writing it now.`
        : 'You already chose. We\u2019re writing it now.',
    writingTitle: 'We\u2019re writing the ideas',
    writingBody: 'This can take a few minutes. This page updates when they\u2019re ready.',
    notYetTitle: 'Not ready to pick yet',
    notYetBody: 'Check in on last week first. The ideas come right after.',
    checkIn: 'Check in',
    unknownChild: 'We couldn\u2019t find that child',
  },
  print: {
    back: 'Back to this week',
    title: (name: string) => `Print ${name}\u2019s week`,
    intro: (name: string) =>
      `Print all three, in this order: ${name}\u2019s pages, then your guide, then your prep sheet. Double-sided works well.`,
    introLegacy: (name: string) => `Print ${name}\u2019s pages. Double-sided works well.`,
    covers: (range: string) => `Covers ${range}`,
    printBy: (day: string) => `Print by ${day}`,
    deadlinePassed: (day: string) =>
      `The print-by day (${day}) has passed. You can still print it now.`,
    documentsLabel: 'Documents to print',
    openToPrint: 'Open to print',
    newTab: '(opens in a new tab)',
    docs: {
      packet: {
        title: (name: string) => `${name}\u2019s pages`,
        body: 'The worksheets for each day, Monday to Friday. These go to your child.',
      },
      guide: {
        title: 'Your teacher guide',
        body: 'The answers and what to say each day. Keep this one for yourself.',
      },
      prep: {
        title: 'Your prep sheet',
        body: 'What to gather before Monday and a few quick checks to do with your child.',
      },
    },
    legacyNote: 'This older week only has your child\u2019s pages.',
    confirm: 'I\u2019ve printed it',
    confirming: 'Saving\u2026',
    confirmHint: 'Tap this once everything is printed, so we know you\u2019re set.',
    confirmErrorTitle: 'We couldn\u2019t save that',
    confirmErrorBody: 'Nothing was lost. Please try again.',
    doneTitle: 'You\u2019re all set',
    doneBody: (name: string) => `${name}\u2019s week is printed and ready for Monday.`,
    alreadyTitle: 'This week is already printed',
    alreadyBody: 'You can open the documents again if you need another copy.',
    loadingDocs: 'Loading the documents',
    docsErrorTitle: 'We couldn\u2019t load the documents',
    notReadyTitle: 'Nothing to print yet',
    notReady: {
      check_in: (name: string) =>
        `Check in on ${name}\u2019s last week first, and we\u2019ll start the next one.`,
      writing: (name: string) =>
        `We\u2019re still writing ${name}\u2019s week. We\u2019ll let you know when it\u2019s ready.`,
      pick: (name: string) => `Pick ${name}\u2019s next week first, and then it can be printed.`,
    },
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
