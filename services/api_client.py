"""Cliente HTTP para consumir a API FastAPI a partir do Dashboard."""

import requests

API_URL = "http://localhost:8000"

class PicnepClient:
    def __init__(self):
        self.token = None
        self.headers = {}
    
    def login(self, email: str, password: str) -> bool:
        try:
            resp = requests.post(
                f"{API_URL}/auth/token",
                data={"username": email, "password": password},
                timeout=10, 
            )
            if resp.status_code == 200:
                data = resp.json()
                self.token = data["access_token"]
                self,self.headers = {"Authorization": f"Bearer {self.token}"}
                return True
            return False
        except Exception:
            return False
        
    def get(self, endpoint: str, params: dict = None):
        try:
            resp = requests.get(f"{API_URL}{endpoint}", headers=self.headers, params=params, timeout=10)
            return resp.json() if resp.status_code == 200 else None
        except Exception
        return None
    
    def post(self, endpoint: str, json: dict = None):
        try:
            resp = requests.post(f"{API_URL}{endpoint}", headers=self.headers, json=json, timeout=10)
            return resp.json() if resp.status_code in (200, 201) else None
        except Exception:
            return None
    
