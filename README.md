# LPP Lineup Lab

A web app for [IS Liigapörssi](https://liigaporssi.fi), the Liiga fantasy hockey game. It shows every Liiga player's current price, season stats and games left. It finds the team with the most Liigapörssi points (LPP) that fits your budget, and it plans when to trade players to teams that play more.

This is an unofficial fan tool. It isn't affiliated with Liigapörssi, Ilta-Sanomat or Liiga.

## Features

- **Player table.** All Liiga players with price, LPP, LPP per game, games left and projected LPP, plus position stats: goals, assists, +/−, PIM, shots and blocks for skaters, and wins, saves, save % and shutouts for goalies. You can search, filter by position, team and max price, and click any column header to sort.
- **Games left and projection.** For each Liigapörssi period (jakso), the app counts how many games each team plays. *Projected LPP* is a player's LPP per team game multiplied by their team's games in the selected window.
- **Team optimizer.** Enter a budget and the app builds the best legal Liigapörssi team: 1 goalie (MV), 2 defencemen (P) and 3 forwards (H). The result is exact, not a guess: the app finds the highest possible total within the budget.
- **Trade planner.** Players only score on days their team plays. The planner suggests trades that swap a player whose team is about to rest for one whose team plays more. It tells you which day to make each trade, how many games it gains and the expected LPP gain.
- **Player cards.** Click any player's name to open their card. It has a bar chart of their LPP in every game this season with a 5-game average line, their stats by period, their last-5-games form, their upcoming games, and a list of all their games with the opponent and the points.
- **Played periods.** Pick a finished period (jakso) to see every player's games, LPP, LPP per game and best game in that period. It also shows the best team you could have picked with your budget in hindsight.
- **Schedule grid.** Every team's games day by day for the selected window, with home and away games, total games, games in the next 7 days and the longest break.
- **Captain bonus.** The optimizer can include the captain's ×1.3 multiplier.
- **Lock and exclude.** Lock a player to force them into the team, or exclude one (for example an injured player) to see the next best option.

## How to use

Open `index.html` in a browser. It's a single file with no server or install needed.

### Build a team

1. **Budget.** Type your budget, or pick a preset. Liigapörssi's starting budget is 2 000 000 €. If you already own players, enter your total team value plus your cash.
2. **Optimize for.**
   - *Projected* (recommended) uses LPP per team game × games in the window, so players on teams with more games rank higher.
   - *Season LPP* ranks players by total points so far this season.
   - *LPP/game* ranks players by average points per game played.
3. **Period and window.** Pick the period (the current or next one is selected automatically) and how far ahead to look: the whole period, or the next 14 or 7 days. The window starts today, or on the first day of the period if it hasn't started yet.
4. **Min. games played.** Leaves out players with too few games for their stats to be reliable. The default is 5.
5. **Captain bonus.** Turn this off to rank teams without the ×1.3 multiplier.
6. **Lock and exclude buttons.** Each player card and table row has a lock button and an exclude (✕) button. The team updates right away. Your locked and excluded players appear in the left panel, and **Clear all** removes them.

Players in the optimized team are highlighted in the table, and the captain is marked with **C**. Your settings are saved in your browser.

### Plan trades

The trade planner always looks at the rest of the selected period and starts from the team on the rink.

- **To plan for your real team,** lock your six players and set the budget to your team value plus your cash.
- **Trades to use** limits the number of trades. A period includes 11 trades, and you can buy up to 20.
- **Min. gain per trade** hides trades that gain less than that many projected LPP, so trades aren't spent on tiny gains.

Each suggestion shows when to make the trade. For example, "before **ti 15.12.**, after su 13.12." means: make the trade after the points from 13.12 are updated and before the first game on 15.12. Trades lock when the first game of a game day starts. The timeline under the list shows each lineup slot day by day, and a red line marks the day a new player takes over.

**Trade on a chosen day.** Below the timeline, use the **Trade before** slider to pick the day you want to make a trade (for example ti 1.12.). Use **Keep until** to pick how long you'd keep the new player; the default is the end of the period. For each player in your lineup, the cards show how many games their team plays in that stretch, and the 3 best affordable replacements with their games and LPP gain. The player with the biggest possible gain is listed first. If no one gains points, the card says **Keep**. A replacement is affordable if it costs no more than the player's price plus your money left.

The schedule grid shows which teams have the most games and the longest breaks. Click a team name to see that team's players in the table.

### Player cards and past periods

Click a player's name anywhere in the app (the rink, the trade list, the period results or the player table) to open their card. Hover over or tap a bar in the chart to see the date, the opponent, the points and the 5-game average. Shaded bands show the periods. You can lock or exclude the player from the card. Press Esc or **Close** to close it.

In **Period results**, choose a period and a position. The best hindsight team uses today's prices, because the prices at the start of that period aren't available.

## Updating the data

Prices change every day and stats change after every game, so update the data before you make trades.

You need [Python 3.9 or newer](https://www.python.org/). No extra packages are required.

```sh
python build.py
```

The script:

1. downloads all players from the feed behind the [Liigapörssi player search](https://liigaporssi.fi/liigaporssi/pelaajahaku), using season totals
2. downloads the regular-season schedule and results from the official Liiga API (`liiga.fi/api/v2/games`)
3. reads the period dates from the [Liigapörssi rules page](https://liigaporssi.fi/ohjeet)
4. downloads every player's LPP game by game for each period that has started (the data behind the charts on Liigapörssi's player cards). Finished periods are saved in `cache/history.json`, so later builds only download the current period. This takes about 10 seconds per period.
5. adds all of this to `template.html` and writes `index.html`, stamped with today's date

If Liigapörssi changes its page format, the script stops with an error instead of writing a broken page.

The page uses your computer's date, so games already played drop out of the window. Prices and stats stay as they were on the last build, so rebuild regularly.

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
| `cache/history.json` | Saved game-by-game points for finished periods. Delete it to download everything again. |

## How it works

### Projection

A player's **LPP per team game** is their season LPP divided by the number of games their team has played. Using team games, not the player's own games, matters for backup goalies and for players who sit out games. A backup goalie with great stats in a few games doesn't get counted for every team game. Projected LPP = LPP per team game × the team's games in the window.

### Optimizer

Picking 6 players from about 500 gives too many combinations to check one by one. Instead the optimizer uses a 0/1 knapsack (dynamic programming) over:

- the number of goalies, defencemen and forwards picked so far
- the money spent, in 1 000 € steps (Liigapörssi prices move in 1 000 € steps)

To include the captain bonus, players are added in order from lowest to highest score. That way the last player added is always the team's top scorer and gets the ×1.3 multiplier. Before the search, the app drops players who can never be part of the best team. A forward is dropped, for example, if three other forwards are both cheaper and better. One search takes about 25–50 ms. The results have been checked against an exhaustive search over every possible team.

### Trade planner

The planner works step by step. It tries every possible trade (which player out, which player in, which day) and makes the one with the biggest projected gain. It repeats until it runs out of trades, or until no trade gains at least the minimum. A trade's gain is the new player's projected LPP minus the old player's, from the trade day until that slot's next trade or the end of the period. The planner checks that the team never costs more than your budget on any day, using today's prices. The captain bonus isn't included in the planner totals.

## Limitations

- Projections use season totals, not form or the strength of the opponent.
- Prices change during the period (±1 000 € per point and with trading volume). The planner uses today's prices, so a planned trade might cost a little more or less when you make it.
- The data feed doesn't include injuries, so exclude injured players yourself.
- Only regular-season games are included.
- Past points don't guarantee future points. Treat the results as a starting point.
