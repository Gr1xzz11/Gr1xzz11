import json
import os
import urllib.request
from collections import Counter
from pathlib import Path

USER = os.environ.get("GITHUB_USERNAME", "Gr1xzz11")
TOKEN = os.environ.get("GITHUB_TOKEN", "")
OUT = Path("assets")
OUT.mkdir(exist_ok=True)

HEADERS = {
    "Accept": "application/vnd.github+json",
    "User-Agent": "grxt-profile-stats",
}
if TOKEN:
    HEADERS["Authorization"] = f"Bearer {TOKEN}"


def get_json(url: str):
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))


def esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def card(title, lines, width=520, height=220):
    y = 72
    body = []
    for label, value in lines:
        body.append(
            f'<text x="28" y="{y}" fill="#8B949E" font-size="15">{esc(label)}</text>'
            f'<text x="{width-28}" y="{y}" fill="#F0F6FC" font-size="16" text-anchor="end" font-weight="600">{esc(value)}</text>'
        )
        y += 34
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
<rect width="100%" height="100%" rx="18" fill="#0D1117" stroke="#30363D"/>
<text x="28" y="40" fill="#58A6FF" font-size="21" font-weight="700" font-family="Segoe UI,Arial,sans-serif">{esc(title)}</text>
<g font-family="Segoe UI,Arial,sans-serif">{''.join(body)}</g>
</svg>'''


repos = []
page = 1
while True:
    batch = get_json(f"https://api.github.com/users/{USER}/repos?per_page=100&page={page}&sort=updated")
    if not batch:
        break
    repos.extend(batch)
    if len(batch) < 100:
        break
    page += 1

public_repos = len(repos)
stars = sum(r.get("stargazers_count", 0) for r in repos)
forks = sum(r.get("forks_count", 0) for r in repos)
watchers = sum(r.get("watchers_count", 0) for r in repos)

langs = Counter()
for repo in repos:
    if repo.get("fork"):
        continue
    lang = repo.get("language")
    if lang:
        langs[lang] += 1

stats_svg = card(
    "GitHub Stats",
    [
        ("Публичные репозитории", public_repos),
        ("Всего звёзд", stars),
        ("Всего форков", forks),
        ("Watchers", watchers),
    ],
)
(OUT / "github-stats.svg").write_text(stats_svg, encoding="utf-8")

max_count = max(langs.values()) if langs else 1
rows = []
y = 78
for lang, count in langs.most_common(6):
    bar_w = int(300 * count / max_count)
    rows.append(f'<text x="28" y="{y}" fill="#F0F6FC" font-size="15" font-family="Segoe UI,Arial,sans-serif">{esc(lang)}</text>')
    rows.append(f'<rect x="150" y="{y-13}" width="{bar_w}" height="12" rx="6" fill="#58A6FF"/>')
    rows.append(f'<text x="472" y="{y}" fill="#8B949E" font-size="14" text-anchor="end" font-family="Segoe UI,Arial,sans-serif">{count} repo</text>')
    y += 30

langs_svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="520" height="260" viewBox="0 0 520 260">
<rect width="100%" height="100%" rx="18" fill="#0D1117" stroke="#30363D"/>
<text x="28" y="40" fill="#58A6FF" font-size="21" font-weight="700" font-family="Segoe UI,Arial,sans-serif">Top Languages</text>
{''.join(rows) if rows else '<text x="28" y="90" fill="#8B949E" font-family="Segoe UI,Arial,sans-serif">Нет данных</text>'}
</svg>'''
(OUT / "top-langs.svg").write_text(langs_svg, encoding="utf-8")
