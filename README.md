# HRMS

![Django](https://img.shields.io/badge/Django-092E20?logo=django&logoColor=white)
![DRF](https://img.shields.io/badge/DRF-a30000?logo=django&logoColor=white)
![React](https://img.shields.io/badge/React-61DAFB?logo=react&logoColor=black)
![Docker](https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=white)
![License](https://img.shields.io/badge/license-unspecified-lightgrey)

An HR management system built as a modular Django/DRF backend with a React SPA frontend, per `docs/03-tech-stack.md`. See `CONTEXT.md` for domain vocabulary and `docs/` for the full requirements/architecture/schema/API/IAM documentation set.

## Prerequisites

- Docker and Docker Compose (this project has no local Python/Node runtime dependency for running the app — everything runs in containers)

## First run

```bash
cp .env.example .env   # fill in real values for anything marked "change-me"; placeholders are fine for local dev
docker compose up -d
docker compose run --rm django-migrate python manage.py migrate
```

The stack is served through a single origin via Caddy (ADR-0004/ADR-0009 — the SPA and API share one origin so session-cookie auth is exercised as deployed, not approximated by CORS):

| Service | URL |
|---|---|
| App (SPA + API, reverse-proxied) | http://localhost:8080 |
| Mailpit (catches outgoing email) | http://localhost:8025 |

MinIO and Postgres have no host port published by default — reach them from inside the Compose network only.

### Bootstrapping the first account

`System Administrator` is deliberately never Django's `is_superuser` (see `docs/07-iam-rbac.md` §7.3 — that flag would make HRMS-NFR-019 unenforceable), so there is no `createsuperuser` command. Assigned-role groups are seeded by a migration, but no user is. Create the first account and grant it a role via shell:

```bash
docker compose run --rm --entrypoint "" django-migrate python manage.py shell -c "
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
User = get_user_model()
u = User.objects.create_user(email='admin@example.com', password='change-me')
u.groups.add(Group.objects.get(name='System Administrator'))
"
```

## Rebuilding after code changes

There is no bind mount — the stack does not auto-reload on file changes. Rebuild the affected image(s) and restart:

```bash
# Backend code changed
docker compose build django django-migrate celery-worker
docker compose up -d django celery-worker

# Frontend code changed (the SPA is built into the caddy image, see caddy/Dockerfile)
docker compose build caddy
docker compose up -d caddy
```

`django` and `django-migrate` build separate images from the same context (no shared `image:` key) — rebuild both explicitly, not just one. `celery-worker` also builds its own image and needs an explicit rebuild; it doesn't share `django`'s.

## Running tests

**Backend** — the plain `django` service's Postgres role lacks `CREATEDB`, so tests must run through `django-migrate`'s role, with its entrypoint bypassed (otherwise it re-runs migrations first):

```bash
docker compose run --rm --entrypoint "" django-migrate python manage.py test
docker compose run --rm --entrypoint "" django-migrate python manage.py test <app_label>   # single app
```

`minio` and `minio-init` must be up first (document-storage tests need them; a Compose teardown between sessions can leave them down).

Never run two `manage.py test` invocations concurrently — a second run starting before the first has torn down its test database produces a `test_hrms already exists` / `does not exist` failure cascade that looks like real regressions but isn't. Wait for one to finish before starting another.

Full suite takes roughly 200s — longer than a typical foreground command timeout, so run it as a background job rather than assuming a fast return.

**Frontend** — from `frontend/`:

```bash
npm run lint                              # oxlint
npx tsc --noEmit -p tsconfig.app.json     # NOT bare `npx tsc --noEmit` — see below
npx vitest run
```

**Do not run bare `npx tsc --noEmit`** at the repo root or from `frontend/` without `-p`. The root `tsconfig.json` has `"files": []` and only builds through project references (`tsconfig.app.json`/`tsconfig.node.json`); plain `tsc --noEmit` doesn't follow references without `-b`, so it silently reports success having type-checked nothing. Always pass `-p tsconfig.app.json`.

A handful of frontend tests interact with antd `Select`/`Table`/`Tabs` components under jsdom; `getByRole` queries against those pages are dramatically slower than `getByText`/`queryByText` in this environment (roughly 6s vs <10ms per call) — prefer text queries in new tests unless the accessible role itself is what's under test.

## Troubleshooting

- **Docker commands hang with no output**: Docker Desktop can be in a "manually paused" state with no CLI-only way to resume — only the GUI Whale menu's resume works. Running containers stay up throughout the pause.
- **`docker compose` says a container "already exists" or similarly stale-looking**: check `docker compose ps` before assuming something is broken; a prior session's containers are often still running and just need `up -d` again, not a rebuild.

## Further reading

- `CONTEXT.md` — domain vocabulary, architecture summary, constraints, deployment conditions
- `docs/01-srs.md` through `docs/08-testing-plan.md` — the full requirements/planning/architecture/schema/API/IAM/testing documentation set, in dependency order
- `docs/adr/` — architecture decision records

## License

No license specified.
