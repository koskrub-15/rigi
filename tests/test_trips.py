from datetime import datetime, timezone

from apps.models.scan import ScanModel, ScanType
from apps.schemas.trip import TripResponse
from apps.services.trips import build_trips, farthest_path

IN = ScanType.CHECK_IN
OUT = ScanType.CHECK_OUT


def at(hh: int, mm: int = 0) -> datetime:
    return datetime(2026, 10, 17, hh, mm)


def scan(kind: ScanType, hh: int, mm: int = 0, zone: str = "A") -> ScanModel:
    # ScanModel можно создать без БД — это просто объект Python
    return ScanModel(user_id=1, scan_type=kind, timestamp=at(hh, mm), zone=zone)


def trip(
    h1: int,
    m1: int,
    h2: int,
    m2: int,
    *,
    from_zone: str = "A",
    to_zone: str = "A",
    zones: int = 1,
    forgotten: bool = False,
) -> TripResponse:
    return TripResponse(
        start=at(h1, m1),
        end=at(h2, m2),
        from_zone=from_zone,
        to_zone=to_zone,
        zones=zones,
        forgotten=forgotten,
    )


def build(scans: list[ScanModel], now: datetime | None = None) -> list[TripResponse]:
    if now is None:
        now = at(23, 59)
    return build_trips(scans=scans, now=now)


def test_farthest_path_returns_longest_shortest_route():
    graph = {
        "A": ("B", "C"),
        "B": ("A", "D"),
        "C": ("A",),
        "D": ("B",),
    }

    assert farthest_path(graph=graph, start_zone="A") == ["A", "B", "D"]


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
    assert build(scans) == [
        trip(8, 0, 8, 30),
        trip(12, 0, 15, 0, to_zone="F", zones=4, forgotten=True),
        trip(18, 0, 18, 40),
    ]


# --- по клетке таблицы 2x2 ---


def test_in_then_out():
    assert build([scan(IN, 8), scan(OUT, 9)]) == [trip(8, 0, 9, 0)]


def test_in_then_in_closes_first():
    # Первый вход закрывается как забытая поездка, второй остаётся открытым.
    assert build([scan(IN, 8), scan(IN, 9)], now=at(11, 59)) == [
        trip(8, 0, 11, 0, to_zone="F", zones=4, forgotten=True)
    ]


def test_out_without_open_is_ignored():
    assert build([scan(OUT, 8)]) == []


def test_unclosed_in_is_ignored():
    assert build([scan(IN, 8)], now=at(10, 59)) == []


def test_empty():
    assert build([]) == []


# --- зоны ---


def test_trip_takes_zones_from_both_scans():
    trips = build([scan(IN, 8, zone="A"), scan(OUT, 9, zone="F")])

    assert (trips[0].from_zone, trips[0].to_zone, trips[0].zones) == ("A", "F", 4)


def test_checkout_at_max_duration_is_forgotten():
    trips = build([scan(IN, 8, zone="A"), scan(OUT, 11, zone="B")])

    assert trips == [trip(8, 0, 11, 0, to_zone="F", zones=4, forgotten=True)]


def test_open_trip_becomes_forgotten_at_max_duration():
    trips = build([scan(IN, 8)], now=at(11).replace(tzinfo=timezone.utc))

    assert trips == [trip(8, 0, 11, 0, to_zone="F", zones=4, forgotten=True)]


def test_checkin_before_checkout_closes_first_trip_as_forgotten():
    trips = build([scan(IN, 8, zone="B"), scan(IN, 9, zone="F")], now=at(11, 59))

    assert trips == [
        trip(8, 0, 11, 0, from_zone="B", to_zone="E", zones=4, forgotten=True)
    ]
