import argparse
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


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI parser for the QR generation script."""
    parser = argparse.ArgumentParser(
        description="Generate signed QR codes for every zone.",
    )
    parser.add_argument(
        "output_dir",
        nargs="?",
        type=Path,
        default=OUTPUT_DIR,
        help="directory for PNG files (default: %(default)s)",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Parse CLI arguments and generate QR codes."""
    args = build_parser().parse_args(argv)
    generate_zone_qr_codes(args.output_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
