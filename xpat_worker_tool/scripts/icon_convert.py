"""Convert `assets/icon.svg` into platform icon formats.

This script generates:
- assets/icon.png
- assets/icon.ico
- assets/icon.icns

Requirements:
- cairosvg
- pillow

Usage:
    python scripts/icon_convert.py

This is useful for packaging with PyInstaller (which requires .ico on Windows and .icns on macOS).
"""

from __future__ import annotations

import io
from pathlib import Path


def _ensure_deps() -> None:
    try:
        import cairosvg  # noqa: F401
        from PIL import Image  # noqa: F401
    except ImportError as exc:
        raise SystemExit(
            "Missing dependencies. Install with: pip install cairosvg pillow"
        ) from exc


def main() -> None:
    _ensure_deps()

    import cairosvg
    from PIL import Image

    assets_dir = Path(__file__).resolve().parents[1] / "assets"
    svg_file = assets_dir / "icon.svg"
    if not svg_file.exists():
        raise SystemExit(f"SVG icon not found at {svg_file}")

    print(f"Rendering SVG -> PNG (assets/icon.png)")
    png_out = assets_dir / "icon.png"
    png_bytes = cairosvg.svg2png(url=str(svg_file), output_width=1024, output_height=1024)
    png_out.write_bytes(png_bytes)

    print(f"Generating ICO (assets/icon.ico)")
    img = Image.open(io.BytesIO(png_bytes)).convert("RGBA")
    img.save(assets_dir / "icon.ico", sizes=[(256, 256), (128, 128), (64, 64), (32, 32), (16, 16)])

    print(f"Generating ICNS (assets/icon.icns)")
    img.save(assets_dir / "icon.icns")

    print("Done. You can now use the generated icon files with PyInstaller.")


if __name__ == "__main__":
    main()
