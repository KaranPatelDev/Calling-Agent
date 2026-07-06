# Calling Agent Backend

Automated outbound calling agent platform built with FastAPI.

## Setup

1. Create virtual environment:
```bash
python3.12 -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment:
```bash
cp .env.example .env
# Edit .env with your settings
```

4. Run migrations:
```bash
alembic upgrade head
```

5. Start server:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## API Documentation

Visit `http://localhost:8000/docs` for interactive Swagger docs.

## Docker

```bash
docker-compose up -d
```
