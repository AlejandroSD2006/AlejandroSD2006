"""Genera la barra de lenguajes del perfil a partir de datos reales.

Solo cuenta repositorios PUBLICOS propios (no forks). No usa servicios de
terceros: consulta la API GraphQL de GitHub y escribe SVG estaticos.

Uso:  GITHUB_TOKEN=... python scripts/make_languages.py [usuario]
      (sin GITHUB_TOKEN usa `gh auth token` si esta disponible)
Salida: assets/languages-dark.svg, assets/languages-light.svg
"""
import json
import os
import subprocess
import sys
import urllib.request
from pathlib import Path

USER = sys.argv[1] if len(sys.argv) > 1 else "AlejandroSD2006"
OUT = Path(__file__).resolve().parent.parent / "assets"
TOP = 6  # lenguajes mostrados; el resto se agrupa en "Otros"

QUERY = """
query($login:String!){ user(login:$login){
  repositories(privacy:PUBLIC, isFork:false, first:100){
    totalCount
    nodes{ name languages(first:12, orderBy:{field:SIZE, direction:DESC}){ edges{ size node{ name } } } }
  } } }
"""

# Rampa de un solo tono para mantener la identidad visual (no colores oficiales).
RAMP = {
    "dark": ["#5EEAD4", "#3FBFAE", "#2E9486", "#246F66", "#1B4F49", "#163A37", "#2A313C"],
    "light": ["#0F766E", "#2A9087", "#55AAA2", "#86C3BD", "#B3DAD6", "#D5EBE8", "#C9CFD8"],
}
THEMES = {
    "dark": dict(bg="#0B0D10", ink="#E8ECF2", muted="#8A93A3", line="#222831"),
    "light": dict(bg="#FAFAF8", ink="#0E141B", muted="#5B6676", line="#DDE1E7"),
}
SANS = "Inter, -apple-system, 'Segoe UI', Helvetica, Arial, sans-serif"
MONO = "'JetBrains Mono', ui-monospace, SFMono-Regular, Consolas, Menlo, monospace"


def token():
    t = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if t:
        return t
    return subprocess.check_output(["gh", "auth", "token"], text=True).strip()


def fetch():
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": USER}}).encode(),
        headers={"Authorization": f"bearer {token()}", "User-Agent": "profile-readme"},
    )
    with urllib.request.urlopen(req) as r:
        data = json.load(r)
    if "errors" in data:
        raise SystemExit(data["errors"])
    repos = data["data"]["user"]["repositories"]
    totals = {}
    for repo in repos["nodes"]:
        for e in repo["languages"]["edges"]:
            totals[e["node"]["name"]] = totals.get(e["node"]["name"], 0) + e["size"]
    return repos["totalCount"], totals


def svg(name, count, totals):
    t, ramp = THEMES[name], RAMP[name]
    items = sorted(totals.items(), key=lambda kv: -kv[1])
    total = sum(v for _, v in items) or 1
    head, rest = items[:TOP], items[TOP:]
    if rest:
        head.append(("Otros", sum(v for _, v in rest)))
    W, PAD, BAR_W = 600, 28, 544
    rows = (len(head) + 1) // 2
    H = 120 + rows * 30
    # barra segmentada
    x, bar = PAD, []
    for i, (_, v) in enumerate(head):
        w = max(4, round(BAR_W * v / total))
        bar.append(f'<rect x="{x}" y="64" width="{w}" height="12" fill="{ramp[min(i, 6)]}"/>')
        x += w
    legend = []
    for i, (lang, v) in enumerate(head):
        col, row = i % 2, i // 2
        lx, ly = PAD + col * 280, 112 + row * 30
        legend.append(
            f'<rect x="{lx}" y="{ly-11}" width="10" height="10" rx="2" fill="{ramp[min(i, 6)]}"/>'
            f'<text x="{lx+18}" y="{ly}" font-family="{SANS}" font-size="16" fill="{t["ink"]}">{lang}</text>'
            f'<text x="{lx+236}" y="{ly}" font-family="{MONO}" font-size="15" fill="{t["muted"]}" text-anchor="end">{100*v/total:.1f}%</text>'
        )
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Lenguajes en repositorios públicos">
  <rect width="{W}" height="{H}" rx="12" fill="{t['bg']}"/>
  <rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="11.5" fill="none" stroke="{t['line']}"/>
  <text x="{PAD}" y="38" font-family="{MONO}" font-size="14" fill="{t['muted']}" letter-spacing="1.5">LENGUAJES · REPOSITORIOS PÚBLICOS</text>
  <clipPath id="c"><rect x="{PAD}" y="64" width="{BAR_W}" height="12" rx="6"/></clipPath>
  <g clip-path="url(#c)">{''.join(bar)}</g>
  {''.join(legend)}
</svg>
"""


if __name__ == "__main__":
    count, totals = fetch()
    OUT.mkdir(exist_ok=True)
    for n in THEMES:
        (OUT / f"languages-{n}.svg").write_text(svg(n, count, totals), encoding="utf-8")
    print(count, "repos;", json.dumps(totals))
