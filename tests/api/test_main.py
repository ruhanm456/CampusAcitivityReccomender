from fastapi.testclient import TestClient
from app.api.main import app 

client = TestClient(app)

