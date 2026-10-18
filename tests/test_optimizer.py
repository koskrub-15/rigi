from datetime import datetime

from apps.core.enums import TicketType
from apps.schemas.trip import TripResponse
from apps.services.optimizer import optimizer


def trip(day: int, hh: int) -> TripResponse:
    return TripResponse(
        start=datetime(2026, 10, day, hh, 0),
        end=datetime(2026, 10, day, hh, 30),
    )


def test_one_single_ticket_per_trip():
    trips = [trip(13, 8), trip(14, 8), trip(15, 18)]

    tickets = optimizer(trips)

    assert len(tickets) == 3
    assert all(t.type == TicketType.SINGLE_TICKET for t in tickets)
    assert [t.valid_from for t in tickets] == [t.start for t in trips]
    assert sum(t.price for t in tickets) == 9


def test_no_trips_no_tickets():
    assert optimizer([]) == []
