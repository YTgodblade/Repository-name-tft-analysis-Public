import pandas as pd

FILES = [
    ("unit_tier.csv", "website_unit_table.csv"),
    ("item_tier.csv", "website_item_table.csv"),
    ("trait_tier.csv", "website_trait_table.csv"),
]

for input_file, output_file in FILES:

    df = pd.read_csv(input_file)

    cols = [
        "tier",
        df.columns[0],
        "pick_rate",
        "avg_place",
        "top4_rate",
        "win_rate",
        "games",
        "score"
    ]

    df = df[cols]

    df = df.sort_values(
        by=["tier", "score"],
        ascending=[True, False]
    )

    df.to_csv(
        output_file,
        index=False,
        encoding="utf-8-sig"
    )

    print(output_file, "생성 완료")