"""Genera los banners del perfil (variantes oscura y clara).

Uso: python scripts/make_banner.py
Salida: assets/banner-dark.svg, assets/banner-light.svg
"""
from pathlib import Path

W, H = 1200, 340
OUT = Path(__file__).resolve().parent.parent / "assets"

THEMES = {
    "dark": dict(bg="#0B0D10", ink="#E8ECF2", muted="#8A93A3", line="#222831",
                 dot="#2A313C", accent="#5EEAD4"),
    "light": dict(bg="#FAFAF8", ink="#0E141B", muted="#5B6676", line="#DDE1E7",
                  dot="#C9CFD8", accent="#0F766E"),
}

SANS = "Inter, -apple-system, 'Segoe UI', Helvetica, Arial, sans-serif"
MONO = "'JetBrains Mono', ui-monospace, SFMono-Regular, Consolas, Menlo, monospace"


def dot_grid(t):
    """Rejilla de puntos que se desvanece hacia la izquierda; unos pocos puntos
    resaltados dibujan una 'A' discreta (inicial del nombre)."""
    step, x0, y0 = 28, 700, 56
    cols, rows = 18, 9
    # Patron de una 'A' en una rejilla 7x9, posicionada a la derecha.
    letter = {
        (3, 0),
        (2, 1), (4, 1),
        (2, 2), (4, 2),
        (1, 3), (5, 3),
        (1, 4), (2, 4), (3, 4), (4, 4), (5, 4),
        (1, 5), (5, 5),
        (0, 6), (6, 6),
        (0, 7), (6, 7),
    }
    ox, oy = 9, 0  # desplazamiento de la letra dentro de la rejilla
    hi = {(c + ox, r + oy) for c, r in letter}
    out = []
    for r in range(rows):
        for c in range(cols):
            x, y = x0 + c * step, y0 + r * step
            fade = min(1.0, 0.12 + c / 9)  # mas tenue a la izquierda
            if (c, r) in hi:
                out.append(f'<circle cx="{x}" cy="{y}" r="4" fill="{t["accent"]}"/>')
            else:
                out.append(f'<circle cx="{x}" cy="{y}" r="2" fill="{t["dot"]}" '
                           f'opacity="{fade:.2f}"/>')
    return "\n    ".join(out)


def banner(name):
    t = THEMES[name]
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-labelledby="t d">
  <title id="t">Alejandro Suárez Durán</title>
  <desc id="d">Estudiante de DAW. Desarrollo web con Vue y FastAPI. Granada, España.</desc>
  <rect width="{W}" height="{H}" rx="16" fill="{t['bg']}"/>
  <rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="15.5" fill="none" stroke="{t['line']}"/>
  <g>
    {dot_grid(t)}
  </g>
  <!-- marcas de esquina -->
  <path d="M48 40h24M48 40v24" stroke="{t['accent']}" stroke-width="2" fill="none"/>
  <text x="48" y="104" font-family="{MONO}" font-size="22" fill="{t['muted']}" letter-spacing="1">~/alejandrosd2006</text>
  <text x="48" y="198" font-family="{SANS}" font-size="72" font-weight="650" fill="{t['ink']}" letter-spacing="-2">Alejandro</text>
  <text x="48" y="272" font-family="{SANS}" font-size="72" font-weight="650" fill="{t['ink']}" letter-spacing="-2">Suárez Durán<tspan fill="{t['accent']}">_</tspan></text>
  <line x1="48" y1="296" x2="{W-48}" y2="296" stroke="{t['line']}"/>
  <text x="48" y="322" font-family="{MONO}" font-size="18" fill="{t['muted']}" letter-spacing="1">GRANADA, ES  ·  37.1773° N  3.5986° O</text>
  <text x="{W-48}" y="322" font-family="{MONO}" font-size="18" fill="{t['muted']}" letter-spacing="1" text-anchor="end">DAW  ·  VUE  ·  FASTAPI</text>
</svg>
"""


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    for n in THEMES:
        (OUT / f"banner-{n}.svg").write_text(banner(n), encoding="utf-8")
        print("escrito", OUT / f"banner-{n}.svg")
