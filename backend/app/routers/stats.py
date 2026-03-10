"""
Stats endpoints for the dashboard.
GET /stats/weekly?week_start=YYYY-MM-DD
"""
from datetime import datetime, timedelta, date as date_type
from typing import Optional

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.database import get_session
from app.models.activity import Activity, ActivityOut

router = APIRouter(tags=["stats"])


# ─── Response models ──────────────────────────────────────────────────────────

class DayActivities(BaseModel):
    date: str  # YYYY-MM-DD
    activities: list[ActivityOut]


class WeeklyStats(BaseModel):
    week_start: str
    week_end: str
    total_activities: int
    total_hours: float
    total_elevation_m: float
    by_type: dict[str, int]
    by_day: list[DayActivities]


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _monday_of_week(d: date_type) -> date_type:
    return d - timedelta(days=d.weekday())


# ─── Endpoint ─────────────────────────────────────────────────────────────────

@router.get("/stats/weekly", response_model=WeeklyStats)
async def weekly_stats(
    week_start: Optional[str] = Query(default=None),
    session: AsyncSession = Depends(get_session),
) -> WeeklyStats:
    if week_start:
        try:
            start_date = date_type.fromisoformat(week_start)
        except ValueError:
            start_date = _monday_of_week(date_type.today())
    else:
        start_date = _monday_of_week(date_type.today())

    start_date = _monday_of_week(start_date)
    end_date = start_date + timedelta(days=6)

    start_dt = datetime.combine(start_date, datetime.min.time())
    end_dt = datetime.combine(end_date, datetime.max.time())

    stmt = (
        select(Activity)
        .where(Activity.date >= start_dt)
        .where(Activity.date <= end_dt)
        .order_by(Activity.date)
    )
    result = await session.execute(stmt)
    activities = result.scalars().all()

    total_hours = 0.0
    total_elev = 0.0
    by_type: dict[str, int] = {}

    day_buckets: dict[str, list[ActivityOut]] = {}
    for i in range(7):
        d = (start_date + timedelta(days=i)).isoformat()
        day_buckets[d] = []

    for act in activities:
        act_type = act.activity_type.value
        by_type[act_type] = by_type.get(act_type, 0) + 1
        if act.duration_minutes:
            total_hours += act.duration_minutes / 60
        if act.elevation_gain_m:
            total_elev += act.elevation_gain_m
        day_key = act.date.date().isoformat()
        if day_key in day_buckets:
            day_buckets[day_key].append(ActivityOut.model_validate(act))

    by_day = [
        DayActivities(date=d, activities=acts)
        for d, acts in sorted(day_buckets.items())
    ]

    return WeeklyStats(
        week_start=start_date.isoformat(),
        week_end=end_date.isoformat(),
        total_activities=len(activities),
        total_hours=round(total_hours, 1),
        total_elevation_m=round(total_elev),
        by_type=by_type,
        by_day=by_day,
    )
