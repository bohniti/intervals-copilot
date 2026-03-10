# Climbers Journal

Log rock climbs, alpine objectives, hikes, trail runs, and bouldering sessions via a chat interface powered by Kimi K2.5.

## Stack

| Layer | Tech |
|---|---|
| Backend | FastAPI + SQLModel + PostgreSQL |
| LLM | Kimi K2.5 via Nvidia NIM |
| CLI | Python + Typer |
| Frontend | Next.js 15 + TypeScript + Tailwind |
| Dev env | Docker Compose |
| CI/CD | GitHub Actions → Hostinger VPS |

## Quick Start

### 1. Configure environment

```bash
cp .env.example .env
# Edit .env — set NVIDIA_API_KEY at minimum
```

### 2. Start local stack

```bash
docker compose up -d
```

- Backend: http://localhost:8000
- Frontend: http://localhost:3000
- API docs: http://localhost:8000/docs

### 3. Run database migrations

```bash
docker compose exec backend alembic upgrade head
```

### 4. Use the CLI

```bash
cd cli
uv sync
uv run journal add       # chat to log a climb
uv run journal list      # see recent activities
uv run journal show 1    # detail view
```

Or install globally:

```bash
cd cli && uv tool install .
journal add
```

## Development

### Backend

```bash
cd backend
uv sync --dev
uv run uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
pnpm install
pnpm dev
```

### Generate a new migration

```bash
cd backend
uv run alembic revision --autogenerate -m "description"
uv run alembic upgrade head
```

## Production Deployment (Hostinger VPS)

### One-time VPS setup

```bash
# On the VPS:
git clone https://github.com/your-username/climbers-journal.git /opt/climbers-journal
cp /opt/climbers-journal/.env.example /opt/climbers-journal/.env
# Edit .env with production values
```

### GitHub Secrets required

| Secret | Description |
|---|---|
| `VPS_HOST` | VPS IP or hostname |
| `VPS_USER` | SSH username |
| `VPS_SSH_KEY` | Private SSH key |

Push to `main` → tests run → images built → deployed automatically.

## Activity Types

- `sport_climb` — bolt-protected sport routes
- `trad_climb` — trad / gear routes
- `alpine` — mountaineering / alpine objectives
- `hike` — hiking
- `trail_run` — trail running
- `boulder` — bouldering problems
