import httpx
from typing import Optional
from dataclasses import dataclass


@dataclass
class LocationInfo:
    city: Optional[str]
    region: Optional[str]
    country: Optional[str]
    lat: Optional[float]
    lon: Optional[float]

    def as_context_string(self) -> str:
        parts = [p for p in [self.city, self.region, self.country] if p]
        loc = ", ".join(parts) if parts else "Unknown location"
        if self.lat and self.lon:
            return f"{loc} (lat={self.lat:.4f}, lon={self.lon:.4f})"
        return loc


def get_current_location() -> Optional[LocationInfo]:
    try:
        with httpx.Client(timeout=5.0) as client:
            resp = client.get("https://ipinfo.io/json")
            data = resp.json()
            loc_str = data.get("loc", "")
            lat, lon = None, None
            if loc_str and "," in loc_str:
                parts = loc_str.split(",")
                lat = float(parts[0])
                lon = float(parts[1])
            return LocationInfo(
                city=data.get("city"),
                region=data.get("region"),
                country=data.get("country"),
                lat=lat,
                lon=lon,
            )
    except Exception:
        return None
