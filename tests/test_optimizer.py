from datetime import datetime

from apps.core.enums import TicketType
from apps.schemas.trip import TripResponse
from apps.services.optimizer import min_cost, optimizer


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


def test_min_cost_weekly_ticket():
    trips = [trip(day, hour) for day in range(13, 17) for hour in (8, 12, 16, 20)]

    assert min_cost(trips) == 25


def test_min_cost_no_trips():
    assert min_cost([]) == 0


def test_min_cost_one_trip():
    assert min_cost([trip(13, 8)]) == 3


def test_min_cost_three_trips_in_one_day():
    trips = [trip(13, 8), trip(13, 12), trip(13, 18)]

    assert min_cost(trips) == 8


def test_min_cost_trips_seven_days_apart():
    trips = [trip(1, 8), trip(8, 8)]

    assert min_cost(trips) == 6


def test_min_cost_order_of_trips_does_not_matter():
    trips = [trip(1, 8), trip(1, 12), trip(2, 8), trip(5, 18), trip(9, 8)]

    assert min_cost(list(reversed(trips))) == min_cost(trips)

