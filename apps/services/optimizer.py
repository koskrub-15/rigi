from apps.core.tariffs import tariffs
from apps.core.enums import TicketType
from apps.schemas.ticket import TicketResponse
from apps.schemas.trip import TripResponse


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


def total_price(tickets: list[TicketResponse]) -> int:
    return sum(ticket.price for ticket in tickets)
