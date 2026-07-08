import json
import urllib.request
import pandas as pd
from pathlib import Path

INPUT_FILE = "unit_tier_kr.csv"
OUT_DIR = Path("recommender/assets/units")
OUT_DIR.mkdir(parents=True, exist_ok=True)

VERSION_URL = "https://ddragon.leagueoflegends.com/api/versions.json"

SPECIAL_NAMES = {
    "Chogath": "ChoGath",
    "Kaisa": "KaiSa",
    "Leblanc": "LeBlanc",
    "RekSai": "RekSai",
    "TahmKench": "TahmKench",
    "TwistedFate": "TwistedFate",
    "AurelionSol": "AurelionSol",
    "Belveth": "Belveth",
    "MasterYi": "MasterYi",
    "MissFortune": "MissFortune",
}

def get_latest_version():
    req = urllib.request.Request(VERSION_URL, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req) as res:
        versions = json.loads(res.read().decode("utf-8"))
    return versions[0]

def download(url, path):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req) as res:
        path.write_bytes(res.read())

version = get_latest_version()
print("Data Dragon 버전:", version)

df = pd.read_csv(INPUT_FILE)

success = 0
fail = 0

for _, row in df.iterrows():
    unit = str(row["unit"]).strip()
    if not unit or unit == "nan":
        continue

    champ_id = SPECIAL_NAMES.get(unit, unit)
    url = f"https://ddragon.leagueoflegends.com/cdn/{version}/img/champion/{champ_id}.png"
    save_path = OUT_DIR / f"{unit}.png"

    try:
        download(url, save_path)
        print("저장 완료:", unit)
        success += 1
    except Exception as e:
        print("실패:", unit, "/", e)
        fail += 1

print("완료!")
print("성공:", success)
print("실패:", fail)
print("저장 폴더:", OUT_DIR)