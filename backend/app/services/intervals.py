"""
intervals.icu API client.

Auth: Basic auth — username = "API_KEY", password = your API key.
Docs: https://intervals.icu/api/v1/docs
"""

from typing import Optional
from datetime import date, timedelta
from dataclasses import dataclass, field
import httpx
from app.config import get_settings

settings = get_settings()

BASE_URL = "https://intervals.icu/api/v1"


def _auth() -> tuple[str, str]:
    return ("API_KEY", settings.intervals_icu_api_key)


@dataclass
class IntervalsActivity:
    """Flattened view of an intervals.icu activity, ready for LLM consumption."""
    id: str
    name: str
    activity_type: str          # "Run", "Hike", "Walk", "Ride", etc.
    start_date_local: str       # ISO datetime string, local time
    duration_seconds: int
    distance_m: Optional[float]
    elevation_gain_m: Optional[float]
    start_lat: Optional[float]
    start_lon: Optional[float]
    avg_hr: Optional[int]
    calories: Optional[int]
    description: Optional[str]

    def to_llm_dict(self) -> dict:
        """Human-readable dict for the LLM tool result."""
        d: dict = {
            "intervals_id": self.id,
            "name": self.name,
            "type": self.activity_type,
            "date": self.start_date_local[:10],
            "start_time": self.start_date_local[11:16] if len(self.start_date_local) > 10 else None,
            "duration_minutes": round(self.duration_seconds / 60) if self.duration_seconds else None,
        }
        if self.distance_m:
            d["distance_km"] = round(self.distance_m / 1000, 2)
        if self.elevation_gain_m is not None:
            d["elevation_gain_m"] = round(self.elevation_gain_m)
        if self.start_lat and self.start_lon:
            d["start_location"] = {"lat": round(self.start_lat, 5), "lon": round(self.start_lon, 5)}
        if self.avg_hr:
            d["avg_hr"] = self.avg_hr
        if self.calories:
            d["calories"] = self.calories
        if self.description:
            d["description"] = self.description
        return d


def _parse_activity(raw: dict) -> IntervalsActivity:
    # start_latlng may be a [lat, lon] list, or absent entirely
    latlng = raw.get("start_latlng") or []
    start_lat = latlng[0] if len(latlng) >= 1 else None
    start_lon = latlng[1] if len(latlng) >= 2 else None

    # Fallback: some Garmin activities store lat/lon as top-level fields
    if start_lat is None:
        start_lat = raw.get("start_lat") or raw.get("lat")
    if start_lon is None:
        start_lon = raw.get("start_lon") or raw.get("lng") or raw.get("lon")

    return IntervalsActivity(
        id=str(raw.get("id", "")),
        name=raw.get("name", "Unnamed"),
        activity_type=raw.get("type", "Unknown"),
        start_date_local=raw.get("start_date_local", ""),
        duration_seconds=int(raw.get("moving_time") or raw.get("elapsed_time") or 0),
        distance_m=raw.get("distance") or raw.get("icu_distance"),
        elevation_gain_m=raw.get("total_elevation_gain") or raw.get("icu_elevation_gain"),
        start_lat=float(start_lat) if start_lat is not None else None,
        start_lon=float(start_lon) if start_lon is not None else None,
        avg_hr=raw.get("average_heartrate"),
        calories=raw.get("calories") or raw.get("kilojoules"),
        description=raw.get("description") or None,
    )


async def search_activities(
    around_date: date,
    days_around: int = 1,
    athlete_id: Optional[str] = None,
) -> list[IntervalsActivity]:
    """
    Return intervals.icu activities within [around_date - days_around, around_date + days_around].
    Returns an empty list if the API key is not configured.
    """
    api_key = settings.intervals_icu_api_key
    _athlete_id = athlete_id or settings.intervals_icu_athlete_id

    if not api_key or not _athlete_id:
        return []

    oldest = (around_date - timedelta(days=days_around)).isoformat()
    newest = (around_date + timedelta(days=days_around)).isoformat()

    url = f"{BASE_URL}/athlete/{_athlete_id}/activities"
    params = {"oldest": oldest, "newest": newest}

    async with httpx.AsyncClient(auth=_auth(), timeout=10.0) as client:
        resp = await client.get(url, params=params)
        resp.raise_for_status()
        data = resp.json()

    return [_parse_activity(a) for a in data]


async def fetch_all_activities(
    days_back: int = 365,
    athlete_id: Optional[str] = None,
) -> list[IntervalsActivity]:
    """
    Fetch all activities from intervals.icu going back `days_back` days from today.
    Used for the bulk import feature.
    """
    from datetime import date as date_cls
    api_key = settings.intervals_icu_api_key
    _athlete_id = athlete_id or settings.intervals_icu_athlete_id

    if not api_key or not _athlete_id:
        return []

    today = date_cls.today()
    oldest = (today - timedelta(days=days_back)).isoformat()
    newest = today.isoformat()

    url = f"{BASE_URL}/athlete/{_athlete_id}/activities"
    params = {"oldest": oldest, "newest": newest}

    async with httpx.AsyncClient(auth=_auth(), timeout=30.0) as client:
        resp = await client.get(url, params=params)
        resp.raise_for_status()
        data = resp.json()

    return [_parse_activity(a) for a in data]


async def get_activity(activity_id: str, athlete_id: Optional[str] = None) -> Optional[IntervalsActivity]:
    """Fetch a single activity by ID."""
    api_key = settings.intervals_icu_api_key
    _athlete_id = athlete_id or settings.intervals_icu_athlete_id

    if not api_key or not _athlete_id:
        return None

    url = f"{BASE_URL}/activity/{activity_id}"

    async with httpx.AsyncClient(auth=_auth(), timeout=10.0) as client:
        resp = await client.get(url)
        if resp.status_code == 404:
            return None
        resp.raise_for_status()
        return _parse_activity(resp.json())
