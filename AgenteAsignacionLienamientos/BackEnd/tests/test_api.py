from app.main import app


client = app.test_client()


def test_healthcheck():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}
