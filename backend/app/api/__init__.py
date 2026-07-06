from app.api.auth import router as auth_router
from app.api.scripts import router as scripts_router
from app.api.contacts import router as contacts_router
from app.api.campaigns import router as campaigns_router
from app.api.webhooks import router as webhooks_router
from app.api.reports import router as reports_router

__all__ = [
    "auth_router",
    "scripts_router",
    "contacts_router",
    "campaigns_router",
    "webhooks_router",
    "reports_router",
]
