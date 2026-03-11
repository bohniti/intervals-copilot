from typing import Optional
from datetime import datetime
from sqlmodel import Field, SQLModel
from app.models.activity import GradeSystem, ClimbStyle


class SessionRoute(SQLModel, table=True):
    __tablename__ = "session_routes"

    id: Optional[int] = Field(default=None, primary_key=True)
    activity_id: int = Field(foreign_key="activities.id", index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    route_name: Optional[str] = None
    grade: Optional[str] = None
    grade_system: Optional[GradeSystem] = None
    style: Optional[ClimbStyle] = None    # onsight / flash / redpoint etc.
    pitches: Optional[int] = None         # 1 for single-pitch; >1 for multi-pitch
    height_m: Optional[float] = None
    rock_type: Optional[str] = None
    sector: Optional[str] = None          # sub-area name within crag
    notes: Optional[str] = None
    sort_order: int = Field(default=0)    # ordering within session

    # Enrichment fields (from blog CSV / manual entry)
    tries: Optional[int] = None           # attempts before send (1 = flash/OS, 2+ = took multiple goes)
    stars: Optional[int] = None           # personal rating 0–3 (0=no stars, 3=classic)
    url: Optional[str] = None            # link to route on thecrag / bergsteigen / mountain project


# ─── Pydantic request/response models ─────────────────────────────────────────

class SessionRouteCreate(SQLModel):
    route_name: Optional[str] = None
    grade: Optional[str] = None
    grade_system: Optional[GradeSystem] = None
    style: Optional[ClimbStyle] = None
    pitches: Optional[int] = None
    height_m: Optional[float] = None
    rock_type: Optional[str] = None
    sector: Optional[str] = None
    notes: Optional[str] = None
    sort_order: int = 0
    tries: Optional[int] = None
    stars: Optional[int] = None
    url: Optional[str] = None


class SessionRouteUpdate(SQLModel):
    route_name: Optional[str] = None
    grade: Optional[str] = None
    grade_system: Optional[GradeSystem] = None
    style: Optional[ClimbStyle] = None
    pitches: Optional[int] = None
    height_m: Optional[float] = None
    rock_type: Optional[str] = None
    sector: Optional[str] = None
    notes: Optional[str] = None
    sort_order: Optional[int] = None
    tries: Optional[int] = None
    stars: Optional[int] = None
    url: Optional[str] = None


class SessionRouteOut(SQLModel):
    id: int
    activity_id: int
    created_at: datetime
    route_name: Optional[str] = None
    grade: Optional[str] = None
    grade_system: Optional[GradeSystem] = None
    style: Optional[ClimbStyle] = None
    pitches: Optional[int] = None
    height_m: Optional[float] = None
    rock_type: Optional[str] = None
    sector: Optional[str] = None
    notes: Optional[str] = None
    sort_order: int
    tries: Optional[int] = None
    stars: Optional[int] = None
    url: Optional[str] = None
