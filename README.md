# AI Manga Studio

**AI Manga Studio** is an agentic AI-powered manga and comic creation platform. It empowers storytellers to upload manuscripts, develop character profiles and continuity bibles, orchestrate a 9-agent LangGraph workflow, generate stylized panel artwork via Cloudflare Workers AI (Flux 1 Schnell), interactively format dialogue and speech bubbles, read chapters with authentic Right-to-Left manga pacing, and publish downloadable print-ready PDFs.

---

## 1. Key Features

- **Document Ingestion & Text Extraction**: Upload story manuscripts and lore documents (`.txt`, `.pdf`, `.docx`) with automatic text parsing and an in-browser editable inspector.
- **Character Continuity Engine**: Stable character IDs, canonical appearance profiles (hair, eyes, costume, accessories), visual consistency rules, reference image uploads, and canon approval locks.
- **9-Agent LangGraph Workflow**:
  1. *Story Ingestion Agent*: Analyzes raw manuscripts, isolates facts, and extracts core narrative elements.
  2. *Story Architect Agent*: Structures synopses, central conflicts, plot arcs, and stakes.
  3. *Character & World Bible Agent*: Builds canonical profiles, factions, locations, and worldbuilding rules.
  4. *Chapter Planner Agent*: Plans narrative progression, chapter objectives, and dramatic beats.
  5. *Scene & Dialogue Agent*: Drafts vivid character dialogue, narration, and actions (keeping dialogue strictly separated from image prompts).
  6. *Manga Director Agent*: Directs panel composition, camera angles, lighting, speech bubbles, and onomatopoeia sound effects (SFX).
  7. *Art Generation Agent*: Compiles prompts with canonical traits and invokes Cloudflare Workers AI (`@cf/black-forest-labs/flux-1-schnell`) or the high-contrast studio mock engine.
  8. *Critic & Continuity Agent*: Audits visual consistency, dialogue separation, and narrative continuity with automated quality scoring.
  9. *Publishing Agent*: Assembles page grids and prepares layouts for publishing.
- **Interactive Manga Canvas & Editor**:
  - 2x2 grid layouts and custom panel arrangements.
  - Live editable speech bubbles, thought bubbles, narration boxes, and sound effects.
  - Targeted single-panel AI image regeneration with prompt tweaking.
  - Autosave state indicator.
- **Manga Reader**:
  - Page-by-page reader supporting authentic Right-to-Left (Japanese Manga) and Left-to-Right (Western Comic) flip flows.
  - Full-screen reading mode and bottom thumbnail ribbon.
- **Publishing & PDF Exporter**:
  - Deterministic ReportLab publishing engine generating B5 (Tankobon ratio), A4, and Letter PDFs.
  - Embedded cover page, chapter metadata, dialogue bubbles, narration boxes, sound effects, and page numbers.
- **Zero-Credential Studio Mock Fallback**:
  - Operates out-of-the-box with deterministic high-contrast manga panel artwork and mock LLM reasoning when API keys are not supplied.

---

## 2. Technology Stack

### Frontend
- **React JS** (Functional components, Hooks)
- **Strict JavaScript requirement**: Pure JavaScript and JSX (`.js`, `.jsx`). Zero TypeScript files.
- **Vite** build tool
- **Tailwind CSS** with dark manga studio palette (`#0a0b0e`, `#12141a`, `#161922`, `#7c3aed`)
- **React Router v6**
- **TanStack Query** (React Query)
- **Zustand** state stores
- **Lucide React** icons
- **Server-Sent Events (SSE)** for real-time generation progress

### Backend
- **Python 3.11**
- **FastAPI**
- **Pydantic v2**
- **SQLAlchemy 2.0** (Async engine supporting SQLite and PostgreSQL)
- **Alembic** database migrations
- **LangChain** & **LangGraph** (StateGraph multi-agent pipeline)
- **ReportLab** (Manga PDF publishing)
- **Pillow (PIL)** (Image processing & mock panel generation)
- **PyPDF** & **python-docx** (Document extraction)
- **PyJWT** & **bcrypt** (User authentication and multi-tenant data isolation)
- **Pytest** & **pytest-asyncio**

### AI Providers
- **OpenRouter**: Primary cloud LLM integration (`OPENROUTER_API_KEY`, `OPENROUTER_MODEL`, `OPENROUTER_FALLBACK_MODEL`).
- **Cloudflare Workers AI**: Image generation service using `@cf/black-forest-labs/flux-1-schnell` REST API (`CLOUDFLARE_ACCOUNT_ID`, `CLOUDFLARE_API_TOKEN`).

---

## 3. Project Structure

```
manga/
├── backend/
│   ├── app/
│   │   ├── agents/
│   │   │   ├── graph/
│   │   │   │   ├── state.py         # MangaWorkflowState TypedDict
│   │   │   │   └── workflow.py      # LangGraph StateGraph & quality gates
│   │   │   ├── manga_agents.py      # Agents 5-9 (Dialogue, Director, Art, Critic, Publishing)
│   │   │   └── story_agents.py      # Agents 1-4 (Ingestion, Architect, Bible, Planner)
│   │   ├── api/
│   │   │   ├── routes/
│   │   │   │   ├── assets.py        # Private media streaming
│   │   │   │   ├── auth.py          # Register, Login, Me, Logout
│   │   │   │   ├── characters.py    # Characters, References, Approval
│   │   │   │   ├── exports.py       # PDF Chapter Export & Download
│   │   │   │   ├── jobs.py          # Job status, cancellation, SSE stream
│   │   │   │   ├── manga.py         # Pages, Panels, Targeted Regeneration
│   │   │   │   ├── projects.py      # Project CRUD & ownership verification
│   │   │   │   ├── settings.py      # Provider health, models, usage
│   │   │   │   ├── story.py         # Story Bible & Chapter workflow triggers
│   │   │   │   └── uploads.py       # Manuscript upload & text extraction
│   │   │   └── dependencies.py      # Current user & ownership guards
│   │   ├── core/
│   │   │   ├── config.py            # Pydantic v2 settings & env loader
│   │   │   ├── database.py          # Async SQLAlchemy engine & sessionmaker
│   │   │   ├── logging.py           # Structured logging
│   │   │   └── security.py          # JWT tokens & bcrypt password hashing
│   │   ├── exporters/
│   │   │   └── pdf_exporter.py      # ReportLab Manga Tankobon PDF generator
│   │   ├── models/                  # SQLAlchemy ORM models
│   │   │   ├── asset.py
│   │   │   ├── character.py
│   │   │   ├── job.py
│   │   │   ├── manga.py
│   │   │   ├── project.py
│   │   │   ├── publishing.py
│   │   │   ├── story.py
│   │   │   └── user.py
│   │   ├── providers/               # AI & Mock adapters
│   │   │   ├── cloudflare_ai.py     # Flux 1 Schnell REST client
│   │   │   ├── mock_provider.py     # Local manga mock LLM & image generator
│   │   │   └── openrouter.py        # OpenRouter client with retry & fallback
│   │   ├── schemas/                 # Pydantic v2 validation models
│   │   ├── storage/                 # Media storage adapters
│   │   ├── workers/
│   │   │   └── job_manager.py       # Async job queue & SSE pub/sub
│   │   └── main.py                  # FastAPI application entrypoint
│   ├── migrations/                  # Alembic database migrations
│   ├── tests/                       # Pytest test suite
│   │   ├── test_agents_and_graph.py
│   │   ├── test_auth_and_projects.py
│   │   ├── test_e2e_pipeline.py
│   │   └── test_pdf_export.py
│   ├── alembic.ini
│   ├── pyproject.toml
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── api/                     # Centralized API fetch modules
│   │   ├── components/              # Navbar, NotificationToast, Modal
│   │   ├── features/
│   │   │   ├── auth/                # Login & Registration
│   │   │   ├── characters/          # Character Studio & Continuity
│   │   │   ├── dashboard/           # Project Dashboard
│   │   │   ├── manga-editor/        # Interactive Manga Canvas & Dialogue Editor
│   │   │   ├── projects/            # New Project Wizard
│   │   │   ├── reader/              # Manga Reader (RTL/LTR)
│   │   │   ├── settings/            # Settings & AI Provider status
│   │   │   ├── story-editor/        # Story Bible & Lore Planning
│   │   │   ├── uploads/             # Manuscript & Document Inspector
│   │   │   └── LandingPage.jsx      # Studio Landing Page
│   │   ├── hooks/                   # useSSE
│   │   ├── stores/                  # Zustand authStore & studioStore
│   │   ├── App.jsx                  # React Router routes
│   │   ├── index.css                # Tailwind directives & manga styles
│   │   └── main.jsx                 # Client entrypoint
│   ├── index.html
│   ├── package.json
│   ├── postcss.config.js
│   ├── tailwind.config.js
│   └── vite.config.js
├── docker-compose.yml               # PostgreSQL & Redis infrastructure
├── .env.example
└── README.md
```

---

## 4. Setup and Local Development

### Prerequisites
- **Python**: 3.11+
- **Node.js**: v18+ (tested on v24)
- **Docker**: Optional (for PostgreSQL & Redis; SQLite runs out-of-the-box)

### Step 1: Environment Variables
Create a `.env` file in the project root:
```bash
cp .env.example .env
```

Configuration defaults:
```env
APP_ENV=development
APP_SECRET_KEY=dev_secret_key_manga_studio_super_secure_change_in_prod_123456
FRONTEND_URL=http://localhost:5173
API_BASE_URL=http://localhost:8000
DATABASE_URL=sqlite+aiosqlite:///./manga_studio.db
# For PostgreSQL: postgresql+asyncpg://postgres:password@localhost:5432/manga_studio
REDIS_URL=redis://localhost:6379/0
OPENROUTER_API_KEY=
OPENROUTER_MODEL=anthropic/claude-3.5-sonnet
OPENROUTER_FALLBACK_MODEL=meta-llama/llama-3.3-70b-instruct:free
CLOUDFLARE_ACCOUNT_ID=
CLOUDFLARE_API_TOKEN=
CLOUDFLARE_IMAGE_MODEL=@cf/black-forest-labs/flux-1-schnell
STORAGE_BACKEND=local
MEDIA_ROOT=./media
MAX_UPLOAD_SIZE_MB=20
MAX_PAGES_PER_CHAPTER=20
MAX_IMAGE_RETRIES=2
MAX_CONCURRENT_IMAGE_JOBS=2
```

*(Note: If `OPENROUTER_API_KEY` or `CLOUDFLARE_API_TOKEN` are omitted, the application operates smoothly in Mock Mode, generating high-contrast manga drawings with full pipeline functionality.)*

---

### Step 2: Backend Setup & Migrations

1. Activate virtual environment:
   ```powershell
   # Windows
   .\.venv\Scripts\activate
   ```
2. Install dependencies:
   ```bash
   pip install -r backend/requirements.txt
   ```
3. Run Alembic migrations:
   ```bash
   cd backend
   python -m alembic upgrade head
   cd ..
   ```
4. Start FastAPI server:
   ```bash
   cd backend
   uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
   ```
   API Documentation is available at `http://127.0.0.1:8000/docs`.

---

### Step 3: Frontend Setup

1. Install npm packages:
   ```bash
   cd frontend
   npm install
   ```
2. Build verification (pure JS + JSX, no TypeScript):
   ```bash
   npm run build
   ```
3. Start Vite development server:
   ```bash
   npm run dev -- --host 127.0.0.1 --port 5173
   ```
   Access the Studio in your browser at `http://127.0.0.1:5173`.

---

## 5. Running Automated Tests

Run the full backend test suite covering Authentication, Project Isolation, LangGraph Workflows, Quality Gate Routers, ReportLab PDF Export, and End-to-End Pipelines:

```powershell
cd backend
..\.venv\Scripts\python.exe -m pytest tests -v
```

### Test Results
```
tests/test_agents_and_graph.py::test_providers_initialization PASSED
tests/test_agents_and_graph.py::test_quality_gate_router PASSED
tests/test_agents_and_graph.py::test_langgraph_full_workflow_execution PASSED
tests/test_auth_and_projects.py::test_auth_registration_login_and_me PASSED
tests/test_auth_and_projects.py::test_project_crud_and_isolation PASSED
tests/test_e2e_pipeline.py::test_full_end_to_end_manga_studio_pipeline PASSED
tests/test_pdf_export.py::test_manga_pdf_generation_b5 PASSED

======================= 7 passed in 2.86s =======================
```

---

## 6. End-to-End User Workflow

1. **Sign Up & Workspace**: Register an account at `http://127.0.0.1:5173/register` and land on the Dashboard.
2. **Project Wizard**: Click **New Project**, specify series title, premise, genre (Action, Dark Fantasy, Sci-Fi, etc.), and reading direction (Right-to-Left or Left-to-Right).
3. **Uploads**: Drag and drop `.txt`, `.pdf`, or `.docx` story drafts. Review extracted text in the Document Inspector.
4. **Story Planning & Bible**: Click **AI Story Bible Agent** to analyze lore and structure plot arcs, factions, and world rules.
5. **Character Studio**: Manage canonical character profiles and lock in consistency rules (hair, eyes, signature outfits) to anchor image prompts across panels.
6. **Manga Chapter Generation**: Launch chapter scripting and panel generation. The LangGraph pipeline runs director composition, image synthesis, and continuity critique with live progress streamed over SSE.
7. **Interactive Manga Canvas**:
   - Preview assembled pages in a 2x2 grid.
   - Click any panel to edit speech bubbles, thought bubbles, captions, and sound effects.
   - Click **Regenerate Panel Artwork** to run targeted re-generation without disturbing other panels.
8. **Manga Reader & PDF Publishing**: Switch to Reader mode to preview page turns with Right-to-Left manga pacing, then click **Download PDF** for an authentic Tankobon PDF export.

---

## 7. Production Deployment Guidance

- **Frontend**: Deploy `frontend/dist` to Cloudflare Pages, Vercel, or AWS S3 + CloudFront with `VITE_API_BASE_URL` pointing to your backend API.
- **Backend**: Deploy the FastAPI app via Docker or AWS EC2 / ECS / Cloud Run with Gunicorn + Uvicorn workers (`gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app`).
- **Database**: Managed PostgreSQL (e.g. AWS RDS or Supabase) with `DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/manga_studio`. Run `alembic upgrade head` in your deployment CI/CD.
- **Job Workers**: For high-volume background jobs, use Redis and Celery or RQ workers.
- **Object Storage**: Swap `LocalStorageAdapter` for `S3StorageAdapter` with AWS S3, Cloudflare R2, or Google Cloud Storage.
