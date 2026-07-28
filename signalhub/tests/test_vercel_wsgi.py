"""WSGI / Vercel entry — smoke sem rede."""

from __future__ import annotations

from signalhub.apps.api.http_dispatch import app, dispatch, reset_state


def test_dispatch_health():
    reset_state()
    code, payload = dispatch("GET", "/health")
    assert code == 200
    assert payload["status"] == "ok"
    assert "providers" in payload


def test_dispatch_snapshot():
    reset_state()
    code, payload = dispatch("GET", "/v1/admin/snapshot")
    assert code == 200
    assert payload["product"] == "signalhub"
    assert "integrity" in payload or "providers" in payload


def test_wsgi_app_health():
    reset_state()
    status_headers: list = []

    def start_response(status, headers):
        status_headers.append((status, headers))

    environ = {
        "REQUEST_METHOD": "GET",
        "PATH_INFO": "/health",
        "QUERY_STRING": "",
        "CONTENT_LENGTH": "0",
        "wsgi.input": __import__("io").BytesIO(b""),
    }
    body = b"".join(app(environ, start_response))
    assert status_headers[0][0].startswith("200")
    assert b'"status": "ok"' in body or b'"status":"ok"' in body
