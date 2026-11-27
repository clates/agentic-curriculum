# Why the login needs HTTPS and a proxy

The login is deliberately small: email addresses and passwords, and sign-up only with an invite.
It gives each family its own data and a small set of permissions. These choices hold it together.

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
existence isn't revealed either. The console reaches every family, so each look at another
family's data leaves a row in the audit log. Permissions are read on every request, so taking one
away takes effect at once rather than when a session ends.

## Why sign-up needs an invite

The app spends money on every family's behalf, on model calls. Open signup would let anyone run up
that bill. An invite makes the owner decide who comes in. Each code works once and expires, and
only a hash is stored, so a leaked database gives nobody a way in. The code uses letters that
can't be mistaken for each other, because people copy it by eye.

## Why the email is confirmed

Without it, anyone could register with someone else's address, and the app would later write to
that person. A 6-digit code sent to the address proves the registrant can read it. The code also
needs the password chosen at sign-up. Otherwise a stranger who registers a pending address again
could be handed the real owner's confirmation. Codes are short-lived and allow few tries because 6
digits are easy to guess otherwise.

## Why register and resend never reveal accounts

"That email is already registered" tells a stranger who uses the app. So the register and resend
answers are identical whatever the email, and a code goes out only when there is a pending account
to send it to. Every accepted registration also uses up its invite, so a stranger can't tell a
taken address from a new one by whether the invite survived. Register spends the same password
hashing on every path and the mail is sent after the reply, so timing reveals little.

Signing in is different: with the right password, it does show that an account is still pending,
because the person who knows the password is the one who needs to hear it.

The cost is a plain failure when the code never arrives. The sign-up screen offers a new code, and
the answer to that looks the same.

## Why admins' looks at other families are audited

An admin can open any family's child in the loop console, because someone has to fix stuck jobs.
That power reaches children's data, so it leaves a trail: each look at another family's child or
job is recorded by id and action, and never by content. The overview refreshes every few seconds,
so it is recorded once per admin per 10 minutes, or the log would fill with noise. Another
family's job errors show only the error type, since a message can quote what a child wrote.

Facts and commands: [Login reference](../reference/login.md#families),
[registration](../reference/login.md#registration).
