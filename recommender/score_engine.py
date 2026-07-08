import pandas as pd

COMP_FILE = "recommender/comp_dataset_kr.csv"


def split_list(value):
    if pd.isna(value) or str(value).strip() == "":
        return []
    return [x.strip() for x in str(value).split(",") if x.strip()]


def calc_match_score(current, target):
    current_set = set(current)
    target_set = set(target)

    if len(target_set) == 0:
        return 0, []

    matched = list(current_set & target_set)
    score = len(matched) / len(target_set) * 100

    return score, matched


def situation_bonus(hp, gold, level):
    bonus = 0
    reasons = []

    if hp >= 80:
        bonus += 8
        reasons.append("체력이 높아 후반 덱 전환이 가능합니다.")
    elif hp >= 60:
        bonus += 5
        reasons.append("체력이 안정적이라 덱 전환 여유가 있습니다.")
    elif hp <= 30:
        bonus -= 6
        reasons.append("체력이 낮아 빠르게 강해지는 방향이 필요합니다.")

    if gold >= 60:
        bonus += 6
        reasons.append("골드가 많아 레벨업 또는 후반 운영이 가능합니다.")
    elif gold >= 40:
        bonus += 3
        reasons.append("골드가 충분해 선택지가 넓습니다.")
    elif gold <= 15:
        bonus -= 3
        reasons.append("골드가 적어 큰 전환보다는 현재 보드 강화가 필요합니다.")

    if level >= 8:
        bonus += 5
        reasons.append("레벨이 높아 고코스트 기물을 활용하기 좋습니다.")
    elif level <= 6:
        bonus -= 2
        reasons.append("아직 레벨이 낮아 완성 덱까지 시간이 필요합니다.")

    return bonus, reasons


def score_comp(row, current_units, current_items, current_traits, hp=50, gold=30, level=7):
    comp_units = split_list(row["units_kr"])
    core_units = split_list(row["core_units_kr"])
    core_items = split_list(row["core_items_kr"])
    core_traits = split_list(row["core_traits_kr"])

    main_carry = str(row["main_carry_kr"])
    main_tank = str(row["main_tank_kr"])

    unit_score, matched_units = calc_match_score(current_units, comp_units)
    core_unit_score, matched_core_units = calc_match_score(current_units, core_units)
    item_score, matched_items = calc_match_score(current_items, core_items)
    trait_score, matched_traits = calc_match_score(current_traits, core_traits)

    meta_score = min(float(row["stability_score"]), 220) / 220 * 100

    carry_bonus = 0
    tank_bonus = 0
    reasons = []

    if main_carry in current_units:
        carry_bonus += 12
        reasons.append(f"메인 캐리인 {main_carry}를 이미 보유하고 있습니다.")

    if main_tank in current_units:
        tank_bonus += 8
        reasons.append(f"메인 탱커인 {main_tank}를 이미 보유하고 있습니다.")

    situation, situation_reasons = situation_bonus(hp, gold, level)

    final_score = (
        unit_score * 0.25
        + core_unit_score * 0.25
        + trait_score * 0.20
        + item_score * 0.15
        + meta_score * 0.15
        + carry_bonus
        + tank_bonus
        + situation
    )

    missing_units = [u for u in comp_units if u not in current_units]

    if matched_units:
        reasons.append(f"현재 기물 {len(matched_units)}명이 추천 덱과 일치합니다.")

    if matched_core_units:
        reasons.append(f"핵심 기물 {len(matched_core_units)}명을 이미 보유하고 있습니다.")

    if matched_items:
        reasons.append("보유 아이템이 추천 덱의 핵심 아이템과 연결됩니다.")

    if matched_traits:
        reasons.append("현재 시너지가 추천 덱의 핵심 시너지와 연결됩니다.")

    reasons.extend(situation_reasons)

    reasons.append(
        f"이 덱은 평균 등수 {row['avg_place']}, TOP4률 {row['top4_rate']}%의 데이터를 기반으로 합니다."
    )

    return {
        "score": round(final_score, 2),
        "unit_score": round(unit_score, 2),
        "core_unit_score": round(core_unit_score, 2),
        "item_score": round(item_score, 2),
        "trait_score": round(trait_score, 2),
        "meta_score": round(meta_score, 2),
        "matched_units": matched_units,
        "matched_items": matched_items,
        "matched_traits": matched_traits,
        "missing_units": missing_units[:6],
        "reasons": reasons,
    }


def recommend(current_units, current_items=None, current_traits=None, hp=50, gold=30, level=7, top_n=5):
    current_items = current_items or []
    current_traits = current_traits or []

    df = pd.read_csv(COMP_FILE)
    results = []

    for _, row in df.iterrows():
        score_data = score_comp(
            row,
            current_units,
            current_items,
            current_traits,
            hp,
            gold,
            level
        )

        results.append({
            "score": score_data["score"],
            "comp": row["comp"],
            "units": row["units_kr"],
            "core_units": row["core_units_kr"],
            "core_items": row["core_items_kr"],
            "core_traits": row["core_traits_kr"],
            "main_carry": row["main_carry_kr"],
            "main_tank": row["main_tank_kr"],
            "avg_place": row["avg_place"],
            "top4_rate": row["top4_rate"],
            "win_rate": row["win_rate"],
            "games": row["games"],
            "unit_score": score_data["unit_score"],
            "core_unit_score": score_data["core_unit_score"],
            "item_score": score_data["item_score"],
            "trait_score": score_data["trait_score"],
            "meta_score": score_data["meta_score"],
            "matched_units": score_data["matched_units"],
            "matched_items": score_data["matched_items"],
            "matched_traits": score_data["matched_traits"],
            "missing_units": score_data["missing_units"],
            "reasons": score_data["reasons"],
        })

    results = sorted(results, key=lambda x: x["score"], reverse=True)

    return results[:top_n]