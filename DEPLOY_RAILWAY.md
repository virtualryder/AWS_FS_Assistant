# Railway Deployment Guide

Complete step-by-step instructions for deploying the AWS Financial Services Assistant to Railway.

---

## What Gets Deployed

Three Railway resources inside **one project**:

```
Railway Project: aws-finserv-assistant
│
├── PostgreSQL plugin          ← database + pgvector KB
│     └── auto-injects DATABASE_URL into the API service
│
├── Service: API               ← FastAPI backend (Dockerfile.api, repo root)
│     Runs: uvicorn + dual AI agents + SSE streaming
│     Port: $PORT (Railway assigns, health check at /health)
│     Needs: ANTHROPIC_API_KEY · TAVILY_API_KEY · DATABASE_URL (auto)
│
└── Service: Frontend          ← Next.js 14 (frontend/ subdirectory)
      Runs: npm run build → npm run start
      Port: $PORT (Railway assigns)
      Needs: NEXT_PUBLIC_API_URL → points at the API service URL above
```

**Deployment order matters:**
1. PostgreSQL → 2. API service → 3. Frontend service → 4. Update CORS → done

---

## Pre-Flight Checklist

Before starting, have these ready:

| Item | Where to get it |
|------|----------------|
| `ANTHROPIC_API_KEY` | [console.anthropic.com](https://console.anthropic.com) → Settings → API Keys |
| `TAVILY_API_KEY` | [app.tavily.com](https://app.tavily.com) → dashboard (free tier: 1,000/month) |
| GitHub access | Repo must be at github.com/virtualryder/AWS_FS_Assistant |
| Railway account | [railway.app](https://railway.app) — sign up, verify email |

---

## Step 1 — Create the Railway Project

1. Go to [railway.app](https://railway.app) → Dashboard
2. Click **New Project**
3. Select **Empty Project**
4. Name it something like `aws-finserv-assistant`

---

## Step 2 — Add PostgreSQL

> This must come first — the API service needs `DATABASE_URL` at startup.

1. Inside your project, click **+ New**
2. Select **Database** → **Add PostgreSQL**
3. Railway provisions a PostgreSQL 16 instance and creates a `DATABASE_URL` variable
4. Wait ~30 seconds for the database to be ready (green status dot)

**Enable pgvector:**

Railway's UI does not have a reliable Query tab — use one of these methods instead:

**Option A — Railway CLI (easiest, no extra tools needed):**
```bash
# Install Railway CLI if you don't have it
npm install -g @railway/cli

# Log in and link to your project
railway login
railway link   # select your project when prompted

# Open a psql shell directly into the Railway PostgreSQL instance
railway connect PostgreSQL
```
Once the `psql` prompt appears, run:
```sql
CREATE EXTENSION IF NOT EXISTS vector;
\q
```

**Option B — psql with the connection string:**
1. Click the PostgreSQL service tile → **Variables** tab
2. Copy the `DATABASE_URL` value (looks like `postgresql://postgres:xxxx@xxxx.railway.app:5432/railway`)
3. In your local terminal (requires psql installed):
   ```bash
   psql "postgresql://postgres:xxxx@xxxx.railway.app:5432/railway"
   ```
4. Run:
   ```sql
   CREATE EXTENSION IF NOT EXISTS vector;
   \q
   ```

**Option C — TablePlus / DBeaver (if you prefer a GUI):**
1. Copy `DATABASE_URL` from the PostgreSQL Variables tab
2. Open TablePlus or DBeaver → New Connection → PostgreSQL → paste the URL
3. Run: `CREATE EXTENSION IF NOT EXISTS vector;`

> You can verify it worked by running: `SELECT extversion FROM pg_extension WHERE extname = 'vector';`
> You should see a version number like `0.7.0`.

---

## Step 3 — Deploy the API Service

### 3a — Connect the GitHub repo

1. In your project, click **+ New**
2. Select **GitHub Repo**
3. If prompted, authorize Railway to access your GitHub
4. Select **virtualryder/AWS_FS_Assistant**
5. Leave **Root Directory** empty (deploy from repo root)
6. Click **Deploy Now**

Railway will detect `railway.toml` at the repo root and use `Dockerfile.api` to build.

### 3b — Set environment variables

The first deploy will fail until you set the API keys. That's expected.

1. Click on the API service tile → **Variables** tab
2. Add these variables one at a time using **+ New Variable**:

   | Variable | Value |
   |----------|-------|
   | `ANTHROPIC_API_KEY` | `sk-ant-api03-...` (your key) |
   | `TAVILY_API_KEY` | `tvly-...` (your key) |

3. **Link DATABASE_URL from PostgreSQL:**
   - Still in Variables tab, click **+ New Variable**
   - In the variable name field type `DATABASE_URL`
   - Click **Add Reference** (the icon next to the value field)
   - Select your **PostgreSQL** service → select `DATABASE_URL`
   - This auto-injects the correct connection string and keeps it in sync

> **Do not type DATABASE_URL manually.** Using the reference keeps it updated if Railway rotates credentials.

### 3c — Trigger a redeploy

1. Go to the **Deployments** tab
2. Click **Redeploy** on the failed deployment (or it may auto-redeploy after you added variables)
3. Watch the deploy log — you should see:
   ```
   INFO:     Started server process
   INFO:     Waiting for application startup.
   INFO:     Application startup complete.
   INFO:     Uvicorn running on http://0.0.0.0:XXXX
   ```
   Plus background output from `startup_ingest.py` starting the knowledge base index.

### 3d — Generate the API public URL

1. API service → **Settings** tab
2. Under **Networking** → click **Generate Domain**
3. Note your API URL, e.g.: `https://aws-finserv-api-production.up.railway.app`

### 3e — Verify the API is running

Open in your browser:
```
https://your-api-url.up.railway.app/health
```
Expected response:
```json
{"status": "ok", "sessions": 0}
```

If you get a 502 or timeout, check the **Logs** tab — the most common causes are:
- Missing `ANTHROPIC_API_KEY` → `ValueError: ANTHROPIC_API_KEY is not set`
- pgvector not enabled → `UndefinedFile: could not open extension control file`
- DATABASE_URL not linked → `ValueError: DATABASE_URL is not set`

---

## Step 4 — Deploy the Frontend Service

### 4a — Connect the same repo, different subdirectory

1. In your project, click **+ New**
2. Select **GitHub Repo** → same repo (`virtualryder/AWS_FS_Assistant`)
3. **Important:** Under **Root Directory**, type `frontend`
4. Click **Deploy Now**

Railway will detect Next.js via Nixpacks, run `npm install && npm run build`, then `npm run start`.

### 4b — Set the API URL variable

The frontend needs to know where to send API calls.

1. Frontend service → **Variables** tab
2. Add:

   | Variable | Value |
   |----------|-------|
   | `NEXT_PUBLIC_API_URL` | `https://your-api-url.up.railway.app` |

   (Use the exact URL from Step 3d — no trailing slash)

3. Railway will redeploy automatically after you add the variable

### 4c — Generate the frontend public URL

1. Frontend service → **Settings** tab
2. Under **Networking** → **Generate Domain**
3. Note your frontend URL, e.g.: `https://aws-finserv-production.up.railway.app`

---

## Step 5 — Update CORS (Required)

The API blocks requests from unknown origins by default. You must add your frontend URL.

1. In your local repo, open `api/main.py`
2. Find the `allow_origins` list (around line 60) and add your frontend URL:

   ```python
   allow_origins=[
       "http://localhost:3000",
       "http://127.0.0.1:3000",
       "https://aws-finserv-production.up.railway.app",  # ← your frontend URL
   ],
   ```

3. Save, commit, and push:
   ```bash
   git add api/main.py
   git commit -m "Add Railway frontend URL to CORS allow_origins"
   git push origin main
   ```

Railway detects the push and redeploys the API automatically (~2 minutes).

---

## Step 6 — Verify End-to-End

Run through this checklist:

- [ ] `https://your-api-url/health` returns `{"status":"ok"}`
- [ ] `https://your-api-url/api/knowledge-base/status` returns a JSON object (chunk_count may be 0 initially — KB indexing runs in background)
- [ ] `https://your-frontend-url` loads the customer list page with the 🏦 header
- [ ] Create a test customer → appears in the sidebar
- [ ] Start a new conversation → send a message → Phase 1 / Phase 2 status tickers appear → response streams in

---

## Step 7 — Weekly Documentation Refresh (Cron)

Sets up automatic re-indexing of AWS documentation every Sunday at 3 AM UTC.

1. Railway project → **+ New** → **Cron Job**
2. Select your **API service**
3. Set:
   - **Command:** `python refresh_ingest.py`
   - **Schedule:** `0 3 * * 0`
4. Save

---

## Environment Variable Reference

### API Service

| Variable | Required | Source | Description |
|----------|----------|--------|-------------|
| `ANTHROPIC_API_KEY` | YES | Manual | Powers all three Claude agents |
| `TAVILY_API_KEY` | YES | Manual | Web search for discovery briefs |
| `DATABASE_URL` | YES | Reference from PostgreSQL plugin | pgvector KB + all app data |
| `PORT` | Auto | Railway injects | Uvicorn listens on this port — do not set manually |

### Frontend Service

| Variable | Required | Source | Description |
|----------|----------|--------|-------------|
| `NEXT_PUBLIC_API_URL` | YES | Manual | Full URL of the API service (no trailing slash) |
| `PORT` | Auto | Railway injects | Next.js listens on this port — do not set manually |

---

## Troubleshooting

### API won't start — health check fails

Check **Logs** tab for the specific error:

| Error message | Fix |
|---------------|-----|
| `ValueError: ANTHROPIC_API_KEY is not set` | Add the variable in API service → Variables |
| `ValueError: DATABASE_URL is not set` | Link DATABASE_URL from PostgreSQL plugin (Step 3b) |
| `psycopg2.OperationalError: could not connect` | Check DATABASE_URL reference is correct; PostgreSQL service is running |
| `could not open extension control file "vector"` | Run `CREATE EXTENSION IF NOT EXISTS vector;` in PostgreSQL Query tab |
| `Address already in use` | Another process on $PORT — Railway handles this; try redeploying |

### Frontend shows blank page or API errors

| Symptom | Fix |
|---------|-----|
| Browser console: `CORS error` | Complete Step 5 — add frontend URL to `allow_origins` in `api/main.py` |
| All API calls return 502 | API service is down — check API service Logs tab |
| `NEXT_PUBLIC_API_URL` not working | Make sure there's no trailing slash; redeploy frontend after setting |
| Knowledge base shows 0 chunks | Normal on first deploy — `startup_ingest.py` runs in background; wait 15-20 min |

### Railway health check keeps failing

The API service `railway.toml` is configured with:
```toml
healthcheckPath = "/health"
healthcheckTimeout = 300
```

Railway polls `GET /health` every 10 seconds and allows up to 300 seconds for the first successful response. If it still fails:
1. Check that `$PORT` is not hardcoded anywhere — the Dockerfile uses `${PORT:-8000}` (shell variable expansion)
2. Check the deploy log for Python import errors (missing packages, etc.)
3. In Railway service → Settings → Health Checks — confirm the path is `/health`

### Discovery briefs not working

`TAVILY_API_KEY` is missing or invalid. Check:
```
https://your-api-url/health
```
The health endpoint doesn't test Tavily — but an attempt to generate a brief will return a `500` error with `TavilyAPIError` in the API logs if the key is wrong.

---

## Resource Sizing

| Service | Minimum Plan | Recommended | Notes |
|---------|-------------|-------------|-------|
| API | Hobby ($5/mo, 1 GB RAM) | Pro (2 GB+) for team use | Embedding model uses ~90 MB; agents need headroom for concurrent calls |
| Frontend | Starter (512 MB) | Starter is fine | Next.js static build is lightweight |
| PostgreSQL | Hobby ($5/mo) | Hobby or Pro | pgvector HNSW index is memory-efficient |

**Estimated monthly cost (Hobby tier):** ~$15-20/month (API + Frontend + PostgreSQL)

---

## Quick Reference

```
Project structure on Railway:
  Project: aws-finserv-assistant
    ├─ PostgreSQL           → DATABASE_URL (auto-injected)
    ├─ Service: api
    │    Source:            github/virtualryder/AWS_FS_Assistant  (root)
    │    Build:             Dockerfile.api
    │    Start:             startup_ingest.py & uvicorn ... --port $PORT
    │    Health check:      GET /health  (timeout 300s)
    │    Vars:              ANTHROPIC_API_KEY, TAVILY_API_KEY, DATABASE_URL (ref)
    │    Domain:            https://xxx-api.up.railway.app
    └─ Service: frontend
         Source:            github/virtualryder/AWS_FS_Assistant  (root = frontend/)
         Build:             Nixpacks (auto-detects Next.js)
         Start:             npm run start
         Vars:              NEXT_PUBLIC_API_URL = https://xxx-api.up.railway.app
         Domain:            https://xxx.up.railway.app
```
