from datetime import datetime, timezone


def month_bounds_utc(year: int, month: int) -> tuple[datetime, datetime]:
    """Return a half-open UTC interval [start, end) covering the given month."""
    start = datetime(year, month, 1, tzinfo=timezone.utc)
    carry, next_month_zero_based = divmod(month, 12)
    end = datetime(year + carry, next_month_zero_based + 1, 1, tzinfo=timezone.utc)

    return start, end
