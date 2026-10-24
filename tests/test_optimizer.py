import random
from collections import Counter
from datetime import datetime, timedelta

from apps.core.enums import TicketType
from apps.core.tariffs import tariffs
from apps.schemas.ticket import TicketResponse
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


# --- какие именно билеты ---


def test_example_from_briefing():
    # день 1: три поездки -> дневной (8 < 9); дни 10 и 11: по одной -> разовые
    trips = [trip(1, 8), trip(1, 12), trip(1, 18), trip(10, 8), trip(11, 8)]

    tickets = optimizer(trips)

    assert [t.type for t in tickets] == [
        TicketType.DAY_TICKET,
        TicketType.SINGLE_TICKET,
        TicketType.SINGLE_TICKET,
    ]
    assert tickets[0].valid_from == datetime(2026, 10, 1)  # полночь дня
    assert sum(t.price for t in tickets) == 14


def test_weekly_starts_at_first_day_of_window():
    trips = [trip(day, hour) for day in range(13, 17) for hour in (8, 12, 16, 20)]

    tickets = optimizer(trips)

    assert [t.type for t in tickets] == [TicketType.WEEKLY_TICKET]
    assert tickets[0].valid_from == datetime(2026, 10, 13)


def test_tickets_are_sorted_by_time():
    # внутри одного дня разовые тоже должны идти по порядку: 8:00, потом 12:00
    trips = [trip(1, 8), trip(1, 12), trip(9, 9)]

    tickets = optimizer(trips)

    assert [t.valid_from for t in tickets] == [
        datetime(2026, 10, 1, 8),
        datetime(2026, 10, 1, 12),
        datetime(2026, 10, 9, 9),
    ]


def test_tickets_are_sorted_even_if_trips_are_not():
    trips = [trip(9, 9), trip(1, 12), trip(1, 8)]

    tickets = optimizer(trips)

    assert [t.valid_from for t in tickets] == sorted(t.valid_from for t in tickets)


# --- свойства на случайных входах ---


def random_trips(rng: random.Random) -> list[TripResponse]:
    trips = [
        trip(rng.randint(1, 21), rng.randint(6, 22)) for _ in range(rng.randint(0, 12))
    ]
    rng.shuffle(trips)
    return trips


def brute_force_cost(trips: list[TripResponse]) -> int:
    # эталон: честный перебор. Самый ранний непокрытый день закрываем
    # разовыми, дневным или недельным, который НАЧИНАЕТСЯ в этот день
    per_day = Counter(t.start.date() for t in trips)
    days = sorted(per_day)

    def cost_from(k: int) -> int:
        if k == len(days):
            return 0
        day = days[k]
        after_week = k
        while after_week < len(days) and days[after_week] <= day + timedelta(days=6):
            after_week += 1
        return min(
            tariffs[TicketType.SINGLE_TICKET] * per_day[day] + cost_from(k + 1),
            tariffs[TicketType.DAY_TICKET] + cost_from(k + 1),
            tariffs[TicketType.WEEKLY_TICKET] + cost_from(after_week),
        )

    return cost_from(0)


def is_covered(one_trip: TripResponse, tickets: list[TicketResponse]) -> bool:
    day = one_trip.start.date()
    for t in tickets:
        start = t.valid_from.date()
        if t.type == TicketType.SINGLE_TICKET and t.valid_from == one_trip.start:
            return True
        if t.type == TicketType.DAY_TICKET and start == day:
            return True
        if t.type == TicketType.WEEKLY_TICKET and start <= day <= start + timedelta(days=6):
            return True
    return False


def test_min_cost_matches_brute_force():
    rng = random.Random(0)
    for _ in range(2000):
        trips = random_trips(rng)
        assert min_cost(trips) == brute_force_cost(trips)


def test_tickets_cost_exactly_min_cost():
    rng = random.Random(1)
    for _ in range(2000):
        trips = random_trips(rng)
        assert sum(t.price for t in optimizer(trips)) == min_cost(trips)


def test_every_trip_is_covered():
    rng = random.Random(2)
    for _ in range(2000):
        trips = random_trips(rng)
        tickets = optimizer(trips)
        assert all(is_covered(t, tickets) for t in trips)
