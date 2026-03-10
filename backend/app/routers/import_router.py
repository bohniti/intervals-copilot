"""
Bulk import from intervals.icu (Garmin data).
POST /import/intervals?days_back=365
"""
from datetime import datetime
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.database import get_session
from app.models.activity import Activity, ActivityType, ActivitySource

router = APIRouter(tags=["import"])


# ─── Type mapping ─────────────────────────────────────────────────────────────
# intervals.icu / Garmin activity type strings → our ActivityType + tags

_TYPE_MAP: dict[str, tuple[ActivityType, list[str]]] = {
    # Cycling
    "Ride":        (ActivityType.cycling, []),
    "VirtualRide": (ActivityType.cycling, ["indoor"]),
    "EBikeRide":   (ActivityType.cycling, ["e_bike"]),
    "MountainBikeRide": (ActivityType.cycling, ["mtb"]),
    "GravelRide":  (ActivityType.cycling, ["gravel_bike"]),
    "Handcycle":   (ActivityType.cycling, []),
    # Hiking / walking
    "Hike":        (ActivityType.hiking, []),
    "Walk":        (ActivityType.hiking, []),
    "Snowshoe":    (ActivityType.hiking, []),
    "Backpacking": (ActivityType.hiking, []),
    # Running / fitness
    "Run":         (ActivityType.fitness, ["run"]),
    "VirtualRun":  (ActivityType.fitness, ["run", "indoor"]),
    "TrailRun":    (ActivityType.fitness, ["trail_run"]),
    "Swim":        (ActivityType.fitness, ["swim"]),
    "OpenWaterSwim": (ActivityType.fitness, ["swim"]),
    "WeightTraining": (ActivityType.fitness, ["gym"]),
    "Workout":     (ActivityType.fitness, []),
    "Yoga":        (ActivityType.fitness, ["yoga"]),
    "Crossfit":    (ActivityType.fitness, ["gym"]),
    "HIIT":        (ActivityType.fitness, ["gym"]),
    "Pilates":     (ActivityType.fitness, []),
    "Elliptical":  (ActivityType.fitness, ["gym"]),
    "StairStepper": (ActivityType.fitness, ["gym"]),
    # Climbing
    "RockClimbing":  (ActivityType.sport_climb, []),
    "Climb":         (ActivityType.sport_climb, []),
    "Bouldering":    (ActivityType.bouldering, []),
    # Alpine / ski
    "AlpineSki":       (ActivityType.other, ["alpine_ski"]),
    "BackcountrySki":  (ActivityType.other, ["backcountry_ski"]),
    "NordicSki":       (ActivityType.other, ["nordic_ski"]),
    "Snowboard":       (ActivityType.other, ["snowboard"]),
    # Other
    "Kayaking":      (ActivityType.other, ["kayak"]),
    "Canoeing":      (ActivityType.other, ["canoe"]),
    "Rowing":        (ActivityType.other, ["row"]),
    "StandUpPaddling": (ActivityType.other, ["sup"]),
    "Soccer":        (ActivityType.fitness, ["team_sport"]),
    "Tennis":        (ActivityType.fitness, ["tennis"]),
    "Golf":          (ActivityType.other, ["golf"]),
}

_DEFAULT = (ActivityType.other, [])


def _map_type(raw_type: str) -> tuple[ActivityType, list[str]]:
    return _TYPE_MAP.get(raw_type, _DEFAULT)


# ─── Response model ───────────────────────────────────────────────────────────

class ImportResult(BaseModel):
    total_fetched: int
    imported: int
    skipped: int
    errors: list[str]


# ─── Endpoint ─────────────────────────────────────────────────────────────────

@router.post("/import/intervals", response_model=ImportResult)
async def import_from_intervals(
    days_back: int = Query(default=365, ge=1, le=3650,
                           description="How many days back to import"),
    session: AsyncSession = Depends(get_session),
) -> ImportResult:
    """
    Bulk-import all activities from intervals.icu (Garmin sync) for the last
    `days_back` days. Already-imported activities (matched by intervals_activity_id)
    are skipped so the endpoint is safe to call repeatedly.
    """
    from app.services.intervals import fetch_all_activities

    errors: list[str] = []

    # 1. Fetch from intervals.icu
    try:
        raw_activities = await fetch_all_activities(days_back=days_back)
    except Exception as exc:
        return ImportResult(
            total_fetched=0, imported=0, skipped=0,
            errors=[f"intervals.icu fetch failed: {exc}"],
        )

    if not raw_activities:
        return ImportResult(
            total_fetched=0, imported=0, skipped=0,
            errors=["No activities returned — check INTERVALS_ICU_API_KEY and INTERVALS_ICU_ATHLETE_ID"],
        )

    # 2. Load the set of already-imported intervals IDs
    existing_result = await session.execute(
        select(Activity.intervals_activity_id)
        .where(Activity.intervals_activity_id.isnot(None))
    )
    existing_ids: set[str] = {str(r[0]) for r in existing_result.all()}

    # 3. Import new activities
    imported = 0
    skipped = 0

    for raw in raw_activities:
        if raw.id in existing_ids:
            skipped += 1
            continue

        activity_type, tags = _map_type(raw.activity_type)

        # Parse date
        try:
            date = datetime.fromisoformat(raw.start_date_local)
        except (ValueError, TypeError):
            date = datetime.utcnow()

        activity = Activity(
            activity_type=activity_type,
            title=raw.name,
            date=date,
            duration_minutes=round(raw.duration_seconds / 60) if raw.duration_seconds else None,
            distance_km=round(raw.distance_m / 1000, 2) if raw.distance_m else None,
            elevation_gain_m=round(raw.elevation_gain_m) if raw.elevation_gain_m is not None else None,
            lat=raw.start_lat,
            lon=raw.start_lon,
            tags=tags,
            source=ActivitySource.intervals_icu,
            intervals_activity_id=raw.id,
        )
        session.add(activity)
        imported += 1

    if imported > 0:
        try:
            await session.commit()
        except Exception as exc:
            await session.rollback()
            errors.append(f"DB commit failed: {exc}")
            imported = 0

    return ImportResult(
        total_fetched=len(raw_activities),
        imported=imported,
        skipped=skipped,
        errors=errors,
    )
