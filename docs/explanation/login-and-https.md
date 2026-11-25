# Why the login needs HTTPS and a proxy

The login is deliberately small: usernames and passwords, accounts made from the command line, no
signup page. It gives each family its own data and a small set of permissions. These choices hold it
together.

## HTTPS before anything else

A password sent over plain `http://` can be read by anyone between the browser and the server. So
the login is never exposed without TLS in front. The app itself listens only on `127.0.0.1:3000`,
and something else on the machine terminates HTTPS: the Caddy container in the deploy, or
Tailscale for a private setup.

## Why the proxy has to write the visitor's address

Lockouts count wrong guesses per visitor address. Behind a proxy the app never sees that address
directly, only the `X-Forwarded-For` header the proxy adds. Anyone can send that header, so the
app trusts only the entry the proxy itself wrote, the rightmost one. Exposed with no proxy in
front, the app would let a guesser claim a new address on every request and never be locked out.

## Why the host is checked

A sign-in or change request carries the browser's `Origin`, and the app compares it with the
host it was asked for. That stops another website from submitting a form to this one on a
signed-in parent's behalf. It only works if the proxy passes `Host` through unchanged, which is
why nginx needs a line that Caddy doesn't. Setting `AUTH_ALLOWED_HOSTS` pins the list outright, so
the check stops depending on proxy behaviour at all. A cross-site page can't set a custom header
such as `X-Forwarded-Host` without a preflight the server refuses, so pinning is defence in depth
rather than a fix for a known hole.

## Why lockouts are per address and username

Locking a username outright would let any stranger keep its owner locked out by guessing badly.
Locking a whole address would let one guesser lock out everyone who shares that network. Pairing
the two limits the damage: a stranger can only lock the pair they're guessing at, from where they
are. Addresses that signed in recently are trusted more, so a parent at home isn't held up by
noise from elsewhere.

The gap left is someone on your own network, such as a shared home or office connection, who
guesses your username. They can lock that pair. The 30-day session means you rarely type the
password anyway, and an unlock from the server clears it.

## Why password checks are rationed

scrypt is slow on purpose, so a burst of sign-ins could tie up the machine. Only two run at once,
and a few more may queue briefly. A sign-in turned away for being busy counts against nobody, so
the limit can't be used to lock people out.

## How families are kept apart

Every request acts for the signed-in user's family, and every route that touches a child, packet,
week, plan or job checks that the record belongs to that family. The check lives in the route, next to the
data it guards, rather than in one gate at the door that has to guess which ids belong to whom.

A record in another family answers 404 with the same body as a record that doesn't exist. A 403
would tell a stranger that the id is real. With 404 they learn nothing, so guessing ids gets them
nowhere. New child ids are random for the same reason: they can't be counted up from one to the
next.

With login off there is one family, `fam_local`, and nothing changes for a self-hoster.

Admin powers follow the same rule. A non-admin gets 404 from the admin routes, so the console's
existence isn't revealed either, and the console acts only on the admin's own family. Permissions
are read on every request, so taking one away takes effect at once rather than when a session
ends.

Facts and commands: [Login reference](../reference/login.md#families).
