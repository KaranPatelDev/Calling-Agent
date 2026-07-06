# Calling Agent Platform - Setup & Run Commands

## Prerequisites

**For Local Development (no Docker):**
- **Python 3.12** (NOT 3.13 or 3.14 — asyncpg and pydantic-core don't have wheels for newer versions)
- Node.js 18+
- PostgreSQL (running locally)
- Git

**For Docker:**
- Python 3.12+
- Node.js 18+
- Docker & Docker Compose
- Git

> **IMPORTANT**: Use Python 3.12 specifically. Python 3.13/3.14 will fail to install asyncpg and pydantic-core because they require C++ build tools that most systems don't have.

---

## 1. Clone & Navigate

```bash
cd "E:\Calling Agent Static"
```

---

## 2. PostgreSQL Local Setup (Required for Without-Docker)

### Install PostgreSQL

#### Windows

1. Download installer: `https://www.postgresql.org/download/windows/`
2. Run the installer
3. During setup:
   - Port: `5432` (default)
   - Set superuser password: `postgres` (or your choice)
   - Complete installation

Add PostgreSQL to PATH (if not added by installer):

```powershell
# PowerShell - add to system PATH permanently
$pgPath = "C:\Program Files\PostgreSQL\16\bin"
$currentPath = [Environment]::GetEnvironmentVariable("Path", "User")
if ($currentPath -notlike "*$pgPath*") {
    [Environment]::SetEnvironmentVariable("Path", "$currentPath;$pgPath", "User")
}
```

Or manually: System Properties -> Environment Variables -> Path -> Edit -> Add `C:\Program Files\PostgreSQL\16\bin`

#### macOS

```bash
# Using Homebrew (recommended)
brew install postgresql@16

# Start the service
brew services start postgresql@16

# Verify it's running
pg_isready
```

#### Linux (Ubuntu/Debian)

```bash
# Install
sudo apt update
sudo apt install postgresql postgresql-contrib

# Start the service
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Verify it's running
sudo systemctl status postgresql
```

#### Linux (CentOS/RHEL/Fedora)

```bash
# Install
sudo dnf install postgresql-server postgresql-contrib

# Initialize database
sudo postgresql-setup --initdb

# Start the service
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

---

### Create Database & User

#### Windows (psql in Command Prompt)

```cmd
psql -U postgres -c "CREATE DATABASE calling_agent;"
psql -U postgres -c "CREATE USER calling_agent WITH PASSWORD 'calling_agent_secret';"
psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE calling_agent TO calling_agent;"
psql -U postgres -d calling_agent -c "GRANT ALL ON SCHEMA public TO calling_agent;"
```

#### Windows (PowerShell)

```powershell
psql -U postgres -c "CREATE DATABASE calling_agent;"
psql -U postgres -c "CREATE USER calling_agent WITH PASSWORD 'calling_agent_secret';"
psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE calling_agent TO calling_agent;"
psql -U postgres -d calling_agent -c "GRANT ALL ON SCHEMA public TO calling_agent;"
```

#### macOS

```bash
# Using default 'postgres' user (no password prompt with Homebrew)
psql -d postgres -c "CREATE DATABASE calling_agent;"
psql -d postgres -c "CREATE USER calling_agent WITH PASSWORD 'calling_agent_secret';"
psql -d postgres -c "GRANT ALL PRIVILEGES ON DATABASE calling_agent TO calling_agent;"
psql -d postgres -d calling_agent -c "GRANT ALL ON SCHEMA public TO calling_agent;"
```

#### Linux

```bash
# Switch to postgres user
sudo -u postgres psql -c "CREATE DATABASE calling_agent;"
sudo -u postgres psql -c "CREATE USER calling_agent WITH PASSWORD 'calling_agent_secret';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE calling_agent TO calling_agent;"
sudo -u postgres psql -d calling_agent -c "GRANT ALL ON SCHEMA public TO calling_agent;"
```

#### Verify Database Was Created

```bash
# Windows
psql -U postgres -c "\l"

# macOS/Linux
psql -d postgres -c "\l"
```

Expected output should list `calling_agent` database.

#### Connect to the New Database (Test)

```bash
# Windows
psql -U calling_agent -d calling_agent -h localhost

# macOS
psql -U calling_agent -d calling_agent -h localhost

# Linux
psql -U calling_agent -d calling_agent -h localhost
```

If prompted for password, enter: `calling_agent_secret`

Run `\dt` to list tables (empty before migrations). Type `\q` to quit.

---

### Common PostgreSQL Commands

```bash
# Check if PostgreSQL is running
# Windows:
pg_isready
# macOS/Linux:
pg_isready -h localhost -p 5432

# List all databases
psql -U postgres -c "\l"

# Connect to a database
psql -U calling_agent -d calling_agent -h localhost

# List all tables in current database
\dt

# List all users
psql -U postgres -c "\du"

# Drop database (if you need a fresh start)
psql -U postgres -c "DROP DATABASE IF EXISTS calling_agent;"

# Drop and recreate everything
psql -U postgres -c "DROP DATABASE IF EXISTS calling_agent;"
psql -U postgres -c "DROP USER IF EXISTS calling_agent;"
psql -U postgres -c "CREATE DATABASE calling_agent;"
psql -U postgres -c "CREATE USER calling_agent WITH PASSWORD 'calling_agent_secret';"
psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE calling_agent TO calling_agent;"
psql -U postgres -d calling_agent -c "GRANT ALL ON SCHEMA public TO calling_agent;"
```

---

### Troubleshooting PostgreSQL

```bash
# Error: role "calling_agent" does not exist
# -> Run the CREATE USER command above

# Error: database "calling_agent" does not exist
# -> Run the CREATE DATABASE command above

# Error: permission denied for schema public
# -> Run the GRANT ALL ON SCHEMA command above

# Error: connection refused
# -> PostgreSQL is not running. Start it:
# Windows: net start postgresql-x64-16 (or your version)
# macOS: brew services start postgresql@16
# Linux: sudo systemctl start postgresql

# Error: password authentication failed
# -> Check pg_hba.conf (PostgreSQL config directory):
#    - Windows: C:\Program Files\PostgreSQL\16\data\pg_hba.conf
#    - macOS: /opt/homebrew/var/postgresql@16/pg_hba.conf
#    - Linux: /etc/postgresql/16/main/pg_hba.conf
#    Ensure these lines exist:
#    local   all   all                 md5
#    host    all   all   127.0.0.1/32  md5
#    host    all   all   ::1/128       md5

# After editing pg_hba.conf, restart PostgreSQL:
# Windows: net restart postgresql-x64-16
# macOS: brew services restart postgresql@16
# Linux: sudo systemctl restart postgresql
```

---

## 3. Backend Setup (After PostgreSQL is Ready)

---

### OPTION A: WITHOUT DOCKER (Local Development)

#### Step 1 - Create Virtual Environment

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate it
# Windows CMD:
venv\Scripts\activate
# Windows PowerShell:
.\venv\Scripts\Activate.ps1
# macOS/Linux:
source venv/bin/activate
```

#### Step 2 - Install Dependencies

```bash
pip install -r requirements.txt
```

#### Step 3 - Setup PostgreSQL

Make sure PostgreSQL is installed and running on your machine.

```bash
# Connect to PostgreSQL as superuser
psql -U postgres

# Inside psql, run these SQL commands:
CREATE DATABASE calling_agent;
CREATE USER calling_agent WITH PASSWORD 'calling_agent_secret';
GRANT ALL PRIVILEGES ON DATABASE calling_agent TO calling_agent;
\c calling_agent
GRANT ALL ON SCHEMA public TO calling_agent;
\q
```

If you don't have `psql` in PATH, use pgAdmin or any PostgreSQL GUI tool to run the above SQL.

#### Step 4 - Configure Environment

```bash
# The .env file already has dummy values.
# For local dev, DATABASE_URL should point to localhost:
# DATABASE_URL=postgresql+asyncpg://calling_agent:calling_agent_secret@localhost:5432/calling_agent
# DATABASE_URL_SYNC=postgresql://calling_agent:calling_agent_secret@localhost:5432/calling_agent

# These are already the defaults in .env, so no change needed unless your PostgreSQL config differs.
```

#### Step 5 - Run Migrations

```bash
alembic upgrade head
```

#### Step 6 - Start Backend Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend running at: `http://localhost:8000`
API docs (Swagger): `http://localhost:8000/docs`
Health check: `http://localhost:8000/health`

#### Stop Commands

```bash
# Stop the server: press Ctrl+C in the terminal

# Deactivate virtual environment when done:
deactivate
```

---

### OPTION B: WITH DOCKER

#### Step 1 - Start Everything (PostgreSQL + Redis + Backend)

```bash
cd backend

# Build and start all services
docker-compose up -d

# Check status
docker-compose ps
```

#### Step 2 - View Logs

```bash
# All services
docker-compose logs -f

# Backend only
docker-compose logs -f backend

# PostgreSQL only
docker-compose logs -f db
```

#### Step 3 - Run Migrations (inside Docker)

```bash
# The app auto-creates tables on startup via SQLAlchemy create_all.
# But if you want to run Alembic manually:
docker-compose exec backend alembic upgrade head
```

Backend running at: `http://localhost:8000`
API docs (Swagger): `http://localhost:8000/docs`

#### Stop Commands

```bash
# Stop all services
docker-compose down

# Stop and delete all data (fresh start)
docker-compose down -v

# Rebuild after code changes
docker-compose up -d --build
```

---

## 4. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend running at: `http://localhost:3000`
API calls auto-proxy to backend at `http://localhost:8000`

#### Other Frontend Commands

```bash
# Build for production
npm run build

# Preview production build
npm run preview
```

---

## 5. Full Startup (Both Backend + Frontend)

### Without Docker - Terminal 1 (Backend):

```bash
cd "E:\Calling Agent Static\backend"
venv\Scripts\activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Without Docker - Terminal 2 (Frontend):

```bash
cd "E:\Calling Agent Static\frontend"
npm run dev
```

### With Docker - Single Command:

```bash
# Start backend (Docker)
cd "E:\Calling Agent Static\backend"
docker-compose up -d

# Start frontend (local)
cd "E:\Calling Agent Static\frontend"
npm run dev
```

---

## 6. Create First User

### Via UI:
Open `http://localhost:3000/register` and fill the form.

### Via API:

```bash
curl -X POST http://localhost:8000/api/v1/auth/register ^
  -H "Content-Type: application/json" ^
  -d "{\"email\": \"admin@example.com\", \"password\": \"password123\", \"full_name\": \"Admin User\", \"phone\": \"+919999999999\"}"
```

PowerShell:
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/register" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"email":"admin@example.com","password":"password123","full_name":"Admin User","phone":"+919999999999"}'
```

---

## 7. Login & Get Token

```bash
curl -X POST http://localhost:8000/api/v1/auth/login ^
  -H "Content-Type: application/json" ^
  -d "{\"email\": \"admin@example.com\", \"password\": \"password123\"}"
```

PowerShell:
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/login" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"email":"admin@example.com","password":"password123"}'
```

Response contains `access_token` — use it in all subsequent API calls as `Authorization: Bearer <token>`.

---

## 8. API Usage Examples

Replace `YOUR_TOKEN` with the token from login.

### Scripts

```bash
# Create script
curl -X POST http://localhost:8000/api/v1/scripts ^
  -H "Authorization: Bearer YOUR_TOKEN" ^
  -H "Content-Type: application/json" ^
  -d "{\"name\": \"Summer Sale\", \"content\": \"Namaste {customer_name}! Main ABC Corp se bol raha hoon.\", \"language\": \"hi-IN\", \"audio_type\": \"uploaded\"}"

# List scripts
curl http://localhost:8000/api/v1/scripts -H "Authorization: Bearer YOUR_TOKEN"

# Upload audio to script
curl -X POST http://localhost:8000/api/v1/scripts/SCRIPT_ID/audio ^
  -H "Authorization: Bearer YOUR_TOKEN" ^
  -F "file=@C:\path\to\pitch.mp3"

# Activate script
curl -X POST http://localhost:8000/api/v1/scripts/SCRIPT_ID/activate -H "Authorization: Bearer YOUR_TOKEN"
```

### Contacts

```bash
# Create contact list
curl -X POST http://localhost:8000/api/v1/contacts/lists ^
  -H "Authorization: Bearer YOUR_TOKEN" ^
  -H "Content-Type: application/json" ^
  -d "{\"name\": \"June Leads\", \"description\": \"Potential customers\"}"

# Upload CSV
curl -X POST "http://localhost:8000/api/v1/contacts/upload?list_id=LIST_ID" ^
  -H "Authorization: Bearer YOUR_TOKEN" ^
  -F "file=@C:\path\to\contacts.csv"
```

### Campaigns

```bash
# Create campaign
curl -X POST http://localhost:8000/api/v1/campaigns ^
  -H "Authorization: Bearer YOUR_TOKEN" ^
  -H "Content-Type: application/json" ^
  -d "{\"name\": \"June Outreach\", \"script_id\": \"SCRIPT_ID\", \"list_id\": \"LIST_ID\", \"schedule_type\": \"immediate\", \"max_concurrent_calls\": 5, \"retry_limit\": 3, \"calling_hours_start\": 9, \"calling_hours_end\": 21}"

# Start campaign
curl -X POST http://localhost:8000/api/v1/campaigns/CAMPAIGN_ID/start -H "Authorization: Bearer YOUR_TOKEN"

# Pause campaign
curl -X POST http://localhost:8000/api/v1/campaigns/CAMPAIGN_ID/pause -H "Authorization: Bearer YOUR_TOKEN"

# Resume campaign
curl -X POST http://localhost:8000/api/v1/campaigns/CAMPAIGN_ID/resume -H "Authorization: Bearer YOUR_TOKEN"
```

### Reports

```bash
# Dashboard stats
curl http://localhost:8000/api/v1/reports/dashboard -H "Authorization: Bearer YOUR_TOKEN"

# Campaign stats
curl http://localhost:8000/api/v1/reports/campaigns/CAMPAIGN_ID/stats -H "Authorization: Bearer YOUR_TOKEN"

# Export CSV
curl "http://localhost:8000/api/v1/reports/campaigns/CAMPAIGN_ID/export?format=csv" -H "Authorization: Bearer YOUR_TOKEN" -o call_logs.csv
```

---

## 9. Exotel Setup (For Actual Calling)

1. Sign up: `https://my.exotel.com/auth/register`
2. Complete KYC
3. Get 140-series virtual number (ExoPhone)
4. Note credentials: Account SID, API Key, API Token, Caller ID

Update `backend/.env`:

```
EXOTEL_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxx
EXOTEL_API_KEY=your_api_key
EXOTEL_API_TOKEN=your_api_token
EXOTEL_CALLER_ID=0123456789
```

Set Exotel webhook in Exotel Dashboard:
- Status Callback: `https://your-domain.com/api/v1/webhooks/exotel/status`
- Recording Callback: `https://your-domain.com/api/v1/webhooks/exotel/recording`

---

## 10. Environment Variables

### Backend (.env)

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL async URL | `postgresql+asyncpg://calling_agent:calling_agent_secret@localhost:5432/calling_agent` |
| `DATABASE_URL_SYNC` | PostgreSQL sync URL | `postgresql://calling_agent:calling_agent_secret@localhost:5432/calling_agent` |
| `REDIS_URL` | Redis URL | `redis://localhost:6379/0` |
| `SECRET_KEY` | JWT secret | `super-secret-change-me-in-production-9f8e7d6c5b4a` |
| `EXOTEL_ACCOUNT_SID` | Exotel Account SID | - |
| `EXOTEL_API_KEY` | Exotel API Key | - |
| `EXOTEL_API_TOKEN` | Exotel API Token | - |
| `EXOTEL_CALLER_ID` | 140-series number | `+919999999999` |
| `MAX_UPLOAD_SIZE_MB` | Max audio upload | `10` |
| `UPLOAD_DIR` | Upload directory | `uploads` |

### Frontend (.env)

| Variable | Description | Default |
|----------|-------------|---------|
| `VITE_API_BASE_URL` | Backend API URL | `/api/v1` |

---

## 11. Production Deployment

### Backend -> Render

1. Push to GitHub
2. Go to `https://dashboard.render.com`
3. New -> Web Service
4. Connect repo
5. Settings:
   - Name: `calling-agent-api`
   - Runtime: Python
   - Build: `pip install -r requirements.txt`
   - Start: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
6. Add env vars from `.env`
7. New -> PostgreSQL (add database)
8. Update `DATABASE_URL` with Render PostgreSQL URL
9. Deploy

### Frontend -> Vercel

1. Push to GitHub
2. Go to `https://vercel.com`
3. New Project -> Import repo
4. Settings:
   - Framework: Vite
   - Root Directory: `frontend`
   - Build: `npm run build`
   - Output: `dist`
5. Env var: `VITE_API_BASE_URL` = `https://your-backend.onrender.com/api/v1`
6. Deploy

Update `frontend/vercel.json` with your actual backend URL:

```json
{
  "rewrites": [
    {
      "source": "/api/(.*)",
      "destination": "https://your-backend.onrender.com/api/$1"
    }
  ]
}
```

---

## 12. Troubleshooting

### Port 8000 already in use

```bash
# Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# macOS/Linux:
lsof -i :8000
kill -9 <PID>
```

### Database connection error (without Docker)

```bash
# Check PostgreSQL is running
# Windows:
pg_isready
# macOS/Linux:
pg_isready -h localhost -p 5432

# Check database exists
psql -U postgres -c "\l" | grep calling_agent
```

### Database reset (without Docker)

```bash
psql -U postgres -c "DROP DATABASE IF EXISTS calling_agent;"
psql -U postgres -c "CREATE DATABASE calling_agent;"
psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE calling_agent TO calling_agent;"
psql -U postgres -d calling_agent -c "GRANT ALL ON SCHEMA public TO calling_agent;"
cd backend && alembic upgrade head
```

### Database reset (with Docker)

```bash
cd backend
docker-compose down -v
docker-compose up -d
```

### Frontend not connecting to backend

```bash
# Verify backend is running
curl http://localhost:8000/health

# Check vite proxy config
cat frontend/vite.config.js
```

---

## 13. File Formats

### Contact Lists (CSV/Excel)

```
phone,name,email,company
+919876543210,Rahul,rahul@example.com,ABC Corp
+919876543211,Priya,priya@example.com,XYZ Ltd
```

Auto-detected columns: `phone`, `mobile`, `number`, `name`, `full_name`, `email`, `company`, `organization`

### Audio Files (for pre-recorded scripts)

| Format | Max Size | Notes |
|--------|----------|-------|
| MP3 | 10 MB | Best for telephony |
| WAV | 10 MB | 8kHz recommended |
| OGG | 10 MB | Good compression |

Max duration: 5 minutes.
