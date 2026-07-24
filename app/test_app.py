from app import app

def test_home():
    client = app.test_client()
    resp = client.get("/")
    assert resp.status_code == 200

def test_perso_endpoint():
    client = app.test_client()
    resp = client.get("/fadyl-axel-bamba")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["etudiant"] == "Fadyl Axel BAMBA"

def test_healthz():
    client = app.test_client()
    resp = client.get("/healthz")
    assert resp.status_code == 200
