from apps.core.zones import ZONES_GRAPH
from apps.core.security import create_zone_token


if __name__ == "__main__":
    for zone in ZONES_GRAPH.keys():
        print(f"{zone}: {create_zone_token(zone)}")
