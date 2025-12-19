from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health_check_unauthorized():
    response = client.get("/health")
    # Should fail without auth
    assert response.status_code == 401 or response.status_code == 403

# Note: More comprehensive tests would require mocking the database and auth
