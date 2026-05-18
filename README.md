# AWS Financial Services Assistant

**AWS Financial Services Practice**

A compliance-validated AWS architecture assistant purpose-built for financial services — banks, credit unions, payment processors, insurers, fintechs, and capital markets firms. Powered by two specialized AI agents that validate every recommendation against the full financial services regulatory stack.

---

## What It Does

The assistant fields architecture and GenAI/ML questions from your account team and automatically:

1. **Identifies applicable regulations** based on the customer's entity type (bank, payment processor, insurer, etc.)
2. **Runs two specialized AI agents** against every question:
   - 🏗️ **AWS Architect Agent** — designs scalable, secure architectures with full compliance mapping
   - 🤖 **GenAI/ML Expert Agent** — identifies Bedrock/AgentCore/SageMaker opportunities with AI governance frameworks
3. **Synthesizes a unified response** covering architecture, compliance, and AI — every time
4. **Generates financial services discovery briefs** with regulatory risk profiling and 20 targeted discovery questions

---

## Regulations Applied to Every Recommendation

| Regulation | Current Version | Key Scope |
|------------|----------------|-----------|
| **GLBA / FTC Safeguards Rule** | June 2023 amendments; breach notification effective May 2024 | All financial institutions handling NPI. AES-256 encryption, MFA for all users, annual pen testing, 30-day FTC breach notification |
| **PCI DSS** | v4.0.1 (all requirements mandatory since March 31, 2025) | Anyone storing/processing/transmitting cardholder data. MFA for ALL CDE access, field-level PAN encryption, automated SIEM |
| **SOX Section 404** | PCAOB AS 2201 (amended version effective Dec 15, 2026); AS 1105 effective Dec 2024 | Public companies. ITGCs (access mgmt, change mgmt, computer ops, SDLC) and ITACs for financial reporting systems |
| **FFIEC IT Handbook** | AIO (Jun 2021), DA&M (Aug 2024), InfoSec (Sep 2016) | Banks and credit unions. Cloud shared responsibility, AI/ML governance, API security, SSDLC |
| **Interagency MRM Guidance** | April 17, 2026 (supersedes SR 11-7 / OCC 2011-12) | Traditional ML models in scope; Gen AI explicitly excluded pending RFI. Tiered by materiality |
| **NIST AI RMF** | 1.0 + AI 600-1 GenAI Profile (Jul 2024); Agentic AI Profile (draft 2025) | Voluntary but cited by regulators. GOVERN/MAP/MEASURE/MANAGE. 12 GenAI risk categories |

---

## Architecture

```
+------------------------------------------------------------------+
|                     Next.js Frontend (App Router)                |
|  Sidebar: KB metrics · compliance reference · customer list      |
|  Pages: /customers · /customers/[id] · /conversations/[id]       |
|  SSE streaming via fetch + ReadableStream                        |
+----------------------------+-------------------------------------+
                             | REST + SSE (JSON / text/event-stream)
                             v
+------------------------------------------------------------------+
|              FastAPI Backend  (api/)                             |
|  /api/customers  /api/conversations  /api/conversations/{id}/chat|
|  /api/customers/{id}/discovery  /api/knowledge-base/status       |
|  Session store: FinServChatAgent per conversation (TTL eviction) |
|  SSE bridge: ThreadPoolExecutor → asyncio.Queue → EventSource    |
+----------------------------+-------------------------------------+
                             |
                             v
+------------------------------------------------------------------+
|              FinServChatAgent (Orchestrator)                     |
|  Routes: full analysis vs. quick answer                          |
|  Runs: Phase 1 (Architect) → Phase 2 (GenAI) → Synthesis        |
+---------------+---------------------------+----------------------+
                |                           |
                v                           v
+--------------------------+  +------------------------------+
|  AWSArchitectAgent       |  |  GenAIMLAgent                |
|  (Phase 1)               |  |  (Phase 2)                   |
|                          |  |                              |
| · Architecture design    |  | · Bedrock/AgentCore/SageMaker|
| · GLBA compliance map    |  | · NIST AI RMF governance     |
| · PCI DSS v4.0.1         |  | · MRM Guidance alignment     |
| · SOX ITGC coverage      |  | · Fair lending (ECOA)        |
| · FFIEC alignment        |  | · AI workflow diagrams       |
| · Whiteboard diagram     |  | · Model inventory templates  |
| · CIO/CSO/CTO/LoB views  |  | · Human review gates (A2I)   |
+-----------+--------------+  +------------+-----------------+
            |                              |
            +---------------+--------------+
                            |
                            v
+------------------------------------------------------------------+
|  Synthesis Pass — Combined Response                              |
|  Unified: Architecture + Compliance + GenAI + Governance         |
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

## Every Architecture Response Includes

1. **Situation Summary & Regulatory Context** — Entity type, applicable regulations
2. **Key Assumptions** — Every inference flagged with warning
3. **Recommended Architecture** — Whiteboard-ready text diagram
4. **Why This Architecture Solves the Problem** — "Why" behind every decision
5. **Compliance Mapping Tables** — GLBA / PCI DSS / SOX / FFIEC row-by-row
6. **Security Architecture** — Zero Trust, network segmentation, IAM, encryption
7. **Two Alternative Architectures** — With compliance implications per alternative
8. **Scalability & Resilience** — HA, DR, RTO/RPO for financial services
9. **Implementation Guide** — Step-by-step with AWS Console paths and CLI commands
10. **Stakeholder Perspectives** — CIO / CSO/CISO / CTO / Line of Business
11. **Component Deep-Dive** — Plain English + compliance notes per service
12. **GenAI/ML Opportunities** — Bedrock workflows with AI governance
13. **Discovery Questions** — For unknown gaps
14. **Sources & Freshness Note** — All citations with retrieval dates

---

## Module Layout

```
AWS Financial Services Assistant/
├── app.py                          # Legacy Streamlit UI (still runnable)
├── config.py                       # Settings (model, chunking, retrieval, branding)
├── requirements.txt                # Python deps for Streamlit app
├── requirements-api.txt            # Python deps for FastAPI backend
├── railway.toml                    # Railway config — FastAPI backend service
├── Dockerfile.api                  # Docker image for FastAPI backend
├── docker-compose.yml              # Local dev: API on :8000 + frontend on :3000
├── startup_ingest.py               # Background indexer on first boot
├── refresh_ingest.py               # Weekly stale-content refresh
│
├── api/                            # FastAPI backend (replaces Streamlit for prod)
│   ├── main.py                     # FastAPI app, CORS, lifespan
│   ├── session_store.py            # In-memory FinServChatAgent sessions w/ TTL
│   ├── streaming.py                # ThreadPoolExecutor → asyncio.Queue SSE bridge
│   └── routers/
│       ├── customers.py            # GET/POST/PUT/DELETE /api/customers
│       ├── conversations.py        # Conversation CRUD + message history
│       ├── chat.py                 # POST /api/conversations/{id}/chat  (SSE)
│       ├── documents.py            # Upload/toggle/delete customer documents
│       ├── discovery.py            # POST /api/customers/{id}/discovery (SSE)
│       └── knowledge_base.py       # KB status + ingest trigger
│
├── frontend/                       # Next.js 14 App Router frontend
│   ├── package.json
│   ├── next.config.ts              # Rewrites /api/* → FastAPI backend
│   ├── tailwind.config.ts          # AWS orange + Presidio blue theme
│   ├── railway.toml                # Railway config — frontend service
│   ├── app/
│   │   ├── layout.tsx              # Root layout with Inter font
│   │   ├── globals.css             # Tailwind base + custom styles
│   │   ├── customers/page.tsx      # Customer list / welcome screen
│   │   ├── customers/[id]/page.tsx # Customer detail (tabs: Conversations/Discovery/Docs)
│   │   └── customers/[id]/conversations/[id]/page.tsx  # Chat interface
│   ├── components/
│   │   ├── chat/ChatWindow.tsx     # Streaming chat with status ticker
│   │   ├── discovery/DiscoveryPanel.tsx  # Discovery brief generator
│   │   ├── sidebar/Sidebar.tsx     # Customer list + compliance reference
│   │   ├── customers/             # CustomerHeader, CustomerList, DocumentsPanel, NewCustomerModal
│   │   ├── conversations/         # ConversationList
│   │   └── common/                # MarkdownRenderer, CopyButton, StageBadge, StatusTicker
│   ├── hooks/
│   │   ├── useSSEStream.ts         # Generic POST → ReadableStream SSE hook
│   │   ├── useChatStream.ts        # Chat-specific wrapper
│   │   └── useDiscoveryStream.ts   # Discovery brief wrapper
│   └── lib/
│       ├── types.ts                # TypeScript interfaces
│       ├── api.ts                  # Fetch wrappers for all endpoints
│       ├── constants.ts            # Stages, entity types, compliance refs, API base
│       └── utils.ts                # timeAgo, truncate, copyToClipboard, downloadText
│
├── agent/
│   ├── chat_agent.py               # FinServChatAgent orchestrator
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
    └── test_build_validation.py    # 48-test build validation suite
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

### Getting Your API Keys

**Anthropic API Key:**
1. Go to [console.anthropic.com](https://console.anthropic.com)
2. Settings → API Keys → Create Key
3. Copy the `sk-ant-...` key

**Tavily API Key:**
1. Go to [app.tavily.com](https://app.tavily.com)
2. Sign up (free tier: 1,000 searches/month)
3. Copy your API key from the dashboard

---

## Local Development

Two options: **Docker Compose** (easiest) or **manual** (if you have PostgreSQL already).

### Option A — Docker Compose

```bash
# 1. Clone the repo
git clone https://github.com/virtualryder/AWS_FS_Assistant.git
cd "AWS_FS_Assistant"

# 2. Create your .env file
cp .env.example .env
# Edit .env — set ANTHROPIC_API_KEY, DATABASE_URL, TAVILY_API_KEY

# 3. Start API + frontend
docker-compose up
```

- API available at `http://localhost:8000`
- Frontend available at `http://localhost:3000`
- Both services hot-reload on file changes

### Option B — Manual

#### 1. Set up PostgreSQL + pgvector

**Windows:** Download PostgreSQL from [postgresql.org/download/windows](https://www.postgresql.org/download/windows/), then install pgvector from [github.com/pgvector/pgvector/releases](https://github.com/pgvector/pgvector/releases).

**macOS:**
```bash
brew install postgresql@16 && brew services start postgresql@16
```

**Linux (Ubuntu):**
```bash
sudo apt install postgresql postgresql-16-pgvector
```

Create the database:
```sql
CREATE DATABASE aws_finserv;
\c aws_finserv
CREATE EXTENSION IF NOT EXISTS vector;
```

#### 2. Python environment (FastAPI backend)

```bash
python -m venv .venv

# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements-api.txt
```

#### 3. Configure environment

```bash
cp .env.example .env
```

Edit `.env`:
```env
ANTHROPIC_API_KEY=sk-ant-api03-your-key-here
DATABASE_URL=postgresql://postgres:yourpassword@localhost:5432/aws_finserv
TAVILY_API_KEY=tvly-your-key-here
```

#### 4. Start the FastAPI backend

```bash
uvicorn api.main:app --reload --port 8000
```

On first run, start the background indexer separately (optional — app works without it):
```bash
python startup_ingest.py
```

#### 5. Start the Next.js frontend

```bash
cd frontend
npm install
cp .env.local.example .env.local
# .env.local already points to http://localhost:8000 by default
npm run dev
```

Open `http://localhost:3000`.

#### 6. Run tests

```bash
python -m pytest tests/test_build_validation.py -v
# Expected: 48 passed
```

---

## Railway Deployment

> **Full step-by-step guide with infrastructure setup, troubleshooting, and resource sizing: [`DEPLOY_RAILWAY.md`](DEPLOY_RAILWAY.md)**

The app deploys as **three Railway resources** inside one project:

```
Railway Project
  ├─ PostgreSQL plugin       ← pgvector KB + all app data
  ├─ Service: API            ← FastAPI (Dockerfile.api, repo root)
  └─ Service: Frontend       ← Next.js (frontend/ subdirectory)
```

**Deployment order:** PostgreSQL → API → Frontend → Update CORS

### Environment Variables

**API service** (set in Railway → Variables):

| Variable | Value |
|----------|-------|
| `ANTHROPIC_API_KEY` | `sk-ant-api03-...` |
| `TAVILY_API_KEY` | `tvly-...` |
| `DATABASE_URL` | Link from PostgreSQL plugin (do not type manually) |

**Frontend service:**

| Variable | Value |
|----------|-------|
| `NEXT_PUBLIC_API_URL` | `https://your-api-service.up.railway.app` (no trailing slash) |

### After Deploying Both Services — Update CORS

Add your frontend Railway domain to `api/main.py`:

```python
allow_origins=[
    "http://localhost:3000",
    "https://your-frontend.up.railway.app",  # ← add this
],
```

Commit and push — Railway redeploys the API automatically.

### Verify

```
GET https://your-api.up.railway.app/health
→ {"status": "ok", "sessions": 0}

GET https://your-api.up.railway.app/api/knowledge-base/status
→ {"chunk_count": ..., "ingest_running": true/false, ...}
```

### Weekly Documentation Refresh (Cron)

Railway → project → New → Cron Job → connect to API service:
- Command: `python refresh_ingest.py`
- Schedule: `0 3 * * 0` (Sunday 3 AM UTC)

---

## Database Schema

All tables are created automatically on first run. You only need to create the database and enable pgvector.

| Table | Purpose | Key Columns |
|-------|---------|-------------|
| `doc_chunks` | Vector knowledge base — AWS doc chunks | `embedding vector(384)`, `source_url`, `tier`, `ingestion_date` |
| `ingestion_manifest` | Tracks what was indexed when | `data JSONB` (last_updated, total_chunks, sources) |
| `customers` | Customer workspaces | `name`, `industry` (entity type), `arch_context`, `stage` |
| `conversations` | Conversation threads per customer | `customer_id` (FK), `title`, timestamps |
| `messages` | Individual message turns | `conversation_id` (FK), `role`, `content_text`, `is_display_turn` |
| `customer_documents` | Uploaded PDFs, Word docs, etc. | `customer_id` (FK), `filename`, `extracted_text`, `is_active` |

The `doc_chunks` table uses an HNSW index created automatically on first boot:
```sql
CREATE INDEX ON doc_chunks USING hnsw (embedding vector_cosine_ops);
```

---

## Indexed AWS Services

### Primary Services (Auto-indexed at first boot, ~15-20 minutes)

| Category | Services |
|----------|---------|
| Compute | Lambda, EC2, ECS, EKS |
| Storage | S3 |
| Databases | RDS, DynamoDB, Redshift, ElastiCache |
| Networking | VPC, CloudFront, API Gateway, PrivateLink |
| **Security (FinServ Core)** | **IAM, IAM Identity Center, KMS, Cognito, GuardDuty, SecurityHub, Macie, WAF** |
| **Compliance (FinServ Core)** | **CloudTrail, AWS Config, Audit Manager, AWS Backup, Control Tower** |
| Analytics | Glue, Kinesis, Athena |
| Messaging | SQS, SNS, EventBridge, Step Functions |
| **AI / ML (FinServ Core)** | **Bedrock, Bedrock AgentCore, SageMaker, Amazon A2I** |
| DevOps | CloudFormation, CloudWatch, Secrets Manager |

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
> *"Design a secure document processing pipeline for mortgage applications. We're an OCC-regulated bank handling NPI and need to comply with GLBA and FFIEC requirements."*

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

| Setting | File | Default | Notes |
|---------|------|---------|-------|
| `MODEL_NAME` | `config.py` | `claude-sonnet-4-6` | Claude model for all agents |
| `MAX_TOKENS` | `config.py` | `32,000` | Max tokens per agent call |
| `TOP_K` | `config.py` | `10` | KB chunks per search |
| `CHUNK_SIZE` | `config.py` | `800` | Characters per chunk |
| `CHUNK_OVERLAP` | `config.py` | `100` | Overlap between chunks |
| `COLLECTION_NAME` | `config.py` | `aws_finserv_docs` | pgvector collection identifier |
| `EMBEDDING_MODEL` | `config.py` | `all-MiniLM-L6-v2` | Sentence-transformers model (384-dim) |

---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| LLM | Claude Sonnet 4.6 (Anthropic) — streaming API |
| Agent framework | Native Anthropic tool use (no LangChain) |
| Backend API | FastAPI + uvicorn + sse-starlette |
| Frontend | Next.js 14 (App Router) + Tailwind CSS |
| SSE streaming | ThreadPoolExecutor → asyncio.Queue → EventSourceResponse |
| Vector store | PostgreSQL + pgvector (HNSW cosine similarity) |
| Embeddings | `all-MiniLM-L6-v2` (sentence-transformers, 384-dim) |
| Web search | Tavily API (discovery briefs) |
| Web scraping | requests + BeautifulSoup4 + markdownify |
| Doc parsing | pdfplumber (PDF), python-docx (Word) |
| Deployment | Railway — API service (Dockerfile) + Frontend service (Nixpacks) |
| Legacy UI | Streamlit (`app.py` — still runnable for local use) |

---

## Regulatory Accuracy Note

The compliance guidance embedded in this assistant reflects the regulatory landscape as of **May 2026**. Key dates:

- GLBA FTC Safeguards Rule: June 2023 amendments in effect; breach notification effective May 13, 2024
- PCI DSS v4.0.1: All formerly future-dated requirements mandatory since March 31, 2025
- PCAOB AS 1105 (audit evidence): Effective for fiscal years ending December 15, 2024+
- FFIEC DA&M Booklet: Updated August 2024 (replaced 2004 version)
- Interagency MRM Guidance: April 17, 2026 supersedes SR 11-7 and OCC 2011-12; Gen AI explicitly excluded pending RFI
- NIST AI 600-1 (Generative AI Profile): July 26, 2024
- NIST Agentic AI Profile: Draft 2025 (CSA/NIST collaboration)

**Always validate regulatory guidance with qualified legal and compliance counsel before customer use. This tool provides architectural guidance and is not legal advice.**
