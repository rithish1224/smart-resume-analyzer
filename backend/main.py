"""
Smart Competency Diagnostic & Candidate Profile Score Calculator
FastAPI Application Entry Point
"""
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import os
import logging

logger = logging.getLogger(__name__)

# ── Lazy imports inside lifespan to avoid circular imports at module load ──────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: startup and shutdown events."""
    # ── Startup ────────────────────────────────────────────────────────────────
    logger.info("🚀 Starting Smart Competency Diagnostic API...")

    # Create upload directory
    os.makedirs("uploads", exist_ok=True)
    logger.info("📁 Upload directory ready")

    # Initialize database (create tables)
    try:
        from backend.db.database import init_db
        await init_db()
        logger.info("✅ Database initialized")
    except Exception as e:
        logger.error(f"❌ Database init failed: {e}")

    # Load spaCy model
    try:
        import spacy
        app.state.nlp = spacy.load("en_core_web_sm")
        logger.info("✅ spaCy model loaded")
    except OSError:
        logger.warning("⚠️  spaCy model not found. Run: python -m spacy download en_core_web_sm")
        app.state.nlp = None

    # Load XGBoost model
    try:
        from backend.models.xgb_model import xgb_model
        from backend.config import settings
        if os.path.exists(settings.MODEL_PATH):
            loaded = xgb_model.load(settings.MODEL_PATH)
            if loaded:
                logger.info(f"✅ XGBoost model loaded: {settings.MODEL_PATH}")
            else:
                logger.warning("⚠️  XGBoost model load failed — using rule-based only")
        else:
            logger.warning("⚠️  No trained model found — using rule-based scoring only")
            logger.info("   Run: cd ml_training && python train_xgboost.py")
        app.state.xgb_model = xgb_model
    except Exception as e:
        logger.error(f"❌ XGBoost load error: {e}")
        app.state.xgb_model = None

    logger.info("🎯 Startup complete. API ready at http://localhost:8000")
    logger.info("📚 Swagger docs: http://localhost:8000/api/docs")

    yield  # App is running here

    # ── Shutdown ───────────────────────────────────────────────────────────────
    logger.info("👋 Shutting down gracefully...")


# ── FastAPI App Instance ───────────────────────────────────────────────────────
app = FastAPI(
    title="Smart Competency Diagnostic Platform",
    description="""
## AI-Powered Candidate Scoring with XGBoost + SHAP Explainability

Features:
- 📄 Multi-format resume parsing (PDF, DOCX, TXT, JPG, PNG + OCR)
- 🎯 XGBoost + rule-based hybrid scoring
- 🔍 SHAP TreeExplainer waterfall explanations
- 📊 Skill gap analysis with prioritization
- 🛡️ Fairness audit (DIR, DP, Equalized Odds)
- 🤖 AI-powered roadmap (OpenRouter → Google AI → Rule-based)
- 🔐 JWT authentication with Recruiter/Candidate roles
- 📝 Resume Improvement Module with ATS analysis, bullet optimizer, keyword gap
- 🧠 Self-Learning Engine (free/open-source: spaCy, sklearn, XGBoost, HuggingFace)
    """,
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# ── CORS Middleware ────────────────────────────────────────────────────────────
try:
    from backend.config import settings
    origins = settings.ALLOWED_ORIGINS
except Exception:
    origins = ["http://localhost:5173", "http://localhost:3000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Static Files (uploaded resumes & frontend assets) ───────────────────────────
STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
assets_dir = os.path.join(STATIC_DIR, "assets")
if os.path.exists(assets_dir):
    app.mount("/assets", StaticFiles(directory=assets_dir), name="static_assets")

if os.path.exists("uploads"):
    app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# ── Include Routers ────────────────────────────────────────────────────────────
from backend.routers import auth, upload, score, explain, fairness, compare, roadmap, export, admin
from backend.routers import improve  # ← Resume Improvement Module (additive)

app.include_router(auth.router,     prefix="/api/auth",     tags=["Authentication"])
app.include_router(upload.router,   prefix="/api/upload",   tags=["Resume Upload"])
app.include_router(score.router,    prefix="/api/score",    tags=["Scoring"])
app.include_router(explain.router,  prefix="/api/explain",  tags=["Explainability"])
app.include_router(fairness.router, prefix="/api/fairness", tags=["Fairness Audit"])
app.include_router(compare.router,  prefix="/api/compare",  tags=["Comparison"])
app.include_router(roadmap.router,  prefix="/api/roadmap",  tags=["AI Roadmap"])
app.include_router(export.router,   prefix="/api/export",   tags=["Export"])
app.include_router(admin.router,    prefix="/api/admin",    tags=["Admin"])
app.include_router(improve.router,  prefix="/api/improve",  tags=["Resume Improvement"])  # ← NEW

# ── Exception Handlers ─────────────────────────────────────────────────────────
@app.exception_handler(404)
async def not_found_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"status": "error", "message": "Resource not found", "path": str(request.url.path)}
    )

@app.exception_handler(422)
async def validation_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"status": "error", "message": "Validation error", "details": str(exc)}
    )

@app.exception_handler(500)
async def server_error_handler(request: Request, exc: Exception):
    logger.error(f"Internal server error: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"status": "error", "message": "Internal server error"}
    )

# ── Health Check ───────────────────────────────────────────────────────────────
@app.get("/health", tags=["Health"], summary="System health check")
async def health_check():
    """Returns system health status including DB, model, and API version."""
    from backend.config import settings

    model_loaded = False
    try:
        if hasattr(app.state, "xgb_model") and app.state.xgb_model:
            model_loaded = app.state.xgb_model.is_loaded()
    except Exception:
        pass

    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "model_version": settings.MODEL_VERSION,
        "model_loaded": model_loaded,
        "spacy_loaded": hasattr(app.state, "nlp") and app.state.nlp is not None,
        "db_status": "connected",
        "upload_dir": os.path.exists("uploads"),
    }

# ── SPA Catch-all Route for React Frontend ───────────────────────────────────────
@app.get("/{full_path:path}", include_in_schema=False)
async def serve_spa(full_path: str):
    if full_path.startswith("api/"):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"status": "error", "message": f"API endpoint '/{full_path}' not found"}
        )
    
    file_path = os.path.join(STATIC_DIR, full_path)
    if full_path and os.path.isfile(file_path):
        return FileResponse(file_path)
    
    index_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"status": "error", "message": "Frontend index.html not found"}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
