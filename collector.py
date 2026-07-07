import json
import os
import time
import requests

from config import *

MATCH_FILE = "matches.jsonl"
PROGRESS_FILE = "progress.json"


# Match ID 읽기
with open("match_ids.txt", "r") as f:
    match_ids = [line.strip() for line in f]

# 이어받기 위치
start = 0

if os.path.exists(PROGRESS_FILE):

    with open(PROGRESS_FILE, "r") as f:
        start = json.load(f)["index"]

print(f"총 경기 : {len(match_ids)}")
print(f"이어받기 : {start}")

for i in range(start, len(match_ids)):

    match_id = match_ids[i]

    url = f"https://asia.api.riotgames.com/tft/match/v1/matches/{match_id}"

    success = False

    while not success:

        response = requests.get(
            url,
            headers=HEADERS
        )

        if response.status_code == 200:

            data = response.json()

            with open(MATCH_FILE, "a", encoding="utf-8") as out:

                out.write(
                    json.dumps(
                        data,
                        ensure_ascii=False
                    )
                )

                out.write("\n")

            with open(PROGRESS_FILE, "w") as p:

                json.dump(
                    {
                        "index": i + 1
                    },
                    p
                )

            print(f"[{i+1}/{len(match_ids)}] 완료")

            success = True

        elif response.status_code == 429:

            print("429 발생...10초 대기")

            time.sleep(10)

        else:

            print(response.status_code)

            time.sleep(5)

    time.sleep(1.2)

print("모든 경기 다운로드 완료!")