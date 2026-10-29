"""
Main FastAPI Application Entrypoint for VeritasAI Fake News Detector.
"""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from backend.config import STATIC_DIR, HOST, PORT, DEBUG
from backend.database import init_db
from backend.routes.api import router as api_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: initialize database
    init_db()
    print("✓ VeritasAI database initialized.")
    yield
    # Shutdown logic if needed

app = FastAPI(
    title="VeritasAI - Fake News Detection Platform",
    description="Full-stack AI fake news detector using BERT, NLP Stylometry, and Gemini Deep Fact-Checking.",
    version="2.0.0",
    lifespan=lifespan
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Router
app.include_router(api_router)

# Mount static assets
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

@app.get("/", include_in_schema=False)
async def serve_index():
    """Serve the single-page application frontend."""
    index_file = STATIC_DIR / "index.html"
    return FileResponse(str(index_file))

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "VeritasAI Fake News Detector", "version": "2.0.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host=HOST, port=PORT, reload=DEBUG)

