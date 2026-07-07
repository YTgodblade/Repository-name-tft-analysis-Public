import pandas as pd
import os

os.makedirs("site", exist_ok=True)

CDRAGON_BASE = "https://raw.communitydragon.org/latest/game/"

PAGES = [
    {
        "title": "기물 티어표",
        "file": "unit_tier_kr.csv",
        "name_col": "unit_kr",
        "raw_col": "unit",
        "output": "units.html",
        "kind": "unit",
    },
    {
        "title": "아이템 티어표",
        "file": "item_tier_kr.csv",
        "name_col": "item_kr",
        "raw_col": "item",
        "output": "items.html",
        "kind": "item",
    },
    {
        "title": "시너지 티어표",
        "file": "trait_tier_kr.csv",
        "name_col": "trait_kr",
        "raw_col": "trait",
        "output": "traits.html",
        "kind": "trait",
    },
]


def safe_text(value):
    return str(value).replace("<", "").replace(">", "")


def icon_url(row, kind):
    raw = str(row.get("raw_name", ""))

    if kind == "unit":
        return f"https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/assets/characters/{raw.lower()}/hud/{raw.lower()}_square.png"

    if kind == "item":
        return f"https://raw.communitydragon.org/latest/game/assets/maps/particles/tft/item_icons/{raw.lower()}.png"

    if kind == "trait":
        trait = raw.split(":")[0].lower()
        return f"https://raw.communitydragon.org/latest/game/assets/ux/tft/traiticons/{trait}.png"

    return ""


def make_nav(active):
    links = [
        ("index.html", "홈"),
        ("units.html", "기물"),
        ("items.html", "아이템"),
        ("traits.html", "시너지"),
    ]

    html = ""

    for href, label in links:
        cls = "active" if label == active else ""
        html += f'<a class="{cls}" href="{href}">{label}</a>'

    return html


def make_table_page(page):
    df = pd.read_csv(page["file"])

    df = df.copy()
    df["raw_name"] = df[page["raw_col"]]

    rows = ""

    for _, row in df.iterrows():
        name = safe_text(row[page["name_col"]])
        raw = safe_text(row["raw_name"])
        tier = safe_text(row["tier"])
        url = icon_url(row, page["kind"])

        rows += f"""
        <tr class="tier-row" data-tier="{tier}" data-name="{name.lower()} {raw.lower()}">
            <td class="name-cell">
                <img class="icon" src="{url}" onerror="this.style.display='none'">
                <span>{name}</span>
            </td>
            <td><span class="badge badge-{tier}">{tier}</span></td>
            <td>{row["games"]}</td>
            <td>{row["pick_rate"]}%</td>
            <td>{row["avg_place"]}</td>
            <td>{row["top4_rate"]}%</td>
            <td>{row["win_rate"]}%</td>
            <td>{row["score"]}</td>
        </tr>
        """

    html = base_html(
        title=page["title"],
        active=page["title"].replace(" 티어표", ""),
        body=f"""
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

            <table>
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

        <script>
        let currentTier = "ALL";

        function filterTier(tier) {{
            currentTier = tier;
            applyFilters();
        }}

        document.getElementById("searchInput").addEventListener("input", applyFilters);

        function applyFilters() {{
            const search = document.getElementById("searchInput").value.toLowerCase();
            const rows = document.querySelectorAll(".tier-row");

            rows.forEach(row => {{
                const tierMatch = currentTier === "ALL" || row.dataset.tier === currentTier;
                const nameMatch = row.dataset.name.includes(search);

                row.style.display = tierMatch && nameMatch ? "" : "none";
            }});
        }}
        </script>
        """
    )

    with open(f"site/{page['output']}", "w", encoding="utf-8") as f:
        f.write(html)


def base_html(title, active, body):
    return f"""
<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<title>{title}</title>

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
    box-shadow: 0 0 25px rgba(0,0,0,0.25);
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
    position: sticky;
    top: 0;
}}

td {{
    padding: 10px;
    border-bottom: 1px solid #334155;
    text-align: center;
}}

tr:hover {{
    background: #1e293b;
}}

.name-cell {{
    display: flex;
    align-items: center;
    gap: 10px;
    text-align: left;
}}

.icon {{
    width: 34px;
    height: 34px;
    border-radius: 8px;
    object-fit: cover;
    background: #020617;
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

.home-grid {{
    display: grid;
    grid-template-columns: repeat(3, 1fr);
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

.home-card h2 {{
    margin-top: 0;
}}

@media (max-width: 900px) {{
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


index_html = base_html(
    title="TFT 통계 홈",
    active="홈",
    body="""
    <div class="home-grid">
        <a class="home-card" href="units.html">
            <h2>기물 티어표</h2>
            <p>기물별 평균 등수, TOP4률, 1등률, 채용률을 확인합니다.</p>
        </a>

        <a class="home-card" href="items.html">
            <h2>아이템 티어표</h2>
            <p>아이템별 성능과 채용률을 확인합니다.</p>
        </a>

        <a class="home-card" href="traits.html">
            <h2>시너지 티어표</h2>
            <p>시너지별 평균 성적과 티어를 확인합니다.</p>
        </a>
    </div>
    """
)

with open("site/index.html", "w", encoding="utf-8") as f:
    f.write(index_html)

for page in PAGES:
    make_table_page(page)

print("사이트 생성 완료!")
print("site/index.html, site/units.html, site/items.html, site/traits.html 생성 완료")