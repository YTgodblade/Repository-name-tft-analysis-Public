import pandas as pd
import json
from collections import defaultdict

df = pd.read_csv("player_dataset.csv")

stats = defaultdict(lambda: {
    "games": 0,
    "place_sum": 0,
    "top4": 0,
    "win": 0
})

for _, row in df.iterrows():

    placement = row["placement"]

    units = json.loads(row["units"])

    for unit in units:

        name = unit["name"]

        stats[name]["games"] += 1
        stats[name]["place_sum"] += placement

        if placement <= 4:
            stats[name]["top4"] += 1

        if placement == 1:
            stats[name]["win"] += 1

rows = []

for name, s in stats.items():

    games = s["games"]

    if games < 20:
        continue

    rows.append({
        "unit": name,
        "games": games,
        "avg_place": round(s["place_sum"] / games, 2),
        "top4_rate": round(s["top4"] / games * 100, 2),
        "win_rate": round(s["win"] / games * 100, 2)
    })

result = pd.DataFrame(rows)

result = result.sort_values(
    by="avg_place"
)

result.to_csv(
    "unit_stats.csv",
    index=False,
    encoding="utf-8-sig"
)

print(result.head(30))