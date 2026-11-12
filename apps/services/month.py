from collections.abc import Iterator
from datetime import datetime, timezone


def month_bounds_utc(year: int, month: int) -> tuple[datetime, datetime]:
    """Return a half-open UTC interval [start, end) covering the given month."""
    start = datetime(year, month, 1, tzinfo=timezone.utc)
    carry, next_month_zero_based = divmod(month, 12)
    end = datetime(year + carry, next_month_zero_based + 1, 1, tzinfo=timezone.utc)
    return start, end


def _to_utc(dt: datetime) -> datetime:
    """Normalize a datetime to aware UTC"""
    if dt.utcoffset() is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def split_by_months(
    start: datetime, end: datetime
) -> Iterator[tuple[datetime, datetime]]:
    """Split the half-open interval ``[start, end)`` into UTC calendar-month chunks."""
    start_utc, end_utc = _to_utc(start), _to_utc(end)
    if start_utc > end_utc:
        raise ValueError(f"start ({start}) must not be later than end ({end})")
    return _iter_month_chunks(start_utc, end_utc)


def _iter_month_chunks(
    start: datetime, end: datetime
) -> Iterator[tuple[datetime, datetime]]:
    """Yield month chunks of ``[start, end)``. Expects validated UTC inputs."""
    current = start
    while current < end:
        _, month_end = month_bounds_utc(current.year, current.month)
        chunk_end = min(month_end, end)
        yield current, chunk_end
        current = chunk_end
