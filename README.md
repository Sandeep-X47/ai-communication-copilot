# AI Communication Copilot — Full Stack

An AI communication assistant: rewrite messages, generate replies, draft emails,
write LinkedIn outreach, and craft dating-app openers — each with selectable tones
and personas. Built as a complete full-stack app with auth, a database, caching,
rate limiting, and an analytics dashboard.

> Runs with **zero external services**. No OpenAI key? A deterministic mock model
> drives every flow so the whole product is demoable offline. No Redis? Cache,
> rate limiting, and analytics fall back to in-memory automatically. Add a key
> and a `REDIS_URL` to go fully live — no code changes.

---

## Features (all live)

| Module        | Endpoint     | What it does                                            |
|---------------|--------------|---------------------------------------------------------|
| Tone Rewriter | `POST /rewrite`  | Rewrite text in 8 tones (professional → charismatic) |
| Reply         | `POST /reply`    | Turn an incoming message into a ready reply          |
| Email         | `POST /email`    | Draft a full email (subject + body) from a purpose   |
| LinkedIn      | `POST /linkedin` | Networking / referral outreach that gets replies     |
| Dating        | `POST /dating`   | Friendly, respectful openers and replies             |
| Personas      | (param)          | CEO, recruiter, professor, sales expert, founder     |
| History       | `GET/DELETE /history` | Every generation, saved and removable           |
| Analytics     | `GET /analytics` | Most-used tones, latency, cache hits, by-module      |

---

## Stack

| Layer    | Choice                                                            |
|----------|-------------------------------------------------------------------|
| Backend  | FastAPI, SQLAlchemy 2.0, Pydantic v2                              |
| Security | bcrypt password hashing, JWT bearer auth, per-user data scoping, input validation, security headers |
| Database | SQLite by default; one env var → Postgres                        |
| LLM      | OpenAI-compatible client + offline mock fallback                 |
| Cache / limits / analytics | Redis when `REDIS_URL` set; in-memory otherwise    |
| Workers  | Celery (optional, for batch/background jobs)                     |
| Frontend | React 18, Vite 6, React Router                                   |

---

## Run it

### Backend (terminal 1)
```bash
cd backend
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env               # optional — runs without it
uvicorn app.main:app --reload --port 8000
```
API at `http://localhost:8000`, interactive docs at `/docs`.

### Frontend (terminal 2)
```bash
cd frontend
npm install
cp .env.example .env               # optional
npm run dev
```
App at `http://localhost:5173`. Register, then use any module.

### Optional: real model, Redis, Celery
- Set `OPENAI_API_KEY` (any OpenAI-compatible endpoint via `OPENAI_BASE_URL`/`LLM_MODEL`).
- Set `REDIS_URL=redis://localhost:6379/0` to activate Redis cache + distributed rate limiting + analytics counters.
- Start a worker: `celery -A app.celery_app.celery worker --loglevel=info` (needs `REDIS_URL`).

---

## Security model

- **Passwords**: hashed with bcrypt, never stored or returned in plaintext.
- **Auth**: stateless JWT bearer tokens; protected routes resolve the user via the token (`get_current_user`).
- **Authorization**: history and analytics are filtered by the authenticated user's id — never a client-supplied id, so users can't read each other's data.
- **Input validation**: Pydantic schemas enforce types and length caps on every request body.
- **Rate limiting**: per-user daily cap (429 when exceeded).
- **Headers**: `X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy` on every response.
- **CORS**: restricted to configured origins.
- Change `JWT_SECRET` to a long random value in production.

---

## Project layout

```
ai-communication-copilot/
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

## Interview notes (be able to explain these)

- **One generation pipeline, five features.** Every module shares `_run()` in `routers/generate.py`: rate-limit → cache → generate → log history → record analytics. Adding a feature changes only its prompt builder.
- **Prompt-per-variant.** Tones, reply modes, dating modes, and personas are isolated dict entries in `prompts.py` — testable in isolation, no cross-contamination.
- **Redis-or-memory seam.** `cache.py` and `rate_limit.py` expose one function each; the backend swaps to Redis on `REDIS_URL` with no caller changes. This is the honest answer to "how does it scale?"
- **Offline mock.** `llm.generate()` hides whether a real model or the mock ran, so the app is demoable and CI-testable without a key or spend.
- **Security is real, not decorative** — see the Security model section above.

Don't claim usage metrics you don't have. Pitch the architecture and the security model; those are true and defensible.
