# HRMS

![Django](https://img.shields.io/badge/Django-092E20?logo=django&logoColor=white)
![DRF](https://img.shields.io/badge/DRF-a30000?logo=django&logoColor=white)
![React](https://img.shields.io/badge/React-61DAFB?logo=react&logoColor=black)
![Docker](https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=white)
![License](https://img.shields.io/badge/license-unspecified-lightgrey)

An HR management system built as a modular Django/DRF backend with a React SPA frontend. See `CONTEXT.md` for domain vocabulary and `docs/` for the full requirements/architecture/schema/API/IAM documentation set.

## Features

- Role-based access control with a dedicated System Administrator role (not Django's `is_superuser`)
- Single-origin deployment (SPA + API behind Caddy) so session-cookie auth matches production
- Document storage backed by MinIO
- Background email delivery captured locally via Mailpit in development
- Full requirements/architecture/schema/API/IAM documentation set under `docs/`

## Tech Stack

- Django + Django REST Framework
- React (SPA)
- PostgreSQL
- Celery
- MinIO
- Caddy
- Docker Compose

## Installation

```bash
git clone https://github.com/johnnnys3/hr-management-system.git
cd hr-management-system
cp .env.example .env   # fill in real values for anything marked "change-me"
docker compose up -d
docker compose run --rm django-migrate python manage.py migrate
```

## Usage

The stack is served through a single origin via Caddy:

| Service | URL |
|---|---|
| App (SPA + API, reverse-proxied) | http://localhost:8080 |
| Mailpit (catches outgoing email) | http://localhost:8025 |

Create the first account and grant it a role via shell (there is no `createsuperuser` command):

```bash
docker compose run --rm --entrypoint "" django-migrate python manage.py shell -c "
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
User = get_user_model()
u = User.objects.create_user(email='admin@example.com', password='change-me')
u.groups.add(Group.objects.get(name='System Administrator'))
"
```

Rebuild after code changes (no bind mount / auto-reload):

```bash
docker compose build django django-migrate celery-worker
docker compose up -d django celery-worker
docker compose build caddy
docker compose up -d caddy
```

Run tests:

```bash
docker compose run --rm --entrypoint "" django-migrate python manage.py test
cd frontend && npm run lint && npx tsc --noEmit -p tsconfig.app.json && npx vitest run
```

## Project Structure

```text
.
├── docs/              # Requirements, architecture, schema, API, IAM, testing docs
├── docs/adr/          # Architecture decision records
├── frontend/          # React SPA
├── caddy/             # Reverse proxy config/Dockerfile
├── CONTEXT.md         # Domain vocabulary and architecture summary
└── README.md
```

## Contributing

Contributions are welcome. Fork the repository, create a feature branch, and open a pull request describing your changes.

## License

No license specified.
