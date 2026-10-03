from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes.dashboard import router as dashboard_router

from app.routes import (
    history,
    infrastructure,
    safety,
    uob,
    vehicles,
)
from app.services.simulation_service import simulation_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application startup and shutdown."""

    # Start the automatic infrastructure simulation.
    simulation_task = simulation_service._task = __import__(
        "asyncio"
    ).create_task(
        simulation_service.start()
    )

    print("Smart Infrastructure Intelligence API started.")

    try:
        yield

    finally:
        # Stop the simulation gracefully when FastAPI shuts down.
        simulation_service.stop()

        simulation_task.cancel()

        try:
            await simulation_task
        except __import__("asyncio").CancelledError:
            pass

        print("Smart Infrastructure Intelligence API stopped.")


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


app.include_router(infrastructure.router)
app.include_router(vehicles.router)
app.include_router(safety.router)
app.include_router(uob.router)
app.include_router(history.router)
app.include_router(dashboard_router)


@app.get("/api/health")
def health_check():
    return {"status": "ready"}