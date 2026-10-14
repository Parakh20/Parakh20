"""Generate the Swiss-style header and domain markers for the profile README.

Usage: python3 -I gen_swiss.py <fonts_dir> <out_dir>
"""
import base64
import io
import sys
from pathlib import Path

from fontTools.subset import Options, Subsetter
from fontTools.ttLib import TTFont

COBALT, TOMATO, SUN, MINT = "#2B59FF", "#FF5A36", "#FFB800", "#12B886"
THEMES = {
    "light": {"ink": "#1f2328", "muted": "#59636e"},
    "dark": {"ink": "#f0f6fc", "muted": "#9198a1"},
}
NAME = "Parakh Sharma"
ROLE = "AI/ML engineer and full-stack developer, IIT Bombay"
CELL = 84
GAP = 8


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


def circle(x, y, s, color):
    r = s / 2
    return f'<circle cx="{x + r}" cy="{y + r}" r="{r}" fill="{color}"/>'


def square(x, y, s, color):
    return f'<rect x="{x}" y="{y}" width="{s}" height="{s}" fill="{color}"/>'


def triangle(x, y, s, color):
    return f'<path d="M{x},{y + s}L{x + s / 2},{y}L{x + s},{y + s}Z" fill="{color}"/>'


def quarter(x, y, s, color):
    return f'<path d="M{x},{y + s}V{y}A{s},{s} 0 0 1 {x + s},{y + s}Z" fill="{color}"/>'


# One shape per domain; the README reuses them as bullets.
DOMAINS = [("agents", circle, COBALT), ("vision", square, TOMATO), ("products", triangle, SUN), ("quant", quarter, MINT)]


def header(theme: dict, fonts: dict) -> str:
    w, h = 880, 2 * CELL + GAP + 28
    mark = "".join(
        fn((i % 2) * (CELL + GAP), (i // 2) * (CELL + GAP), CELL, color) for i, (_, fn, color) in enumerate(DOMAINS)
    )
    tx = 2 * CELL + GAP + 44
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" '
        f'aria-label="{NAME}, {ROLE}"><title>{NAME}, {ROLE}</title><style>'
        f"@font-face{{font-family:SG;font-weight:700;src:url(data:font/woff2;base64,{fonts['bold']}) format('woff2');}}"
        f"@font-face{{font-family:SG;font-weight:500;src:url(data:font/woff2;base64,{fonts['medium']}) format('woff2');}}"
        "</style>"
        f"{mark}"
        f'<text x="{tx}" y="{(h - 28) / 2 + 8}" font-family="SG, sans-serif" font-weight="700" font-size="66" '
        f'letter-spacing="-2" fill="{theme["ink"]}">{NAME}</text>'
        f'<text x="{tx + 3}" y="{(h - 28) / 2 + 50}" font-family="SG, sans-serif" font-weight="500" font-size="22" '
        f'fill="{theme["muted"]}">{ROLE}</text></svg>'
    )


def marker(fn, color) -> str:
    s = 14
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{s}" height="{s}" viewBox="0 0 {s} {s}">{fn(0, 0, s, color)}</svg>'


def main() -> None:
    fonts_dir, out = Path(sys.argv[1]), Path(sys.argv[2])
    out.mkdir(parents=True, exist_ok=True)
    fonts = {
        "bold": font_b64(fonts_dir / "SpaceGrotesk-Bold.ttf", NAME),
        "medium": font_b64(fonts_dir / "SpaceGrotesk-Medium.ttf", ROLE),
    }
    for name, theme in THEMES.items():
        (out / f"header-{name}.svg").write_text(header(theme, fonts))
    for key, fn, color in DOMAINS:
        (out / f"mark-{key}.svg").write_text(marker(fn, color))
    print("ok", sorted(p.name for p in out.iterdir()))


if __name__ == "__main__":
    main()
