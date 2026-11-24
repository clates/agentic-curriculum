# Read the access log

This guide shows you how to answer "who asked the server for what" from Caddy's access log. On
the server:

```bash
cd /srv/curriculum
C="docker compose --env-file .deploy.env exec -T caddy"
```

## The latest requests

```bash
$C tail -n 20 /data/access.log
```

## The mix of status codes

```bash
$C sh -c 'grep -o "\"status\":[0-9]*" /data/access.log | sort | uniq -c | sort -rn'
```

## The busiest visitors

```bash
$C sh -c 'grep -o "\"remote_ip\":\"[^\"]*\"" /data/access.log | sort | uniq -c | sort -rn | head'
```

## Scanners probing for secrets

```bash
$C sh -c 'grep -E "\.env|\.git/|wp-login|phpmyadmin|id_rsa|actuator" /data/access.log | tail'
```

## Failed sign-ins

```bash
$C sh -c 'grep "/api/auth/login" /data/access.log | grep -v "\"status\":200" | tail'
```

## Read it on your own computer

```bash
docker compose --env-file .deploy.env cp caddy:/data/access.log .
```

Then copy it down with `scp`.

## SSH logins

These aren't in the access log. Read the host journal instead:

```bash
journalctl -u ssh --since today
```

Fields, retention and what is left out: [Server reference](../reference/server.md#access-log).
