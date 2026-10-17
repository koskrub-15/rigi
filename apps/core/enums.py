from enum import Enum


class ScanType(str, Enum):
    CHECK_IN = "check_in"
    CHECK_OUT = "check_out"


class TicketType(str, Enum):
    SINGLE_TICKET = "single_ticket"
    DAY_TICKET = "day_ticket"
    WEEKLY_TICKET = "weekly_ticket"
