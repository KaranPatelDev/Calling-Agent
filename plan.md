# Automated Outbound Calling Agent Platform — Complete System Design & Implementation Plan

## Table of Contents

1. [Business Requirements Summary](#1-business-requirements-summary)
2. [Critical Clarification: "Zero Cost" Reality](#2-critical-clarification-zero-cost-reality)
3. [High-Level Architecture](#3-high-level-architecture)
4. [Recommended Tech Stack](#4-recommended-tech-stack)
5. [Full Folder Structure](#5-full-folder-structure)
6. [PostgreSQL Schema](#6-postgresql-schema)
7. [Key API Endpoints](#7-key-api-endpoints)
8. [Scheduling & Reliability Mechanism](#8-scheduling--reliability-mechanism)
9. [Pre-Recorded Audio Upload Feature](#9-pre-recorded-audio-upload-feature)
10. [Phased Implementation Roadmap](#10-phased-implementation-roadmap)
11. [Key Risks & Edge Cases](#11-key-risks--edge-cases)
12. [Dependency Lists](#12-dependency-lists)
13. [Environment Configuration](#13-environment-configuration)
14. [TRAI Compliance (India)](#14-trai-compliance-india)

---

## 1. Business Requirements Summary

A system that automatically calls a list of phone numbers and delivers a fixed script (pitch/message) to each person who picks up. The script must be editable at any time.

### Core Features

- **Script Management**: Create, edit, save business pitch scripts. Support multiple saved scripts (versioning), with one marked "active." Support variables/placeholders (e.g., `{customer_name}`). Support pre-recorded audio upload as alternative to TTS.
- **Number Management**: Add numbers manually or bulk upload via Excel/CSV with column mapping and validation. Store in campaigns/lists for reuse.
- **Calling Engine**: Integrate with telephony API (Exotel for India). Auto-dial numbers, play script (TTS or pre-recorded audio). Track call status per number. Handle retries with configurable limits. Respect concurrency/rate limits.
- **Call Scheduling**: Schedule campaigns for future date/time. Support one-time schedules (required now) and recurring (optional/future). Resilient to backend restarts.
- **Dashboard / Reporting**: Campaign status, call logs, success/failure rates, per-number call history. Export call logs/reports.

### Technical Requirements

- **Backend**: Python, FastAPI (production-grade)
- **Frontend**: Vue 3, Composition API (separate folder)
- **Database**: PostgreSQL
- **Auth**: JWT-based
- **File Handling**: Secure Excel/CSV parsing
- **Job Scheduling & Reliability**: Persistent job scheduling that survives restarts
- **Production Concerns**: .env config, logging, error handling, retry/backoff, rate limiting, input validation, security, containerization, CI/CD
- **Scalability**: Queue-based calling, pagination, background workers

---

## 2. Critical Clarification: "Zero Cost" Reality

Telephony providers **always** charge per-minute/per-call. This is a hard cost. What is designed here minimizes everything else to zero:

| Component | Cost Strategy |
|-----------|--------------|
| **Telephony** | Exotel free trial (₹500 credits, ~166 min) for development. Dabbler plan ₹9,999/6mo for production (~₹1,667/mo) |
| **TTS** | Google Cloud TTS free tier — 1M chars/month (free forever, supports Hindi, Tamil, Telugu, Bengali, etc.) OR skip TTS entirely with pre-recorded audio upload |
| **Backend hosting** | Render free tier OR Railway $5/month credit |
| **Frontend hosting** | Vercel free tier |
| **PostgreSQL** | Neon free tier (0.5 GB storage, scales to zero) |
| **Redis** | Upstash free tier (10K commands/day) |
| **File parsing** | openpyxl (free, local) |

**Estimated total running cost: ₹0/month during dev, ~₹1,700-2,000/month in production** (mostly telephony credits).

> **Note**: TRAI compliance requires DLT registration (~₹5,900/operator/entity) and a 160-series registered number. This is a one-time regulatory cost, not optional.

---

## 3. High-Level Architecture

```
┌──────────────────────────────────────────────────────────────────────┐
│                         FRONTEND (Vue 3)                            │
│  Vercel Free Tier — Vue 3 + Composition API + Pinia + TailwindCSS   │
│                                                                     │
│  Pages: Dashboard │ Scripts │ Contacts │ Campaigns │ Reports │ Auth  │
└──────────────────────────┬───────────────────────────────────────────┘
                           │ HTTPS / REST API
                           ▼
┌──────────────────────────────────────────────────────────────────────┐
│                     BACKEND (FastAPI)                                │
│  Render Free Tier — Python 3.12 + FastAPI + Uvicorn                 │
│                                                                     │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────────────────────┐  │
│  │  Auth (JWT)  │  │  API Routes  │  │  Webhook Receiver          │  │
│  │  /auth/*     │  │  /scripts/*  │  │  /webhooks/exotel          │  │
│  │             │  │  /contacts/* │  │  (call status callbacks)    │  │
│  │             │  │  /campaigns/*│  │                             │  │
│  └─────────────┘  └──────┬───────┘  └─────────────┬──────────────┘  │
│                          │                        │                  │
│  ┌───────────────────────┴────────────────────────┴──────────────┐   │
│  │                    SERVICE LAYER                               │   │
│  │  ScriptService │ ContactService │ CampaignService             │   │
│  │  CallingEngine │ TTSService     │ ComplianceService           │   │
│  │  AudioUploadService                                         │   │
│  └───────────────────────┬────────────────────────┬──────────────┘   │
│                          │                        │                  │
│  ┌───────────────────────┴────────────────────────┴──────────────┐   │
│  │                 BACKGROUND WORKERS                            │   │
│  │  ┌──────────────────┐  ┌──────────────────────────────────┐   │   │
│  │  │  APScheduler      │  │  Calling Worker (asyncio)        │   │   │
│  │  │  PostgreSQL Job   │  │  - Dials numbers from queue      │   │   │
│  │  │  Store             │  │  - Respects concurrency limits   │   │   │
│  │  │  - Campaign sched │  │  - Handles retries               │   │   │
│  │  │  - Recurring jobs │  │  - Rate limit compliance         │   │   │
│  │  └──────────────────┘  └──────────────────────────────────┘   │   │
│  └───────────────────────────────────────────────────────────────┘   │
│                          │                                           │
│  ┌───────────────────────┴───────────────────────────────────────┐   │
│  │                    INTEGRATIONS                               │   │
│  │  Exotel API ──→ Outbound calls + status webhooks              │   │
│  │  Google Cloud TTS ──→ Script text to audio (optional)         │   │
│  │  TRAI DND API ──→ NCPR scrubbing (optional)                  │   │
│  └───────────────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────────────┘
                           │
           ┌───────────────┼───────────────┐
           ▼               ▼               ▼
┌─────────────────┐ ┌─────────────┐ ┌───────────────┐
│  PostgreSQL      │ │  Redis       │ │  File Storage  │
│  Neon Free Tier  │ │  Upstash     │ │  Local/Uploads │
│  - Users         │ │  - Job queue │ │  - Excel/CSV   │
│  - Scripts       │ │  - Cache     │ │  - Audio files │
│  - Contacts      │ │  - Rate      │ │  - TTS cache   │
│  - Campaigns     │ │    limiter   │ │                │
│  - Call Logs     │ │              │ │                │
│  - Scheduled Jobs│ │              │ │                │
└─────────────────┘ └─────────────┘ └───────────────┘
```

---

## 4. Recommended Tech Stack

### Telephony Provider: Exotel (India Winner)

| Provider | Rate (India) | TTS Support | DLT Compliance | Free Trial | Verdict |
|----------|-------------|-------------|----------------|------------|---------|
| **Exotel** | ~₹0.30-0.50/min | Via app + external TTS | Built-in | ₹500 credits | **Best for India** |
| Twilio | ~₹0.80-1.20/min | Built-in TwiML | Manual setup | $15 credit | Too expensive for India |
| Plivo | ~₹0.40-0.60/min | Via external TTS | Manual | $5 credit | Decent but less India-focused |
| FreJun | ~₹0.50-0.70/min | AI voice agents | Built-in | Free trial | Good but pricier |

**Why Exotel**: India-native, cheapest per-minute rates, DLT-registered 140-series numbers included, built-in webhook support, REST API for outbound calls. The "Dabbler" plan (₹9,999 for 6 months = ~₹1,667/mo) includes 5,000 credits + 3 agents + unlimited channels.

**Exotel API flow**:
1. Your app calls Exotel API: `POST /v1/.../calls/connect` with `from`, `to`, `callerid`
2. Exotel connects the call and plays your TTS audio via a call flow app
3. Exotel sends status webhooks to your backend: `queued`, `ringing`, `in-progress`, `completed`, `no-answer`, `busy`, `failed`

### TTS Provider: Google Cloud TTS (Free Tier) — Optional

| Provider | Free Tier | Indian Languages | Quality | API Access |
|----------|-----------|-----------------|---------|------------|
| **Google Cloud TTS** | 1M chars/month | 10+ (Hindi, Tamil, Telugu, Bengali, etc.) | WaveNet quality | REST API |
| Amazon Polly | 5M chars/12mo | Hindi, Tamil, Telugu | Good | REST API |
| Sarvam AI | Free trial | 11 Indian languages | Excellent (Bulbul v3) | REST API |
| Azure TTS | 0.5M chars/month | 7+ Indian languages | Good | REST API |

**Why Google Cloud TTS**: Most generous free tier (1M characters/month = ~2,000+ script plays), excellent Indian language support with WaveNet voices.

**Alternative**: Users can skip TTS entirely by uploading pre-recorded audio files (see Section 9).

### Task Scheduling: APScheduler + PostgreSQL Job Store

| Option | Persistence | Complexity | Reliability | Verdict |
|--------|------------|------------|-------------|---------|
| **APScheduler + PostgreSQL** | Survives restarts | Low | High for small scale | **Best fit** |
| Celery + Redis | Via broker | High | Very high | Overkill for <500 calls/day |
| FastAPI BackgroundTasks | Lost on restart | Lowest | Low | Not suitable |

### Frontend: Vue 3 + Vite + TailwindCSS + Pinia

### Database: PostgreSQL on Neon (Free tier)

### Backend Hosting: Render (Free tier) or Railway ($5 credit)

---

## 5. Full Folder Structure

### /backend (FastAPI)

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                          # FastAPI app, lifespan, CORS, router includes
│   ├── config.py                        # Settings via pydantic-settings, .env loading
│   ├── database.py                      # SQLAlchemy async engine, session factory
│   │
│   ├── models/                          # SQLAlchemy ORM models
│   │   ├── __init__.py
│   │   ├── user.py                      # User model (id, email, hashed_password, created_at)
│   │   ├── script.py                    # Script model (id, user_id, name, content, language, is_active, version, audio_type, audio_file_path)
│   │   ├── contact_list.py              # ContactList model (id, user_id, name, description, contact_count)
│   │   ├── contact.py                   # Contact model (id, list_id, phone, name, metadata, dnd_status)
│   │   ├── campaign.py                  # Campaign model (id, user_id, name, script_id, list_id, status, schedule)
│   │   ├── call_log.py                  # CallLog model (id, campaign_id, contact_id, status, duration, etc.)
│   │   └── scheduled_job.py             # ScheduledJob model (id, campaign_id, apscheduler_job_id, next_run, status)
│   │
│   ├── schemas/                         # Pydantic request/response models
│   │   ├── __init__.py
│   │   ├── auth.py                      # TokenResponse, LoginRequest, RegisterRequest
│   │   ├── script.py                    # ScriptCreate, ScriptUpdate, ScriptResponse
│   │   ├── contact_list.py              # ContactListCreate, ContactListResponse, BulkUploadResponse
│   │   ├── contact.py                   # ContactCreate, ContactResponse, ContactImportRow
│   │   ├── campaign.py                  # CampaignCreate, CampaignSchedule, CampaignResponse
│   │   ├── call_log.py                  # CallLogResponse, CampaignStats, ExportRequest
│   │   └── common.py                    # PaginationParams, MessageResponse, ErrorResponse
│   │
│   ├── api/                             # API route handlers
│   │   ├── __init__.py
│   │   ├── deps.py                      # Dependency injection (get_db, get_current_user)
│   │   ├── auth.py                      # POST /auth/register, /auth/login, /auth/refresh
│   │   ├── scripts.py                   # CRUD for scripts + audio upload
│   │   ├── contacts.py                  # Contact list + bulk upload endpoints
│   │   ├── campaigns.py                 # Campaign CRUD + scheduling
│   │   ├── webhooks.py                  # Exotel status callback receiver
│   │   └── reports.py                   # Dashboard stats, export endpoints
│   │
│   ├── services/                        # Business logic layer
│   │   ├── __init__.py
│   │   ├── auth_service.py              # JWT creation, password hashing, token verification
│   │   ├── script_service.py            # Script CRUD, versioning, variable interpolation
│   │   ├── audio_upload_service.py      # Audio file upload, validation, storage
│   │   ├── contact_service.py           # Contact CRUD, bulk import, validation, DND check
│   │   ├── campaign_service.py          # Campaign lifecycle, scheduling, status tracking
│   │   ├── calling_engine.py            # Core calling logic: dial, retry, rate limit, concurrency
│   │   ├── tts_service.py               # Google Cloud TTS integration, audio caching
│   │   ├── compliance_service.py        # TRAI DND check, calling hours enforcement, consent tracking
│   │   └── scheduler_service.py         # APScheduler integration, job management
│   │
│   ├── workers/                         # Background workers
│   │   ├── __init__.py
│   │   ├── calling_worker.py            # Main calling loop, queue processing
│   │   └── scheduler_worker.py          # APScheduler startup, job recovery
│   │
│   ├── integrations/                    # Third-party API clients
│   │   ├── __init__.py
│   │   ├── exotel_client.py             # Exotel API wrapper (make_call, get_status)
│   │   ├── google_tts_client.py         # Google Cloud TTS API wrapper
│   │   └── dnd_checker.py              # TRAI NCPR/DND check (if API available)
│   │
│   ├── utils/                           # Utilities
│   │   ├── __init__.py
│   │   ├── security.py                  # JWT encode/decode, password hashing
│   │   ├── file_parser.py              # Excel/CSV parsing, validation
│   │   ├── phone_validator.py           # Indian phone number validation
│   │   ├── rate_limiter.py             # Token bucket rate limiter (Redis-backed)
│   │   └── timezone_utils.py           # IST timezone handling
│   │
│   └── migrations/                      # Alembic database migrations
│       ├── env.py
│       ├── script.py.mako
│       └── versions/
│           └── 001_initial.py
│
├── uploads/                             # Uploaded files
│   ├── audio/                           # Pre-recorded audio files per user
│   │   └── {user_id}/
│   │       ├── a1b2c3d4.mp3
│   │       └── e5f6g7h8.wav
│   └── tts_cache/                       # Generated TTS audio cache
│       └── {hash}.mp3
│
├── tests/                               # Pytest test suite
│   ├── __init__.py
│   ├── conftest.py                      # Test fixtures, test DB setup
│   ├── test_auth.py
│   ├── test_scripts.py
│   ├── test_contacts.py
│   ├── test_campaigns.py
│   ├── test_webhooks.py
│   └── test_calling_engine.py
│
├── alembic.ini                          # Alembic configuration
├── Dockerfile                           # Multi-stage Docker build
├── docker-compose.yml                   # Local dev: backend + postgres + redis
├── requirements.txt                     # Pinned dependencies
├── pyproject.toml                       # Project metadata, tool config
├── .env.example                         # Environment variable template
├── .gitignore
└── README.md
```

### /frontend (Vue 3)

```
frontend/
├── public/
│   └── favicon.ico
│
├── src/
│   ├── main.js                          # Vue app entry point
│   ├── App.vue                          # Root component with router-view
│   ├── router/
│   │   └── index.js                     # Vue Router config, route guards
│   │
│   ├── stores/                          # Pinia stores (state management)
│   │   ├── auth.js                      # Auth state, login/logout, token management
│   │   ├── scripts.js                   # Script CRUD state
│   │   ├── contacts.js                  # Contact list state
│   │   ├── campaigns.js                 # Campaign state
│   │   └── dashboard.js                 # Dashboard stats state
│   │
│   ├── api/                             # API client layer
│   │   ├── client.js                    # Axios instance with interceptors (auth, error handling)
│   │   ├── auth.js                      # Auth API calls
│   │   ├── scripts.js                   # Script API calls
│   │   ├── contacts.js                  # Contact API calls
│   │   ├── campaigns.js                 # Campaign API calls
│   │   └── reports.js                   # Report API calls
│   │
│   ├── views/                           # Page components
│   │   ├── auth/
│   │   │   ├── LoginView.vue
│   │   │   └── RegisterView.vue
│   │   ├── DashboardView.vue            # Main dashboard with campaign stats
│   │   ├── scripts/
│   │   │   ├── ScriptsView.vue          # Script list + editor
│   │   │   └── ScriptEditor.vue         # Rich text editor with variable placeholders + audio upload
│   │   ├── contacts/
│   │   │   ├── ContactsView.vue         # Contact list management
│   │   │   └── BulkUploadModal.vue      # Excel/CSV upload with column mapping
│   │   ├── campaigns/
│   │   │   ├── CampaignsView.vue        # Campaign list + creation
│   │   │   ├── CampaignCreate.vue       # Campaign setup wizard
│   │   │   └── CampaignDetail.vue       # Campaign status, live call tracking
│   │   ├── reports/
│   │   │   └── ReportsView.vue          # Call logs, charts, export
│   │   └── settings/
│   │       └── AccountSettings.vue      # Profile, API keys, preferences
│   │
│   ├── components/                      # Reusable UI components
│   │   ├── layout/
│   │   │   ├── AppHeader.vue
│   │   │   ├── AppSidebar.vue
│   │   │   └── AppFooter.vue
│   │   ├── common/
│   │   │   ├── DataTable.vue            # Generic sortable/filterable table
│   │   │   ├── StatusBadge.vue          # Call status colored badges
│   │   │   ├── ConfirmDialog.vue
│   │   │   ├── FileUpload.vue
│   │   │   ├── AudioUpload.vue          # Audio file upload with drag-drop + preview
│   │   │   └── LoadingSpinner.vue
│   │   └── charts/
│   │       ├── CallStatsChart.vue       # Campaign call statistics
│   │       └── SuccessRateChart.vue     # Success/failure pie chart
│   │
│   ├── composables/                     # Vue 3 composables (reusable logic)
│   │   ├── useAuth.js                   # Auth state + token refresh logic
│   │   ├── useApi.js                    # API call wrapper with error handling
│   │   └── usePagination.js             # Pagination logic
│   │
│   └── assets/
│       ├── styles/
│       │   └── main.css                 # TailwindCSS + custom styles
│       └── images/
│           └── logo.svg
│
├── index.html                           # HTML entry point
├── vite.config.js                       # Vite configuration
├── tailwind.config.js                   # TailwindCSS config
├── postcss.config.js                    # PostCSS config
├── package.json                         # Dependencies
├── .env.example                         # Frontend env vars (VITE_API_BASE_URL)
├── Dockerfile                           # Multi-stage Docker build for nginx
├── nginx.conf                           # Nginx config for production
├── .gitignore
└── README.md
```

---

## 6. PostgreSQL Schema

```sql
-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =============================================
-- USERS TABLE
-- =============================================
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(15),
    full_name VARCHAR(255) NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    exotel_account_sid VARCHAR(100),
    exotel_api_key VARCHAR(100),
    exotel_api_token VARCHAR(100),
    exotel_caller_id VARCHAR(20),
    timezone VARCHAR(50) DEFAULT 'Asia/Kolkata',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_users_email ON users(email);

-- =============================================
-- SCRIPTS TABLE
-- =============================================
CREATE TABLE scripts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    language VARCHAR(10) DEFAULT 'hi-IN',
    tts_voice VARCHAR(100),
    audio_type VARCHAR(10) DEFAULT 'tts',          -- 'tts' or 'uploaded'
    audio_file_path VARCHAR(500),
    audio_file_size INTEGER,
    audio_mime_type VARCHAR(50),
    is_active BOOLEAN DEFAULT FALSE,
    version INTEGER DEFAULT 1,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_scripts_user_id ON scripts(user_id);
CREATE INDEX idx_scripts_user_active ON scripts(user_id, is_active) WHERE is_active = TRUE;
CREATE INDEX idx_scripts_audio_type ON scripts(audio_type);

-- =============================================
-- CONTACT LISTS TABLE
-- =============================================
CREATE TABLE contact_lists (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    contact_count INTEGER DEFAULT 0,
    source VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_contact_lists_user_id ON contact_lists(user_id);

-- =============================================
-- CONTACTS TABLE
-- =============================================
CREATE TABLE contacts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    list_id UUID NOT NULL REFERENCES contact_lists(id) ON DELETE CASCADE,
    phone VARCHAR(15) NOT NULL,
    name VARCHAR(255),
    email VARCHAR(255),
    company VARCHAR(255),
    metadata JSONB,
    dnd_registered BOOLEAN DEFAULT FALSE,
    last_called_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_contacts_list_id ON contacts(list_id);
CREATE INDEX idx_contacts_phone ON contacts(phone);
CREATE INDEX idx_contacts_dnd ON contacts(dnd_registered) WHERE dnd_registered = FALSE;

-- =============================================
-- CAMPAIGNS TABLE
-- =============================================
CREATE TABLE campaigns (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    script_id UUID NOT NULL REFERENCES scripts(id),
    list_id UUID NOT NULL REFERENCES contact_lists(id),
    name VARCHAR(255) NOT NULL,
    status VARCHAR(20) DEFAULT 'draft',
    schedule_type VARCHAR(20) DEFAULT 'immediate',
    scheduled_at TIMESTAMP WITH TIME ZONE,
    cron_expression VARCHAR(100),
    timezone VARCHAR(50) DEFAULT 'Asia/Kolkata',
    max_concurrent_calls INTEGER DEFAULT 5,
    retry_limit INTEGER DEFAULT 3,
    retry_cooldown_minutes INTEGER DEFAULT 30,
    calling_hours_start INTEGER DEFAULT 9,
    calling_hours_end INTEGER DEFAULT 21,
    total_contacts INTEGER DEFAULT 0,
    completed_contacts INTEGER DEFAULT 0,
    successful_contacts INTEGER DEFAULT 0,
    failed_contacts INTEGER DEFAULT 0,
    no_answer_contacts INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_campaigns_user_id ON campaigns(user_id);
CREATE INDEX idx_campaigns_status ON campaigns(status);
CREATE INDEX idx_campaigns_scheduled_at ON campaigns(scheduled_at) WHERE status = 'scheduled';

-- =============================================
-- CALL LOGS TABLE
-- =============================================
CREATE TABLE call_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    campaign_id UUID NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE,
    contact_id UUID NOT NULL REFERENCES contacts(id),
    exotel_call_id VARCHAR(100),
    status VARCHAR(20) NOT NULL,
    duration_seconds INTEGER DEFAULT 0,
    started_at TIMESTAMP WITH TIME ZONE,
    ended_at TIMESTAMP WITH TIME ZONE,
    retry_count INTEGER DEFAULT 0,
    error_message TEXT,
    audio_file_url VARCHAR(500),
    recording_url VARCHAR(500),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_call_logs_campaign_id ON call_logs(campaign_id);
CREATE INDEX idx_call_logs_contact_id ON call_logs(contact_id);
CREATE INDEX idx_call_logs_status ON call_logs(status);
CREATE INDEX idx_call_logs_exotel_call_id ON call_logs(exotel_call_id);
CREATE INDEX idx_call_logs_created_at ON call_logs(created_at DESC);

-- =============================================
-- SCHEDULED JOBS TABLE
-- =============================================
CREATE TABLE scheduled_jobs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    campaign_id UUID NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE,
    apscheduler_job_id VARCHAR(100) NOT NULL,
    job_type VARCHAR(50) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    scheduled_at TIMESTAMP WITH TIME ZONE NOT NULL,
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    last_heartbeat TIMESTAMP WITH TIME ZONE,
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_scheduled_jobs_campaign_id ON scheduled_jobs(campaign_id);
CREATE INDEX idx_scheduled_jobs_status ON scheduled_jobs(status);
CREATE INDEX idx_scheduled_jobs_scheduled_at ON scheduled_jobs(scheduled_at) WHERE status = 'pending';

-- =============================================
-- TTS CACHE TABLE
-- =============================================
CREATE TABLE tts_cache (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    script_hash VARCHAR(64) NOT NULL,
    audio_file_path VARCHAR(500) NOT NULL,
    audio_file_size INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE UNIQUE INDEX idx_tts_cache_hash ON tts_cache(script_hash);
```

### Relationship Summary

```
users 1──→ N scripts
users 1──→ N contact_lists
users 1──→ N campaigns

contact_lists 1──→ N contacts
scripts 1──→ N campaigns
contact_lists 1──→ N campaigns

campaigns 1──→ N call_logs
campaigns 1──→ N scheduled_jobs
contacts 1──→ N call_logs
```

---

## 7. Key API Endpoints

### Authentication

| Method | Endpoint | Description | Request | Response |
|--------|----------|-------------|---------|----------|
| POST | `/api/v1/auth/register` | Create account | `{email, password, full_name, phone}` | `{access_token, token_type, user}` |
| POST | `/api/v1/auth/login` | Login | `{email, password}` | `{access_token, refresh_token, token_type}` |
| POST | `/api/v1/auth/refresh` | Refresh token | `{refresh_token}` | `{access_token}` |
| GET | `/api/v1/auth/me` | Get current user | — | `{id, email, full_name, phone, exotel_caller_id}` |
| PUT | `/api/v1/auth/me` | Update profile | `{full_name, phone, exotel_account_sid, exotel_api_key, exotel_api_token, exotel_caller_id}` | `{user}` |

### Scripts CRUD

| Method | Endpoint | Description | Request | Response |
|--------|----------|-------------|---------|----------|
| GET | `/api/v1/scripts` | List all scripts | `?page=1&limit=20` | `{items: [Script], total, page, pages}` |
| POST | `/api/v1/scripts` | Create script | `{name, content, language, tts_voice, audio_type}` | `{Script}` |
| GET | `/api/v1/scripts/{id}` | Get script | — | `{Script with version history}` |
| PUT | `/api/v1/scripts/{id}` | Update script | `{name, content, language, tts_voice, audio_type}` | `{Script}` (version auto-incremented) |
| POST | `/api/v1/scripts/{id}/activate` | Set as active | — | `{message}` (deactivates others) |
| DELETE | `/api/v1/scripts/{id}` | Delete script | — | `{message}` (cannot delete if active/in-use) |
| POST | `/api/v1/scripts/{id}/audio` | Upload audio file | `multipart/form-data: file` | `{Script with audio fields}` |
| DELETE | `/api/v1/scripts/{id}/audio` | Remove uploaded audio | — | `{Script (audio_type reverts to tts)}` |
| GET | `/api/v1/scripts/{id}/audio/preview` | Stream audio file | — | `audio/mpeg binary` |

**ScriptResponse shape**:
```json
{
  "id": "uuid",
  "name": "Summer Sale Pitch",
  "content": "Namaste {customer_name}! Main {business_name} se baat kar raha hoon...",
  "language": "hi-IN",
  "tts_voice": "hi-IN-Wavenet-A",
  "audio_type": "uploaded",
  "audio_file_path": "/uploads/audio/a1b2c3d4.mp3",
  "audio_file_size": 524288,
  "audio_mime_type": "audio/mpeg",
  "is_active": true,
  "version": 3,
  "created_at": "2026-07-01T10:00:00Z",
  "updated_at": "2026-07-05T14:30:00Z"
}
```

### Contact List Management

| Method | Endpoint | Description | Request | Response |
|--------|----------|-------------|---------|----------|
| GET | `/api/v1/contacts/lists` | List all lists | `?page=1&limit=20` | `{items: [ContactList], total}` |
| POST | `/api/v1/contacts/lists` | Create list | `{name, description}` | `{ContactList}` |
| GET | `/api/v1/contacts/lists/{id}` | Get list + contacts | `?page=1&limit=50` | `{ContactList with contacts}` |
| DELETE | `/api/v1/contacts/lists/{id}` | Delete list | — | `{message}` |
| POST | `/api/v1/contacts/lists/{id}/contacts` | Add single contact | `{phone, name, email?, company?, metadata?}` | `{Contact}` |
| POST | `/api/v1/contacts/upload` | Bulk upload | `multipart/form-data: file, list_id` | `{BulkUploadResponse}` |
| GET | `/api/v1/contacts/upload/validate` | Validate file before import | `multipart/form-data: file` | `{validation_errors: [{row, errors}]}` |

**BulkUploadResponse shape**:
```json
{
  "total_rows": 150,
  "valid_rows": 142,
  "invalid_rows": 8,
  "duplicates_skipped": 3,
  "list_id": "uuid",
  "errors": [
    {"row": 5, "phone": "123", "errors": ["Invalid phone format"]},
    {"row": 12, "phone": "+919999999999", "errors": ["Duplicate number in list"]}
  ]
}
```

**File parsing approach**:
1. Accept `.xlsx` (openpyxl) or `.csv` (pandas)
2. Auto-detect columns: phone, name, email, company
3. Validate each row: phone format (`+91XXXXXXXXXX`), duplicate detection, empty required fields
4. Return per-row validation errors BEFORE confirming import
5. On confirmation, bulk insert valid rows

### Campaign Management

| Method | Endpoint | Description | Request | Response |
|--------|----------|-------------|---------|----------|
| GET | `/api/v1/campaigns` | List campaigns | `?status=running&page=1` | `{items: [Campaign], total}` |
| POST | `/api/v1/campaigns` | Create campaign | `{name, script_id, list_id, ...config}` | `{Campaign}` |
| GET | `/api/v1/campaigns/{id}` | Get campaign detail | — | `{Campaign with stats}` |
| PUT | `/api/v1/campaigns/{id}` | Update campaign | `{name, script_id, ...}` | `{Campaign}` |
| POST | `/api/v1/campaigns/{id}/start` | Start/immediate run | — | `{message, job_id}` |
| POST | `/api/v1/campaigns/{id}/pause` | Pause campaign | — | `{message}` |
| POST | `/api/v1/campaigns/{id}/resume` | Resume campaign | — | `{message}` |
| DELETE | `/api/v1/campaigns/{id}` | Delete campaign | — | `{message}` |
| GET | `/api/v1/campaigns/{id}/call-logs` | Get call logs | `?status=completed&page=1` | `{items: [CallLog], total, stats}` |

**CampaignCreate shape**:
```json
{
  "name": "June Outreach Campaign",
  "script_id": "uuid",
  "list_id": "uuid",
  "schedule_type": "one_time",
  "scheduled_at": "2026-07-11T09:00:00+05:30",
  "max_concurrent_calls": 5,
  "retry_limit": 3,
  "retry_cooldown_minutes": 30,
  "calling_hours_start": 9,
  "calling_hours_end": 21
}
```

### Webhooks (Exotel Status Callback)

| Method | Endpoint | Description | Request | Response |
|--------|----------|-------------|---------|----------|
| POST | `/api/v1/webhooks/exotel/status` | Receive call status | Exotel webhook payload | `200 OK` |
| POST | `/api/v1/webhooks/exotel/recording` | Receive recording URL | Exotel webhook payload | `200 OK` |

**Webhook payload handling**:
1. Verify webhook signature (Exotel sends `X-Exotel-Signature`)
2. Parse call SID, status, duration
3. Update `call_logs` table
4. Update campaign counters (completed, failed, etc.)
5. If status is terminal (`completed`, `failed`, `no-answer`) → check if retries needed → re-queue

### Reports

| Method | Endpoint | Description | Request | Response |
|--------|----------|-------------|---------|----------|
| GET | `/api/v1/reports/dashboard` | Dashboard summary | — | `{total_campaigns, active_campaigns, total_calls, success_rate, ...}` |
| GET | `/api/v1/reports/campaigns/{id}` | Campaign detailed stats | — | `{status_distribution, hourly_breakdown, ...}` |
| POST | `/api/v1/reports/export` | Export call logs | `{campaign_id, format: 'csv'|'xlsx', filters}` | `{download_url}` |

---

## 8. Scheduling & Reliability Mechanism

### How APScheduler + PostgreSQL Guarantees Reliability

```
┌─────────────────────────────────────────────────────────────────┐
│                    SCHEDULING FLOW                               │
│                                                                  │
│  User creates campaign with schedule "5 days from now"          │
│         │                                                        │
│         ▼                                                        │
│  1. CampaignService creates Campaign record (status: scheduled) │
│         │                                                        │
│         ▼                                                        │
│  2. SchedulerService.add_job()                                  │
│     - Creates APScheduler job with trigger='date'               │
│     - run_date = scheduled_at                                   │
│     - jobstore = SQLAlchemyJobStore(postgres_url)               │
│     - APScheduler writes job to `apscheduler_jobs` table        │
│         │                                                        │
│         ▼                                                        │
│  3. APScheduler also creates ScheduledJob audit record          │
│     in our `scheduled_jobs` table                               │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │  SERVER RESTART / DOWNTIME SCENARIO                        │  │
│  │                                                            │  │
│  │  When FastAPI restarts:                                    │  │
│  │  1. APScheduler starts in lifespan()                      │  │
│  │  2. Loads ALL jobs from PostgreSQL apscheduler_jobs table  │  │
│  │  3. Checks each job's next_run_time                       │  │
│  │  4. If next_run_time < now → MISFIRE GRACE TIME applies   │  │
│  │  5. Jobs within grace period → executed immediately        │  │
│  │  6. Jobs past grace period → logged as MISSED              │  │
│  │  7. scheduled_jobs table updated with status               │  │
│  └────────────────────────────────────────────────────────────┘  │
│                                                                  │
│  APScheduler config:                                            │
│  - misfire_grace_time = 3600 (1 hour)                           │
│  - job_defaults.coalesce = True                                  │
│  - job_defaults.max_instances = 1                                │
│  - job_defaults.standalone = False                               │
└─────────────────────────────────────────────────────────────────┘
```

### Campaign Execution Flow

```
┌──────────────────────────────────────────────────────────────────┐
│                CAMPAIGN EXECUTION PIPELINE                        │
│                                                                   │
│  1. Scheduler fires campaign_start job                           │
│         │                                                         │
│         ▼                                                         │
│  2. CallingEngine.start_campaign(campaign_id)                    │
│     - Validates: calling hours, script exists, contacts exist    │
│     - Sets campaign status: running                              │
│     - Loads contact list from DB                                  │
│     - Filters: skip dnd_registered, skip already-called-today   │
│         │                                                         │
│         ▼                                                         │
│  3. For each contact:                                             │
│     a. Check calling hours (9 AM - 9 PM IST)                    │
│     b. Check rate limit (max_concurrent_calls)                   │
│     c. Resolve audio:                                             │
│        - If script.audio_type == "uploaded": use audio URL      │
│        - If script.audio_type == "tts": generate TTS (cached)   │
│     d. Call Exotel API: make_outbound_call(from, to, audio_url) │
│     e. Create call_log record (status: dialing)                 │
│         │                                                         │
│         ▼                                                         │
│  4. Exotel sends webhook callbacks:                              │
│     - ringing → call_logs.status = ringing                       │
│     - in-progress → call_logs.status = in-progress              │
│     - completed → call_logs.status = completed                   │
│     - no-answer → call_logs.status = no-answer                   │
│       → IF retry_count < retry_limit → re-queue after cooldown  │
│     - busy → call_logs.status = busy                             │
│       → IF retry_count < retry_limit → re-queue after cooldown  │
│     - failed → call_logs.status = failed                         │
│       → Log error_message                                        │
│         │                                                         │
│         ▼                                                         │
│  5. When all contacts processed:                                 │
│     - Campaign status: completed                                 │
│     - Final stats updated                                        │
│     - User notified (optional: email/dashboard notification)     │
└──────────────────────────────────────────────────────────────────┘
```

### Calling Engine Concurrency & Rate Limiting

```python
class CallingEngine:
    def __init__(self):
        self.semaphore = asyncio.Semaphore(MAX_CONCURRENT_CALLS)
        self.rate_limiter = TokenBucketRedis(
            max_tokens=20,
            refill_rate=1/3
        )

    async def process_campaign(self, campaign_id):
        campaign = await self.get_campaign(campaign_id)
        contacts = await self.get_contacts(campaign.list_id)

        eligible = [c for c in contacts if not c.dnd_registered
                     and not self.called_today(c, campaign_id)]

        for contact in eligible:
            await self.call_queue.put((campaign_id, contact.id))

        workers = [self.call_worker(campaign) for _ in range(campaign.max_concurrent_calls)]
        await asyncio.gather(*workers)

    async def prepare_audio(self, script, contact):
        if script.audio_type == "uploaded":
            return self.get_audio_public_url(script.audio_file_path)
        elif script.audio_type == "tts":
            interpolated_text = self.interpolate(script.content, contact)
            cached_audio = await self.tts_service.get_or_generate(
                text=interpolated_text,
                language=script.language,
                voice=script.tts_voice
            )
            return cached_audio.public_url

    async def call_worker(self, campaign):
        while not self.call_queue.empty():
            campaign_id, contact_id = await self.call_queue.get()

            async with self.semaphore:
                await self.rate_limiter.acquire()

                if not self.within_calling_hours(campaign):
                    await asyncio.sleep(60)
                    continue

                script = await self.get_script(campaign.script_id)
                contact = await self.get_contact(contact_id)
                audio_url = await self.prepare_audio(script, contact)

                result = await self.exotel_client.make_call(
                    from_=campaign.user.exotel_caller_id,
                    to=contact.phone,
                    audio_url=audio_url
                )

                await self.create_call_log(campaign_id, contact_id, result)
                self.call_queue.task_done()
```

---

## 9. Pre-Recorded Audio Upload Feature

### How It Works

```
┌─────────────────────────────────────────────────────────────────┐
│                SCRIPT AUDIO MODES                                │
│                                                                  │
│  User creates/edits script with TWO options:                    │
│                                                                  │
│  Option A: TEXT-TO-SPEECH (default)                             │
│  ┌──────────────────────────────────────────────┐               │
│  │  Script content: "Namaste {customer_name}!..."│               │
│  │  Language: Hindi (hi-IN)                      │               │
│  │  Voice: hi-IN-Wavenet-A                      │               │
│  │  Audio: [Generated on-the-fly via Google TTS] │               │
│  └──────────────────────────────────────────────┘               │
│                                                                  │
│  Option B: PRE-RECORDED AUDIO (FREE — no TTS cost)             │
│  ┌──────────────────────────────────────────────┐               │
│  │  Script content: (display only, for reference)│               │
│  │  Audio file: pitch_final.mp3 [uploaded by    │               │
│  │              user]                            │               │
│  │  Audio: [Played directly from uploaded file]  │               │
│  └──────────────────────────────────────────────┘               │
│                                                                  │
│  When calling engine runs:                                      │
│  IF audio_type == "uploaded":                                   │
│      → Use audio_file_url directly with Exotel API              │
│  IF audio_type == "tts":                                        │
│      → Generate TTS audio, cache, use cached URL                │
└─────────────────────────────────────────────────────────────────┘
```

### Database Schema

Add these columns to the `scripts` table:

```sql
ALTER TABLE scripts ADD COLUMN audio_type VARCHAR(10) DEFAULT 'tts';
    -- 'tts' or 'uploaded'

ALTER TABLE scripts ADD COLUMN audio_file_path VARCHAR(500);
    -- Path to uploaded audio file (e.g., /uploads/audio/uuid.mp3)

ALTER TABLE scripts ADD COLUMN audio_file_size INTEGER;
    -- File size in bytes

ALTER TABLE scripts ADD COLUMN audio_mime_type VARCHAR(50);
    -- 'audio/mpeg', 'audio/wav', 'audio/ogg'

CREATE INDEX idx_scripts_audio_type ON scripts(audio_type);
```

### Audio Upload Service

```python
class AudioUploadService:
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
    ALLOWED_TYPES = {
        "audio/mpeg": ".mp3",
        "audio/wav": ".wav",
        "audio/x-wav": ".wav",
        "audio/ogg": ".ogg",
    }

    async def validate_and_save(self, file: UploadFile, user_id: str):
        content = await file.read()
        if len(content) > self.MAX_FILE_SIZE:
            raise ValueError(f"File too large. Max: {self.MAX_FILE_SIZE // (1024*1024)}MB")

        mime = file.content_type
        if mime not in self.ALLOWED_TYPES:
            raise ValueError(f"Unsupported format. Allowed: MP3, WAV, OGG")

        ext = self.ALLOWED_TYPES[mime]
        file_path = self.save_to_disk(content, user_id, ext)

        duration = self.get_audio_duration(file_path)
        if duration > 300:  # 5 minutes max
            raise ValueError("Audio too long. Max: 5 minutes")

        return file_path, len(content), mime
```

### Exotel API Integration for Pre-Recorded Audio

```python
async def make_call(self, from_: str, to: str, audio_url: str):
    response = await self.http.post(
        f"{self.base_url}/v1/Accounts/{self.account_sid}/Calls/connect",
        auth=(self.api_key, self.api_token),
        data={
            "From": from_,
            "To": to,
            "CallerId": self.caller_id,
            "CallType": "trans",
            "StartPlaybackToNew": "Callee",
            "StartPlaybackValueNew": audio_url,   # Pre-recorded audio URL
            "StatusCallback": self.webhook_url,
            "StatusCallbackEvents": ["terminal", "answered"],
            "Record": "true"
        }
    )
    return response.json()
```

**Key Exotel parameter**: `StartPlaybackValueNew` — plays a pre-recorded audio file (MP3/WAV) from a public URL to the callee immediately after they answer. No TTS involved.

### Frontend Script Editor UI

```
┌─────────────────────────────────────────────────────┐
│  Script: Summer Sale Pitch                          │
│                                                     │
│  Audio Source:  (●) Text-to-Speech  ( ) Upload Audio│
│                                                     │
│  ── If TTS selected ──                              │
│  Language: [Hindi ▼]  Voice: [Wavenet-A ▼]         │
│                                                     │
│  ── If Upload selected ──                           │
│  ┌─────────────────────────────────────────────┐    │
│  │  Drag & drop audio file here                │    │
│  │     or click to browse                      │    │
│  │                                             │    │
│  │  Supported: MP3, WAV, OGG (max 10MB)       │    │
│  │  Currently: pitch_v2.mp3 (456 KB)          │    │
│  │  [Preview]  [Remove]                        │    │
│  └─────────────────────────────────────────────┘    │
│                                                     │
│  Script Content (for reference/display):            │
│  ┌─────────────────────────────────────────────┐    │
│  │ Namaste {customer_name}! Main ABC Corp se    │    │
│  │ baat kar raha hoon. Humari nayi service...   │    │
│  └─────────────────────────────────────────────┘    │
│                                                     │
│  [Save Script]  [Save & Set Active]                 │
└─────────────────────────────────────────────────────┘
```

### Audio Format Recommendations

| Format | Recommended? | Why |
|--------|-------------|-----|
| **MP3 (128kbps, 8kHz mono)** | Best | Smallest file, telephony-optimized, Exotel supports |
| **WAV (8kHz, 16-bit, mono)** | Good | No compression loss, but larger files |
| **OGG Vorbis** | OK | Good compression, but some providers don't support |

**User guidance**: Record audio at 8kHz sample rate (telephony standard). Most phone recordings are already at this quality. Tools like Audacity (free) can convert.

### Updated Cost Table

| Component | With TTS | With Uploaded Audio |
|-----------|----------|-------------------|
| Google Cloud TTS | Free (1M chars/mo) | ₹0 (not used) |
| Exotel telephony | ~₹1,667/month | ~₹1,667/month |
| Hosting | ₹0-500/month | ₹0-500/month |
| **Total** | **~₹1,700-2,200/month** | **~₹1,700-2,200/month** |

**The only unavoidable cost is Exotel telephony (₹0.30-0.50/min per call).** Everything else can be free.

---

## 10. Phased Implementation Roadmap

### Phase 1: Foundation (Weeks 1-3) — "Working Skeleton"

**Goal**: Auth, Script Management, basic contact upload — deployable MVP skeleton

| Task | Details | Deliverable |
|------|---------|-------------|
| 1.1 Project setup | FastAPI + Vue 3 boilerplate, Docker Compose, Alembic | Working local dev environment |
| 1.2 Auth system | JWT auth, register/login, password hashing | Auth-protected routes |
| 1.3 Script CRUD | Create/edit/delete scripts, version tracking, one active | Script management working |
| 1.4 Database schema | All tables created via Alembic migrations | Clean PostgreSQL schema |
| 1.5 Basic frontend | Login/Register pages, Scripts list + editor | Vue frontend with auth |

**Tech work**:
- `pip install fastapi uvicorn sqlalchemy[asyncio] asyncpg alembic pydantic python-jose passlib python-multipart`
- `npm create vue@latest frontend/` with Pinia, Vue Router, TailwindCSS
- Docker Compose with postgres:16 + redis:alpine

**Milestone**: User can register, login, create/edit/save business scripts.

---

### Phase 2: Contact Management (Weeks 3-5) — "Data Ingestion"

**Goal**: Upload contacts, validate, manage lists

| Task | Details | Deliverable |
|------|---------|-------------|
| 2.1 Contact list CRUD | Create/delete lists, add individual contacts | Contact list management |
| 2.2 Bulk upload | Excel/CSV parser with column mapping | Bulk upload with validation |
| 2.3 Validation engine | Phone format check, duplicate detection, per-row errors | Before-import validation |
| 2.4 Frontend contacts page | List view, upload modal, column mapper | Contact management UI |
| 2.5 Phone validation | Indian phone number regex (`+91XXXXXXXXXX`, 10-digit) | Robust validation |

**Libraries**:
- `openpyxl` for Excel parsing (lightweight, no pandas needed)
- `chardet` for CSV encoding detection
- Custom `phone_validator.py` with Indian number patterns

**Milestone**: User can upload Excel/CSV of contacts, see validation errors per row, confirm import.

---

### Phase 3: Audio & TTS Integration (Weeks 5-7) — "Voice Generation"

**Goal**: Generate speech from scripts OR use pre-recorded audio

| Task | Details | Deliverable |
|------|---------|-------------|
| 3.1 Audio upload service | File upload, validation (MP3/WAV/OGG, 10MB max), storage | Pre-recorded audio support |
| 3.2 Audio preview | Frontend play/preview before calling | UX: hear before calling |
| 3.3 Google Cloud TTS client | API integration, auth, audio generation | Working TTS service (optional) |
| 3.4 Variable interpolation | Replace `{customer_name}`, `{business_name}` etc. | Personalized scripts (TTS only) |
| 3.5 Audio caching | SHA256 hash of (script + voice + language) → cache | No redundant TTS calls |
| 3.6 Language support | Hindi, Tamil, Telugu, Bengali, Marathi, English | Multi-lingual TTS (optional) |

**Audio upload validation**:
- Max file size: 10 MB
- Allowed formats: MP3, WAV, OGG
- Max duration: 5 minutes (telephony limit)
- Save to `uploads/audio/{user_id}/` directory

**Milestone**: System can use either uploaded audio files or TTS-generated audio for calls.

---

### Phase 4: Calling Engine (Weeks 7-10) — "Core Calling"

**Goal**: Make actual outbound calls via Exotel, track status

| Task | Details | Deliverable |
|------|---------|-------------|
| 4.1 Exotel client | API wrapper for outbound calls | make_call(), get_status() |
| 4.2 Audio resolution | Choose uploaded vs TTS audio based on script config | Intelligent audio routing |
| 4.3 Webhook receiver | Receive and process call status callbacks | Real-time status tracking |
| 4.4 Call log management | Create/update call logs per contact | Complete call history |
| 4.5 Concurrency control | asyncio.Semaphore for max concurrent calls | Rate limiting |
| 4.6 Retry logic | Configurable retry for no-answer/busy/failed | Automatic retries |
| 4.7 Campaign service | Create/start/pause/resume campaigns | Campaign lifecycle |
| 4.8 Frontend campaign page | Campaign creation wizard, live status | Campaign management UI |

**Exotel integration**:
```python
class ExotelClient:
    async def make_call(self, from_: str, to: str, audio_url: str):
        response = await self.http.post(
            f"{self.base_url}/v1/Accounts/{self.account_sid}/Calls/connect",
            auth=(self.api_key, self.api_token),
            data={
                "From": from_,
                "To": to,
                "CallerId": self.caller_id,
                "CallType": "trans",
                "StartPlaybackToNew": "Callee",
                "StartPlaybackValueNew": audio_url,
                "StatusCallback": self.webhook_url,
                "StatusCallbackEvents": ["terminal", "answered"],
                "Record": "true"
            }
        )
        return response.json()
```

**Milestone**: User can start a campaign, system dials numbers, plays script (uploaded or TTS), tracks status.

---

### Phase 5: Scheduling & Reliability (Weeks 10-12) — "Set & Forget"

**Goal**: Schedule campaigns for future execution, survive restarts

| Task | Details | Deliverable |
|------|---------|-------------|
| 5.1 APScheduler integration | PostgreSQL job store, lifespan management | Persistent scheduling |
| 5.2 One-time scheduling | Schedule campaign for specific date/time | "Run in 5 days" |
| 5.3 Campaign scheduler API | POST /campaigns/{id}/schedule | Schedule via API |
| 5.4 Recovery on restart | APScheduler auto-loads missed jobs | No lost campaigns |
| 5.5 Calling hours enforcement | 9 AM - 9 PM IST check before each call | Compliance |
| 5.6 Scheduled jobs dashboard | View upcoming/past scheduled jobs | Transparency |

**APScheduler configuration**:
```python
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore

scheduler = AsyncIOScheduler(
    jobstores={
        'default': SQLAlchemyJobStore(url=settings.DATABASE_URL_SYNC)
    },
    job_defaults={
        'coalesce': True,
        'max_instances': 1,
        'misfire_grace_time': 3600
    }
)
```

**Milestone**: Campaign scheduled for 5 days later will execute automatically, even if server restarts.

---

### Phase 6: Dashboard & Reports (Weeks 12-13) — "Visibility"

**Goal**: Complete dashboard with stats, charts, export

| Task | Details | Deliverable |
|------|---------|-------------|
| 6.1 Dashboard stats | Campaign overview, call stats, success rates | Real-time dashboard |
| 6.2 Call log table | Filterable, sortable, paginated call logs | Detailed call history |
| 6.3 Charts | Call volume, success/failure, by-status breakdown | Visual analytics |
| 6.4 Export | CSV/XLSX export of call logs | Report generation |
| 6.5 TRAI compliance | DND scrubbing, consent tracking, call records | Legal compliance |

**Milestone**: Full dashboard showing campaign performance, exportable reports.

---

### Phase 7: Production Hardening (Weeks 13-15) — "Ship It"

**Goal**: Security, deployment, monitoring

| Task | Details | Deliverable |
|------|---------|-------------|
| 7.1 Security hardening | CORS, rate limiting, input validation, secrets mgmt | Production security |
| 7.2 Docker + deploy | Dockerfile, docker-compose.prod, env config | Deployable container |
| 7.3 Frontend deploy | Vercel deployment, env vars | Public frontend |
| 7.4 Backend deploy | Render/Railway deployment | Public API |
| 7.5 Monitoring | Structured logging, error tracking (Sentry free) | Observability |
| 7.6 CI/CD | GitHub Actions: lint, test, build | Automated pipeline |

**Cost at this stage**:
| Component | Provider | Monthly Cost |
|-----------|----------|-------------|
| Backend | Render free tier | ₹0 (sleeps after 15min inactivity) |
| Frontend | Vercel free tier | ₹0 |
| Database | Neon free tier | ₹0 (0.5 GB) |
| Redis | Upstash free tier | ₹0 (10K cmds/day) |
| TTS | Google Cloud free tier | ₹0 (1M chars/month) — or ₹0 if using uploaded audio |
| Telephony | Exotel Dabbler | ~₹1,667/month |
| **Total** | | **~₹1,667/month** |

---

## 11. Key Risks & Edge Cases

### Regulatory Compliance (India)

| Risk | Mitigation |
|------|-----------|
| **TRAI DND/NCPR violations** | Mandatory DND scrubbing before every campaign. Check `dnd_registered` field on contacts. |
| **DLT registration required** | User must register as telemarketer with their telecom provider and get 140-series number. Platform prompts during setup. |
| **Calling hours (9 AM - 9 PM IST)** | System enforces `calling_hours_start` and `calling_hours_end`. No calls outside window. |
| **AI disclosure** | Script must open with "This is an automated call from [Business]" — enforced in script template. |
| **Consent records** | Contact import timestamps + consent flag. Campaign logs prove consent. |
| **Penalties (₹2-10 lakh)** | Proper compliance architecture prevents this. Include DND scrub, registered numbers, consent tracking. |
| **DPDPA 2023 (data protection)** | Data encryption at rest, user can delete their data, no data sharing with third parties. |

### Technical Edge Cases

| Risk | Mitigation |
|------|-----------|
| **Exotel throttling/rate limits** | Token bucket rate limiter (Redis). Max 20 calls/minute configurable. Respect provider limits (200/min). |
| **Invalid phone numbers** | Regex validation before import. Re-check before dialing. Log + skip invalid. |
| **Timezone issues** | All times stored as UTC in DB. Display in IST. Scheduling uses timezone-aware datetimes. |
| **Server restart during campaign** | APScheduler persists jobs in PostgreSQL. On restart, recover missed jobs within grace period. |
| **TTS API failure** | Cache generated audio. Fallback to pre-recorded audio if TTS fails 3 times. |
| **Exotel webhook delays** | Polling fallback: if no webhook in 5 minutes, query Exotel API for status. |
| **Duplicate calls to same number** | Track `last_called_at` on contacts. Prevent same-number calls within configurable cooldown. |
| **Script changes mid-campaign** | Campaign snapshots script at creation time. Script edits don't affect running campaigns. |
| **Long-running campaigns** | Campaigns process contacts in batches. Each batch is a DB transaction. Partial progress saved. |
| **Contact list deletion** | CASCADE delete. Campaign referencing list gets status: `failed`. |

### Audio Upload Edge Cases

| Risk | Mitigation |
|------|-----------|
| **Corrupted audio files** | Validate file integrity on upload. ffprobe to check duration and format. |
| **Unsupported formats** | Whitelist only MP3, WAV, OGG. Reject others with clear error message. |
| **Large files** | 10 MB max limit. Show progress bar during upload. |
| **Audio too long** | 5 minute max for telephony. Warn user if exceeded. |
| **File storage running out** | Monitor disk usage. Implement cleanup of old unused audio files. |
| **Audio not playable by Exotel** | Test with Exotel's supported formats. Prefer MP3 (most compatible). |

### Cost Risks

| Risk | Mitigation |
|------|-----------|
| **Telephony costs exceeding budget** | Set per-campaign credit limit. Alert when 80% credits used. Pause on limit reached. |
| **TTS free tier exhaustion** | Monitor usage. Switch to uploaded audio or Sarvam AI (₹30/10K chars). |
| **Render free tier sleep** | Background worker needs always-on. Consider Railway ($5 credit) or VPS for worker process. |
| **Neon free tier 0.5 GB limit** | Aggressive cleanup of old call_logs. Archive to S3 after 90 days. |

---

## 12. Dependency Lists

### Backend (requirements.txt)

```
fastapi==0.115.0
uvicorn[standard]==0.30.0
pydantic==2.9.0
pydantic-settings==2.5.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.9
sqlalchemy[asyncio]==2.0.35
asyncpg==0.29.0
alembic==1.13.0
httpx==0.27.0
openpyxl==3.1.5
chardet==5.2.0
apscheduler==3.10.4
google-cloud-texttospeech==2.16.0
python-dotenv==1.0.1
structlog==24.4.0
pyotp==2.9.0
```

### Frontend (package.json dependencies)

```json
{
  "vue": "^3.5.0",
  "vue-router": "^4.4.0",
  "pinia": "^2.2.0",
  "axios": "^1.7.0",
  "tailwindcss": "^3.4.0",
  "@vueuse/core": "^11.0.0",
  "chart.js": "^4.4.0",
  "vue-chartjs": "^5.3.0",
  "papaparse": "^5.4.0",
  "xlsx": "^0.18.0"
}
```

---

## 13. Environment Configuration

### .env.example (Backend)

```env
# Backend
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/calling_agent
DATABASE_URL_SYNC=postgresql://user:pass@localhost:5432/calling_agent
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your-super-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Exotel
EXOTEL_ACCOUNT_SID=your_account_sid
EXOTEL_API_KEY=your_api_key
EXOTEL_API_TOKEN=your_api_token
EXOTEL_CALLER_ID=+91XXXXXXXXXX
EXOTEL_BASE_URL=https://api.exotel.com/v1

# Google Cloud TTS (optional — not needed if using uploaded audio only)
GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account.json
TTS_LANGUAGE_CODE=hi-IN
TTS_VOICE_NAME=hi-IN-Wavenet-A

# Upload settings
MAX_UPLOAD_SIZE_MB=10
UPLOAD_DIR=uploads

# Frontend
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

### .env.example (Frontend)

```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_APP_NAME=CallingAgent
```

---

## 14. TRAI Compliance (India)

### Required Registrations

| Requirement | Details | Cost | Timeline |
|-------------|---------|------|----------|
| **Telemarketer Registration** | Register with your telecom operator as a telemarketer | ~₹5,900 + GST per operator | 3-7 business days |
| **DLT Platform Registration** | Register business entity on Jio/Airtel/Vi/BSNL DLT platform | ~₹5,900 per operator | 3-7 business days each |
| **140-series Number** | Get registered virtual number for commercial calls | Included in Exotel plan | Immediate with Exotel |
| **Header Registration** | Register alphanumeric sender ID (e.g., "MYBIZ") | ~₹5,900 per operator | 3-7 business days |

### Compliance Checklist

- [ ] Register as telemarketer with TRAI via telecom operator
- [ ] Register business on DLT platform (Jio, Airtel, Vi, BSNL)
- [ ] Get 140-series virtual number (via Exotel)
- [ ] Register caller ID headers (alphanumeric business name)
- [ ] Implement DND/NCPR scrubbing before every campaign
- [ ] Enforce calling hours: 9 AM to 9 PM IST only
- [ ] Add AI disclosure at start of every automated call
- [ ] Maintain consent records for all contacted numbers
- [ ] Store call records (CDR) for minimum 12 months
- [ ] Display valid caller ID on all outbound calls
- [ ] Honor opt-out requests immediately

### Calling Hours Enforcement

```python
def is_within_calling_hours(campaign) -> bool:
    """Check if current time is within allowed calling hours (IST)"""
    now = datetime.now(IST timezone)
    current_hour = now.hour
    return campaign.calling_hours_start <= current_hour < campaign.calling_hours_end
```

### DND Scrubbing

```python
async def scrub_dnd_contacts(contacts: List[Contact]) -> List[Contact]:
    """Remove contacts registered on DND/NCPR"""
    eligible = []
    for contact in contacts:
        if not contact.dnd_registered:
            eligible.append(contact)
        else:
            logger.info(f"Skipping DND-registered contact: {contact.phone}")
    return eligible
```

---

## Summary

This plan delivers a production-grade, India-optimized calling platform with:

- **Two audio modes**: TTS (Google Cloud free tier) or pre-recorded audio upload (zero TTS cost)
- **Zero hosting cost** during development (all free tiers)
- **~₹1,667/month** in production (mostly Exotel telephony)
- **TRAI-compliant** architecture with DND scrubbing, calling hours, consent tracking
- **Reliable scheduling** via APScheduler + PostgreSQL (survives restarts)
- **Scalable** from 50 to 500+ calls/day without redesign

The only unavoidable cost is Exotel telephony charges (₹0.30-0.50/min per call), which is required for any outbound calling system.
