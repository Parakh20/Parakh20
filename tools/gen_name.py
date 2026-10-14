"""Render the profile name as theme-aware SVGs with an embedded serif subset.

Usage: python3 -I gen_name.py <fonts_dir> <out_dir>
"""
import base64
import io
import sys
from pathlib import Path

from fontTools.subset import Options, Subsetter
from fontTools.ttLib import TTFont

NAME = "Parakh Sharma"
WIDTH, HEIGHT = 840, 120
FONT_SIZE = 84
BASELINE = 92

# GitHub's own foreground colours, so the name reads as native text in each theme.
THEMES = {"light": "#1f2328", "dark": "#e6edf3"}


def font_b64(path: Path, text: str) -> str:
    font = TTFont(path)
    opts = Options()
    opts.flavor = "woff2"
    sub = Subsetter(opts)
    sub.populate(text=text)
    sub.subset(font)
    font.flavor = "woff2"
    buf = io.BytesIO()
    font.save(buf)
    return base64.b64encode(buf.getvalue()).decode()


def render(color: str, font: str) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" '
        f'viewBox="0 0 {WIDTH} {HEIGHT}" role="img" aria-label="{NAME}"><title>{NAME}</title>'
        f"<style>@font-face{{font-family:IS;src:url(data:font/woff2;base64,{font}) format('woff2');}}</style>"
        f'<text x="0" y="{BASELINE}" font-family="IS, Georgia, serif" font-size="{FONT_SIZE}" '
        f'fill="{color}" letter-spacing="-0.5">{NAME}</text></svg>'
    )


def main() -> None:
    fonts_dir, out_dir = Path(sys.argv[1]), Path(sys.argv[2])
    out_dir.mkdir(parents=True, exist_ok=True)
    font = font_b64(fonts_dir / "InstrumentSerif-Regular.ttf", NAME)
    for theme, color in THEMES.items():
        (out_dir / f"name-{theme}.svg").write_text(render(color, font))
    print("ok", sorted(p.name for p in out_dir.glob("name-*.svg")))


if __name__ == "__main__":
    main()
