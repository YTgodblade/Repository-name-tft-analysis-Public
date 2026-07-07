import pandas as pd

FILES = [
    ("unit_tier.csv", "unit"),
    ("item_tier.csv", "item"),
    ("trait_tier.csv", "trait"),
]

for file, name_col in FILES:
    df = pd.read_csv(file)

    print("\n==============================")
    print(file)
    print("==============================")

    for tier in ["S", "A", "B", "C", "D"]:
        tier_df = df[df["tier"] == tier]

        print(f"\n[{tier} Tier]")
        print(tier_df[[name_col, "games", "avg_place", "top4_rate", "win_rate", "pick_rate", "score"]].head(10))