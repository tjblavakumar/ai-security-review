from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.database import Base, engine
from app.models import Question
from app.routers import (
    ai_router,
    notifications_router,
    policies_router,
    questions_router,
    reviews_router,
    risk_router,
    submissions_router,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)

    from app.database import SessionLocal

    db = SessionLocal()
    try:
        count = db.query(Question).count()
        if count == 0:
            print("No questions found — running seed script...")
            from seed_data import seed

            seed()
            print("Seed complete.")
        
        # Seed default risk configuration
        from app.services.risk_config_service import seed_default_risk_config
        seed_default_risk_config(db)
        print("Risk configuration check complete.")
    finally:
        db.close()

    yield


app = FastAPI(
    title=settings.APP_TITLE,
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(questions_router)
app.include_router(submissions_router)
app.include_router(reviews_router)
app.include_router(notifications_router)
app.include_router(ai_router)
app.include_router(policies_router)
app.include_router(risk_router)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"data": None, "message": str(exc), "success": False},
    )


@app.get("/api/health")
def health_check():
    return {"data": {"status": "healthy"}, "message": "OK", "success": True}
