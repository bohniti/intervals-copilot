# Intervals.icu Copilot

A local-first AI copilot for [intervals.icu](https://intervals.icu). Chat with your training data — ask questions about your workouts, performance trends, and training load, and the LLM fetches the data from intervals.icu and responds conversationally.

Use this as a starting point to build your own training tool on top of intervals.icu.

## Prerequisites

- Python 3.12+ with [uv](https://docs.astral.sh/uv/)
- Node.js 22+ with [pnpm](https://pnpm.io/)
- An [intervals.icu](https://intervals.icu) account with an API key
- At least one LLM provider API key (Nvidia NIM for Kimi K2.5, or Google AI for Gemini)

## Setup

```bash
# Clone and configure
cp .env.example .env
# Edit .env with your API keys

# Install backend dependencies
cd app/backend
uv sync

# Install frontend dependencies
cd ../frontend
pnpm install
```

## Running

Start both services in separate terminals:

```bash
# Terminal 1 — Backend (port 8000)
cd app/backend
uv run fastapi dev climbers_journal/main.py

# Terminal 2 — Frontend (port 3000)
cd app/frontend
pnpm dev
```

Open [http://localhost:3000](http://localhost:3000) and start chatting.

## Claude Code (gstack)

This project includes [gstack](https://github.com/garrytan/gstack) skills for Claude Code. After cloning, run the one-time setup:

```bash
cd .claude/skills/gstack && ./setup
```

Requires [bun](https://bun.sh/). This gives you these slash commands in Claude Code:

| Command | Description |
|---|---|
| `/browse` | Headless browser for QA testing and dogfooding |
| `/qa` | Systematic QA testing with structured reports |
| `/review` | Pre-landing PR review (diff analysis) |
| `/ship` | Ship workflow (tests, review, version bump, PR) |
| `/plan-eng-review` | Engineering plan review |
| `/plan-ceo-review` | CEO/founder-mode plan review |
| `/setup-browser-cookies` | Import browser cookies for authenticated testing |
| `/retro` | Weekly engineering retrospective |

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `NVIDIA_API_KEY` | One of these | Kimi K2.5 via Nvidia NIM |
| `GOOGLE_API_KEY` | One of these | Gemini via Google AI |
| `DEFAULT_LLM_PROVIDER` | No | `kimi` or `gemini` (default: `kimi`) |
| `INTERVALS_API_KEY` | Yes | intervals.icu API key |
| `INTERVALS_ATHLETE_ID` | Yes | intervals.icu athlete ID (e.g. `i12345`) |
| `CORS_ORIGINS` | No | JSON array (default: `["http://localhost:3000"]`) |
