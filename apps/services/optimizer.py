from apps.core.tariffs import tariffs
from apps.core.enums import TicketType
from apps.schemas.ticket import TicketResponse
from apps.schemas.trip import TripResponse
from datetime import date, datetime, time, timedelta
from collections import defaultdict


def optimizer(trips: list[TripResponse]) -> list[TicketResponse]:
    """Return the cheapest set of tickets covering the trips, sorted by valid_from.

    Walks the table from fill_table backwards: start at i = len(days), read
    choice[i] = (type, k), buy that ticket and jump to i = k, until i == 0.

    A day or weekly ticket is one ticket that starts at midnight of days[k]:
    for a weekly ticket that is the first day it covers. A single ticket means
    one ticket per trip of days[i - 1], priced by its zones.

    O(n log n) in trips: grouping trips by day is linear, the final sort is not.
    """
    list_of_tickets = []
    table = fill_table(trips=trips)
    i = len(table[0])

    trips_by_day: defaultdict[date, list[TripResponse]] = defaultdict(list)

    for trip in trips:
        trips_by_day[trip.start.date()].append(trip)

    while i > 0:
        type, where_to_past = table[2][i]
        valid = (
            datetime.combine(table[0][where_to_past], time.min)
            if type in (TicketType.DAY_TICKET, TicketType.WEEKLY_TICKET)
            else None
        )
        if valid:
            list_of_tickets.append(
                TicketResponse(type=type, valid_from=valid, price=tariffs[type])
            )
        else:
            day = table[0][i - 1]
            for trip in trips_by_day[day]:
                list_of_tickets.append(
                    TicketResponse(
                        type=TicketType.SINGLE_TICKET,
                        valid_from=trip.start,
                        price=get_price_of_single_ticket(trip=trip),
                    )
                )

        i = where_to_past
    list_of_tickets.sort(key=get_valid_from)
    return list_of_tickets


def min_cost(trips: list[TripResponse]) -> int:
    table = fill_table(trips=trips)
    return table[1][len(table[0])]


def fill_table(
    trips: list[TripResponse],
) -> tuple[list[date], dict[int, int], dict[int, tuple[TicketType, int]]]:
    """Dynamic programming over travel days; returns (days, best, choice).

    days      -- sorted travel dates without repeats; days[i - 1] is "day i".
    best[i]   -- cheapest cost of covering days 1..i; best[0] = 0.
    choice[i] -- (ticket type, k): the last ticket covers days k+1..i, the rest
                 costs best[k]. Single and day tickets give k = i - 1; a weekly
                 ticket gives k = j, the number of days before its 7-day window.

    On equal cost the later candidate wins, as it overwrites the same buffer key:
    weekly beats day, day beats single.

    j only grows: days increase, so the window edge increases too, and a day
    that fell out of one window stays out of every later one. It stops at i - 1
    at the latest, since days[i - 1] is always inside its own window. So j moves
    at most len(days) times in total, and the table is filled in O(n).
    """
    buffer = {}
    best = {}
    choice = {}
    best[0] = 0
    dates_of_trips = sorted([el.start.date() for el in trips])
    # Keep only unique dates while preserving order
    days = list(dict.fromkeys(dates_of_trips))

    singles_prices: defaultdict[date, int] = defaultdict(int)

    for trip in trips:
        singles_prices[trip.start.date()] += get_price_of_single_ticket(trip=trip)

    j = 0
    for i in range(1, len(days) + 1):
        buffer[singles_prices[days[i - 1]] + best[i - 1]] = (
            TicketType.SINGLE_TICKET,
            i - 1,
        )
        buffer[tariffs[TicketType.DAY_TICKET] + best[i - 1]] = (
            TicketType.DAY_TICKET,
            i - 1,
        )

        edge = days[i - 1] - timedelta(days=6)
        while days[j] < edge:
            j += 1

        buffer[tariffs[TicketType.WEEKLY_TICKET] + best[j]] = (
            TicketType.WEEKLY_TICKET,
            j,
        )
        best[i] = min(buffer.keys())
        choice[i] = buffer[best[i]]
        buffer.clear()
    return (days, best, choice)


def get_price_of_single_ticket(trip: TripResponse) -> int:
    return tariffs[TicketType.SINGLE_TICKET] * trip.zones


def get_valid_from(ticket: TicketResponse) -> datetime:
    return ticket.valid_from


def total_price(tickets: list[TicketResponse]) -> int:
    return sum(ticket.price for ticket in tickets)
