# AuditAI Dashboard (minimal)

Next.js App Router UI for **Cloud API** run history.

- Login with `AUDITAI_PROJECT_KEY` (sessionStorage only)
- Metric cards + pure-SVG sparklines
- Runs table + detail page (aggregates, top failures)
- Create stub project from the login screen (local dev)

## Prerequisites

1. Cloud API running on `:8080` (see `../api/README.md`)
2. Node 20+

## Run

```bash
cd cloud/dashboard
cp .env.example .env.local
npm install
npm run dev
# → http://127.0.0.1:3000
```

`.env.local`:

```
NEXT_PUBLIC_AUDITAI_API_URL=http://127.0.0.1:8080
```

## Flow

1. Open dashboard → **Create** project (or paste existing key)
2. Copy key → export as `AUDITAI_PROJECT_KEY` for CLI
3. `auditai run …` pushes metrics
4. **Refresh** dashboard to see history + sparklines

## Stack

- Next.js 15 / React 19 / TypeScript
- Tailwind CSS
- No chart library (SVG sparklines)
- Browser → Cloud API (CORS already open on API stub)

## Not included (later)

- Multi-user login / teams
- Billing
- PDF compliance export
- Dark/light toggle (dark-only for now)
