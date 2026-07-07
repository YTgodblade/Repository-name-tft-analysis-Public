import pandas as pd
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

    if pd.isna(row["traits"]):
        continue

    traits = str(row["traits"]).split(";")

    for trait in traits:

        if trait == "":
            continue

        stats[trait]["games"] += 1
        stats[trait]["place_sum"] += placement

        if placement <= 4:
            stats[trait]["top4"] += 1

        if placement == 1:
            stats[trait]["win"] += 1

rows = []

for trait, s in stats.items():

    games = s["games"]

    if games < 20:
        continue

    rows.append({
        "trait": trait,
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
    "trait_stats.csv",
    index=False,
    encoding="utf-8-sig"
)

print(result.head(30))