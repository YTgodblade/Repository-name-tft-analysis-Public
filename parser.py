import json
import csv

INPUT = "matches.jsonl"
OUTPUT = "player_dataset.csv"


def clean_name(name):
    if not name:
        return ""
    return name.split("_")[-1]


with open(INPUT, "r", encoding="utf-8") as infile, \
     open(OUTPUT, "w", newline="", encoding="utf-8") as outfile:

    writer = csv.writer(outfile)

    writer.writerow([
        "match_id",
        "placement",
        "level",
        "gold_left",
        "last_round",
        "players_eliminated",
        "total_damage_to_players",
        "traits",
        "units",
        "patch",
        "game_length",
        "set_number"
    ])

    count = 0

    for line in infile:
        if not line.strip():
            continue

        match = json.loads(line)

        match_id = match["metadata"]["match_id"]
        info = match["info"]

        patch = info.get("game_version", "")
        game_length = info.get("game_length", "")
        set_number = info.get("tft_set_number", "")

        for p in info["participants"]:

            traits = ";".join([
                f'{clean_name(t["name"])}:{t["num_units"]}'
                for t in p.get("traits", [])
                if t.get("style", 0) > 0
            ])

            units = []

            for u in p.get("units", []):
                units.append({
                    "name": clean_name(u.get("character_id", "")),
                    "star": u.get("tier", ""),
                    "rarity": u.get("rarity", ""),
                    "items": [clean_name(item) for item in u.get("itemNames", [])]
                })

            writer.writerow([
                match_id,
                p.get("placement", ""),
                p.get("level", ""),
                p.get("gold_left", ""),
                p.get("last_round", ""),
                p.get("players_eliminated", ""),
                p.get("total_damage_to_players", ""),
                traits,
                json.dumps(units, ensure_ascii=False),
                patch,
                game_length,
                set_number
            ])

            count += 1

print(f"CSV 생성 완료! 총 {count}명의 플레이어 데이터 저장")