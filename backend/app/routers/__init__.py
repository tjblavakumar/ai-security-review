from app.routers.ai import router as ai_router
from app.routers.notifications import router as notifications_router
from app.routers.policies import router as policies_router
from app.routers.questions import router as questions_router
from app.routers.reviews import router as reviews_router
from app.routers.risk import router as risk_router
from app.routers.submissions import router as submissions_router

__all__ = [
    "ai_router",
    "notifications_router",
    "policies_router",
    "questions_router",
    "submissions_router",
    "reviews_router",
    "risk_router",
]
