# Documentation

These docs follow [Diátaxis](https://diataxis.fr/). Each page is exactly one of four kinds, and
each kind does one job:

| Kind | Read it when you want to… | Lives in |
|---|---|---|
| **Tutorial** | learn by doing, start to finish, with nothing to decide | [`tutorials/`](tutorials/) |
| **How-to guide** | get one specific thing done | [`how-to/`](how-to/) |
| **Reference** | look up a fact: a command, a field, a limit | [`reference/`](reference/) |
| **Explanation** | understand why something works the way it does | [`explanation/`](explanation/) |

## Tutorials

- [Your first week](tutorials/your-first-week.md): install, print a ready-made week, then have
  Claude Code write one for your student.

## How-to guides

Writing weeks:

- [Get a better week from `/generate-week`](how-to/write-a-better-week.md)
- [Track a student over time in the web app](how-to/track-a-student.md)
- [Fix common problems](how-to/fix-common-problems.md)

Running the hosted app:

- [Set up a new server with HTTPS](how-to/set-up-a-server.md)
- [Turn on the login](how-to/turn-on-login.md)
- [Manage accounts and lockouts](how-to/manage-accounts.md)
- [Invite a family](how-to/invite-a-family.md)
- [Add a child](how-to/add-a-child.md)
- [Print an old week](how-to/print-an-old-week.md)
- [Run the worker and turn the weekly loop on](how-to/run-the-worker.md)
- [Recover a dead job](how-to/recover-a-dead-job.md)
- [Read the access log](how-to/read-the-access-log.md)
- Deploy, roll back, rotate the CI key, move providers: [`deploy/README.md`](../deploy/README.md)

Changing the code: [`CONTRIBUTING.md`](../CONTRIBUTING.md).

## Reference

- [Included weeks and worksheet types](reference/included-weeks.md)
- [Development: commands, code map, API, settings](reference/development.md)
- [Children: adding a child, fields, limits, the child page, coverage](reference/children.md)
- [Login: sessions, registration, lockouts, commands](reference/login.md)
- [Worker and scheduler: commands, settings, job states, windows](reference/worker-and-scheduler.md)
- [Friday form API](reference/friday-form.md)
- [Hosted images](reference/hosted-images.md)
- [Worksheet types](reference/worksheet-types.md)
- [Worksheet request schema](reference/worksheet-request-schema.md)
- [Worksheet utilities](reference/worksheet-utilities.md)
- [Student data blobs](reference/data-schemas.md)
- [Single-request plan endpoint](reference/plan-generation-endpoint.md)
- HTTP API: [`api_reference.yaml`](../api_reference.yaml), also served at `/docs` by a running backend
- Worksheet internals for agents: [`AGENTS.md`](../AGENTS.md)

## Explanation

- [Why a week is a script](explanation/why-a-week-is-a-script.md)
- [The weekly loop](explanation/the-weekly-loop.md)
- [Why the login needs HTTPS and a proxy, and why invites](explanation/login-and-https.md)
- [Why hosted weeks are data](explanation/hosted-weeks-are-data.md)
- [Dependencies and test isolation](explanation/dependencies-and-test-isolation.md)
- [Worksheet pedagogy: what each type is good and bad at](explanation/worksheet-pedagogy.md)

## Not documentation

These are project records. They are kept for history and are not maintained.

- [`archive/`](archive/): old milestone and code-review reports, and a dated flow check
- [`superpowers/`](superpowers/): design specs and implementation plans
- [`user_stories/`](user_stories/): feature stories
- [`previews/`](previews/): rendered worksheet samples

## Writing a new page

Decide its kind first. Ask two questions: does it guide **action** or inform **understanding**? Is
it for **learning** or for **doing the work**? Then:

| | Learning | Doing the work |
|---|---|---|
| **Action** | tutorial | how-to guide |
| **Understanding** | explanation | reference |

Keep each page to its kind. When a how-to guide needs a reason, link to an explanation. When a
tutorial needs a list of options, link to reference. Don't add the material inline.
