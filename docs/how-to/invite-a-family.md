# Invite a family

This guide shows you how to let a new family create an account. Sign-up needs an invite code, and
the family must be able to receive email. The server needs `SMTP_HOST` and the other mail settings
set, or no sign-in code is sent; see the [login reference](../reference/login.md#settings).

## Make a code in the admin panel

1. Sign in as an admin. Open "Admin" in the header.
2. In "Invite a family", press "Make an invite code".
3. Copy the code. It is shown once, and so is its expiry date.

## Or make one on the server

From `/srv/curriculum`:

```bash
docker compose --env-file .deploy.env exec -u appuser app python -m auth invite
```

For a different lifetime, add `--days 3`.

## Send it to the family

Give them the code and the sign-in page. They choose "Create an account" and enter a family name,
their email, a password twice and the code. A 6-digit code arrives by email; they enter it on the
"Check your email" step and are signed in.

## If something goes wrong

- **The email doesn't come.** Ask them to check spam, then press "Send a new code". It can be sent
  once a minute.
- **The code is rejected.** It may be used, expired or mistyped. Make a new one. Each code works
  once, even when the sign-up then stalls.
- **They closed the page before confirming.** They sign in with the email and password. That goes
  to the same code step.
- **They forgot the password.** Set a new one with
  `python -m auth set-password <email>`. See [Manage accounts](manage-accounts.md).

Code lifetimes, limits and routes: [Login reference](../reference/login.md#registration). Why it
works this way: [Why the login needs HTTPS and a proxy](../explanation/login-and-https.md).
