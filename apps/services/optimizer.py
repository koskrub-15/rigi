from apps.core.tariffs import tariffs
from apps.core.enums import TicketType
from apps.schemas.ticket import TicketResponse
from apps.schemas.trip import TripResponse
from datetime import date, datetime, time, timedelta
from collections import defaultdict


def optimizer(trips: list[TripResponse]) -> list[TicketResponse]:
    list_of_tickets = []
    table = fill_table(trips=trips)
    i = len(table[0])
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
            for trip in trips:
                if trip.start.date() == table[0][i - 1]:
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
    # requires optimization, now effeciency is O(n^2), it is possible to update to O(n)
    buffer = {}
    best = {}
    choice = {}
    best[0] = 0
    dates_of_trips = sorted([el.start.date() for el in trips])
    days = list(dict.fromkeys(dates_of_trips))

    singles_prices: defaultdict[date, int] = defaultdict(int)

    for trip in trips:
        singles_prices[trip.start.date()] += get_price_of_single_ticket(trip=trip)

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
    return (days, best, choice)


def get_price_of_single_ticket(trip: TripResponse) -> int:
    return tariffs[TicketType.SINGLE_TICKET] * trip.zones


def get_valid_from(ticket: TicketResponse) -> datetime:
    return ticket.valid_from


def total_price(tickets: list[TicketResponse]) -> int:
    return sum(ticket.price for ticket in tickets)
