# Dependencies and test isolation

## Why tests can never call a real model

Model calls cost money, are slow, and give a different answer each time. A test that makes one is
expensive, flaky and can leak a key. So the suites are built so a real call can't happen, rather
than relying on people to remember not to make one.

In pytest, every test gets a fake key and model address that point at a closed local port, and
sockets to anything but localhost are blocked. A separate test fails if `src/` gains a second model
client or a new module that talks to the network, because each one would be a new way around the
fakes. The end-to-end suite starts its own stub model server and forces the backend's settings
onto it, overriding whatever is in your shell.

The canned model replies are shared by both suites. A scenario written once, such as "the model
returns a broken Wednesday", is exercised by the fast unit tests and through the real browser.

## Why the E2E suite runs a production build

The end-to-end suite starts `next build` and `next start`, not the dev server, on its own ports
and against its own database. Dev mode hides problems that only show up once the app is built,
and a separate database means a test run can't damage your local data. Separate ports let several
checkouts run their suites at once.

## Why runtime and dev packages are split

The production image installs `requirements.txt` only. Test and lint tools live in
`requirements-dev.txt`. Every package in the image is something that can have a vulnerability,
and test tools have no reason to be on a server. CI fails if pytest ends up in the image, so the
split can't quietly erode.

## Why the audit runs every week, not only on pull requests

An advisory can be published for a package months after it was merged. An audit that only runs on
new pull requests would never see it. The Monday run catches those, and so does the run on every
pull request.

The Python audit installs the requirements into a clean environment and audits what they resolve
to that day. The requirements files hold version ranges, so auditing the ranges themselves would
miss what is actually installed.

## When to ignore an advisory

Sometimes an advisory has no fix yet, or doesn't apply to how this project uses the package. The
rule then is to ignore that one advisory id, with a comment saying why it isn't exploitable here
and a date to look again. Ignoring a whole package or severity level would hide the next,
real advisory along with this one.

## Why some tools are held back

The project tracks the newest Python and the newest Node LTS, so it stays in support for years.
ESLint and TypeScript are the exception. Next.js's lint configuration doesn't load under ESLint 10,
and typescript-eslint doesn't support TypeScript 6.1 or later. Upgrading either one would break
linting without making the app any safer. Both move once those packages catch up, and Dependabot
will propose it.

Facts and versions: [Development reference](../reference/development.md#runtime-and-dependencies).
