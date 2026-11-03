import random

import pytest

from apps.core.zones import ZONES_GRAPH
from apps.services.trips import bfs_zones

# Карта:
#   A ─ B ─ D ─ F
#   │       │   │
#   C ──────┘   │
#   │           │
#   E ──────────┘


def is_valid_path(graph, path: list[str], start: str, end: str) -> bool:
    return (
        path[0] == start
        and path[-1] == end
        and all(path[i + 1] in graph[path[i]] for i in range(len(path) - 1))
    )


# --- конкретные пути (на карте они единственные кратчайшие) ---


def test_same_zone():
    assert bfs_zones(ZONES_GRAPH, "A", "A") == ["A"]


def test_neighbour():
    assert bfs_zones(ZONES_GRAPH, "A", "B") == ["A", "B"]


def test_two_steps():
    assert bfs_zones(ZONES_GRAPH, "A", "E") == ["A", "C", "E"]
    assert bfs_zones(ZONES_GRAPH, "B", "F") == ["B", "D", "F"]


def test_reverse_direction():
    assert bfs_zones(ZONES_GRAPH, "F", "B") == ["F", "D", "B"]


def test_does_not_take_first_long_branch():
    # поиск в глубину по порядку соседей пошёл бы B-D-F-E-C (5 зон),
    # кратчайших путей два (B-A-C и B-D-C), оба по 3 зоны
    path = bfs_zones(ZONES_GRAPH, "B", "C")

    assert len(path) == 3
    assert is_valid_path(ZONES_GRAPH, path, "B", "C")


def test_all_pairs_are_valid_and_symmetric():
    for a in ZONES_GRAPH:
        for b in ZONES_GRAPH:
            path = bfs_zones(ZONES_GRAPH, a, b)
            assert is_valid_path(ZONES_GRAPH, path, a, b)
            assert len(path) == len(bfs_zones(ZONES_GRAPH, b, a))


@pytest.mark.parametrize("start, end", [("A", "Z"), ("Z", "A"), ("Z", "Z")])
def test_unknown_zone(start: str, end: str):
    with pytest.raises(ValueError):
        bfs_zones(ZONES_GRAPH, start, end)


# --- против перебора на случайных графах ---


def random_graph(rng: random.Random) -> dict[str, tuple[str, ...]]:
    n = rng.randint(1, 8)
    names = [str(i) for i in range(n)]
    edges: dict[str, set[str]] = {v: set() for v in names}
    # остовное дерево — чтобы граф был связный
    for i in range(1, n):
        j = rng.randrange(i)
        edges[names[i]].add(names[j])
        edges[names[j]].add(names[i])
    # плюс случайные лишние рёбра, чтобы появились циклы
    for _ in range(rng.randint(0, n)):
        a, b = rng.choice(names), rng.choice(names)
        if a != b:
            edges[a].add(b)
            edges[b].add(a)
    graph = {}
    for v, ns in edges.items():
        ordered = sorted(ns)
        rng.shuffle(ordered)
        graph[v] = tuple(ordered)
    return graph


def brute_force_len(graph, start: str, end: str) -> int:
    # эталон: перебор всех простых путей, минимум по числу зон
    best = len(graph) + 1

    def walk(v: str, seen: set[str]) -> None:
        nonlocal best
        if v == end:
            best = min(best, len(seen))
            return
        for n in graph[v]:
            if n not in seen:
                walk(n, seen | {n})

    walk(start, {start})
    return best


def test_bfs_matches_brute_force():
    rng = random.Random(0)
    for _ in range(2000):
        graph = random_graph(rng)
        start, end = rng.choice(list(graph)), rng.choice(list(graph))
        path = bfs_zones(graph, start, end)
        assert is_valid_path(graph, path, start, end)
        assert len(path) == brute_force_len(graph, start, end)
