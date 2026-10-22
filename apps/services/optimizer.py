from apps.core.tariffs import tariffs
from apps.core.enums import TicketType
from apps.schemas.ticket import TicketResponse
from apps.schemas.trip import TripResponse
from datetime import timedelta


def optimizer(trips: list[TripResponse]) -> list[TicketResponse]:
    tickets = []
    for trip in trips:
        tickets.append(
            TicketResponse(
                type=TicketType.SINGLE_TICKET,
                valid_from=trip.start,
                price=tariffs[TicketType.SINGLE_TICKET],
            )
        )
    return tickets


def min_cost(trips: list[TripResponse]) -> int:
    # requires optimization, now effeciency is O(n^2), it is possible to update to O(n)
    buffer = []
    best = {}
    best[0] = 0
    dates_of_trips = sorted([el.start.date() for el in trips])
    days = list(dict.fromkeys(dates_of_trips))
    for i in range(1, len(days) + 1):
        j = 0
        buffer.append(
            dates_of_trips.count(days[i - 1]) * tariffs[TicketType.SINGLE_TICKET]
            + best[i - 1]
        )
        buffer.append(tariffs[TicketType.DAY_TICKET] + best[i - 1])
        for day in days:
            if days[i - 1] - timedelta(days=6) > day:
                j += 1
        buffer.append(tariffs[TicketType.WEEKLY_TICKET] + best[j])
        best[i] = min(buffer)
        buffer.clear()
    return best[len(days)]


def total_price(tickets: list[TicketResponse]) -> int:
    return sum(ticket.price for ticket in tickets)
