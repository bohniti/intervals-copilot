import httpx
from typing import Optional, Any
from .config import get_settings

settings = get_settings()


class JournalAPIClient:
    def __init__(self, base_url: Optional[str] = None):
        self.base_url = base_url or settings.backend_url

    def _client(self) -> httpx.Client:
        return httpx.Client(base_url=self.base_url, timeout=30.0)

    def list_activities(self, activity_type: Optional[str] = None, limit: int = 20) -> list[dict]:
        params = {"limit": limit}
        if activity_type:
            params["activity_type"] = activity_type
        with self._client() as client:
            resp = client.get("/activities/", params=params)
            resp.raise_for_status()
            return resp.json()

    def create_activity(self, data: dict) -> dict:
        with self._client() as client:
            resp = client.post("/activities/", json=data)
            resp.raise_for_status()
            return resp.json()

    def get_activity(self, activity_id: int) -> dict:
        with self._client() as client:
            resp = client.get(f"/activities/{activity_id}")
            resp.raise_for_status()
            return resp.json()

    def chat(self, messages: list[dict], location_context: Optional[str] = None) -> dict:
        payload = {"messages": messages}
        if location_context:
            payload["location_context"] = location_context
        with self._client() as client:
            resp = client.post("/chat/", json=payload)
            resp.raise_for_status()
            return resp.json()
