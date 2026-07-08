import argparse
from score_engine import recommend


def split_input(value):
    if not value:
        return []

    return [
        x.strip()
        for x in value.split(",")
        if x.strip()
    ]


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("--units", required=True)
    parser.add_argument("--items", default="")
    parser.add_argument("--traits", default="")
    parser.add_argument("--hp", type=int, default=50)
    parser.add_argument("--gold", type=int, default=30)
    parser.add_argument("--level", type=int, default=7)

    args = parser.parse_args()

    current_units = split_input(args.units)
    current_items = split_input(args.items)
    current_traits = split_input(args.traits)

    results = recommend(
        current_units=current_units,
        current_items=current_items,
        current_traits=current_traits,
        hp=args.hp,
        gold=args.gold,
        level=args.level,
        top_n=5
    )

    print("\n==============================")
    print("추천 덱 TOP 5")
    print("==============================")

    for i, r in enumerate(results, 1):
        print(f"\n{i}위")
        print(f"점수: {r['score']}")
        print(f"메인 캐리: {r['main_carry']}")
        print(f"메인 탱커: {r['main_tank']}")
        print(f"평균 등수: {r['avg_place']}")
        print(f"TOP4률: {r['top4_rate']}%")
        print(f"1등률: {r['win_rate']}%")
        print(f"표본 수: {r['games']}")

        print("\n완성 덱:")
        print(r["units"])

        print("\n부족한 기물:")
        print(", ".join(r["missing_units"]))

        print("\n추천 이유:")
        for reason in r["reasons"]:
            print("-", reason)

        print("------------------------------")


if __name__ == "__main__":
    main()