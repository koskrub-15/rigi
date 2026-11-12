from datetime import datetime, timedelta, timezone

import pytest

from apps.services.month import month_bounds_utc, split_by_months


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


def test_split_by_months_within_one_month():
    start = datetime(2026, 10, 13, 8)
    end = datetime(2026, 10, 20, 18)

    assert list(split_by_months(start, end)) == [
        (start.replace(tzinfo=timezone.utc), end.replace(tzinfo=timezone.utc))
    ]


def test_split_by_months_exactly_one_month():
    start = datetime(2026, 10, 1)
    end = datetime(2026, 11, 1)

    assert list(split_by_months(start, end)) == [
        (start.replace(tzinfo=timezone.utc), end.replace(tzinfo=timezone.utc))
    ]


def test_split_by_months_three_months():
    start = datetime(2026, 10, 1)
    end = datetime(2027, 1, 1)

    assert list(split_by_months(start, end)) == [
        (
            datetime(2026, 10, 1, tzinfo=timezone.utc),
            datetime(2026, 11, 1, tzinfo=timezone.utc),
        ),
        (
            datetime(2026, 11, 1, tzinfo=timezone.utc),
            datetime(2026, 12, 1, tzinfo=timezone.utc),
        ),
        (
            datetime(2026, 12, 1, tzinfo=timezone.utc),
            datetime(2027, 1, 1, tzinfo=timezone.utc),
        ),
    ]


def test_split_by_months_with_partial_edges():
    start = datetime(2026, 10, 15, 9)
    end = datetime(2026, 12, 5, 17)

    assert list(split_by_months(start, end)) == [
        (
            datetime(2026, 10, 15, 9, tzinfo=timezone.utc),
            datetime(2026, 11, 1, tzinfo=timezone.utc),
        ),
        (
            datetime(2026, 11, 1, tzinfo=timezone.utc),
            datetime(2026, 12, 1, tzinfo=timezone.utc),
        ),
        (
            datetime(2026, 12, 1, tzinfo=timezone.utc),
            datetime(2026, 12, 5, 17, tzinfo=timezone.utc),
        ),
    ]


def test_split_by_months_across_december_and_january():
    start = datetime(2026, 12, 15)
    end = datetime(2027, 1, 15)

    assert list(split_by_months(start, end)) == [
        (
            datetime(2026, 12, 15, tzinfo=timezone.utc),
            datetime(2027, 1, 1, tzinfo=timezone.utc),
        ),
        (
            datetime(2027, 1, 1, tzinfo=timezone.utc),
            datetime(2027, 1, 15, tzinfo=timezone.utc),
        ),
    ]


def test_split_by_months_normalizes_aware_datetimes_to_utc():
    input_timezone = timezone(timedelta(hours=2))
    start = datetime(2026, 11, 1, 1, tzinfo=input_timezone)
    end = datetime(2026, 11, 1, 3, tzinfo=input_timezone)

    assert list(split_by_months(start, end)) == [
        (
            datetime(2026, 10, 31, 23, tzinfo=timezone.utc),
            datetime(2026, 11, 1, tzinfo=timezone.utc),
        ),
        (
            datetime(2026, 11, 1, tzinfo=timezone.utc),
            datetime(2026, 11, 1, 1, tzinfo=timezone.utc),
        ),
    ]


def test_split_by_months_empty_interval():
    instant = datetime(2026, 10, 13, 8)

    assert list(split_by_months(instant, instant)) == []


def test_split_by_months_rejects_start_after_end():
    with pytest.raises(ValueError):
        list(split_by_months(datetime(2026, 10, 2), datetime(2026, 10, 1)))
