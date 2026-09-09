from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import initialise_database
from .routes.history import router as history_router
from .routes.infrastructure import router as infrastructure_router
from .routes.safety import router as safety_router
from .routes.uob import router as uob_router
from .routes.vehicles import router as vehicles_router

@asynccontextmanager
async def lifespan(_: FastAPI):
    initialise_database()
    yield


app = FastAPI(
    title="Smart Infrastructure Intelligence API",
    version="0.1.0",
    description="Virtual infrastructure monitoring and safety intelligence.",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(infrastructure_router)
app.include_router(vehicles_router)
app.include_router(safety_router)
app.include_router(uob_router)
app.include_router(history_router)


@app.get("/api/health")
def health_check() -> dict[str, str]:
    return {"status": "ready"}
