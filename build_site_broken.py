import pandas as pd
import os
import json

os.makedirs("site", exist_ok=True)

PAGES = [
    {
        "title": "기물 티어표",
        "file": "unit_tier_kr.csv",
        "name_col": "unit_kr",
        "raw_col": "unit",
        "output": "units.html",
        "active": "기물",
    },
    {
        "title": "아이템 티어표",
        "file": "item_tier_kr.csv",
        "name_col": "item_kr",
        "raw_col": "item",
        "output": "items.html",
        "active": "아이템",
    },
    {
        "title": "시너지 티어표",
        "file": "trait_tier_kr.csv",
        "name_col": "trait_kr",
        "raw_col": "trait",
        "output": "traits.html",
        "active": "시너지",
    },
]


def safe_text(value):
    return str(value).replace("<", "").replace(">", "")


def make_nav(active):
    links = [
        ("index.html", "홈"),
        ("units.html", "기물"),
        ("items.html", "아이템"),
        ("traits.html", "시너지"),
        ("about.html", "프로젝트 소개"),
    ]

    html = ""
    for href, label in links:
        cls = "active" if label == active else ""
        html += f'<a class="{cls}" href="{href}">{label}</a>'

    return html


def base_html(title, active, body):
    return f"""
<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<title>{title}</title>

<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

<style>
body {{
    margin: 0;
    background: #0f172a;
    color: #e5e7eb;
    font-family: Arial, sans-serif;
}}

header {{
    padding: 30px 40px;
    background: #020617;
    border-bottom: 1px solid #1e293b;
}}

h1 {{
    margin: 0;
    font-size: 32px;
}}

.subtitle {{
    color: #94a3b8;
    margin-top: 8px;
}}

nav {{
    margin-top: 22px;
}}

nav a {{
    color: #cbd5e1;
    text-decoration: none;
    margin-right: 12px;
    padding: 8px 14px;
    border-radius: 999px;
    background: #111827;
}}

nav a.active {{
    background: #facc15;
    color: #111827;
    font-weight: bold;
}}

main {{
    padding: 40px;
}}

.card {{
    background: #111827;
    padding: 24px;
    border-radius: 18px;
    margin-bottom: 34px;
}}

.chart-grid {{
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 24px;
    margin-bottom: 34px;
}}

.chart-card {{
    background: #111827;
    padding: 24px;
    border-radius: 18px;
}}

.chart-card h2 {{
    margin-top: 0;
    color: #facc15;
}}

canvas {{
    max-height: 360px;
}}

.section-header {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 20px;
}}

h2 {{
    color: #facc15;
}}

.search {{
    background: #020617;
    color: white;
    border: 1px solid #334155;
    border-radius: 10px;
    padding: 10px 14px;
    width: 260px;
}}

.filters {{
    margin: 18px 0;
}}

.filters button {{
    background: #1e293b;
    color: white;
    border: 1px solid #334155;
    padding: 8px 13px;
    border-radius: 8px;
    cursor: pointer;
    margin-right: 6px;
}}

.filters button:hover {{
    background: #334155;
}}

table {{
    width: 100%;
    border-collapse: collapse;
}}

th {{
    background: #1e293b;
    padding: 12px;
    cursor: pointer;
}}

td {{
    padding: 10px;
    border-bottom: 1px solid #334155;
    text-align: center;
}}

tr:hover {{
    background: #1e293b;
    cursor: pointer;
}}

.name-cell {{
    text-align: left;
    font-weight: bold;
}}

.badge {{
    font-weight: bold;
    padding: 5px 12px;
    border-radius: 999px;
}}

.badge-S {{ background: #facc15; color: #111827; }}
.badge-A {{ background: #38bdf8; color: #111827; }}
.badge-B {{ background: #4ade80; color: #111827; }}
.badge-C {{ background: #c084fc; color: #111827; }}
.badge-D {{ background: #f87171; color: #111827; }}

.home-grid {{
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 24px;
}}

.home-card {{
    background: #111827;
    padding: 28px;
    border-radius: 18px;
    text-decoration: none;
    color: white;
    border: 1px solid #1e293b;
}}

.home-card:hover {{
    background: #1e293b;
}}

.modal-bg {{
    display: none;
    position: fixed;
    inset: 0;
    background: rgba(0,0,0,0.7);
    justify-content: center;
    align-items: center;
    z-index: 999;
}}

.modal {{
    background: #111827;
    border: 1px solid #334155;
    border-radius: 18px;
    padding: 28px;
    width: 360px;
}}

.close-btn {{
    margin-top: 16px;
    width: 100%;
    background: #facc15;
    color: #111827;
    border: none;
    padding: 10px;
    border-radius: 10px;
    font-weight: bold;
    cursor: pointer;
}}

@media (max-width: 1000px) {{
    .chart-grid {{
        grid-template-columns: 1fr;
    }}

    .home-grid {{
        grid-template-columns: 1fr;
    }}

    .section-header {{
        flex-direction: column;
        align-items: flex-start;
    }}

    .search {{
        width: 100%;
    }}
}}
</style>
</head>

<body>
<header>
    <h1>TFT Challenger Data Analysis</h1>
    <div class="subtitle">한국 챌린저 4466경기 / 35,539명 플레이어 분석</div>
    <nav>{make_nav(active)}</nav>
</header>

<main>
{body}
</main>
</body>
</html>
"""


def make_chart_data(df, name_col):
    pick_top = df.sort_values("pick_rate", ascending=False).head(10)
    avg_top = df.sort_values("avg_place", ascending=True).head(10)
    win_top = df.sort_values("win_rate", ascending=False).head(10)
    scatter = df[df["games"] >= 100].copy()

    return {
        "pick_labels": pick_top[name_col].tolist(),
        "pick_values": pick_top["pick_rate"].tolist(),

        "avg_labels": avg_top[name_col].tolist(),
        "avg_values": avg_top["avg_place"].tolist(),

        "win_labels": win_top[name_col].tolist(),
        "win_values": win_top["win_rate"].tolist(),

        "scatter_values": [
            {
                "x": float(row["pick_rate"]),
                "y": float(row["avg_place"]),
                "name": str(row[name_col]),
            }
            for _, row in scatter.iterrows()
        ],
    }


def make_table_page(page):
    df = pd.read_csv(page["file"])
    chart_data = make_chart_data(df, page["name_col"])

    rows = ""

    for _, row in df.iterrows():
        name = safe_text(row[page["name_col"]])
        raw = safe_text(row[page["raw_col"]])
        tier = safe_text(row["tier"])

        rows += f"""
        <tr class="tier-row"
            data-tier="{tier}"
            data-name="{name.lower()} {raw.lower()}"
            data-display-name="{name}"
            data-games="{row['games']}"
            data-pick-rate="{row['pick_rate']}"
            data-avg-place="{row['avg_place']}"
            data-top4="{row['top4_rate']}"
            data-win="{row['win_rate']}"
            data-score="{row['score']}">
            <td class="name-cell">{name}</td>
            <td><span class="badge badge-{tier}">{tier}</span></td>
            <td>{row["games"]}</td>
            <td>{row["pick_rate"]}%</td>
            <td>{row["avg_place"]}</td>
            <td>{row["top4_rate"]}%</td>
            <td>{row["win_rate"]}%</td>
            <td>{row["score"]}</td>
        </tr>
        """

    chart_json = json.dumps(chart_data, ensure_ascii=False)

    html = base_html(
        title=page["title"],
        active=page["active"],
        body=f"""
        <div class="chart-grid">
            <div class="chart-card">
                <h2>채용률 TOP 10</h2>
                <canvas id="pickChart"></canvas>
            </div>

            <div class="chart-card">
                <h2>평균 등수 TOP 10</h2>
                <canvas id="avgChart"></canvas>
            </div>

            <div class="chart-card">
                <h2>승률 TOP 10</h2>
                <canvas id="winChart"></canvas>
            </div>

            <div class="chart-card">
                <h2>채용률 vs 평균 등수</h2>
                <canvas id="scatterChart"></canvas>
            </div>
        </div>

        <section class="card">
            <div class="section-header">
                <h2>{page["title"]}</h2>
                <input id="searchInput" class="search" placeholder="검색어 입력">
            </div>

            <div class="filters">
                <button onclick="filterTier('ALL')">전체</button>
                <button onclick="filterTier('S')">S</button>
                <button onclick="filterTier('A')">A</button>
                <button onclick="filterTier('B')">B</button>
                <button onclick="filterTier('C')">C</button>
                <button onclick="filterTier('D')">D</button>
            </div>

            <table id="dataTable">
                <thead>
                    <tr>
                        <th onclick="sortTable(0, 'text')">이름</th>
                        <th onclick="sortTable(1, 'text')">티어