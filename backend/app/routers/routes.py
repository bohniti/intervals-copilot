"""
Session routes — the individual climbs within a climbing activity.
Each Activity (bouldering / sport_climb / multi_pitch) can have n routes.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.database import get_session
from app.models.activity import Activity
from app.models.route import SessionRoute, SessionRouteCreate, SessionRouteUpdate, SessionRouteOut

router = APIRouter(tags=["routes"])


# ─── List routes for an activity ─────────────────────────────────────────────

@router.get("/activities/{activity_id}/routes", response_model=list[SessionRouteOut])
async def list_routes(
    activity_id: int,
    session: AsyncSession = Depends(get_session),
) -> list[SessionRoute]:
    # Verify activity exists
    activity = await session.get(Activity, activity_id)
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")

    result = await session.execute(
        select(SessionRoute)
        .where(SessionRoute.activity_id == activity_id)
        .order_by(SessionRoute.sort_order, SessionRoute.id)
    )
    return list(result.scalars().all())


# ─── Add a route to an activity ──────────────────────────────────────────────

@router.post(
    "/activities/{activity_id}/routes",
    response_model=SessionRouteOut,
    status_code=status.HTTP_201_CREATED,
)
async def create_route(
    activity_id: int,
    body: SessionRouteCreate,
    session: AsyncSession = Depends(get_session),
) -> SessionRoute:
    activity = await session.get(Activity, activity_id)
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")

    route = SessionRoute(activity_id=activity_id, **body.model_dump())
    session.add(route)
    await session.commit()
    await session.refresh(route)
    return route


# ─── Update a route ───────────────────────────────────────────────────────────

@router.put("/routes/{route_id}", response_model=SessionRouteOut)
async def update_route(
    route_id: int,
    body: SessionRouteUpdate,
    session: AsyncSession = Depends(get_session),
) -> SessionRoute:
    route = await session.get(SessionRoute, route_id)
    if not route:
        raise HTTPException(status_code=404, detail="Route not found")

    for key, value in body.model_dump(exclude_unset=True).items():
        setattr(route, key, value)

    session.add(route)
    await session.commit()
    await session.refresh(route)
    return route


# ─── Delete a route ───────────────────────────────────────────────────────────

@router.delete("/routes/{route_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_route(
    route_id: int,
    session: AsyncSession = Depends(get_session),
) -> None:
    route = await session.get(SessionRoute, route_id)
    if not route:
        raise HTTPException(status_code=404, detail="Route not found")

    await session.delete(route)
    await session.commit()
