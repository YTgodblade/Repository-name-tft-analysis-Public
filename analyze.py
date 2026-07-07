import pandas as pd
import json
from collections import Counter, defaultdict

INPUT = "player_dataset.csv"

df = pd.read_csv(INPUT)

print("전체 플레이어 수:", len(df))

# 상위권 데이터
top4 = df[df["placement"] <= 4]

print("TOP4 플레이어 수:", len(top4))
print("TOP4 비율:", round(len(top4) / len(df) * 100, 2), "%")

# 덱 이름 만들기: 유닛 이름들을 정렬해서 하나의 조합으로 묶기
def get_comp_name(units_json):
    try:
        units = json.loads(units_json)
        names = sorted([u["name"] for u in units])
        return "+".join(names)
    except:
        return ""

df["comp"] = df["units"].apply(get_comp_name)

# 덱별 통계
comp_stats = df.groupby("comp").agg(
    games=("placement", "count"),
    avg_place=("placement", "mean"),
    top4_rate=("placement", lambda x: (x <= 4).mean() * 100),
    win_rate=("placement", lambda x: (x == 1).mean() * 100)
).reset_index()

# 표본 적은 덱 제거
comp_stats = comp_stats[comp_stats["games"] >= 20]

# 평균 등수 좋은 순
comp_stats = comp_stats.sort_values("avg_place")

comp_stats.to_csv("comp_stats.csv", index=False, encoding="utf-8-sig")

print("comp_stats.csv 생성 완료")
print(comp_stats.head(20))