from datetime import datetime

from apps.models.scan import ScanModel, ScanType
from apps.schemas.trip import TripResponse
from apps.services.trips import build_trips

IN = ScanType.CHECK_IN
OUT = ScanType.CHECK_OUT


def at(hh: int, mm: int = 0) -> datetime:
    return datetime(2026, 10, 17, hh, mm)


def scan(kind: ScanType, hh: int, mm: int = 0, zone: str = "A") -> ScanModel:
    # ScanModel можно создать без БД — это просто объект Python
    return ScanModel(user_id=1, scan_type=kind, timestamp=at(hh, mm), zone=zone)


def trip(h1: int, m1: int, h2: int, m2: int) -> TripResponse:
    return TripResponse(
        start=at(h1, m1), end=at(h2, m2), from_zone="A", to_zone="A", zones=1
    )


# --- таблица из брифинга целиком ---


def test_full_day():
    scans = [
        scan(IN, 8, 0),
        scan(OUT, 8, 30),
        scan(IN, 12, 0),
        scan(IN, 18, 0),  # забыл check_out
        scan(OUT, 18, 40),
        scan(OUT, 19, 0),  # out без открытой поездки
        scan(IN, 21, 0),  # незакрыта до конца
    ]
    assert build_trips(scans) == [
        trip(8, 0, 8, 30),
        trip(12, 0, 18, 0),
        trip(18, 0, 18, 40),
    ]


# --- по клетке таблицы 2x2 ---


def test_in_then_out():
    assert build_trips([scan(IN, 8), scan(OUT, 9)]) == [trip(8, 0, 9, 0)]


def test_in_then_in_closes_first():
    # вторая поездка остаётся открытой, поэтому в результат не попадает
    assert build_trips([scan(IN, 8), scan(IN, 9)]) == [trip(8, 0, 9, 0)]


def test_out_without_open_is_ignored():
    assert build_trips([scan(OUT, 8)]) == []


def test_unclosed_in_is_ignored():
    assert build_trips([scan(IN, 8)]) == []


def test_empty():
    assert build_trips([]) == []


# --- зоны ---


def test_trip_takes_zones_from_both_scans():
    trips = build_trips([scan(IN, 8, zone="A"), scan(OUT, 9, zone="F")])

    assert (trips[0].from_zone, trips[0].to_zone, trips[0].zones) == ("A", "F", 4)


def test_forgotten_check_out_ends_in_zone_of_next_check_in():
    trips = build_trips([scan(IN, 8, zone="B"), scan(IN, 12, zone="F")])

    assert (trips[0].from_zone, trips[0].to_zone, trips[0].zones) == ("B", "F", 3)
