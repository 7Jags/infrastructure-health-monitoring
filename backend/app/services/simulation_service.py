"""Background service for continuously updating virtual infrastructure."""

import asyncio
from threading import Lock

from sqlalchemy.orm import Session

from ..database import SessionLocal
from .infrastructure_simulator import bridge_simulator
from .persistence_service import record_infrastructure_state


class SimulationService:
    """Run the virtual infrastructure simulation continuously."""

    def __init__(self, interval_seconds: float = 1.0):
        self.interval_seconds = interval_seconds
        self._running = False
        self._task: asyncio.Task | None = None # type: ignore
        self._lock = Lock()

    async def start(self) -> None:
        """Start the background simulation loop."""

        with self._lock:
            if self._running:
                return

            self._running = True

        print("Infrastructure simulation started.")

        try:
            while self._running:
                self._generate_and_store_state()

                await asyncio.sleep(
                    self.interval_seconds
                )

        except asyncio.CancelledError:
            print("Infrastructure simulation stopped.")
            raise

    def stop(self) -> None:
        """Stop the simulation loop."""

        with self._lock:
            self._running = False

    def _generate_and_store_state(self) -> None:
        """Generate one bridge state and save it."""

        state = bridge_simulator.next_state()

        session: Session = SessionLocal()

        try:
            record_infrastructure_state(
                session,
                state,
            )

        finally:
            session.close()


simulation_service = SimulationService(
    interval_seconds=1.0
)