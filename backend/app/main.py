from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.routers.auth import router as auth_router
from app.routers.post import router as post_router
from app.routers.comment import router as comment_router


app = FastAPI(title="Blog API")

# API routes must be registered before the frontend catch-all mount.
app.include_router(auth_router)
app.include_router(post_router)
app.include_router(comment_router)


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok"}


# Serve the HTML/CSS/JavaScript frontend from the same Render service.
# main.py -> app -> backend -> project root -> frontend
PROJECT_ROOT = Path(__file__).resolve().parents[2]
FRONTEND_DIR = PROJECT_ROOT / "frontend"

app.mount(
    "/",
    StaticFiles(directory=FRONTEND_DIR, html=True),
    name="frontend",
)
