# AWS Financial Services Assistant

**AWS Financial Services Practice**

A compliance-validated AWS architecture assistant purpose-built for financial services — banks, credit unions, payment processors, insurers, fintechs, and capital markets firms. Powered by two specialized AI agents that run in parallel and validate every recommendation against the full financial services regulatory stack.

---

## What It Does

The assistant fields architecture and GenAI/ML questions from your account team and automatically:

1. **Identifies applicable regulations** based on the customer's entity type (bank, payment processor, insurer, etc.)
2. **Runs two specialized AI agents in parallel** against every question:
   - 🏗️ **AWS Architect Agent** — designs scalable, secure architectures with full compliance mapping
   - 🤖 **GenAI/ML Expert Agent** — identifies Bedrock / AgentCore / SageMaker opportunities with AI governance frameworks
3. **Synthesizes a unified response** structured as a consultative engagement walkthrough — from discovery questions through implementation roadmap
4. **Generates financial services discovery briefs** with regulatory risk profiling and targeted discovery questions, powered by live web research (Tavily)
5. **Remembers conversation history** per customer, injecting prior session summaries into new conversations
6. **Grounds every response** in real AWS documentation indexed in a pgvector knowledge base

---

## Regulations Applied to Every Recommendation

| Regulation | Current Version | Key Scope |
|------------|----------------|-----------|
| **GLBA / FTC Safeguards Rule** | June 2023; breach notification effective May 2024 | All financial institutions handling NPI. AES-256, MFA for all users, annual pen testing, 30-day FTC breach notification |
| **PCI DSS** | v4.0.1 — all requirements mandatory since March 31, 2025 | Anyone storing/processing/transmitting cardholder data. MFA for ALL CDE access, field-level PAN encryption, automated SIEM |
| **SOX Section 404** | PCAOB AS 2201; AS 1105 effective Dec 2024 | Public companies. ITGCs (access mgmt, change mgmt, computer ops, SDLC) and ITACs for financial reporting systems |
| **FFIEC IT Handbook** | AIO (Jun 2021), DA&M (Aug 2024), InfoSec (Sep 2016) | Banks and credit unions. Cloud shared responsibility, AI/ML governance, API security, SSDLC |
| **Interagency MRM Guidance** | April 17, 2026 (supersedes SR 11-7 / OCC 2011-12) | Traditional ML models in scope; Gen AI explicitly excluded pending RFI. Tiered by materiality |
| **NIST AI RMF** | 1.0 + AI 600-1 GenAI Profile (Jul 2024); Agentic AI Profile (draft 2025) | Voluntary but cited by regulators. GOVERN/MAP/MEASURE/MANAGE. 12 GenAI risk categories |

---

## Architecture

```
+------------------------------------------------------------------+
|                     Next.js Frontend (App Router)                |
|  Sidebar: KB catalog · compliance links · customer list          |
|  Pages: /customers · /customers/[id] · /conversations/[id]       |
|  SSE: fetch + ReadableStream → direct to API (bypasses proxy)    |
+----------------------------+-------------------------------------+
                             | REST + SSE (JSON / text/event-stream)
                             v
+------------------------------------------------------------------+
|              FastAPI Backend  (api/)                             |
|  /api/customers  /api/conversations  /api/conversations/{id}/chat|
|  /api/customers/{id}/discovery  /api/knowledge-base/status       |
|  Session store: FinServChatAgent per conversation (1hr TTL)      |
|  SSE bridge: ThreadPoolExecutor → asyncio.Queue → EventSource    |
|  SSE keepalive: ping=20s to prevent Railway proxy timeout        |
+----------------------------+-------------------------------------+
                             |
                             v
+------------------------------------------------------------------+
|              FinServChatAgent (Orchestrator)                     |
|  Routes: full analysis vs. quick answer (classifier call)        |
|  Full analysis: Phase 1 + Phase 2 run IN PARALLEL via            |
|  ThreadPoolExecutor → Phase 3 Synthesis                          |
+---------------+---------------------------+----------------------+
                |  parallel                 |  parallel
                v                           v
+--------------------------+  +------------------------------+
|  AWSArchitectAgent       |  |  GenAIMLAgent                |
|  (runs concurrently)     |  |  (runs concurrently)         |
|                          |  |                              |
| · Architecture design    |  | · Bedrock/AgentCore/SageMaker|
| · GLBA compliance map    |  | · NIST AI RMF governance     |
| · PCI DSS v4.0.1         |  | · MRM Guidance alignment     |
| · SOX ITGC coverage      |  | · Fair lending (ECOA)        |
| · FFIEC alignment        |  | · AI workflow diagrams       |
| · Whiteboard diagram     |  | · Model inventory templates  |
| · Tool use: KB + web     |  | · Tool use: KB + web         |
+-----------+--------------+  +------------+-----------------+
            |                              |
            +---------------+--------------+
                            |
                            v
+------------------------------------------------------------------+
|  Synthesis Pass — Combined Response (engagement flow)            |
|  13-section structure: discovery → recommendation → compliance   |
|  → security → alternatives → GenAI → roadmap → next steps       |
+-------------------+-------------------------+--------------------+
                    |                         |
                    v                         v
+-------------------+          +------------------------------+
| pgvector KB       |          | Live AWS Documentation       |
| PostgreSQL        |          | docs.aws.amazon.com          |
| all-MiniLM-L6-v2  |          | aws.amazon.com/solutions     |
| HNSW indexing     |          | aws.amazon.com/architecture  |
+-------------------+          +------------------------------+
```

---

## Response Structure

Every full analysis response follows a consultative engagement walkthrough — the same order a senior AWS account team would use in a real engagement:

| # | Section | Purpose |
|---|---------|---------|
| 1 | **Situation & What We Heard** | Restates the problem to confirm understanding |
| 2 | **Discovery Questions First** | 8–12 questions to ask before committing to a design |
| 3 | **Our Recommendation** | Opinionated "we recommend..." with named AWS services |
| 4 | **Architecture Design** | Whiteboard-ready text diagram + narrated walkthrough |
| 5 | **Why We Made These Choices** | Decision rationale tied to regulations and business outcomes |
| 6 | **Compliance & Regulatory Coverage** | Full mapping tables — GLBA / PCI DSS / SOX / FFIEC / MRM / NIST AI RMF |
| 7 | **Security Architecture** | Layered controls: perimeter → IAM → data protection → threat detection |
| 8 | **Alternative Approaches** | 2–3 alternatives with trade-offs and why we didn't lead with them |
| 9 | **GenAI & ML Opportunities** | Bedrock/SageMaker use cases with governance and model risk alignment |
| 10 | **Implementation Roadmap** | Phased plan specific enough to hand to a project manager |
| 11 | **Stakeholder Briefing Guide** | CIO / CISO / CTO / Line of Business talking points |
| 12 | **Proposed Next Steps** | 3–5 concrete actions with a clear ask from the customer |
| 13 | **Sources & References** | Real AWS doc URLs from the knowledge base search and live fetches |

---

## Module Layout

```
AWS Financial Services Assistant/
├── config.py                       # Settings (model, tokens, chunking, retrieval)
├── requirements-api.txt            # Python deps for FastAPI backend
├── railway.toml                    # Railway config — FastAPI backend service
├── Dockerfile.api                  # Docker image for FastAPI backend (CPU-only PyTorch)
├── start.sh                        # Entrypoint: startup_ingest.py & → exec uvicorn (PID 1)
├── docker-compose.yml              # Local dev: API on :8000 + frontend on :3000
├── startup_ingest.py               # Background indexer on first boot
├── refresh_ingest.py               # Weekly stale-content refresh
├── test_chat_e2e.py                # End-to-end test against deployed API
│
├── api/                            # FastAPI backend
│   ├── main.py                     # FastAPI app, CORS, lifespan
│   ├── session_store.py            # In-memory FinServChatAgent sessions w/ 1hr TTL
│   ├── streaming.py                # ThreadPoolExecutor → asyncio.Queue SSE bridge
│   └── routers/
│       ├── customers.py            # GET/POST/PUT/DELETE /api/customers
│       ├── conversations.py        # Conversation CRUD + message history
│       ├── chat.py                 # POST /api/conversations/{id}/chat (SSE, ping=20s)
│       ├── documents.py            # Upload/toggle/delete customer documents
│       ├── discovery.py            # POST /api/customers/{id}/discovery (SSE, ping=20s)
│       └── knowledge_base.py       # KB status + sources + ingest trigger
│
├── frontend/                       # Next.js 14 App Router frontend
│   ├── package.json                # next@14.2.35 (CVE-patched)
│   ├── Dockerfile                  # Multi-stage build; standalone Next.js for Railway
│   ├── next.config.mjs             # Rewrites /api/* → FastAPI; standalone output
│   ├── tailwind.config.ts          # AWS orange + dark mode (class strategy)
│   ├── railway.toml                # Railway config — frontend service (dockerfile)
│   ├── app/
│   │   ├── layout.tsx              # Root layout: ThemeProvider + DarkModeToggle
│   │   ├── globals.css             # Tailwind base + custom dark mode styles
│   │   ├── customers/page.tsx      # Welcome screen with KB panel
│   │   ├── customers/[id]/page.tsx # Customer detail (Conversations/Discovery/Documents/KB tabs)
│   │   └── customers/[id]/conversations/[id]/page.tsx  # Chat interface
│   ├── components/
│   │   ├── chat/ChatWindow.tsx          # Streaming chat: connecting→status→tokens→done
│   │   ├── discovery/DiscoveryPanel.tsx # Discovery brief generator with save confirmation
│   │   ├── sidebar/Sidebar.tsx          # Customer list + 📚 KB catalog + ⚖️ compliance links
│   │   ├── knowledge/KnowledgeBasePanel.tsx  # Full KB status with indexed sources
│   │   ├── customers/                   # CustomerHeader, CustomerList, DocumentsPanel, Modal
│   │   ├── conversations/               # ConversationList
│   │   └── common/                      # MarkdownRenderer, CopyButton, StatusTicker, DarkModeToggle
│   ├── hooks/
│   │   ├── useSSEStream.ts         # POST → ReadableStream SSE; uses NEXT_PUBLIC_API_URL directly
│   │   ├── useChatStream.ts        # Chat-specific wrapper
│   │   └── useDiscoveryStream.ts   # Discovery brief wrapper
│   └── lib/
│       ├── types.ts                # TypeScript interfaces (includes StreamState.connecting)
│       ├── api.ts                  # Fetch wrappers for all endpoints
│       ├── constants.ts            # Stages, compliance refs (with URLs), KB_CATALOG (31 docs)
│       ├── theme.tsx               # ThemeProvider (dark by default)
│       └── utils.ts                # timeAgo, truncate, copyToClipboard, downloadText
│
├── agent/
│   ├── chat_agent.py               # FinServChatAgent orchestrator (parallel Phase 1+2)
│   ├── aws_architect_agent.py      # AWS architecture + compliance specialist
│   ├── genai_ml_agent.py           # GenAI/ML + AI governance specialist
│   ├── discovery_agent.py          # Financial services discovery brief generator
│   ├── tools.py                    # Tool schemas for Claude API
│   └── tool_executor.py            # Tool implementations (KB search, live fetch, web)
│
├── scraper/
│   ├── aws_scraper.py              # BFS HTML crawler → markdown converter
│   └── aws_doc_urls.py             # 60+ seed URLs (financial services priority)
│
├── ingestion/
│   ├── ingest_pipeline.py          # Orchestrate crawl → chunk → embed → upsert
│   ├── chunker.py                  # Overlapping character-window chunking
│   └── document_parser.py          # PDF / DOCX / TXT extraction
│
├── vectorstore/
│   └── pg_client.py                # PostgreSQL + pgvector client (HNSW index)
│
└── tests/
    └── test_build_validation.py    # Build validation test suite
```

---

## Prerequisites & API Keys

You need **three** credentials. Set them as environment variables (`.env` locally, Railway Variables in production).

| Variable | Required | Where to Get It | Purpose |
|----------|----------|----------------|---------|
| `ANTHROPIC_API_KEY` | YES | [console.anthropic.com/settings/keys](https://console.anthropic.com/settings/keys) | Powers all Claude agents |
| `DATABASE_URL` | YES | Railway PostgreSQL plugin (auto-injected) or your own PostgreSQL with pgvector | Vector KB + customer workspaces + conversations |
| `TAVILY_API_KEY` | YES (Discovery Briefs) | [app.tavily.com](https://app.tavily.com) | Web search for discovery brief company research |

> `DATABASE_URL` is **automatically injected** by the Railway PostgreSQL plugin. Do not add it manually to the API service.

---

## Local Development

### Option A — Docker Compose

```bash
git clone https://github.com/virtualryder/AWS_FS_Assistant.git
cd "AWS_FS_Assistant"
cp .env.example .env
# Edit .env — set ANTHROPIC_API_KEY, DATABASE_URL, TAVILY_API_KEY
docker-compose up
```

- API: `http://localhost:8000`
- Frontend: `http://localhost:3000`

### Option B — Manual

#### 1. PostgreSQL + pgvector

**macOS:** `brew install postgresql@16 && brew services start postgresql@16`

**Linux:** `sudo apt install postgresql postgresql-16-pgvector`

**Windows:** [postgresql.org/download/windows](https://www.postgresql.org/download/windows/) + pgvector from [github.com/pgvector/pgvector](https://github.com/pgvector/pgvector/releases)

```sql
CREATE DATABASE aws_finserv;
\c aws_finserv
CREATE EXTENSION IF NOT EXISTS vector;
```

#### 2. Python environment

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements-api.txt
```

#### 3. Configure

```bash
cp .env.example .env
```

```env
ANTHROPIC_API_KEY=sk-ant-api03-your-key-here
DATABASE_URL=postgresql://postgres:yourpassword@localhost:5432/aws_finserv
TAVILY_API_KEY=tvly-your-key-here
```

#### 4. Start the API

```bash
uvicorn api.main:app --reload --port 8000
```

Background indexer (optional — app works without it, KB starts empty):
```bash
python startup_ingest.py
```

#### 5. Start the frontend

```bash
cd frontend
npm install
npm run dev   # http://localhost:3000
```

#### 6. Run the e2e test

```bash
# Against local API
PYTHONIOENCODING=utf-8 python test_chat_e2e.py http://localhost:8000

# Against deployed Railway API
PYTHONIOENCODING=utf-8 python test_chat_e2e.py https://your-api.up.railway.app
```

Expected: 6/6 tests passed (health, create customer, create conversation, chat stream, status updates, messages persisted).

---

## Railway Deployment

The app deploys as **three Railway resources** inside one project:

```
Railway Project
  ├─ PostgreSQL plugin       ← pgvector KB + all app data (auto-injects DATABASE_URL)
  ├─ Service: API            ← FastAPI (Dockerfile.api, repo root)
  └─ Service: Frontend       ← Next.js (frontend/ subdirectory)
```

**Deployment order:** PostgreSQL → API → Frontend

### API Service Environment Variables

| Variable | Value |
|----------|-------|
| `ANTHROPIC_API_KEY` | `sk-ant-api03-...` |
| `TAVILY_API_KEY` | `tvly-...` |
| `DATABASE_URL` | Link from PostgreSQL plugin — do not type manually |

### Frontend Service Environment Variables

| Variable | Value | Notes |
|----------|-------|-------|
| `NEXT_PUBLIC_API_URL` | `https://your-api-service.up.railway.app` | **Required.** No trailing slash. SSE calls go directly to the API from the browser to avoid Railway's frontend proxy timeout on long responses (~9 min). This variable is baked into the build — set it before deploying. |

### After Deploying Both Services — Update CORS

Add your frontend Railway domain to `api/main.py`:

```python
allow_origins=[
    "http://localhost:3000",
    "https://your-frontend.up.railway.app",  # ← add this
],
```

Commit and push — Railway redeploys the API automatically.

### Railway Networking — Target Port

In Railway → Frontend Service → Settings → Networking, set **Target Port to 8080** (the Dockerfile exposes 8080).

### Verify Deployment

```bash
# API health
curl https://your-api.up.railway.app/health
# → {"status": "ok", "sessions": 0}

# KB status
curl https://your-api.up.railway.app/api/knowledge-base/status
# → {"chunk_count": ..., "ingest_running": true/false, ...}

# Full e2e test
PYTHONIOENCODING=utf-8 python test_chat_e2e.py https://your-api.up.railway.app
```

### Weekly Documentation Refresh (Cron)

Railway → project → New → Cron Job → connect to API service:
- Command: `python refresh_ingest.py`
- Schedule: `0 3 * * 0` (Sunday 3 AM UTC)

---

## Database Schema

All tables are created automatically on first run.

| Table | Purpose | Key Columns |
|-------|---------|-------------|
| `doc_chunks` | Vector knowledge base — AWS doc chunks | `embedding vector(384)`, `source_url`, `source_label`, `tier`, `ingestion_date` |
| `ingestion_manifest` | Tracks what was indexed when | `data JSONB` (last_updated, total_chunks, sources) |
| `customers` | Customer workspaces | `name`, `industry`, `arch_context`, `stage` |
| `conversations` | Conversation threads per customer | `customer_id` (FK), `title`, timestamps |
| `messages` | Individual message turns | `conversation_id` (FK), `role`, `content_text`, `display_content`, `is_display_turn` |
| `customer_documents` | Uploaded PDFs, Word docs, etc. | `customer_id` (FK), `filename`, `extracted_text`, `is_active` |

HNSW index created automatically on first boot:
```sql
CREATE INDEX ON doc_chunks USING hnsw (embedding vector_cosine_ops);
```

---

## Indexed AWS Services

### Services Auto-Indexed at First Boot (~15–20 minutes)

| Category | Services |
|----------|---------|
| Compute | Lambda, EC2, ECS, EKS |
| Storage | S3, EFS, AWS Backup |
| Databases | RDS, Aurora, DynamoDB, Redshift, ElastiCache |
| Networking | VPC, CloudFront, API Gateway, PrivateLink, Network Firewall, Direct Connect |
| **Security (FinServ Core)** | **IAM, IAM Identity Center, KMS, Cognito, GuardDuty, Security Hub, Macie, WAF, Inspector, Audit Manager, Config, Control Tower, Secrets Manager** |
| Analytics | Glue, Kinesis, Athena, OpenSearch |
| Messaging | SQS, SNS, EventBridge, Step Functions |
| **AI / ML (FinServ Core)** | **Bedrock, Bedrock AgentCore, SageMaker** |
| **Financial Services** | **AWS Payment Cryptography** |
| DevOps | CloudFormation, CloudWatch, CloudTrail, CodePipeline |
| Solutions | AWS Prescriptive Guidance (FinServ), Well-Architected Framework |

### CLI Ingestion

```bash
# Index specific services
python -m ingestion.ingest_pipeline --keys macie inspector shield --max-pages 20

# Index by topic keywords
python -m ingestion.ingest_pipeline --topics "pci dss" "fraud detection" "aml"

# Index everything (slow — 30+ minutes)
python -m ingestion.ingest_pipeline --all --max-pages 20
```

---

## Example Questions

**Compliance-First Architecture:**
> *"Design a secure payment processing pipeline for a community bank. We're OCC-regulated, $2B assets, and need PCI DSS v4.0.1 and GLBA coverage."*

**GenAI with Governance:**
> *"We want to build an AI assistant for AML investigators to generate transaction monitoring narratives. What does the Bedrock architecture look like, and how do we align with the April 2026 Interagency Model Risk Management Guidance?"*

**PCI DSS Remediation:**
> *"Our QSA flagged that our disk-level encryption doesn't satisfy PCI DSS v4.0.1 Requirement 3. We store PANs in RDS. What exactly do we need to change and how?"*

**Multi-Stakeholder:**
> *"Design a fraud detection system. Address the CIO's cost concerns, the CSO's PCI DSS obligations, and the CTO's need to integrate with our existing Kafka pipeline."*

**Discovery Brief:**
> *"Generate a discovery brief for First National Bank of Springfield — website firstnationalbank.com, CISO on the call, upcoming OCC exam, interested in GenAI."*

---

## Configuration Reference

| Setting | File | Current Value | Notes |
|---------|------|--------------|-------|
| `MODEL_NAME` | `config.py` | `claude-sonnet-4-6` | Claude model for all agents |
| `MAX_TOKENS` | `config.py` | `16,000` | Max tokens per sub-agent call; synthesis uses same budget |
| `TOP_K` | `config.py` | `10` | KB chunks returned per search |
| `CHUNK_SIZE` | `config.py` | `800` | Characters per chunk |
| `CHUNK_OVERLAP` | `config.py` | `100` | Overlap between adjacent chunks |
| `EMBEDDING_MODEL` | `config.py` | `all-MiniLM-L6-v2` | Sentence-transformers model (384-dim) |

---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| LLM | Claude Sonnet 4.6 (Anthropic) — streaming API |
| Agent framework | Native Anthropic tool use — no LangChain |
| Parallel execution | `ThreadPoolExecutor` — AWS Architect + GenAI/ML run concurrently |
| Backend API | FastAPI + uvicorn + sse-starlette |
| SSE keepalive | `ping=20` on `EventSourceResponse` — prevents Railway proxy timeout |
| Frontend | Next.js 14.2.35 (App Router) + Tailwind CSS (dark mode by default) |
| SSE client | Browser `fetch` + `ReadableStream` — calls API directly via `NEXT_PUBLIC_API_URL` |
| Vector store | PostgreSQL + pgvector (HNSW cosine similarity) |
| Embeddings | `all-MiniLM-L6-v2` (sentence-transformers, 384-dim) |
| Web search | Tavily API (discovery briefs) |
| Web scraping | requests + BeautifulSoup4 + markdownify |
| Doc parsing | pdfplumber (PDF), python-docx (Word) |
| Deployment | Railway — API service (`Dockerfile.api` + `start.sh`) + Frontend service (`Dockerfile`) |

---

## UI Features

| Feature | Description |
|---------|-------------|
| **Dark mode** | Dark by default; toggle in bottom-right corner and sidebar header |
| **Customer workspaces** | Per-customer context, conversation history, document uploads, opportunity stages |
| **Streaming status** | Real-time status ticker shows which agent is running, which KB queries are firing, token count |
| **Connecting state** | "Connecting to agent…" spinner shown immediately on send — no blank wait |
| **📚 KB catalog** | Collapsible sidebar panel showing 31 AWS docs — green when indexed, links to official AWS docs |
| **⚖️ Compliance reference** | Collapsible sidebar panel with clickable links to GLBA, PCI DSS, SOX, FFIEC, MRM, NIST AI RMF |
| **Discovery briefs** | One-click generation + prominent "Saved to Conversations" confirmation banner |
| **Copy / Download** | Every response has copy-to-clipboard and download-as-markdown buttons |
| **Per-customer memory** | Prior conversation summaries injected into new chats automatically |

---

## Regulatory Accuracy Note

Compliance guidance reflects the regulatory landscape as of **May 2026**. Key dates:

- **GLBA FTC Safeguards Rule:** June 2023 amendments; breach notification (500+ consumers) effective May 13, 2024
- **PCI DSS v4.0.1:** All formerly future-dated requirements mandatory since March 31, 2025
- **PCAOB AS 1105** (audit evidence from system-generated data): Effective for fiscal years ending December 15, 2024+
- **FFIEC DA&M Booklet:** Updated August 2024 (replaced 2004 version)
- **Interagency MRM Guidance:** April 17, 2026 supersedes SR 11-7 and OCC 2011-12; Gen AI explicitly excluded pending separate RFI
- **NIST AI 600-1** (Generative AI Profile): July 26, 2024
- **NIST Agentic AI Profile:** Draft 2025 (CSA/NIST collaboration)

**Always validate regulatory guidance with qualified legal and compliance counsel before customer use. This tool provides architectural guidance and is not legal advice.**
