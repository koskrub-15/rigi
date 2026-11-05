from pathlib import Path

import segno

from apps.core.security import create_zone_token
from apps.core.zones import ZONES_GRAPH


OUTPUT_DIR = Path(__file__).resolve().parent.parent.parent / "qr_codes"


def generate_zone_qr_codes(output_dir: Path, scale: int = 10) -> None:
    """
    Generate a PNG QR code with a signed token for every zone.
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    tokens = {zone: create_zone_token(zone) for zone in ZONES_GRAPH}

    longest = max(tokens.values(), key=len)
    version = segno.make_qr(longest, error="m").version

    for zone, token in tokens.items():
        qrcode = segno.make_qr(token, version=version, error="m")
        qrcode.save(output_dir / f"{zone}.png", scale=scale)
        print(f"{zone}: {qrcode.designator} -> {token}")


if __name__ == "__main__":
    generate_zone_qr_codes(OUTPUT_DIR)
