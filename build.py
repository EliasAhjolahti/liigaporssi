"""Fetch current Liigapörssi player data, the Liiga schedule and period dates, and build
index.html from template.html.

Usage:  python build.py
Data sources:
  players  - the player-search feed behind https://liigaporssi.fi/liigaporssi/pelaajahaku
  schedule - the official Liiga API, https://liiga.fi/api/v2/games
  periods  - the rules page, https://liigaporssi.fi/ohjeet
"""
import datetime
import html
import json
import pathlib
import re
import urllib.request

HERE = pathlib.Path(__file__).parent
URL = (
    "https://liigaporssi.fi/team/search-players?js=1&player_position=all&player_team=all"
    "&player_value=all&type=player_search&sort_by_m=&sort_by_p=&sort_by_h="
    "&order_m=DESC&order_p=DESC&order_h=DESC&phase=total"
)
POS = {"goalie": "G", "defenseman": "D", "forward": "F"}
# liigaporssi field -> short key used by the page
KEYS = {
    "rounds_played": "gp", "goals": "g", "passes": "a", "power": "pts",
    "plus": "pl", "minus": "mi", "penalty_minutes": "pim", "shots": "sh",
    "blocks": "bl", "win": "w", "defeat": "l", "draw": "d", "saves": "sv",
    "goal_against": "ga", "shutout": "so", "points": "lpp",
    "rewarded_one_star": "s1", "rewarded_two_star": "s2", "rewarded_three_star": "s3",
}


def fetch() -> str:
    req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0", "X-Requested-With": "XMLHttpRequest"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read().decode("utf-8")


def num(v: str):
    v = v.strip().replace(",", ".")
    if v in ("", "-"):
        return 0
    try:
        return float(v) if "." in v else int(v)
    except ValueError:
        return 0


def parse(src: str) -> list[dict]:
    players = []
    for t in re.split(r'<table class="player_result_table" data-player-type="', src)[1:]:
        ptype = t.split('"', 1)[0]
        head, body = t.split("<tbody>", 1)
        fields = re.findall(r'data-field="([^"]+)"', head)
        for row in re.split(r'<tr id="\d+_tr">', body)[1:]:
            m = re.search(r'title="([^"]+)\(([^)]+)\)"', row)
            pid = re.search(r'name="player_id"[^>]*value="(\d+)"', row).group(1)
            cells = re.findall(r'<td class="stat_data[^"]*"[^>]*>\s*([^<]*?)\s*</td>', row)
            p = {
                "id": pid,
                "n": html.unescape(m.group(1).strip()),
                "t": html.unescape(m.group(2).strip()),
                "p": POS[ptype],
                "v": int(re.search(r'data-sort="(\d+)"', row).group(1)),
            }
            for f, v in zip(fields, cells):
                if f in KEYS:
                    p[KEYS[f]] = num(v)
            players.append(p)
    return players


def get(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read().decode("utf-8")


def fetch_schedule(season: int) -> list[list]:
    """Regular-season games from the official Liiga API as [date, home, away, ended]."""
    games = json.loads(get(f"https://liiga.fi/api/v2/games?tournament=runkosarja&season={season}"))
    rows = []
    for g in games:
        start = datetime.datetime.fromisoformat(g["start"].replace("Z", "+00:00"))
        local = (start + datetime.timedelta(hours=3)).date().isoformat()  # Finnish game day
        rows.append([local, g["homeTeam"]["teamName"], g["awayTeam"]["teamName"], 1 if g.get("ended") else 0])
    rows.sort()
    return rows


def fetch_periods() -> list[dict]:
    """Liigapörssi periods (jaksot) from the rules page."""
    src = re.sub(r"<[^>]+>", " ", get("https://liigaporssi.fi/ohjeet"))
    periods = []
    for m in re.finditer(r"Jakso\s*-\s*(\d\d)\.(\d\d)\.(\d{4})\s*-\s*(\d\d)\.(\d\d)\.(\d{4})", src):
        d1, m1, y1, d2, m2, y2 = map(int, m.groups())
        end = datetime.date(y2, m2, d2)
        start = datetime.date(y1, m1, d1)
        if (end - start).days > 150:  # typo on the rules page (e.g. 2025 instead of 2026)
            start = start.replace(year=end.year if m1 <= m2 else end.year - 1)
        periods.append({"n": len(periods) + 1, "start": start.isoformat(), "end": end.isoformat()})
    return periods


def main():
    players = parse(fetch())
    if len(players) < 100:
        raise SystemExit(f"Only {len(players)} players parsed; the source format may have changed.")
    today = datetime.date.today()
    season = today.year + 1 if today.month >= 7 else today.year  # Liiga season is named by its end year
    schedule = fetch_schedule(season)
    periods = fetch_periods()
    if not periods:
        raise SystemExit("Could not read the period dates from liigaporssi.fi/ohjeet.")
    meta = {"updated": today.isoformat(), "count": len(players), "season": season}
    dump = lambda o: json.dumps(o, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    page = (HERE / "template.html").read_text(encoding="utf-8")
    page = (page.replace("/*__DATA__*/[]", dump(players))
                .replace("/*__SCHED__*/[]", dump(schedule))
                .replace("/*__PERIODS__*/[]", dump(periods))
                .replace("/*__META__*/{}", dump(meta)))
    (HERE / "index.html").write_text(page, encoding="utf-8")
    print(f"Built index.html: {len(players)} players, {len(schedule)} games, "
          f"{len(periods)} periods ({meta['updated']}).")


if __name__ == "__main__":
    main()
