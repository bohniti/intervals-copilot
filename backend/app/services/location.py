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


async def get_current_location() -> Optional[LocationInfo]:
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get("https://ipinfo.io/json")
            data = resp.json()
            loc = data.get("loc", "")
            lat, lon = None, None
            if loc and "," in loc:
                parts = loc.split(",")
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
