from fastapi.testclient import TestClient
from CampusActivityReccomender.app.api.main import app

client = TestClient(app)

