# Turn on the login

This guide shows you how to require a username and password on a deployed server. The login is
off by default.

Before you start, the site must already be served over HTTPS through a proxy that sets
`X-Forwarded-For` and `X-Forwarded-Proto`. A server built with
[Set up a new server](set-up-a-server.md) already is. For why this is required, see
[Why the login needs HTTPS and a proxy](../explanation/login-and-https.md).

## If you run your own proxy

Skip this section on a server built with [Set up a new server](set-up-a-server.md): its Caddy is
already configured. For a proxy you manage yourself, forward to the app with the visitor's real address, and keep the Host header unchanged:

```
your-domain.example {
    request_body {
        max_size 10MB
    }
    reverse_proxy 127.0.0.1:3000 {
        header_up X-Forwarded-For {remote_host}
        header_up X-Forwarded-Proto {scheme}
    }
}
```

If you use nginx, add `proxy_set_header Host $host;`, because nginx rewrites Host by default.

## Switch it on

On the server:

```bash
cd /srv/curriculum
$EDITOR .env
```

Add these lines, using your domain:

```
AUTH_REQUIRED=1
COOKIE_SECURE=1
AUTH_ALLOWED_HOSTS=your-domain.example   # several domains: separate them with commas
```

Recreate the containers so they read the new `.env` (a plain restart doesn't):

```bash
docker compose --env-file .deploy.env up -d --force-recreate
```

## Make the first account

> **Every account sees every child in the install.** There is no separation between families yet,
> so only make accounts for people you would show all of them to.

```bash
docker compose --env-file .deploy.env exec -u appuser app python -m auth create-user <username>
```

It asks for the password twice (at least 12 characters). Running it again for a name that
already exists does nothing.

To script it, export `AUTH_NEW_PASSWORD` first and pass it through:
`docker compose --env-file .deploy.env exec -u appuser -e AUTH_NEW_PASSWORD app python -m auth create-user <username>`.

## Check it

Open the site over HTTPS. You land on the sign-in page, and after signing in you land on **This
week**. A request without a session is refused:

```bash
curl -s -o /dev/null -w '%{http_code}\n' https://your-domain.example/api/students   # 401
```

## Turn it off

Delete the `AUTH_REQUIRED` line from `.env` and run the `up -d --force-recreate` line again.
Accounts and sessions are kept and work again when you turn it back on.

Next: [Manage accounts and lockouts](manage-accounts.md). All settings and limits:
[Login reference](../reference/login.md).
