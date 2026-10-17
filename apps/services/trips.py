from collections.abc import Sequence

from apps.core.enums import ScanType
from apps.models.scan import ScanModel
from apps.schemas.trip import TripResponse


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
