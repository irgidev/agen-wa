"""M0 smoke tests: every application is importable and serves /healthz."""

from fastapi.testclient import TestClient

from agent import governance, nlu_tools, session
from mock_service.app import app as mock_app
from operator_console.app import app as console_app
from webhook.app import app as webhook_app


def test_agent_subpackages_importable() -> None:
    assert governance.__doc__
    assert nlu_tools.__doc__
    assert session.__doc__


def test_webhook_healthz() -> None:
    client = TestClient(webhook_app)
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_mock_service_healthz() -> None:
    client = TestClient(mock_app)
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_operator_console_healthz() -> None:
    client = TestClient(console_app)
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
