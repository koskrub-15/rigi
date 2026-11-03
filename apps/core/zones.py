from types import MappingProxyType
from typing import Final, Mapping
from typing import Annotated
from pydantic import AfterValidator

ZONES_GRAPH: Final[Mapping[str, tuple[str, ...]]] = MappingProxyType(
    {
        "A": ("B", "C"),
        "B": ("D", "A"),
        "C": ("D", "E", "A"),
        "D": ("F", "B", "C"),
        "E": ("F", "C"),
        "F": ("D", "E"),
    }
)


def check_zone(value: str) -> str:
    """Ensure the zone is present in the tariff graph."""
    if value not in ZONES_GRAPH:
        raise ValueError(f"unknown zone: {value!r}")
    return value


Zone = Annotated[str, AfterValidator(check_zone)]
