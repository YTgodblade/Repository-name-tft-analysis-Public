import json
import urllib.request
import pandas as pd

CDRAGON_URL = "https://raw.communitydragon.org/latest/cdragon/tft/ko_kr.json"

INPUT_FILE = "recommender/comp_dataset.csv"
OUTPUT_FILE = "recommender/comp_dataset_kr.csv"

print("CommunityDragon 한글 데이터 다운로드 중...")

request = urllib.request.Request(
    CDRAGON_URL,
    headers={"User-Agent": "Mozilla/5.0"}
)

with urllib.request.urlopen(request) as response:
    data = json.loads(response.read().decode("utf-8"))

unit_map = {}
item_map = {}
trait_map = {}


def clean_id(value):
    value = str(value)

    prefixes = [
        "TFT17_",
        "TFT16_",
        "TFT15_",
        "TFT14_",
        "TFT_",
        "Item_",
    ]

    for prefix in prefixes:
        value = value.replace(prefix, "")

    return value


for champ in data.get("sets", {}).get("17", {}).get("champions", []):
    api = clean_id(champ.get("apiName", ""))
    name = champ.get("name", "")

    if api and name:
        unit_map[api] = name


for item in data.get("items", []):
    api = clean_id(item.get("apiName", ""))
    name = item.get("name", "")

    if api and name:
        item_map[api] = name


for trait in data.get("sets", {}).get("17", {}).get("traits", []):
    api = clean_id(trait.get("apiName", ""))
    name = trait.get("name", "")

    if api and name:
        trait_map[api] = name


MANUAL_TRAITS = {
    "SpaceGroove": "우주 그루브",
    "HPTank": "싸움꾼",
    "ResistTank": "요새",
    "ShieldTank": "선봉대",
    "MeleeTrait": "도전자",
    "RangedTrait": "저격수",
    "APTrait": "전달자",
    "ManaTrait": "운명술사",
    "AssassinTrait": "불한당",
    "FlexTrait": "길잡이",
    "PsyOps": "초능력",
    "DarkStar": "암흑의 별",
    "Astronaut": "시간 균열자",
    "Timebreaker": "시간 균열자",
    "DRX": "동물특공대",

    "BlitzcrankUniqueTrait": "파티광",
    "JhinUniqueTrait": "말살자",
    "ShenUniqueTrait": "보루",
    "FioraUniqueTrait": "신성 결투가",
    "TahmKenchUniqueTrait": "예언자",
    "SonaUniqueTrait": "지휘관",
    "VexUniqueTrait": "최신상",
    "MorganaUniqueTrait": "중재자",
    "RhaastUniqueTrait": "태고족",
    "GravesTrait": "최신상",
}


def translate_unit(value):
    value = clean_id(value)
    return unit_map.get(value, value)


def translate_item(value):
    value = clean_id(value)
    return item_map.get(value, value)


def translate_trait(value):
    value = str(value)

    if ":" in value:
        trait, level = value.split(":", 1)
        trait_clean = clean_id(trait)

        kr = (
            trait_map.get(trait_clean)
            or MANUAL_TRAITS.get(trait_clean)
            or trait_clean
        )

        return f"{kr} {level}"

    trait_clean = clean_id(value)

    return (
        trait_map.get(trait_clean)
        or MANUAL_TRAITS.get(trait_clean)
        or trait_clean
    )


def translate_list(value, kind):
    if pd.isna(value) or str(value).strip() == "":
        return ""

    parts = [x.strip() for x in str(value).split(",") if x.strip()]

    if kind == "unit":
        return ",".join(translate_unit(x) for x in parts)

    if kind == "item":
        return ",".join(translate_item(x) for x in parts)

    if kind == "trait":
        return ",".join(translate_trait(x) for x in parts)

    return ",".join(parts)


df = pd.read_csv(INPUT_FILE)

df["units_kr"] = df["units"].apply(lambda x: translate_list(x, "unit"))
df["core_units_kr"] = df["core_units"].apply(lambda x: translate_list(x, "unit"))
df["core_items_kr"] = df["core_items"].apply(lambda x: translate_list(x, "item"))
df["core_traits_kr"] = df["core_traits"].apply(lambda x: translate_list(x, "trait"))
df["main_carry_kr"] = df["main_carry"].apply(translate_unit)
df["main_tank_kr"] = df["main_tank"].apply(translate_unit)

df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")

print("한글 덱 데이터셋 생성 완료!")
print(f"저장 위치: {OUTPUT_FILE}")
print(df.head(5))