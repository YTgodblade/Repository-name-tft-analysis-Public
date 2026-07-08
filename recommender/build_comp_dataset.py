import json
import pandas as pd
from collections import defaultdict, Counter

INPUT_FILE = "matches.jsonl"
OUTPUT_FILE = "recommender/comp_dataset.csv"

MIN_GAMES = 20

BAD_UNITS = {
    "IvernMinion",
    "Summon",
    "bardfollower",
    "tft17_bardfollower",
    "TFT17_bardfollower",
    "ElderDragon",
}

BAD_TRAITS = {
    "SummonTrait",
}

def clean_name(name):
    if not name:
        return ""

    name = str(name)

    prefixes = [
        "TFT17_",
        "TFT16_",
        "TFT15_",
        "TFT14_",
        "TFT_",
    ]

    for prefix in prefixes:
        name = name.replace(prefix, "")

    return name


def is_bad_unit(name):
    if not name:
        return True

    clean = clean_name(name)

    if clean in BAD_UNITS:
        return True

    if "follower" in clean.lower():
        return True

    if "minion" in clean.lower():
        return True

    if "summon" in clean.lower():
        return True

    return False


def is_bad_trait(name):
    if not name:
        return True

    clean = clean_name(name)

    for bad in BAD_TRAITS:
        if bad.lower() in clean.lower():
            return True

    return False


def get_units(participant):
    units = []

    for unit in participant.get("units", []):
        name = clean_name(unit.get("character_id", ""))

        if not is_bad_unit(name):
            units.append(name)

    # 중복 제거
    units = sorted(set(units))

    return units


def get_unit_items(participant):
    result = []

    for unit in participant.get("units", []):
        unit_name = clean_name(unit.get("character_id", ""))

        if is_bad_unit(unit_name):
            continue

        item_names = unit.get("itemNames", [])

        for item in item_names:
            item_name = clean_name(item)

            if unit_name and item_name:
                result.append((unit_name, item_name))

    return result


def get_items(participant):
    items = []

    for unit in participant.get("units", []):
        unit_name = clean_name(unit.get("character_id", ""))

        if is_bad_unit(unit_name):
            continue

        for item in unit.get("itemNames", []):
            item_name = clean_name(item)

            if item_name:
                items.append(item_name)

    return sorted(items)


def get_traits(participant):
    traits = []

    for trait in participant.get("traits", []):
        name = clean_name(trait.get("name", ""))
        tier_current = trait.get("tier_current", 0)

        if name and tier_current > 0 and not is_bad_trait(name):
            traits.append(f"{name}:{tier_current}")

    return sorted(traits)


def make_comp_key(units):
    return "+".join(units)


def guess_main_carry(unit_item_pairs):
    counter = Counter()

    for unit_name, item_name in unit_item_pairs:
        counter[unit_name] += 1

    if not counter:
        return ""

    return counter.most_common(1)[0][0]


def guess_main_tank(unit_item_pairs):
    tank_keywords = [
        "Warmogs",
        "Gargoyle",
        "Bramble",
        "Dragon",
        "Redemption",
        "Protector",
        "Sunfire",
        "Ionic",
        "Steadfast",
        "Crownguard",
        "AdaptiveHelm",
        "Stoneplate",
        "Armor",
        "Claw",
    ]

    counter = Counter()

    for unit_name, item_name in unit_item_pairs:
        for keyword in tank_keywords:
            if keyword.lower() in item_name.lower():
                counter[unit_name] += 1

    if not counter:
        return ""

    return counter.most_common(1)[0][0]


def calc_stability_score(games, avg_place, top4_rate, win_rate):
    score = (
        (8 - avg_place) * 20
        + top4_rate * 0.4
        + win_rate * 0.3
        + min(games, 200) * 0.15
    )

    return round(score, 2)


def main():
    comps = defaultdict(lambda: {
        "games": 0,
        "placements": [],
        "wins": 0,
        "top4": 0,
        "units": None,
        "items": [],
        "traits": [],
        "unit_counts": Counter(),
        "unit_item_pairs": [],
    })

    print("matches.jsonl 읽는 중...")

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue

            match = json.loads(line)
            participants = match.get("info", {}).get("participants", [])

            for p in participants:
                placement = p.get("placement")

                if placement is None:
                    continue

                units = get_units(p)

                if len(units) < 5:
                    continue

                items = get_items(p)
                traits = get_traits(p)
                unit_item_pairs = get_unit_items(p)

                comp_key = make_comp_key(units)

                comps[comp_key]["games"] += 1
                comps[comp_key]["placements"].append(placement)

                if placement <= 4:
                    comps[comp_key]["top4"] += 1

                if placement == 1:
                    comps[comp_key]["wins"] += 1

                comps[comp_key]["units"] = units
                comps[comp_key]["items"].extend(items)
                comps[comp_key]["traits"].extend(traits)
                comps[comp_key]["unit_counts"].update(units)
                comps[comp_key]["unit_item_pairs"].extend(unit_item_pairs)

    rows = []

    for comp_key, data in comps.items():
        games = data["games"]

        if games < MIN_GAMES:
            continue

        avg_place = sum(data["placements"]) / games
        top4_rate = data["top4"] / games * 100
        win_rate = data["wins"] / games * 100

        item_counts = Counter(data["items"]).most_common(12)
        trait_counts = Counter(data["traits"]).most_common(12)
        unit_counts = data["unit_counts"].most_common()

        core_units = [
            unit for unit, count in unit_counts
            if count / games >= 0.6
        ]

        if len(core_units) == 0:
            core_units = data["units"][:5]

        main_carry = guess_main_carry(data["unit_item_pairs"])
        main_tank = guess_main_tank(data["unit_item_pairs"])

        stability_score = calc_stability_score(
            games,
            avg_place,
            top4_rate,
            win_rate
        )

        rows.append({
            "comp": comp_key,
            "units": ",".join(data["units"]),
            "core_units": ",".join(core_units),
            "core_items": ",".join([x[0] for x in item_counts]),
            "core_traits": ",".join([x[0] for x in trait_counts]),
            "main_carry": main_carry,
            "main_tank": main_tank,
            "games": games,
            "avg_place": round(avg_place, 2),
            "top4_rate": round(top4_rate, 2),
            "win_rate": round(win_rate, 2),
            "stability_score": stability_score,
        })

    df = pd.DataFrame(rows)

    df = df.sort_values(
        by=["stability_score", "avg_place", "games"],
        ascending=[False, True, False]
    )

    df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")

    print("추천용 덱 데이터셋 생성 완료!")
    print(f"저장 위치: {OUTPUT_FILE}")
    print(f"총 덱 수: {len(df)}")
    print(df.head(10))


if __name__ == "__main__":
    main()