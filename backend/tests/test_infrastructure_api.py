
from fastapi.testclient import TestClient

from app.main import app


def test_bridge_state_returns_live_telemetry() -> None:
    with TestClient(app) as client:
        response = client.get("/api/infrastructure/bridges/BR-001/state")

    assert response.status_code == 200
    payload = response.json()

    assert payload["node_id"] == "BR-001"
    assert 0 <= payload["load_percent"] <= 100
    assert payload["health"]["category"] in {
        "normal",
        "caution",
        "high_risk",
    }


def test_unknown_bridge_returns_not_found() -> None:
    with TestClient(app) as client:
        response = client.get(
            "/api/infrastructure/bridges/UNKNOWN/state"
        )

    assert response.status_code == 404


def test_vehicle_state_returns_virtual_vehicle_telemetry() -> None:
    with TestClient(app) as client:
        response = client.get("/api/vehicles/V-001/state")

    assert response.status_code == 200
    assert response.json()["vehicle_type"] == "car"


def test_safety_decision_combines_vehicle_and_bridge_state() -> None:
    with TestClient(app) as client:
        response = client.get(
            "/api/safety/vehicles/V-002/decision"
        )

    assert response.status_code == 200

    payload = response.json()

    assert payload["vehicle"]["vehicle_id"] == "V-002"
    assert payload["vehicle"]["approaching_node_id"] == "BR-002"
    assert payload["infrastructure"]["node_id"] == "BR-002"
    assert payload["assessment"]["decision"] in {
        "green",
        "amber",
        "red",
    }


def test_uob_endpoint_returns_an_i2v_packet() -> None:
    with TestClient(app) as client:
        response = client.get(
            "/api/uob/vehicles/V-003/latest"
        )

    assert response.status_code == 200

    payload = response.json()

    assert payload["packet_id"].startswith("UOB-")
    assert payload["target_vehicle_id"] == "V-003"
    assert payload["hazard_code"] in {
        "0x00",
        "0x02",
        "0x03",
    }


def test_history_returns_persisted_uob_packets() -> None:
    with TestClient(app) as client:
        client.get("/api/uob/vehicles/V-001/latest")

        response = client.get(
            "/api/history/uob/vehicles/V-001"
        )

    assert response.status_code == 200

    history = response.json()

    assert history
    assert history[0]["target_vehicle_id"] == "V-001"