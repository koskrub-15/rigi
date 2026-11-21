import calendar
import random
from collections import Counter, defaultdict
from datetime import date, datetime, time, timedelta

from apps.core.enums import TicketType
from apps.core.tariffs import tariffs
from apps.schemas.ticket import TicketResponse
from apps.schemas.trip import TripResponse
from apps.services.optimizer import fill_table, min_cost, optimizer, total_price


def trip(day: int, hh: int, zones: int = 1) -> TripResponse:
    # the optimizer ignores from/to, it only looks at zones
    return TripResponse(
        start=datetime(2026, 10, day, hh, 0),
        end=datetime(2026, 10, day, hh, 30),
        from_zone="A",
        to_zone="A",
        zones=zones,
    )


def test_one_single_ticket_per_trip():
    trips = [trip(13, 8), trip(14, 8), trip(15, 18)]

    tickets = optimizer(trips)

    assert len(tickets) == 3
    assert all(t.type == TicketType.SINGLE_TICKET for t in tickets)
    assert [t.valid_from for t in tickets] == [t.start for t in trips]
    assert sum(t.price for t in tickets) == 9


def test_single_ticket_price_is_per_zone():
    tickets = optimizer([trip(13, 8, zones=2)])

    assert [(t.type, t.price) for t in tickets] == [(TicketType.SINGLE_TICKET, 6)]


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


def test_min_cost_two_trips_with_same_start():
    """Regression: single prices were keyed by trip.start and overwrote each other."""
    assert min_cost([trip(13, 8), trip(13, 8)]) == 6


def test_min_cost_single_price_grows_with_zones():
    assert min_cost([trip(13, 8, zones=2)]) == 6


def test_min_cost_three_zones_cheaper_with_day_ticket():
    assert min_cost([trip(13, 8, zones=3)]) == 8


def test_min_cost_mixed_zones_in_one_day():
    # 3 + 3 = 6 < 8: singles, even with two trips
    assert min_cost([trip(13, 8), trip(13, 18)]) == 6
    # 3 + 6 = 9 > 8: the second trip crosses 2 zones, so a day ticket
    assert min_cost([trip(13, 8), trip(13, 18, zones=2)]) == 8


# --- which tickets exactly ---


def test_example_from_briefing():
    # day 1: three trips -> day ticket (8 < 9); days 10 and 11: one each -> singles
    trips = [trip(1, 8), trip(1, 12), trip(1, 18), trip(10, 8), trip(11, 8)]

    tickets = optimizer(trips)

    assert [t.type for t in tickets] == [
        TicketType.DAY_TICKET,
        TicketType.SINGLE_TICKET,
        TicketType.SINGLE_TICKET,
    ]
    assert tickets[0].valid_from == datetime(2026, 10, 1)  # midnight
    assert sum(t.price for t in tickets) == 14


def test_weekly_starts_at_first_day_of_window():
    trips = [trip(day, hour) for day in range(13, 17) for hour in (8, 12, 16, 20)]

    tickets = optimizer(trips)

    assert [t.type for t in tickets] == [TicketType.WEEKLY_TICKET]
    assert tickets[0].valid_from == datetime(2026, 10, 13)


def test_optimizer_uses_weekly_ticket_for_last_seven_days():
    trips = [
        trip(day, 8, zones) for day, zones in enumerate([1, 2, 2, 2, 2, 2, 2, 2], 1)
    ]

    tickets = optimizer(trips)

    assert [(t.type, t.valid_from) for t in tickets] == [
        (TicketType.SINGLE_TICKET, datetime(2026, 10, 1, 8)),
        (TicketType.WEEKLY_TICKET, datetime(2026, 10, 2)),
    ]


def test_optimizer_uses_weekly_ticket_for_first_seven_days():
    trips = [
        trip(day, 8, zones) for day, zones in enumerate([2, 2, 2, 2, 2, 2, 2, 1], 1)
    ]

    tickets = optimizer(trips)

    assert [(t.type, t.valid_from) for t in tickets] == [
        (TicketType.WEEKLY_TICKET, datetime(2026, 10, 1)),
        (TicketType.SINGLE_TICKET, datetime(2026, 10, 8, 8)),
    ]


def test_tickets_are_sorted_by_time():
    """Singles within one day are in order too: 8:00, then 12:00."""
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


# --- properties on random inputs ---


def random_trips(rng: random.Random) -> list[TripResponse]:
    trips = [
        trip(rng.randint(1, 21), rng.randint(6, 22), rng.randint(1, 4))
        for _ in range(rng.randint(0, 12))
    ]
    rng.shuffle(trips)
    return trips


def random_month_trips(rng: random.Random) -> list[TripResponse]:
    year = rng.randint(2020, 2035)
    month = rng.randint(1, 12)
    days_in_month = calendar.monthrange(year, month)[1]
    trips = []
    for _ in range(rng.randint(0, 100)):
        start = datetime(
            year,
            month,
            rng.randint(1, days_in_month),
            rng.randrange(24),
            rng.randrange(60),
        )
        trips.append(
            TripResponse(
                start=start,
                end=start + timedelta(minutes=30),
                from_zone="A",
                to_zone="A",
                zones=rng.randint(1, 4),
            )
        )
    rng.shuffle(trips)
    return trips


def reference_fill_table(
    trips: list[TripResponse],
) -> tuple[list[date], dict[int, int], dict[int, tuple[TicketType, int]]]:
    buffer = {}
    best = {0: 0}
    choice = {}
    dates_of_trips = sorted([trip.start.date() for trip in trips])
    days = list(dict.fromkeys(dates_of_trips))
    singles_prices: defaultdict[date, int] = defaultdict(int)

    for trip in trips:
        singles_prices[trip.start.date()] += (
            tariffs[TicketType.SINGLE_TICKET] * trip.zones
        )

    for i in range(1, len(days) + 1):
        j = 0
        buffer[singles_prices[days[i - 1]] + best[i - 1]] = (
            TicketType.SINGLE_TICKET,
            i - 1,
        )
        buffer[tariffs[TicketType.DAY_TICKET] + best[i - 1]] = (
            TicketType.DAY_TICKET,
            i - 1,
        )
        for day in days:
            if days[i - 1] - timedelta(days=6) > day:
                j += 1
        buffer[tariffs[TicketType.WEEKLY_TICKET] + best[j]] = (
            TicketType.WEEKLY_TICKET,
            j,
        )
        best[i] = min(buffer.keys())
        choice[i] = buffer[best[i]]
        buffer.clear()
    return days, best, choice


def reference_optimizer(trips: list[TripResponse]) -> list[TicketResponse]:
    list_of_tickets = []
    table = reference_fill_table(trips)
    i = len(table[0])
    while i > 0:
        ticket_type, where_to_past = table[2][i]
        valid = (
            datetime.combine(table[0][where_to_past], time.min)
            if ticket_type in (TicketType.DAY_TICKET, TicketType.WEEKLY_TICKET)
            else None
        )
        if valid:
            list_of_tickets.append(
                TicketResponse(
                    type=ticket_type,
                    valid_from=valid,
                    price=tariffs[ticket_type],
                )
            )
        else:
            for trip in trips:
                if trip.start.date() == table[0][i - 1]:
                    list_of_tickets.append(
                        TicketResponse(
                            type=TicketType.SINGLE_TICKET,
                            valid_from=trip.start,
                            price=tariffs[TicketType.SINGLE_TICKET] * trip.zones,
                        )
                    )

        i = where_to_past

    list_of_tickets.sort(key=lambda ticket: ticket.valid_from)
    return list_of_tickets


def brute_force_cost(trips: list[TripResponse]) -> int:
    """Reference: exhaustive search.

    The earliest uncovered day is covered by singles, a day ticket, or a weekly
    ticket that STARTS on that day.
    """
    per_day: Counter[date] = Counter()
    for t in trips:
        per_day[t.start.date()] += tariffs[TicketType.SINGLE_TICKET] * t.zones
    days = sorted(per_day)

    def cost_from(k: int) -> int:
        if k == len(days):
            return 0
        day = days[k]
        after_week = k
        while after_week < len(days) and days[after_week] <= day + timedelta(days=6):
            after_week += 1
        return min(
            per_day[day] + cost_from(k + 1),
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
        if t.type == TicketType.WEEKLY_TICKET and start <= day <= start + timedelta(
            days=6
        ):
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


def test_fill_table_matches_reference_for_empty_and_single_day_inputs():
    trips_by_case = [
        [],
        [trip(13, 8)],
        [trip(13, 8, zones=2), trip(13, 12), trip(13, 18, zones=2)],
    ]

    for trips in trips_by_case:
        assert fill_table(trips) == reference_fill_table(trips)


def test_fill_table_matches_reference_at_six_day_weekly_boundary(monkeypatch):
    monkeypatch.setitem(tariffs, TicketType.SINGLE_TICKET, 3)
    monkeypatch.setitem(tariffs, TicketType.DAY_TICKET, 8)
    monkeypatch.setitem(tariffs, TicketType.WEEKLY_TICKET, 4)
    trips = [trip(1, 8), trip(7, 8)]

    assert fill_table(trips) == reference_fill_table(trips), trips


def test_fill_table_matches_reference_for_thousands_of_random_months(monkeypatch):
    rng = random.Random(3)
    for _ in range(3000):
        monkeypatch.setitem(tariffs, TicketType.SINGLE_TICKET, rng.randint(1, 10))
        monkeypatch.setitem(tariffs, TicketType.DAY_TICKET, rng.randint(1, 40))
        monkeypatch.setitem(tariffs, TicketType.WEEKLY_TICKET, rng.randint(1, 120))
        trips = random_month_trips(rng)

        assert fill_table(trips) == reference_fill_table(trips)


def test_optimizer_matches_reference_for_thousands_of_random_months(monkeypatch):
    rng = random.Random(4)
    for _ in range(3000):
        monkeypatch.setitem(tariffs, TicketType.SINGLE_TICKET, rng.randint(1, 10))
        monkeypatch.setitem(tariffs, TicketType.DAY_TICKET, rng.randint(1, 40))
        monkeypatch.setitem(tariffs, TicketType.WEEKLY_TICKET, rng.randint(1, 120))
        trips = random_month_trips(rng)

        assert optimizer(trips) == reference_optimizer(trips), trips


def test_optimizer_matches_brute_force_with_random_tariffs(monkeypatch):
    rng = random.Random(42)
    for _ in range(5000):
        monkeypatch.setitem(tariffs, TicketType.SINGLE_TICKET, rng.randint(1, 10))
        monkeypatch.setitem(tariffs, TicketType.DAY_TICKET, rng.randint(1, 40))
        monkeypatch.setitem(tariffs, TicketType.WEEKLY_TICKET, rng.randint(1, 120))
        trips = random_trips(rng)

        assert min_cost(trips) == brute_force_cost(trips)
        assert total_price(optimizer(trips)) == min_cost(trips)
