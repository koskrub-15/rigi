from apps.core.tariffs import tariffs
from apps.core.enums import TicketType
from apps.schemas.ticket import TicketResponse
from apps.schemas.trip import TripResponse
from datetime import date, datetime, time, timedelta


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
                            price=tariffs[TicketType.SINGLE_TICKET],
                        )
                    )

        i = where_to_past
    list_of_tickets.sort(key=get_valid_from)
    # list_of_tickets.reverse()
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
    # choice[0] = TicketType.SINGLE_TICKET
    dates_of_trips = sorted([el.start.date() for el in trips])
    days = list(dict.fromkeys(dates_of_trips))
    for i in range(1, len(days) + 1):
        j = 0
        buffer[
            dates_of_trips.count(days[i - 1]) * tariffs[TicketType.SINGLE_TICKET]
            + best[i - 1]
        ] = (TicketType.SINGLE_TICKET, i - 1)
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
        # diff = best[i] - best[i - 1]
        choice[i] = buffer[best[i]]
        # choice[i] = next(
        #     (t, j if t in (TicketType.DAY_TICKET, TicketType.SINGLE_TICKET) else i - 1)
        #     for t, price in tariffs.items()
        #     if price == diff
        # )
        buffer.clear()
    return (days, best, choice)


def get_valid_from(ticket: TicketResponse) -> datetime:
    return ticket.valid_from


def total_price(tickets: list[TicketResponse]) -> int:
    return sum(ticket.price for ticket in tickets)
