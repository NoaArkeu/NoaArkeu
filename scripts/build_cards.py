#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import datetime as dt
from pathlib import Path
import random
import requests

USERNAME = os.getenv("USERNAME", "NoaArkeu")
TOKEN = os.getenv("GITHUB_TOKEN", "")
API = "https://api.github.com"

HEADERS = {"Accept": "application/vnd.github+json"}
if TOKEN:
    HEADERS["Authorization"] = f"Bearer {TOKEN}"

ROOT = Path(__file__).resolve().parents[1]
CARDS_DIR = ROOT / "assets" / "cards"
CARDS_DIR.mkdir(parents=True, exist_ok=True)
README_PATH = ROOT / "README.md"


def esc(s: str) -> str:
    return (s.replace("&", "&amp;")
             .replace("<", "&lt;")
             .replace(">", "&gt;")
             .replace('"', "&quot;"))


def gh_repos(username: str, per_page=20):
    url = f"{API}/users/{username}/repos"
    params = {"sort": "pushed", "per_page": per_page, "type": "owner"}
    r = requests.get(url, headers=HEADERS, params=params, timeout=20)
    r.raise_for_status()
    return r.json()


def geocode_city(city: str):
    url = "https://geocoding-api.open-meteo.com/v1/search"
    r = requests.get(url, params={"name": city, "count": 1, "language": "en", "format": "json"}, timeout=20)
    r.raise_for_status()
    data = r.json()
    results = data.get("results") or []
    if not results:
        return None
    x = results[0]
    return x["latitude"], x["longitude"], x.get("name", city), x.get("country", "")


def weather_now(city: str, tz_name: str):
    g = geocode_city(city)
    if not g:
        return None
    lat, lon, cname, country = g
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,weather_code",
        "timezone": tz_name
    }
    r = requests.get(url, params=params, timeout=20)
    r.raise_for_status()
    d = r.json().get("current", {})
    return {
        "city": cname,
        "country": country,
        "temp": d.get("temperature_2m"),
        "code": d.get("weather_code")
    }


def code_to_emoji(code):
    if code in [0]:
        return "☀️", "Clear"
    if code in [1, 2]:
        return "🌤️", "Partly Cloudy"
    if code in [3]:
        return "☁️", "Cloudy"
    if code in [45, 48]:
        return "🌫️", "Fog"
    if code in [51, 53, 55, 56, 57]:
        return "🌦️", "Drizzle"
    if code in [61, 63, 65, 66, 67, 80, 81, 82]:
        return "🌧️", "Rain"
    if code in [71, 73, 75, 77, 85, 86]:
        return "❄️", "Snow"
    if code in [95, 96, 99]:
        return "⛈️", "Thunderstorm"
    return "🌈", "Weather"


def shell(title: str, body: str, w=760, h=250):
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">
  <defs>
    <linearGradient id="bg" x1="0" x2="1" y1="0" y2="1">
      <stop offset="0%" stop-color="#f7fbf9"/>
      <stop offset="100%" stop-color="#e8f5ef"/>
    </linearGradient>
    <linearGradient id="mint" x1="0" x2="1">
      <stop offset="0%" stop-color="#8adbc8"/>
      <stop offset="100%" stop-color="#6ec6b4"/>
    </linearGradient>
    <filter id="shadow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="6" stdDeviation="10" flood-color="#1f5a4e" flood-opacity="0.12"/>
    </filter>
  </defs>

  <rect x="10" y="10" rx="24" ry="24" width="{w-20}" height="{h-20}" fill="url(#bg)" stroke="#ffffff" filter="url(#shadow)"/>
  <rect x="28" y="28" rx="10" ry="10" width="10" height="28" fill="url(#mint)"/>
  <text x="48" y="49" font-size="24" font-family="Segoe UI, Arial, sans-serif" fill="#2f3b3a" font-weight="700">{esc(title)}</text>
  {body}
</svg>"""


def card_intro():
    body = f"""
  <text x="48" y="95" font-size="20" font-family="Segoe UI, Arial" fill="#334240">Hi, I'm {esc(USERNAME)} 👋</text>
  <text x="48" y="128" font-size="15" font-family="Segoe UI, Arial" fill="#6b807c">Python / Backend / Embedded Curiosity</text>
  <text x="48" y="156" font-size="15" font-family="Segoe UI, Arial" fill="#6b807c">Building cute + practical interactive pages ✨</text>

  <rect x="470" y="78" rx="14" ry="14" width="250" height="100" fill="#ffffff" stroke="#e0efe9"/>
  <text x="488" y="112" font-size="14" font-family="Segoe UI, Arial" fill="#7c908c">Current Focus</text>
  <text x="488" y="142" font-size="16" font-family="Segoe UI, Arial" fill="#2f3b3a" font-weight="700">IoT + UI + Python Automation</text>
"""
    return shell("🌱 About Me", body, h=230)


def card_projects(repos):
    repos = [r for r in repos if not r.get("fork")]
    repos = [r for r in repos if r.get("name", "").lower() != USERNAME.lower()]
    top = repos[:3]

    y = 94
    lines = []
    for r in top:
        name = r.get("name", "unknown")
        lang = r.get("language") or "Unknown"
        stars = r.get("stargazers_count", 0)
        updated = (r.get("pushed_at") or "")[:10]
        lines.append(
            f'<text x="48" y="{y}" font-size="15" font-family="Segoe UI, Arial" fill="#334240">• {esc(name)} · {esc(lang)} · ★{stars} · {updated}</text>'
        )
        y += 34

    if not lines:
        lines = ['<text x="48" y="95" font-size="15" font-family="Segoe UI, Arial" fill="#6b807c">No public projects yet</text>']

    body = "\n  ".join(lines) + """
  <rect x="540" y="78" rx="12" ry="12" width="180" height="42" fill="#ffffff" stroke="#dff0ea"/>
  <text x="556" y="105" font-size="14" font-family="Segoe UI, Arial" fill="#3b9c87">Data: GitHub API</text>
"""
    return shell("📦 Recent Projects", body, h=230)


def get_multi_city_weather():
    cities = [
        ("Shanghai", "Asia/Shanghai"),
        ("Tokyo", "Asia/Tokyo"),
        ("Paris", "Europe/Paris"),
        ("London", "Europe/London"),
        ("New York", "America/New_York"),
    ]
    result = []
    for city, tz in cities:
        w = weather_now(city, tz)
        if not w:
            result.append({"city": city, "country": "", "temp": None, "code": -1})
        else:
            result.append(w)
    return result


def card_weather():
    now = dt.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    data = get_multi_city_weather()
    focus = random.choice(data) if data else None

    if not focus:
        body = f"""
  <text x="48" y="100" font-size="17" font-family="Segoe UI, Arial" fill="#334240">Weather data unavailable</text>
  <text x="48" y="132" font-size="14" font-family="Segoe UI, Arial" fill="#6b807c">Check API/network</text>
  <text x="48" y="164" font-size="13" font-family="Segoe UI, Arial" fill="#8a9b98">Updated: {now}</text>
"""
        return shell("🍡 Weather Ring", body, h=250)

    others = [x for x in data if x["city"] != focus["city"]]
    while len(others) < 4:
        others.append({"city": "N/A", "temp": None, "code": -1})

    positions = [
        (85, 96),   # left-top
        (525, 96),  # right-top
        (65, 176),  # left-bottom
        (545, 176), # right-bottom
    ]

    small = []
    for i, c in enumerate(others[:4]):
        x, y = positions[i]
        emj, _ = code_to_emoji(c.get("code", -1))
        t = c.get("temp")
        ts = f"{t}°C" if t is not None else "--"
        small.append(f"""
  <g>
    <rect x="{x}" y="{y}" rx="15" ry="15" width="150" height="46" fill="#ffffff" stroke="#e2efe9"/>
    <text x="{x+12}" y="{y+29}" font-size="14" font-family="Segoe UI, Arial" fill="#334240">{emj} {esc(c.get('city','Unknown'))} {esc(ts)}</text>
  </g>""")

    f_emj, f_desc = code_to_emoji(focus.get("code", -1))
    f_temp = focus.get("temp")
    f_temp_s = f"{f_temp}°C" if f_temp is not None else "--"
    f_city = f"{focus.get('city','Unknown')}, {focus.get('country','')}".strip(", ")

    body = f"""
  <rect x="292" y="64" rx="15" ry="15" width="176" height="44" fill="#ffffff" stroke="#e2efe9"/>
  <text x="305" y="92" font-size="14" font-family="Segoe UI, Arial" fill="#334240">🌍 5-City Live Weather</text>

  {''.join(small)}

  <path d="M230 140 C260 128, 290 152, 320 140 C350 128, 380 152, 410 140 C440 128, 470 152, 500 140" stroke="#76cbb7" stroke-width="3" fill="none" stroke-linecap="round"/>
  <path d="M230 163 C260 151, 290 175, 320 163 C350 151, 380 175, 410 163 C440 151, 470 175, 500 163" stroke="#8dd8c6" stroke-width="3" fill="none" stroke-linecap="round"/>
  <path d="M230 186 C260 174, 290 198, 320 186 C350 174, 380 198, 410 186 C440 174, 470 198, 500 186" stroke="#a4e4d5" stroke-width="3" fill="none" stroke-linecap="round"/>

  <text x="240" y="128" font-size="15" font-family="Segoe UI, Arial" fill="#2f3b3a" font-weight="700">Focus: {esc(f_city)}</text>
  <text x="240" y="154" font-size="24" font-family="Segoe UI, Arial" fill="#2f3b3a" font-weight="800">{f_emj} {esc(f_temp_s)} · {esc(f_desc)}</text>
  <text x="240" y="210" font-size="13" font-family="Segoe UI, Arial" fill="#8a9b98">Updated: {esc(now)} · Focus rotates each run</text>
"""
    return shell("🍡 Weather Ring", body, h=250)


def save(path: Path, text: str):
    path.write_text(text, encoding="utf-8")


def update_readme():
    block = """<!-- GENERATED_CARDS_START -->
<p align="center">
  <img src="./assets/cards/about.svg" width="92%" />
</p>
<p align="center">
  <img src="./assets/cards/projects.svg" width="92%" />
</p>
<p align="center">
  <img src="./assets/cards/weather.svg" width="92%" />
</p>
<!-- GENERATED_CARDS_END -->"""

    if not README_PATH.exists():
        README_PATH.write_text("# Hi, I'm NoaArkeu 👋\n\n" + block + "\n", encoding="utf-8")
        return

    content = README_PATH.read_text(encoding="utf-8")
    s, e = "<!-- GENERATED_CARDS_START -->", "<!-- GENERATED_CARDS_END -->"
    if s in content and e in content:
        pre = content.split(s)[0]
        post = content.split(e)[1]
        content = pre + block + post
    else:
        content = content.rstrip() + "\n\n" + block + "\n"
    README_PATH.write_text(content, encoding="utf-8")


def main():
    repos = gh_repos(USERNAME, per_page=20)
    save(CARDS_DIR / "about.svg", card_intro())
    save(CARDS_DIR / "projects.svg", card_projects(repos))
    save(CARDS_DIR / "weather.svg", card_weather())
    update_readme()
    print("Generated cards and updated README successfully.")


if __name__ == "__main__":
    main()