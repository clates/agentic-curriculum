# Manage accounts and lockouts

This guide shows you how to change passwords, lock and unlock accounts, and get back in after a
lockout. Run every command on the server from `/srv/curriculum`. The command line doesn't go
through the login, so these work even when nobody can sign in.

Each command below starts with this prefix:

```bash
docker compose --env-file .deploy.env exec -u appuser app
```

## Change a password

```bash
<prefix> python -m auth set-password <username>
```

This signs that user out everywhere and clears their lockouts.

## Lock someone out

```bash
<prefix> python -m auth disable <username>
```

This also signs them out. To let them back in, and clear their lockouts:

```bash
<prefix> python -m auth enable <username>
```

## Get back in after a lockout

To clear one user's lockouts:

```bash
<prefix> python -m auth unlock <username>
```

If that isn't enough, clear every lockout, including those on addresses:

```bash
<prefix> python -m auth unlock
```

## Add another account

```bash
<prefix> python -m auth create-user <username>
```

## Make someone an admin

```bash
<prefix> python -m auth grant <username> admin
```

Admins see an "Admin" link in the header, which opens the admin panel and the loop console. To
take it away:

```bash
<prefix> python -m auth revoke <username> admin
```

A revoke applies on the user's next request. What admin covers:
[Login reference](../reference/login.md#permissions).

To put a new account in an existing family, add `--family <id>` to `create-user`.

How lockouts are counted: [Login reference](../reference/login.md#lockouts).
