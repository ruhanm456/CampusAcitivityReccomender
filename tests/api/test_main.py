from fastapi.testclient import TestClient
from app.api.main import abb 

client = TestClient(abb)

