from datetime import timedelta
from apps.core.enums import TicketType

MAX_TRIP_DURATION = timedelta(hours=3)

tariffs = {
    TicketType.SINGLE_TICKET: 3,  # price for one zone trip, for more zones, price is gradually increased
    TicketType.DAY_TICKET: 8,  # now all zones included
    TicketType.WEEKLY_TICKET: 25,  # now all zones included
}
