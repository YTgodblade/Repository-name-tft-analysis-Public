import pandas as pd

TOTAL_PLAYERS = len(pd.read_csv("player_dataset.csv"))

FILES = [
    ("unit_stats.csv", "unit", "unit_tier.csv", 100),
    ("item_stats.csv", "item", "item_tier.csv", 100),
    ("trait_stats.csv", "trait", "trait_tier.csv", 50),
]

BAD_UNITS = {
    "bardfollower",
    "ElderDragon",
    "IvernMinion",
    "Summon",
}

BAD_TRAITS = {
    "JhinUniqueTrait:1",
    "ShenUniqueTrait:1",
    "RhaastUniqueTrait:1",
    "TahmKenchUniqueTrait:2",
    "SummonTrait:7",
    "YordleLord:1",
}

BAD_ITEMS = {
    "AS",
    "UwuBlaster",
    "BattleBunnyCrossbow",
    "TacticiansScepter",
}

def calc_score(row):
    score = (
        (8 - row["avg_place"]) * 50
        + row["top4_rate"] * 0.3
        + row["win_rate"] * 0.2
        + row["pick_rate"] * 0.4
    )

    if row["games"] < 100:
        score -= 40
    elif row["games"] < 300:
        score -= 20
    elif row["games"] < 500:
        score -= 10

    return round(score, 2)

def assign_tiers(df):
    df = df.sort_values("score", ascending=False).reset_index(drop=True)
    n = len(df)

    tiers = []

    for i in range(n):
        ratio = i / n

        if ratio < 0.05:
            tiers.append("S")
        elif ratio < 0.20:
            tiers.append("A")
        elif ratio < 0.50:
            tiers.append("B")
        elif ratio < 0.80:
            tiers.append("C")
        else:
            tiers.append("D")

    df["tier"] = tiers
    return df

for input_file, name_col, output_file, min_games in FILES:
    df = pd.read_csv(input_file)

    df = df[df["games"] >= min_games]

    if name_col == "unit":
        df = df[~df["unit"].isin(BAD_UNITS)]

    if name_col == "trait":
        df = df[~df["trait"].isin(BAD_TRAITS)]

    if name_col == "item":
        df = df[~df["item"].isin(BAD_ITEMS)]

    df["pick_rate"] = round(df["games"] / TOTAL_PLAYERS * 100, 2)

    df["score"] = df.apply(calc_score, axis=1)

    df = assign_tiers(df)

    df.to_csv(output_file, index=False, encoding="utf-8-sig")

    print(f"{output_file} 생성 완료")
    print(df.head(20))