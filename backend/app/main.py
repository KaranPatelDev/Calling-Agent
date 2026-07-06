from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from app.config import get_settings
from app.api.auth import router as auth_router
from app.api.scripts import router as scripts_router
from app.api.contacts import router as contacts_router
from app.api.campaigns import router as campaigns_router
from app.api.webhooks import router as webhooks_router
from app.api.reports import router as reports_router

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    upload_dir = Path(settings.UPLOAD_DIR)
    (upload_dir / "audio").mkdir(parents=True, exist_ok=True)
    (upload_dir / "tts_cache").mkdir(parents=True, exist_ok=True)
    yield


app = FastAPI(
    title="Calling Agent API",
    description="Automated outbound calling agent platform",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

upload_path = Path(settings.UPLOAD_DIR)
if upload_path.exists():
    app.mount("/uploads", StaticFiles(directory=str(upload_path)), name="uploads")

app.include_router(auth_router, prefix="/api/v1")
app.include_router(scripts_router, prefix="/api/v1")
app.include_router(contacts_router, prefix="/api/v1")
app.include_router(campaigns_router, prefix="/api/v1")
app.include_router(webhooks_router, prefix="/api/v1")
app.include_router(reports_router, prefix="/api/v1")


@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}


@app.get("/")
async def root():
    return {"message": "Calling Agent API is running", "docs": "/docs"}
