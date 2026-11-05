# LPP Lineup Lab

A web app for [IS Liigapörssi](https://liigaporssi.fi), the Liiga fantasy hockey game. It shows every Liiga player's current price and season stats, and finds the team with the most Liigapörssi points (LPP) that fits your budget.

This is an unofficial fan tool. It isn't affiliated with Liigapörssi, Ilta-Sanomat or Liiga.

## Features

- **Player table.** All Liiga players with price, LPP, LPP per game and position stats: goals, assists, +/−, PIM, shots and blocks for skaters, and wins, saves, save % and shutouts for goalies. You can search, filter by position, team and max price, and click any column header to sort.
- **Value column.** `LPP/100k` shows how many points a player has scored for every 100 000 € of their price.
- **Team optimizer.** Enter a budget and the app builds the best legal Liigapörssi team: 1 goalie (MV), 2 defencemen (P) and 3 forwards (H). The result is exact, not a guess: the app finds the highest possible total within the budget.
- **Captain bonus.** The optimizer can include the captain's ×1.3 multiplier. It makes your highest-scoring player the captain, so it's sometimes worth paying more for one star player.
- **Lock and exclude.** Lock a player to force them into the team, or exclude one (for example an injured player) to see the next best option.

## How to use

Open `index.html` in a browser. It's a single file with no server or install needed.

1. **Budget.** Type your budget, or pick a preset. Liigapörssi's starting budget is 2 000 000 €. If you already own players, enter your total team value plus your cash.
2. **Optimize for.**
   - *Season LPP* ranks players by total points so far this season.
   - *LPP per game* ranks players by average points per game. This works better for players who have missed games. When you choose it, the minimum games filter is set to 5.
3. **Min. games played.** Leaves out players with too few games for their stats to be reliable.
4. **Captain bonus.** Turn this off to rank teams without the ×1.3 multiplier.
5. **Lock and exclude buttons.** Each player card and table row has a lock button and an exclude (✕) button. The team updates right away. Your locked and excluded players appear in the left panel, and **Clear all** removes them.

Players in the optimized team are highlighted in the table, and the captain is marked with **C**. Your settings are saved in your browser.

## Updating the data

Prices change every day and stats change after every game, so update the data before you make trades.

You need [Python 3.9 or newer](https://www.python.org/). No extra packages are required.

```sh
python build.py
```

The script:

1. downloads all players from the feed behind the [Liigapörssi player search](https://liigaporssi.fi/liigaporssi/pelaajahaku), using season totals
2. reads names, teams, positions, prices and stats from it
3. adds that data to `template.html` and writes `index.html`, stamped with today's date

If Liigapörssi changes its page format, the script stops with an error instead of writing a broken page.

To publish an update, commit the new `index.html`:

```sh
python build.py
git add index.html
git commit -m "Update player data"
git push
```

## Files

| File | Purpose |
| --- | --- |
| `template.html` | The app: layout, styles and JavaScript. Edit this file, not `index.html`. |
| `build.py` | Downloads fresh data and builds `index.html` from the template. |
| `index.html` | The generated app with the data included. |

## How the optimizer works

Picking 6 players from about 500 gives too many combinations to check one by one. Instead the optimizer uses a 0/1 knapsack (dynamic programming) over:

- the number of goalies, defencemen and forwards picked so far
- the money spent, in 1 000 € steps (Liigapörssi prices move in 1 000 € steps)

To include the captain bonus, players are added in order from lowest to highest score. That way the last player added is always the team's top scorer and gets the ×1.3 multiplier. Before the search, the app drops players who can never be part of the best team. A forward is dropped, for example, if three other forwards are both cheaper and better. One search takes about 25 ms.

The results have been checked against an exhaustive search over every possible team.

## Limitations

- Only season totals are used, not stats for the current period (jakso).
- The data feed doesn't include injuries, so exclude injured players yourself.
- Past points don't guarantee future points. Treat the result as a starting point and check the schedule: a team with more games in the period gives its players more chances to score.
