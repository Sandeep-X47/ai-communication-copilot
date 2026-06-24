# AI Communication Copilot

A full-stack AI communication assistant. Paste a message, pick a tone and a
persona, and get it back the way you meant it — across five modules: rewriting,
replies, email, LinkedIn outreach, and dating openers. Built with a FastAPI
backend and a React frontend, with authentication, a database, caching, rate
limiting, and an analytics dashboard.

> **Runs with zero external services.** No LLM key? A deterministic mock model
> drives every flow so the whole product is demoable offline. No Redis? Cache,
> rate limiting, and analytics fall back to in-memory automatically. Add a key
> (and optionally a `REDIS_URL`) to go fully live — no code changes.

---

## Table of contents

- [Features](#features)
- [Tech stack](#tech-stack)
- [Prerequisites](#prerequisites)
- [Quick start](#quick-start)
- [Connecting a real AI model (API key)](#connecting-a-real-ai-model-api-key)
- [Verifying live vs mock mode](#verifying-live-vs-mock-mode)
- [API reference](#api-reference)
- [Security model](#security-model)
- [Optional: Redis & Celery](#optional-redis--celery)
- [Project layout](#project-layout)
- [Troubleshooting](#troubleshooting)
- [License](#license)

---

## Features

| Module        | Endpoint          | What it does                                          |
|---------------|-------------------|-------------------------------------------------------|
| Tone Rewriter | `POST /rewrite`   | Rewrite text in 8 tones (professional → charismatic)  |
| Reply         | `POST /reply`     | Turn an incoming message into a ready-to-send reply   |
| Email         | `POST /email`     | Draft a full email (subject + body) from a one-liner  |
| LinkedIn      | `POST /linkedin`  | Networking / referral outreach that gets replies      |
| Dating        | `POST /dating`    | Friendly, respectful openers and replies              |
| Personal      | (request param)   | CEO, recruiter, professor, sales expert, founder      |
| History       | `GET/DELETE /history` | Every generation, saved and removable             |
| Analytics     | `GET /analytics`  | Most-used tones, latency, cache hits, by-module       |

---

## Tech stack

| Layer                       | Choice                                                                                  |
|-----------------------------|-----------------------------------------------------------------------------------------|
| Backend                     | FastAPI, SQLAlchemy 2.0, Pydantic v2                                                     |
| Security                    | bcrypt password hashing, JWT bearer auth, per-user data scoping, input validation, security headers |
| Database                    | SQLite by default; one env var → PostgreSQL                                              |
| LLM                         | OpenAI-compatible client (works with OpenAI, Groq, etc.) + offline mock fallback        |
| Cache / limits / analytics  | Redis when `REDIS_URL` is set; in-memory otherwise                                       |
| Workers                     | Celery (optional, for batch/background jobs)                                             |
| Frontend                    | React 18, Vite 6, React Router                                                           |

---

## Prerequisites

- **Python 3.10+**
- **Node.js 18+** and npm
- (Optional) A free **Groq** or paid **OpenAI** API key for real generation
- (Optional) **Redis** for distributed cache / rate limiting / analytics counters

---

## Quick start

The app needs two processes running at once: the backend (port 8000) and the
frontend (port 5173). Use two terminals.

### Backend

**Windows (PowerShell)** — run from the `backend` folder:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
uvicorn app.main:app --reload --env-file .env --port 8000
```

> If PowerShell blocks activation with *"running scripts is disabled on this
> system"*, run this once in the same window, then activate again:
> `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`

**macOS / Linux:**

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --env-file .env --port 8000
```

The API is now at `http://localhost:8000`. Interactive docs: `http://localhost:8000/docs`.

> **Note the `--env-file .env` flag.** The app reads real environment variables.
> Without this flag (or without exporting the variables manually), your `.env`
> file is ignored and the app stays in mock mode.

### Frontend

In a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`, register an account, and start generating.

---

## Connecting a real AI model (API key)

Out of the box the app runs an offline **mock** model that echoes your input
(prefixed with `[mock]`). To get real AI-generated output, point it at any
OpenAI-compatible endpoint by editing `backend/.env`.

### Option A — Groq (free, no credit card) — recommended

1. Sign up at [console.groq.com](https://console.groq.com) and create an API key (starts with `gsk_`).
2. Put these in `backend/.env`:

   ```env
   OPENAI_API_KEY=gsk_your_key_here
   OPENAI_BASE_URL=https://api.groq.com/openai/v1
   LLM_MODEL=llama-3.3-70b-versatile
   ```

3. Restart the backend (see note below). Done.

### Option B — OpenAI (paid)

1. Create a key at [platform.openai.com](https://platform.openai.com) (requires a funded account).
2. Put these in `backend/.env`:

   ```env
   OPENAI_API_KEY=sk-your_key_here
   OPENAI_BASE_URL=https://api.openai.com/v1
   LLM_MODEL=gpt-4o-mini
   ```

3. Restart the backend.

> **A restart is required** after changing `.env`. The app decides mock-vs-live
> at startup. The `--reload` flag only reloads on *code* changes, not env
> changes — stop the server (Ctrl+C) and start it again.

### Full `.env` reference

| Variable                      | Default                        | Purpose                                                        |
|-------------------------------|--------------------------------|----------------------------------------------------------------|
| `OPENAI_API_KEY`              | *(empty → mock mode)*          | API key for the LLM provider                                   |
| `OPENAI_BASE_URL`            | `https://api.openai.com/v1`    | Provider endpoint (swap to Groq, etc.)                         |
| `LLM_MODEL`                   | `gpt-4o-mini`                  | Model name                                                     |
| `JWT_SECRET`                  | `dev-secret-change-me`         | **Change in production** — signs auth tokens                   |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `10080` (7 days)               | JWT lifetime                                                   |
| `DATABASE_URL`                | `sqlite:///./copilot.db`       | Set to a Postgres URL for production                           |
| `REDIS_URL`                   | *(empty → in-memory)*          | Enables Redis cache, rate limit, analytics, Celery broker      |
| `RATE_LIMIT_PER_DAY`          | `100`                          | Per-user daily generation cap                                  |
| `CORS_ORIGINS`                | `http://localhost:5173`        | Comma-separated allowed frontend origins                       |

> **Never commit `.env`.** It is already in `.gitignore`. If you ever leak a
> key, rotate it immediately.

---

## Verifying live vs mock mode

With the backend running, open `http://localhost:8000/` in a browser, or run:

```powershell
# PowerShell (curl is an alias for Invoke-WebRequest, so use this instead)
Invoke-RestMethod http://localhost:8000/
```

```bash
# macOS / Linux
curl http://localhost:8000/
```

Look at the `llm_mode` field:

- `"live"` → a real model is connected. Generations will be real.
- `"mock"` → no key detected. Check that `.env` has your key and that you started
  the server with `--env-file .env`, then restart.

---

## API reference

| Method | Path             | Auth | Body                                            |
|--------|------------------|------|-------------------------------------------------|
| POST   | `/auth/register` | —    | `{ "email", "password" }`                       |
| POST   | `/auth/login`    | —    | form: `username` (email), `password`            |
| GET    | `/auth/me`       | ✓    | —                                               |
| GET    | `/options`       | —    | — (lists tones, reply modes, dating modes, personas) |
| POST   | `/rewrite`       | ✓    | `{ "text", "tone", "persona"? }`                |
| POST   | `/reply`         | ✓    | `{ "message", "mode", "persona"? }`             |
| POST   | `/email`         | ✓    | `{ "purpose", "tone", "persona"? }`             |
| POST   | `/linkedin`      | ✓    | `{ "intent", "persona"? }`                      |
| POST   | `/dating`        | ✓    | `{ "message", "mode" }`                          |
| GET    | `/history`       | ✓    | —                                               |
| DELETE | `/history/{id}`  | ✓    | —                                               |
| GET    | `/analytics`     | ✓    | —                                               |

Example (after registering and copying the returned `access_token`):

```bash
curl -X POST http://localhost:8000/rewrite \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"text":"send report by eod","tone":"professional","persona":"startup_founder"}'
```

---

## Security model

- **Passwords** are hashed with bcrypt — never stored or returned in plaintext.
- **Auth** uses stateless JWT bearer tokens; protected routes resolve the user
  from the token via `get_current_user`.
- **Authorization**: history and analytics are filtered by the authenticated
  user's id — never a client-supplied id — so users cannot read each other's data.
- **Input validation**: Pydantic schemas enforce types and length caps on every
  request body.
- **Rate limiting**: per-user daily cap (HTTP 429 when exceeded).
- **Security headers**: `X-Content-Type-Options`, `X-Frame-Options`, and
  `Referrer-Policy` on every response.
- **CORS** is restricted to the origins in `CORS_ORIGINS`.
- Change `JWT_SECRET` to a long random value in production.

---

## Optional: Redis & Celery

The app runs fully without these. They activate automatically when configured.

- **Redis** — set `REDIS_URL=redis://localhost:6379/0` in `.env` to enable the
  Redis-backed cache, distributed rate limiting, and analytics counters. With no
  `REDIS_URL`, in-memory equivalents are used.
- **Celery** — for batch/background jobs. Requires `REDIS_URL`. Start a worker:

  ```bash
  celery -A app.celery_app.celery worker --loglevel=info
  ```

---

## Project layout

```
ai-communication-copilot/
├── LICENSE
├── README.md
├── backend/
│   ├── app/
│   │   ├── main.py          # app wiring, CORS, security headers
│   │   ├── config.py        # env-driven settings
│   │   ├── database.py      # engine/session
│   │   ├── models.py        # users, history, analytics_events
│   │   ├── schemas.py       # request/response contracts
│   │   ├── auth.py          # bcrypt hashing + JWT
│   │   ├── deps.py          # get_current_user
│   │   ├── prompts.py       # tones, reply/dating modes, personas (the AI layer)
│   │   ├── llm.py           # generic generate() + offline mock
│   │   ├── cache.py         # Redis-or-memory cache
│   │   ├── rate_limit.py    # Redis-or-memory per-user daily limit
│   │   ├── analytics.py     # record + aggregate usage
│   │   ├── celery_app.py    # optional Celery app
│   │   ├── tasks.py         # example background task
│   │   └── routers/         # auth, generate (5 modules), history, analytics
│   ├── requirements.txt
│   └── .env.example
└── frontend/
    ├── src/
    │   ├── api.js            # API client
    │   ├── auth.jsx          # auth context (JWT in localStorage)
    │   ├── App.jsx           # routes + shell
    │   ├── components/Generator.jsx   # shared generator UI
    │   └── pages/            # Login, Home, Rewrite, Reply, Email, LinkedIn, Dating, History, Analytics
    ├── package.json
    └── .env.example
```

---

## Troubleshooting

**`source : The term 'source' is not recognized...`**
You're on Windows using Mac/Linux syntax. Use `.\.venv\Scripts\Activate.ps1` instead.

**`running scripts is disabled on this system`**
PowerShell is blocking the activation script. Run
`Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` once in that window,
then activate again.

**Output still shows `[mock]` / same text I typed**
The app isn't connected to a real model. Confirm `backend/.env` has your key,
that you started the server with `--env-file .env`, and **restart** the server.
Check `http://localhost:8000/` shows `"llm_mode":"live"`.

**`Invoke-RestMethod`/browser shows nothing for `curl`**
In PowerShell, `curl` is an alias for `Invoke-WebRequest`. Use
`Invoke-RestMethod http://localhost:8000/` or just open the URL in a browser.

**uvicorn runs from global Python, not the venv**
Your prompt must show `(.venv)` before running `pip install` or `uvicorn`.
If it doesn't, activation failed — re-activate first.

**Frontend can't reach the backend (CORS or network error)**
Make sure the backend is running on port 8000 and that `5173` is listed in
`CORS_ORIGINS`. The frontend's API base URL can be set via `frontend/.env`
(`VITE_API_URL`).

---

## License

MIT License

Copyright (c) 2026 Sandeep (Sandeep-X47)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
