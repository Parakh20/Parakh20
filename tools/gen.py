"""Generate thermal-HUD SVG assets for the Parakh20 profile README.

Usage: python3 -I gen.py <fonts_dir> <out_dir>
"""
import base64
import io
import sys
from pathlib import Path
from xml.sax.saxutils import escape

from fontTools.subset import Options, Subsetter
from fontTools.ttLib import TTFont

FONTS_DIR, OUT_DIR = Path(sys.argv[1]), Path(sys.argv[2])
OUT_DIR.mkdir(parents=True, exist_ok=True)

COLD = "#0E0A2A"
PANEL = "#140E36"
PURPLE = "#3B0F70"
MAGENTA = "#B5367A"
ORANGE = "#FB8B24"
HOT = "#FCFFA4"
INK = "#FFF3E6"
MUTED = "#C9B8D9"

GLYPHS = "".join(chr(c) for c in range(32, 127)) + "·–’"


def font_b64(weight: str) -> str:
    font = TTFont(FONTS_DIR / f"ChakraPetch-{weight}.ttf")
    opts = Options()
    opts.flavor = "woff2"
    opts.layout_features = ["kern", "liga"]
    sub = Subsetter(opts)
    sub.populate(text=GLYPHS)
    sub.subset(font)
    buf = io.BytesIO()
    font.flavor = "woff2"
    font.save(buf)
    return base64.b64encode(buf.getvalue()).decode()


FONT_CSS = "".join(
    f"@font-face{{font-family:CP;font-weight:{w};src:url(data:font/woff2;base64,{font_b64(n)}) format('woff2');}}"
    for n, w in (("Medium", 500), ("SemiBold", 600), ("Bold", 700))
)

HEAT_CORE = [HOT, ORANGE, MAGENTA, PURPLE]
WARM_CORE = [MAGENTA, PURPLE]


def radial(gid: str, core=HEAT_CORE) -> str:
    """Hot centre fading through the inferno ramp to transparent cold."""
    step = 1 / len(core)
    stops = "".join(f'<stop offset="{i * step:.2f}" stop-color="{c}"/>' for i, c in enumerate(core))
    return f'<radialGradient id="{gid}">{stops}<stop offset="1" stop-color="{COLD}" stop-opacity="0"/></radialGradient>'


def corners(x, y, w, h, color, arm=22, sw=2, op=0.9) -> str:
    d = (
        f"M{x},{y + arm}V{y}H{x + arm} "
        f"M{x + w - arm},{y}H{x + w}V{y + arm} "
        f"M{x + w},{y + h - arm}V{y + h}H{x + w - arm} "
        f"M{x + arm},{y + h}H{x}V{y + h - arm}"
    )
    return f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{sw}" opacity="{op}"/>'


def t(x, y, text, size, weight=500, fill=INK, anchor="start", extra="") -> str:
    return (
        f'<text x="{x}" y="{y}" font-family="CP, sans-serif" font-size="{size}" '
        f'font-weight="{weight}" fill="{fill}" text-anchor="{anchor}" {extra}>{escape(text)}</text>'
    )


def svg(w, h, body, css="", title="") -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
        f'role="img" aria-label="{escape(title)}"><title>{escape(title)}</title>'
        f"<style>{FONT_CSS}{css}</style>{body}</svg>"
    )


def detection(i, x, y, w, h, label, conf, color) -> str:
    """A YOLO-style box that draws itself in, with a label tab."""
    tab_w = 18 + len(label) * 10.5 + 44
    return (
        f'<g class="det" style="--d:{0.5 + i * 0.35}s">'
        f'<rect class="box" x="{x}" y="{y}" width="{w}" height="{h}" pathLength="1" fill="none" stroke="{color}" stroke-width="2.5"/>'
        f'<g class="tab"><rect x="{x - 1.25}" y="{y - 30}" width="{tab_w}" height="30" fill="{color}"/>'
        + t(x + 10, y - 9, label, 18, 700, COLD)
        + t(x + tab_w - 10, y - 9, conf, 18, 500, COLD, "end", 'opacity="0.75"')
        + "</g></g>"
    )


def hero() -> str:
    W, H = 1280, 440
    blobs = [
        (300, 230, 380, 170, "hb"),
        (1010, 150, 190, 120, "hb"),
        (1080, 250, 200, 120, "hb"),
        (980, 345, 210, 110, "hb"),
        (640, 470, 300, 120, "hc"),
        (90, 40, 200, 120, "hc"),
    ]
    field = "".join(
        f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="url(#{g})"/>' for cx, cy, rx, ry, g in blobs
    )
    ramp = "".join(
        f'<rect x="{80 + i * 9}" y="{H - 52}" width="9" height="10" fill="{c}"/>'
        for i, c in enumerate([COLD, "#1F0C48", PURPLE, "#6A176E", MAGENTA, "#D44842", ORANGE, "#F9C932", HOT])
    )
    dets = (
        detection(0, 62, 140, 640, 180, "parakh", "0.99", HOT)
        + detection(1, 860, 100, 330, 78, "ai/ml engineer", "0.97", HOT)
        + detection(2, 900, 214, 340, 78, "full-stack developer", "0.95", ORANGE)
        + detection(3, 840, 328, 300, 78, "quant / systems", "0.91", MAGENTA)
    )
    tags = (
        t(1025, 150, "LLM agents · RAG · vision", 22, 600, INK, "middle")
        + t(1070, 264, "Next.js · FastAPI · APIs", 22, 600, INK, "middle")
        + t(990, 378, "C++ · pricing · RL", 22, 600, INK, "middle")
    )
    body = (
        f'<defs>{radial("hb")}{radial("hc", WARM_CORE)}'
        '<linearGradient id="name" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0" stop-color="{HOT}"/><stop offset="0.55" stop-color="{ORANGE}"/><stop offset="1" stop-color="{MAGENTA}"/></linearGradient>'
        '<pattern id="scan" width="4" height="4" patternUnits="userSpaceOnUse"><rect width="4" height="1" fill="#000" opacity="0.18"/></pattern>'
        "</defs>"
        f'<rect width="{W}" height="{H}" fill="{COLD}"/>'
        f'<g opacity="0.95">{field}</g>'
        f'<rect width="{W}" height="{H}" fill="url(#scan)"/>'
        + corners(24, 24, W - 48, H - 48, HOT, 34, 2, 0.55)
        + t(48, 58, "cam_01 / thermal / iit bombay", 16, 500, MUTED)
        + f'<circle cx="{W - 170}" cy="52" r="6" fill="{ORANGE}"/>'
        + t(W - 48, 58, "mumbai, india", 16, 500, MUTED, "end")
        + t(80, 268, "Parakh Sharma", 104, 700, "url(#name)")
        + t(82, 304, "AI/ML engineer and full-stack developer", 26, 600, INK)
        + dets
        + tags
        + ramp
        + t(80, H - 60, "cold", 13, 500, MUTED)
        + t(161, H - 60, "hot", 13, 500, MUTED, "end")
        + f'<circle cx="89" cy="345" r="7" fill="{HOT}"/>'
        + t(106, 352, "open to freelance and contract work", 20, 600, HOT)
    )
    css = (
        ".box{stroke-dasharray:1;stroke-dashoffset:0;animation:draw .7s cubic-bezier(.2,.7,.2,1) var(--d) both}"
        ".tab{animation:pop .3s ease-out calc(var(--d) + .55s) both}"
        "@keyframes draw{from{stroke-dashoffset:1}to{stroke-dashoffset:0}}"
        "@keyframes pop{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:none}}"
        "@media (prefers-reduced-motion:reduce){.box,.tab{animation:none}}"
    )
    return svg(W, H, body, css, "Parakh Sharma, AI/ML engineer and full-stack developer, open to freelance work")


CATS = {
    "ai": ("llm agents", HOT),
    "cv": ("computer vision", ORANGE),
    "web": ("full-stack", MAGENTA),
    "quant": ("quant / systems", "#E05A9B"),
}


def wrap(text, limit):
    lines, cur = [], ""
    for word in text.split():
        if len(cur) + len(word) + 1 > limit:
            lines.append(cur)
            cur = word
        else:
            cur = f"{cur} {word}".strip()
    return lines + [cur]


def card(title, desc, stack, cat) -> str:
    W, H = 600, 270
    label, color = CATS[cat]
    lines = wrap(desc, 46)[:3]
    desc_svg = "".join(t(36, 132 + i * 28, ln, 20, 500, MUTED) for i, ln in enumerate(lines))
    chips, x = "", 36
    for s in stack:
        w = 22 + len(s) * 9.2
        chips += (
            f'<rect x="{x}" y="{H - 62}" width="{w}" height="30" rx="4" fill="none" stroke="{color}" stroke-opacity="0.6"/>'
            + t(x + w / 2, H - 41, s, 15, 600, INK, "middle")
        )
        x += w + 10
    body = (
        f'<defs>{radial("g", HEAT_CORE[HEAT_CORE.index(color):] if color in HEAT_CORE else WARM_CORE)}'
        f'<clipPath id="c"><rect width="{W}" height="{H}" rx="12"/></clipPath></defs>'
        f'<rect width="{W}" height="{H}" rx="12" fill="{PANEL}"/>'
        f'<ellipse cx="{W - 40}" cy="30" rx="210" ry="150" fill="url(#g)" opacity="0.5" clip-path="url(#c)"/>'
        + corners(14, 14, W - 28, H - 28, color, 20, 2, 0.85)
        + f'<rect x="36" y="38" width="10" height="10" fill="{color}"/>'
        + t(54, 48, label, 15, 600, color)
        + t(36, 94, title, 32, 700, INK)
        + desc_svg
        + chips
    )
    return svg(W, H, body, "", f"{title}: {desc}")


def tools() -> str:
    W, H = 1280, 250
    groups = [
        ("ml / ai", HOT, ["Python", "PyTorch", "scikit-learn", "YOLOv8", "ONNX", "Whisper", "RAG", "LLM agents"]),
        ("web", ORANGE, ["TypeScript", "React", "Next.js", "Node.js", "Express", "FastAPI", "Django", "Tailwind"]),
        ("data / infra", MAGENTA, ["PostgreSQL", "Supabase", "SQLite", "Redis", "Docker", "GitHub Actions", "Vercel"]),
        ("also", "#E05A9B", ["C++", "MATLAB", "Simulink"]),
    ]
    body = f'<rect width="{W}" height="{H}" rx="12" fill="{PANEL}"/>'
    col_x = [36, 356, 676, 996]
    for (name, color, items), cx in zip(groups, col_x):
        body += f'<rect x="{cx}" y="34" width="10" height="10" fill="{color}"/>' + t(cx + 18, 44, name, 16, 600, color)
        for i, item in enumerate(items):
            row, col = divmod(i, 2)
            x, y = cx + col * 140, 76 + row * 40
            body += t(x, y + 20, item, 19, 500, INK)
    return svg(W, H, body, "", "Tools: " + ", ".join(i for g in groups for i in g[2]))


CARDS = [
    ("autonomous-web-agent", "Browser agent that plans and acts in a real browser through a ReAct loop.", ["Python", "Playwright", "Gemini"], "ai"),
    ("rag-technical-doc-assistant", "Q&A over technical PDFs with reranked retrieval and cited answers.", ["Python", "Cross-encoder", "Gemini"], "ai"),
    ("AxalonSystems", "Thermal-drone solar inspection: anomaly detection, backend and dashboard.", ["YOLOv8", "FastAPI", "Next.js"], "cv"),
    ("realtime-browser-object-detection", "Real-time object detection running fully in the browser, no server.", ["YOLOv8n", "ONNX Web", "React"], "cv"),
    ("darexsaas", "Multi-tenant SaaS CRM with pipeline, unified inbox and an AI agent.", ["Next.js", "TypeScript", "Gemini"], "web"),
    ("cpp-matching-engine", "Limit order book matching engine with a documented optimization journey.", ["C++17", "Low latency"], "quant"),
]

(OUT_DIR / "hero.svg").write_text(hero())
(OUT_DIR / "tools.svg").write_text(tools())
for name, desc, stack, cat in CARDS:
    title = name if len(name) <= 26 else name.replace("realtime-browser-", "browser-")
    (OUT_DIR / f"card-{name}.svg").write_text(card(title, desc, stack, cat))
print("ok", sorted(p.name for p in OUT_DIR.iterdir()))
