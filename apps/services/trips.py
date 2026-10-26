from collections.abc import Sequence
from collections import defaultdict
from apps.core.enums import ScanType
from apps.models.scan import ScanModel
from apps.schemas.stats import PerDaySchema
from apps.schemas.trip import TripResponse

from datetime import datetime
from apps.core.datetimes import to_naive_utc
from sqlalchemy.ext.asyncio import AsyncSession
from apps.CRUD.scan import get_scans
from collections import deque
from typing import Mapping


def build_trips(scans: Sequence[ScanModel]) -> list[TripResponse]:
    opened: ScanModel | None = None
    trips: list[TripResponse] = []
    for el in scans:
        if opened is not None:
            trips.append(TripResponse(start=opened.timestamp, end=el.timestamp))
            opened = None
        if el.scan_type == ScanType.CHECK_IN:
            opened = el
    return trips


def bfs_zones(
    graph: Mapping[str, tuple[str, ...]], start_zone: str, end_zone: str
) -> list[str]:
    """Find shortest path between two zones in graph using BFS."""
    came_from: dict[str, str | None] = {}
    frontier: deque[str] = deque()
    if start_zone in graph and end_zone in graph:
        frontier.append(start_zone)
        came_from[start_zone] = None
    else:
        raise ValueError("Not valid zone")

    while frontier:
        el = frontier.popleft()
        if el == end_zone:
            break
        for neighbor in graph[el]:
            if neighbor not in came_from:
                came_from[neighbor] = el
                frontier.append(neighbor)

    result: list[str] = []
    node: str | None = end_zone
    while node is not None:
        result.append(node)
        node = came_from[node]
    result.reverse()
    return result


def trips_per_day(trips: list[TripResponse]) -> list[PerDaySchema]:
    counts = defaultdict(int)
    trips.sort(key=lambda trip: trip.start)
    for trip in trips:
        trip_date = trip.start.date()
        counts[trip_date] += 1

    return [PerDaySchema(day=day, trips=count) for day, count in counts.items()]


async def get_trips(
    user_id: int,
    date_from: datetime,
    date_to: datetime,
    db: AsyncSession,
) -> list[TripResponse]:
    """Get list of trips for user in given date range"""
    date_from, date_to = to_naive_utc(date_from), to_naive_utc(date_to)
    trips = build_trips(scans=await get_scans(db=db, user_id=user_id))
    trips = [trip for trip in trips if date_from <= trip.start < date_to]
    return trips
