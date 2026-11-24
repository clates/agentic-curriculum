# Server reference

Layout, deploy steps and GitHub secrets: [`deploy/README.md`](../../deploy/README.md). Tasks:
[Set up a new server](../how-to/set-up-a-server.md), [Read the access log](../how-to/read-the-access-log.md).

## Ports

| Port | Open to | Used by |
|---|---|---|
| 22 | your addresses only | SSH |
| 80, 443 | everyone | Caddy (HTTPS, certificate challenges) |
| 3000 | `127.0.0.1` only | the app, behind Caddy |

## Services

`deploy/docker-compose.yml`: `app`, `worker` and `caddy`. `app` and `worker` run the same image
as `appuser` on the same data volume. Requires Docker Compose 2.24.0 or newer.

## Access log

| Property | Value |
|---|---|
| File | `/data/access.log` in the `caddy` container (`caddy_data` volume, survives redeploys) |
| Format | one JSON object per request |
| Fields | time, `request.remote_ip`, method, path, status, size, duration |
| Removed | `Cookie`, `Authorization`, `Proxy-Authorization` request headers; `Set-Cookie` response header |
| Rotation | 20 MiB per file, 10 files, 30 days |
| Not included | SSH logins (host journal) and anything that never reached Caddy |

## Container logs

Every service: at most 3 files of 10 MB.

## Volumes

| Volume | Holds | Warning |
|---|---|---|
| `caddy_data` | certificates, ACME account, access log | `docker compose down -v` deletes it; re-issuing certificates hits Let's Encrypt rate limits |
| `data/` bind mount | `curriculum.db`, authoring run records | |
