import json
import urllib.request
import pandas as pd

CDRAGON_URL = "https://raw.communitydragon.org/latest/cdragon/tft/ko_kr.json"

FILES = [
    ("unit_tier.csv", "unit", "unit_tier_kr.csv"),
    ("item_tier.csv", "item", "item_tier_kr.csv"),
    ("trait_tier.csv", "trait", "trait_tier_kr.csv"),
]

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

unit_icon_map = {}
item_icon_map = {}
trait_icon_map = {}


def clean_id(value):
    value = str(value)
    if "_" in value:
        return value.split("_")[-1]
    return value


def make_cdragon_url(icon_path):
    if not icon_path:
        return ""

    path = str(icon_path).lower()

    if path.startswith("/lol-game-data/assets/"):
        path = path.replace(
            "/lol-game-data/assets/",
            "plugins/rcp-be-lol-game-data/global/default/assets/"
        )

    path = path.replace("\\", "/")

    return "https://raw.communitydragon.org/latest/" + path


# 유닛 매핑
for champ in data.get("sets", {}).get("17", {}).get("champions", []):
    api_name = clean_id(champ.get("apiName", ""))
    name = champ.get("name", "")
    icon = make_cdragon_url(champ.get("icon", ""))

    if api_name and name:
        unit_map[api_name] = name
        unit_icon_map[api_name] = icon


# 아이템 매핑
for item in data.get("items", []):
    api_name = clean_id(item.get("apiName", ""))
    name = item.get("name", "")
    icon = make_cdragon_url(item.get("icon", ""))

    if api_name and name:
        item_map[api_name] = name
        item_icon_map[api_name] = icon


# 시너지 매핑
for trait in data.get("sets", {}).get("17", {}).get("traits", []):
    api_name = clean_id(trait.get("apiName", ""))
    name = trait.get("name", "")
    icon = make_cdragon_url(trait.get("icon", ""))

    if api_name and name:
        trait_map[api_name] = name
        trait_icon_map[api_name] = icon


def translate_trait(value):
    value = str(value)

    if ":" in value:
        trait_name, count = value.split(":", 1)
        return f"{trait_map.get(trait_name, trait_name)} {count}"

    return trait_map.get(value, value)


def get_icon(value, kind):
    value = str(value)

    if kind == "unit":
        return unit_icon_map.get(value, "")

    if kind == "item":
        return item_icon_map.get(value, "")

    if kind == "trait":
        if ":" in value:
            value = value.split(":", 1)[0]
        return trait_icon_map.get(value, "")

    return ""


def translate_value(value, kind):
    value = str(value)

    if kind == "unit":
        return unit_map.get(value, value)

    if kind == "item":
        return item_map.get(value, value)

    if kind == "trait":
        return translate_trait(value)

    return value


for input_file, name_col, output_file in FILES:
    df = pd.read_csv(input_file)

    kr_col = name_col + "_kr"
    icon_col = "icon_url"

    if kr_col in df.columns:
        df = df.drop(columns=[kr_col])

    if icon_col in df.columns:
        df = df.drop(columns=[icon_col])

    df.insert(
        1,
        kr_col,
        df[name_col].apply(lambda x: translate_value(x, name_col))
    )

    df.insert(
        2,
        icon_col,
        df[name_col].apply(lambda x: get_icon(x, name_col))
    )

    df.to_csv(output_file, index=False, encoding="utf-8-sig")

    print(output_file, "생성 완료")

print("번역 + 아이콘 URL 생성 완료!")