import pandas as pd
import os

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
    user-select: none;
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
    box-shadow: 0 0 30px rgba(0,0,0,0.5);
}}

.modal h2 {{
    margin-top: 0;
}}

.modal p {{
    color: #cbd5e1;
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


def make_table_page(page):
    df = pd.read_csv(page["file"])

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

    html = base_html(
        title=page["title"],
        active=page["active"],
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

            <table id="dataTable">
                <thead>
                    <tr>
                        <th onclick="sortTable(0, 'text')">이름</th>
                        <th onclick="sortTable(1, 'text')">티어</th>
                        <th onclick="sortTable(2, 'number')">게임 수</th>
                        <th onclick="sortTable(3, 'number')">채용률</th>
                        <th onclick="sortTable(4, 'number')">평균 등수</th>
                        <th onclick="sortTable(5, 'number')">TOP4률</th>
                        <th onclick="sortTable(6, 'number')">1등률</th>
                        <th onclick="sortTable(7, 'number')">점수</th>
                    </tr>
                </thead>
                <tbody>
                    {rows}
                </tbody>
            </table>
        </section>

        <div id="modalBg" class="modal-bg" onclick="closeModal()">
            <div class="modal" onclick="event.stopPropagation()">
                <h2 id="modalName"></h2>
                <p id="modalTier"></p>
                <p id="modalGames"></p>
                <p id="modalPick"></p>
                <p id="modalAvg"></p>
                <p id="modalTop4"></p>
                <p id="modalWin"></p>
                <p id="modalScore"></p>
                <button class="close-btn" onclick="closeModal()">닫기</button>
            </div>
        </div>

        <script>
        let currentTier = "ALL";
        let sortDirections = {{}};

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

        function sortTable(colIndex, type) {{
            const table = document.getElementById("dataTable");
            const tbody = table.querySelector("tbody");
            const rows = Array.from(tbody.querySelectorAll("tr"));

            const key = colIndex;
            sortDirections[key] = !sortDirections[key];

            rows.sort((a, b) => {{
                let aText = a.children[colIndex].innerText.replace("%", "").trim();
                let bText = b.children[colIndex].innerText.replace("%", "").trim();

                if (type === "number") {{
                    aText = parseFloat(aText);
                    bText = parseFloat(bText);
                }}

                if (aText < bText) return sortDirections[key] ? -1 : 1;
                if (aText > bText) return sortDirections[key] ? 1 : -1;
                return 0;
            }});

            rows.forEach(row => tbody.appendChild(row));
        }}

        document.querySelectorAll(".tier-row").forEach(row => {{
            row.addEventListener("click", () => {{
                document.getElementById("modalName").innerText = row.dataset.displayName;
                document.getElementById("modalTier").innerText = "티어: " + row.dataset.tier;
                document.getElementById("modalGames").innerText = "게임 수: " + row.dataset.games;
                document.getElementById("modalPick").innerText = "채용률: " + row.dataset.pickRate + "%";
                document.getElementById("modalAvg").innerText = "평균 등수: " + row.dataset.avgPlace;
                document.getElementById("modalTop4").innerText = "TOP4률: " + row.dataset.top4 + "%";
                document.getElementById("modalWin").innerText = "1등률: " + row.dataset.win + "%";
                document.getElementById("modalScore").innerText = "점수: " + row.dataset.score;

                document.getElementById("modalBg").style.display = "flex";
            }});
        }});

        function closeModal() {{
            document.getElementById("modalBg").style.display = "none";
        }}
        </script>
        """
    )

    with open(f"site/{page['output']}", "w", encoding="utf-8") as f:
        f.write(html)


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
        <a class="home-card" href="about.html">
    <h2>프로젝트 소개</h2>
    <p>
        데이터 수집 과정, 분석 방법,
        티어 계산 기준 및 프로젝트 설명을 확인합니다.
    </p>
</a>
    </div>
    """
)

with open("site/index.html", "w", encoding="utf-8") as f:
    f.write(index_html)

for page in PAGES:
    make_table_page(page)

about_html = base_html(
    title="프로젝트 소개",
    active="프로젝트 소개",
    body="""
    <section class="card">

        <h2>📊 프로젝트 소개</h2>

        <p>
        Riot Games API를 이용하여 한국 TFT 챌린저 랭크 데이터를
        수집하고 분석한 프로젝트입니다.
        </p>

        <hr>

        <h2>📈 데이터 규모</h2>

        <div class="home-grid">

            <div class="home-card">
                <h2>4,466</h2>
                <p>수집 경기 수</p>
            </div>

            <div class="home-card">
                <h2>35,539</h2>
                <p>플레이어 데이터</p>
            </div>

            <div class="home-card">
                <h2>3</h2>
                <p>분석 카테고리</p>
            </div>

        </div>

        <hr>

        <h2>🧮 티어 계산 기준</h2>

        <p>
        티어 점수는 다음 데이터를 조합하여 계산했습니다.
        </p>

        <ul>
            <li>평균 등수</li>
            <li>TOP4 확률</li>
            <li>1등 확률</li>
            <li>채용률</li>
        </ul>

        <p>
        성적이 좋고 많은 경기에서 사용된 데이터를
        높은 티어로 평가했습니다.
        </p>

        <hr>

        <h2>📖 표 보는 방법</h2>

        <ul>
            <li>게임 수 : 해당 데이터가 등장한 횟수</li>
            <li>채용률 : 전체 경기 중 사용된 비율</li>
            <li>평균 등수 : 평균 최종 등수</li>
            <li>TOP4률 : 4등 이내 비율</li>
            <li>1등률 : 우승 비율</li>
            <li>점수 : 종합 평가 점수</li>
        </ul>

        <hr>

        <h2>⚙️ 데이터 수집 및 분석 파이프라인</h2>

        <div style="
        background:#020617;
        padding:30px;
        border-radius:20px;
        margin-top:20px;
        ">

        <div style="
        display:flex;
        flex-direction:column;
        align-items:center;
        font-size:22px;
        line-height:2.2;
        ">

        <div>🎮 Riot API</div>
        <div>↓</div>

        <div>🏆 Challenger Summoner 수집</div>
        <div>↓</div>

        <div>🎯 Match ID 수집</div>
        <div>↓</div>

        <div>📁 Match Data 다운로드</div>
        <div>↓</div>

        <div>🧹 Parser 전처리</div>
        <div>↓</div>

        <div>📊 Pandas 통계 분석</div>
        <div>↓</div>

        <div>⭐ 티어 계산</div>
        <div>↓</div>

        <div>🌐 GitHub Pages 웹사이트 생성</div>

        </div>
        </div>

        <hr>

        <h2>📂 생성된 데이터</h2>

        <ul>
            <li>matches.jsonl</li>
            <li>player_dataset.csv</li>
            <li>unit_stats.csv</li>
            <li>item_stats.csv</li>
            <li>trait_stats.csv</li>
            <li>unit_tier.csv</li>
            <li>item_tier.csv</li>
            <li>trait_tier.csv</li>
        </ul>

        <hr>

        <h2>🛠 사용 기술</h2>

        <ul>
            <li>Python</li>
            <li>Pandas</li>
            <li>Riot API</li>
            <li>HTML / CSS / JavaScript</li>
            <li>GitHub Pages</li>
        </ul>

        <hr>

        <h2>👨‍💻 제작자</h2>

        <p>
        엄정훈<br>
        TFT Challenger Data Analysis Project
        </p>

    </section>
    """
)

with open("site/about.html", "w", encoding="utf-8") as f:
    f.write(about_html)

print("사이트 생성 완료!")

about_html = base_html(
    title="프로젝트 소개",
    active="프로젝트 소개",
    body="""
    <section class="card">
        <h2>📊 프로젝트 소개</h2>
        <p>Riot Games API를 이용하여 한국 TFT 챌린저 랭크 데이터를 수집하고 분석한 프로젝트입니다.</p>

        <hr>

        <h2>📈 데이터 규모</h2>
        <ul>
            <li>수집 경기 수: 4,466경기</li>
            <li>플레이어 데이터: 35,539명</li>
            <li>분석 카테고리: 기물, 아이템, 시너지</li>
        </ul>

        <hr>

        <h2>🧮 티어 계산 기준</h2>
        <p>평균 등수, TOP4률, 1등률, 채용률을 조합하여 티어 점수를 계산했습니다.</p>

        <hr>

        <h2>📖 표 보는 방법</h2>
        <ul>
            <li>게임 수: 해당 데이터가 등장한 횟수</li>
            <li>채용률: 전체 데이터 중 사용된 비율</li>
            <li>평균 등수: 평균 최종 등수</li>
            <li>TOP4률: 4등 이내 비율</li>
            <li>1등률: 우승 비율</li>
            <li>점수: 종합 평가 점수</li>
        </ul>

        <hr>

        <h2>⚙️ 데이터 수집 및 분석 파이프라인</h2>
        <pre style="background:#020617; padding:20px; border-radius:15px; color:#facc15;">
Riot API
↓
Challenger Summoner 수집
↓
Match ID 수집
↓
Match Data 다운로드
↓
Parser 전처리
↓
Pandas 통계 분석
↓
티어 계산
↓
GitHub Pages 웹사이트 생성
        </pre>

        <hr>

        <h2>🛠 사용 기술</h2>
        <ul>
            <li>Python</li>
            <li>Pandas</li>
            <li>Riot API</li>
            <li>HTML / CSS / JavaScript</li>
            <li>GitHub Pages</li>
        </ul>
    </section>
    """
)

with open("site/about.html", "w", encoding="utf-8") as f:
    f.write(about_html)

print("about.html 생성 완료!")