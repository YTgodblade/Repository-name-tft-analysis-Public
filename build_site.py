import pandas as pd
import os

os.makedirs("site", exist_ok=True)

TABLES = [
    ("기물 티어표", "unit_tier_kr.csv", "unit_kr", "unit-table"),
    ("아이템 티어표", "item_tier_kr.csv", "item_kr", "item-table"),
    ("시너지 티어표", "trait_tier_kr.csv", "trait_kr", "trait-table"),
]

html_sections = ""

for title, file, name_col, table_id in TABLES:
    df = pd.read_csv(file)

    rows = ""

    for _, row in df.iterrows():
        rows += f"""
        <tr class="tier-row tier-{row['tier']}" data-tier="{row['tier']}">
            <td>{row[name_col]}</td>
            <td><span class="badge badge-{row['tier']}">{row['tier']}</span></td>
            <td>{row['games']}</td>
            <td>{row['pick_rate']}%</td>
            <td>{row['avg_place']}</td>
            <td>{row['top4_rate']}%</td>
            <td>{row['win_rate']}%</td>
            <td>{row['score']}</td>
        </tr>
        """

    html_sections += f"""
    <section>
        <div class="section-header">
            <h2>{title}</h2>
            <div class="filters">
                <button onclick="filterTable('{table_id}', 'ALL')">전체</button>
                <button onclick="filterTable('{table_id}', 'S')">S</button>
                <button onclick="filterTable('{table_id}', 'A')">A</button>
                <button onclick="filterTable('{table_id}', 'B')">B</button>
                <button onclick="filterTable('{table_id}', 'C')">C</button>
                <button onclick="filterTable('{table_id}', 'D')">D</button>
            </div>
        </div>

        <table id="{table_id}">
            <thead>
                <tr>
                    <th>이름</th>
                    <th>티어</th>
                    <th>게임 수</th>
                    <th>채용률</th>
                    <th>평균 등수</th>
                    <th>TOP4률</th>
                    <th>1등률</th>
                    <th>점수</th>
                </tr>
            </thead>
            <tbody>
                {rows}
            </tbody>
        </table>
    </section>
    """

html = f"""
<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<title>TFT 통계 사이트</title>

<style>
body {{
    background: #0f172a;
    color: white;
    font-family: Arial, sans-serif;
    margin: 40px;
}}

h1 {{
    text-align: center;
    margin-bottom: 10px;
}}

.subtitle {{
    text-align: center;
    color: #94a3b8;
    margin-bottom: 50px;
}}

section {{
    margin-bottom: 60px;
    background: #111827;
    padding: 24px;
    border-radius: 16px;
}}

.section-header {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16px;
}}

h2 {{
    margin: 0;
    color: #facc15;
}}

.filters button {{
    background: #1e293b;
    color: white;
    border: 1px solid #334155;
    padding: 8px 12px;
    border-radius: 8px;
    cursor: pointer;
    margin-left: 6px;
}}

.filters button:hover {{
    background: #334155;
}}

table {{
    width: 100%;
    border-collapse: collapse;
    overflow: hidden;
    border-radius: 12px;
}}

th {{
    background: #1e293b;
    padding: 12px;
}}

td {{
    padding: 10px;
    border-bottom: 1px solid #334155;
    text-align: center;
}}

tr:hover {{
    background: #1e293b;
}}

.badge {{
    font-weight: bold;
    padding: 5px 12px;
    border-radius: 999px;
}}

.badge-S {{
    background: #facc15;
    color: #111827;
}}

.badge-A {{
    background: #38bdf8;
    color: #111827;
}}

.badge-B {{
    background: #4ade80;
    color: #111827;
}}

.badge-C {{
    background: #c084fc;
    color: #111827;
}}

.badge-D {{
    background: #f87171;
    color: #111827;
}}
</style>
</head>

<body>

<h1>TFT Challenger Data Analysis</h1>
<p class="subtitle">한국 챌린저 4466경기 / 35,539명 플레이어 분석</p>

{html_sections}

<script>
function filterTable(tableId, tier) {{
    const table = document.getElementById(tableId);
    const rows = table.querySelectorAll("tbody tr");

    rows.forEach(row => {{
        if (tier === "ALL" || row.dataset.tier === tier) {{
            row.style.display = "";
        }} else {{
            row.style.display = "none";
        }}
    }});
}}
</script>

</body>
</html>
"""

with open("site/index.html", "w", encoding="utf-8") as f:
    f.write(html)

print("사이트 생성 완료!")