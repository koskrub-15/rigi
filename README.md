# ⛰️ Rigi

[![CI](https://github.com/koskrub-15/rigi/actions/workflows/ci.yml/badge.svg)](https://github.com/koskrub-15/rigi/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/koskrub-15/rigi/branch/main/graph/badge.svg)](https://codecov.io/gh/koskrub-15/rigi)

**Pay-after-you-ride public transport tickets.** Scan the zone's QR code when you
get on and when you get off — at the end of the period Rigi looks at the trips you
actually made and charges you for the **cheapest combination** of single, day and
week tickets. No ticket machine, no guessing which pass pays off.

> Live app: **[rigi-web.fly.dev](https://rigi-web.fly.dev)** — open it on a phone and
> install it from the browser menu.
> Live API: **[rigi-api.fly.dev/docs](https://rigi-api.fly.dev/docs)** (Swagger UI).
> The machines sleep when idle, so the first request takes a few seconds.

---

## 🚀 How it works

```
 scan QR (check_in, zone A) ─┐
                             ├─► trip A → D, 3 zones ─┐
 scan QR (check_out, zone D)─┘                        ├─► optimizer ─► bill
                       ... every trip of the month ...┘
```

1. Every stop has a **signed zone code** printed as a QR. The phone camera reads it
   right in the browser.
2. A `check_in` and the following `check_out` become a **trip**; the number of
   zones travelled is the shortest path between the two zones.
3. `GET /bills/preview` runs the **optimizer** over any period; at the end of a
   month `POST /bills/{year}/{month}` closes it and stores the bill for good.
4. `POST /bills/{id}/payment` opens a **Stripe** payment page (test mode); Stripe's
   webhook marks the bill paid.

### ✨ Features

- **🧮 Ticket optimizer** — dynamic programming over the travel days picks the
  cheapest mix of single, day and week tickets.
- **🗺️ Zone graph** — zones form a graph; the zone count of a trip is the shortest
  path found with **BFS**.
- **🔏 Signed zone QR codes** — each code is a JWT `{"type": "zone", "zone": "C"}`.
  Forged codes, codes of another token type and unknown zones are rejected with `422`.
- **🧾 Closed bills** — a finished month is closed once and stored; a check-in
  without a check-out within 3 hours is billed as a trip to the farthest zone.
- **💳 Payments** — Stripe Checkout in test mode: the card is entered on Stripe's
  page, and only the signed webhook, never the redirect, marks a bill paid.
- **🔐 Authentication** — JWT access/refresh tokens with rotation and revocation,
  Argon2 password hashing; the user always comes from the token, never from the URL.
- **📊 Statistics** — trips per day, the amount paid and what the same trips would
  have cost as single tickets, drawn with Chart.js.
- **⚛️ React front** — login, registration, camera scanning, trips, bills and stats,
  styled with Tailwind CSS for a phone-width screen; forgotten check-outs are marked;
  the access token is refreshed silently on `401`.
- **📱 Installable PWA** — web app manifest and a service worker: Rigi installs to the
  home screen and opens without a network (network-first cache of the app itself;
  API data is never served stale).

### 💶 Tariffs

The tariffs are synthetic on purpose — the project is about the optimizer, not
about any real fare system.

| Ticket | Price      | Valid                       |
| ------ | ---------- | --------------------------- |
| Single | 3 per zone | one trip                    |
| Day    | 8          | all zones, one calendar day |
| Week   | 25         | all zones, seven days       |

Zones `A`–`F`:

```
A ─── B
│     │
C ─── D
│     │
E ─── F
```

---

## 🎬 API in action

A real run: two long trips on Monday, one short trip on Tuesday.

```bash
BASE=http://localhost:8000

# 1. Register and log in
curl -X POST $BASE/auth/register -H "Content-Type: application/json" \
  -d '{"email": "demo@rigi.dev", "first_name": "Demo", "last_name": "Rider", "password": "demo12345"}'

TOKEN=$(curl -s -X POST $BASE/auth/login \
  -d "username=demo@rigi.dev&password=demo12345" | jq -r .access_token)

# 2. Scan in and out — CODE_A / CODE_D come from the zone code script (see below)
curl -X POST $BASE/scans -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d "{\"scan_type\": \"check_in\", \"timestamp\": \"2026-11-02T08:00:00Z\", \"code\": \"$CODE_A\"}"
curl -X POST $BASE/scans -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d "{\"scan_type\": \"check_out\", \"timestamp\": \"2026-11-02T08:30:00Z\", \"code\": \"$CODE_D\"}"
# ... D → A in the evening, A → B on Tuesday ...

# 3. The bill for November
curl "$BASE/bills/preview?date_from=2026-11-01T00:00:00Z&date_to=2026-12-01T00:00:00Z" \
  -H "Authorization: Bearer $TOKEN"
```

Two 3-zone singles on Monday would cost 18, so Monday becomes a day ticket;
Tuesday's 2-zone trip stays a single:

```json
{
  "tickets": [
    { "type": "day_ticket", "valid_from": "2026-11-02T00:00:00", "price": 8 },
    { "type": "single_ticket", "valid_from": "2026-11-03T08:00:00", "price": 6 }
  ],
  "total": 14
}
```

| Endpoint                                                  | What it does                               |
| --------------------------------------------------------- | ------------------------------------------ |
| `POST /auth/register` · `/login` · `/refresh` · `/logout` | accounts and tokens                        |
| `POST /scans`                                             | check in or out with a zone code           |
| `GET /trips`                                              | trips of a period                          |
| `GET /bills/preview`                                      | optimal tickets and the total for a period |
| `POST /bills/{year}/{month}` · `GET /bills`               | close a finished month, list closed bills  |
| `POST /bills/{id}/payment`                                | Stripe payment page for a closed bill      |
| `POST /stripe/webhook`                                    | Stripe marks a bill paid                   |
| `GET /stats`                                              | trips per day and paid amount              |
| `GET /health`                                             | liveness check                             |

---

## 🛠️ Tech stack

**Backend:** FastAPI · async SQLAlchemy 2 · Pydantic v2 · Alembic · PostgreSQL ·
PyJWT · Argon2 · segno (QR codes) · Stripe

**Frontend:** React 19 · TypeScript · Vite · Tailwind CSS · React Router · Chart.js ·
`@yudiel/react-qr-scanner`

**Infrastructure:** Docker · nginx · Fly.io · Neon (serverless Postgres) ·
GitHub Actions · Codecov · uv

**Quality:** pytest · Vitest · ruff · mypy · prettier · pre-commit · pip-audit

### 🛡️ Supply chain

- Every GitHub Action is pinned to a **commit SHA**, not a tag — a tag can be moved
  to another commit.
- `web/.npmrc` sets `ignore-scripts=true`: npm install scripts are how npm worms
  run on a developer machine.
- Production secrets live only in `fly secrets`; the build context is a whitelist
  (`.dockerignore`).

---

## ⚡ Quick start

### 🐳 Docker (API + PostgreSQL)

```bash
cp .env.example .env                 # then set SECRET_KEY
cp compose.override.dev.yaml compose.override.yaml
docker compose up --build            # → http://localhost:8000/docs
```

or, with [just](https://github.com/casey/just): `just app-i-docker-i-run`
(`just app-i-docker-i-purge` wipes everything).

### 🐍 Without Docker

```bash
uv sync
export DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/rigi
export SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(32))")
uv run alembic upgrade head
uv run uvicorn apps.main:app --reload
```

### ⚛️ Front

```bash
cd web
npm ci
npm run dev                          # → http://localhost:5173
```

The service worker is registered only in production builds, so try the PWA with
`npm run build && npm run preview` (→ http://localhost:4173). The API allows only
`:5173` by default; add the preview origin in `.env`:
`CORS_ORIGINS=["http://localhost:5173","http://localhost:4173"]`.

### 🏷️ Zone codes

```bash
uv run python -m apps.scripts.zone_codes
```

Prints the signed code of every zone and saves one QR PNG per zone to `qr_codes/`.
Codes are signed with `SECRET_KEY`, so codes made with the dev key do not work in
production.

---

## 🧪 Development

```bash
just init-i-dev                      # venv, dependencies, pre-commit hooks
just test-i-run                      # pytest with coverage
cd web && npx vitest run             # front tests
```

CI runs on every pull request: tests with coverage, front build and tests,
pre-commit (ruff, mypy, prettier) and a dependency audit. A push to `main` deploys
both apps to Fly.io once the `DEPLOY_ENABLED` repository variable is on: the API
(migrations run as a release command before the new version goes live) and the
front (a multi-stage build — Vite in Node, then static files served by nginx). Each
app has its own deploy token.

---

## 🗺️ Roadmap

- [x] Optimizer, zones, statistics
- [x] Users and JWT authentication, Alembic migrations
- [x] React front with routing
- [x] Signed zone QR codes, scanning with the camera
- [x] API deployed on Fly.io with Neon Postgres, CI/CD
- [x] Front on Fly.io, scanning from a phone
- [x] Installable PWA that opens offline
- [x] Closing a billing period, test payments with Stripe
- [x] Styling with Tailwind CSS
- [ ] Zone-based day and week tickets, an all-zones ticket

### Known limitations

- A zone code never expires, so a photo of it works anywhere. Rotating codes or a
  location check would fix that.
- Offline, the app opens but shows no data: scans, trips and the bill need the API.
