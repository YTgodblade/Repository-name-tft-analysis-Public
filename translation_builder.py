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
    headers={
        "User-Agent": "Mozilla/5.0"
    }
)

with urllib.request.urlopen(request) as response:
    data = json.loads(response.read().decode("utf-8"))

unit_map = {}
item_map = {}
trait_map = {}

def clean_id(value):
    value = str(value)
    if "_" in value:
        return value.split("_")[-1]
    return value

for champ in data.get("sets", {}).get("17", {}).get("champions", []):
    api_name = clean_id(champ.get("apiName", ""))
    name = champ.get("name", "")
    if api_name and name:
        unit_map[api_name] = name

for item in data.get("items", []):
    api_name = clean_id(item.get("apiName", ""))
    name = item.get("name", "")
    if api_name and name:
        item_map[api_name] = name

for trait in data.get("sets", {}).get("17", {}).get("traits", []):
    api_name = clean_id(trait.get("apiName", ""))
    name = trait.get("name", "")
    if api_name and name:
        trait_map[api_name] = name

def translate_trait(value):
    value = str(value)
    if ":" in value:
        trait_name, count = value.split(":", 1)
        return f"{trait_map.get(trait_name, trait_name)} {count}"
    return trait_map.get(value, value)

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

    df.insert(
        1,
        kr_col,
        df[name_col].apply(lambda x: translate_value(x, name_col))
    )

    df.to_csv(output_file, index=False, encoding="utf-8-sig")

    print(output_file, "생성 완료")

print("번역 완료!")