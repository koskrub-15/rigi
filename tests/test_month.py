from datetime import datetime, timezone

import pytest

from apps.services.month import month_bounds_utc


@pytest.mark.parametrize(
    ("year", "month", "expected_start", "expected_end"),
    [
        (2026, 2, datetime(2026, 2, 1), datetime(2026, 3, 1)),
        (2024, 2, datetime(2024, 2, 1), datetime(2024, 3, 1)),
        (2026, 12, datetime(2026, 12, 1), datetime(2027, 1, 1)),
    ],
)
def test_month_bounds_are_half_open_utc(
    year: int,
    month: int,
    expected_start: datetime,
    expected_end: datetime,
):
    start, end = month_bounds_utc(year, month)

    assert start == expected_start.replace(tzinfo=timezone.utc)
    assert end == expected_end.replace(tzinfo=timezone.utc)
    assert start.tzinfo is timezone.utc
    assert end.tzinfo is timezone.utc
