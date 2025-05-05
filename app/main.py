
from fastapi import FastAPI
from app.api.routes import containers, auth, images, system, stats, realtime

app = FastAPI(title="Docker Agent")

app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(containers.router, prefix="/containers", tags=["Containers"])
app.include_router(images.router, prefix="/images", tags=["Images"])
app.include_router(system.router, tags=["System"])
app.include_router(stats.router, prefix="/stats", tags=["Stats"])
app.include_router(realtime.router, tags=["Realtime"])
