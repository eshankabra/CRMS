import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import pytest
from app import create_app
from app.database.connection import get_db_cursor

@pytest.fixture(scope="session")
def app():
    """Create Flask application in testing mode."""
    app = create_app("testing")
    yield app

@pytest.fixture(scope="session")
def client(app):
    """Test client."""
    return app.test_client()

@pytest.fixture(scope="session")
def admin_headers(client):
    """Obtain JWT headers for Admin."""
    res = client.post("/api/v1/auth/login", json={
        "email": "admin@crms.vit.ac.in",
        "password": "Admin@123",
        "role": "Admin"
    })
    token = res.get_json()["data"]["token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture(scope="session")
def faculty_headers(client):
    """Obtain JWT headers for Faculty (Dr. Rajesh Sharma, ID 1, teaches course 1 & 2)."""
    res = client.post("/api/v1/auth/login", json={
        "email": "rajesh.sharma@vit.ac.in",
        "password": "Faculty@123",
        "role": "Faculty"
    })
    token = res.get_json()["data"]["token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture(scope="session")
def faculty2_headers(client):
    """Obtain JWT headers for Faculty 2 (Dr. Arvind Rao, ID 2, teaches course 3 & 4)."""
    res = client.post("/api/v1/auth/login", json={
        "email": "arvind.rao@vit.ac.in",
        "password": "Faculty@123",
        "role": "Faculty"
    })
    token = res.get_json()["data"]["token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture(scope="session")
def student_headers(client):
    """Obtain JWT headers for Student 1 (Eshan Kabra, ID 1)."""
    res = client.post("/api/v1/auth/login", json={
        "email": "eshan.kabra@vitstudent.ac.in",
        "password": "Student@123",
        "role": "Student"
    })
    token = res.get_json()["data"]["token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture(scope="session")
def student2_headers(client):
    """Obtain JWT headers for Student 2 (Roshani, ID 2)."""
    res = client.post("/api/v1/auth/login", json={
        "email": "roshani.k@vitstudent.ac.in",
        "password": "Student@123",
        "role": "Student"
    })
    token = res.get_json()["data"]["token"]
    return {"Authorization": f"Bearer {token}"}
