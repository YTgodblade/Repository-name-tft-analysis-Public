import pandas as pd


COMP_FILE = "recommender/comp_dataset.csv"
OUTPUT_FILE = "recommender/comp_profile.csv"


def classify_play_style(avg_level, avg_gold, avg_place):
    if avg_level >= 8.7:
        return "Fast9"

    if avg_level >= 8.0:
        return "Fast8"

    if avg_level >= 7.0:
        return "Level7 Roll"

    return "Early Roll"


def classify_economy(avg_gold):
    if avg_gold >= 45:
        return "Greedy"

    if avg_gold >= 25:
        return "Standard"

    return "Aggressive"


def main():
    df = pd.read_csv(COMP_FILE)

    # 현재 comp_dataset에는 덱별 평균 레벨/골드가 없으므로
    # 우선 덱의 평균 등수와 표본 수를 기반으로 운영 프로필을 임시 추정한다.
    profiles = []

    for _, row in df.iterrows():
        avg_place = float(row["avg_place"])
        games = int(row["games"])

        if avg_place <= 2.2:
            estimated_level = 8.5
            estimated_gold = 45
        elif avg_place <= 3.5:
            estimated_level = 8.0
            estimated_gold = 35
        elif avg_place <= 4.5:
            estimated_level = 7.5
            estimated_gold = 25
        else:
            estimated_level = 7.0
            estimated_gold = 15

        play_style = classify_play_style(
            estimated_level,
            estimated_gold,
            avg_place
        )

        economy_type = classify_economy(estimated_gold)

        profiles.append({
            "comp": row["comp"],
            "units": row["units"],
            "games": games,
            "avg_place": row["avg_place"],
            "top4_rate": row["top4_rate"],
            "win_rate": row["win_rate"],
            "stability_score": row["stability_score"],
            "estimated_level": estimated_level,
            "estimated_gold": estimated_gold,
            "play_style": play_style,
            "economy_type": economy_type,
        })

    out = pd.DataFrame(profiles)

    out.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")

    print("덱 운영 프로필 생성 완료!")
    print(f"저장 위치: {OUTPUT_FILE}")
    print(out.head(10))


if __name__ == "__main__":
    main()