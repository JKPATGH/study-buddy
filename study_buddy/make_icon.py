"""Generates a simple app icon (icon.icns) for the Zero Study .app bundle."""
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

OUT_DIR = Path(__file__).parent
ICONSET_DIR = OUT_DIR / "StudyBuddy.iconset"
ICNS_PATH = OUT_DIR / "icon.icns"

SIZES = [16, 32, 64, 128, 256, 512, 1024]


def draw_icon(size: int) -> Image.Image:
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    margin = size * 0.06
    draw.rounded_rectangle(
        [margin, margin, size - margin, size - margin],
        radius=size * 0.22,
        fill=(108, 99, 255, 255),
    )

    book_w = size * 0.5
    book_h = size * 0.34
    bx = (size - book_w) / 2
    by = size * 0.32
    draw.rounded_rectangle([bx, by, bx + book_w, by + book_h], radius=size * 0.03, fill=(255, 255, 255, 255))
    draw.line([(size / 2, by), (size / 2, by + book_h)], fill=(108, 99, 255, 255), width=max(1, int(size * 0.015)))

    try:
        font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", int(size * 0.16))
    except OSError:
        font = ImageFont.load_default()
    text = "ZS"
    bbox = draw.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text((size / 2 - tw / 2, by + book_h + size * 0.06 - th / 2), text, fill=(255, 255, 255, 255), font=font)

    return img


def main():
    ICONSET_DIR.mkdir(exist_ok=True)
    for size in SIZES:
        img = draw_icon(size)
        img.save(ICONSET_DIR / f"icon_{size}x{size}.png")
        if size <= 512:
            img2x = draw_icon(size * 2)
            img2x.save(ICONSET_DIR / f"icon_{size}x{size}@2x.png")

    if sys.platform == "darwin":
        subprocess.run(["iconutil", "-c", "icns", str(ICONSET_DIR), "-o", str(ICNS_PATH)], check=True)
        print(f"Wrote {ICNS_PATH}")
    else:
        print("iconutil is macOS-only; .iconset generated but not converted to .icns")


if __name__ == "__main__":
    main()
