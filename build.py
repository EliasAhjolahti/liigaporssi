"""Fetch current Liigapörssi player data and build index.html from template.html.

Usage:  python build.py
Data source: the player-search feed behind https://liigaporssi.fi/liigaporssi/pelaajahaku
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


def main():
    players = parse(fetch())
    if len(players) < 100:
        raise SystemExit(f"Only {len(players)} players parsed; the source format may have changed.")
    meta = {"updated": datetime.date.today().isoformat(), "count": len(players)}
    data = json.dumps(players, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    page = (HERE / "template.html").read_text(encoding="utf-8")
    page = page.replace("/*__DATA__*/[]", data).replace("/*__META__*/{}", json.dumps(meta))
    (HERE / "index.html").write_text(page, encoding="utf-8")
    print(f"Built index.html with {len(players)} players ({meta['updated']}).")


if __name__ == "__main__":
    main()
