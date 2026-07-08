import pandas as pd
import json

INPUT = "recommender/comp_dataset_kr.csv"
OUTPUT = "recommender.html"

df = pd.read_csv(INPUT)

data = []
for _, row in df.iterrows():
    data.append({
        "meta_score": float(row.get("stability_score", 0)),
        "units": str(row.get("units_kr", "")),
        "core_units": str(row.get("core_units_kr", "")),
        "core_items": str(row.get("core_items_kr", "")),
        "core_traits": str(row.get("core_traits_kr", "")),
        "main_carry": str(row.get("main_carry_kr", "")),
        "main_tank": str(row.get("main_tank_kr", "")),
        "games": int(row.get("games", 0)),
        "avg_place": float(row.get("avg_place", 0)),
        "top4_rate": float(row.get("top4_rate", 0)),
        "win_rate": float(row.get("win_rate", 0)),
    })

html = f"""
<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<title>TFT 덱 추천기</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<style>
body {{
    margin: 0;
    background: #020617;
    color: #e5e7eb;
    font-family: Arial, sans-serif;
}}
header {{
    padding: 34px;
    text-align: center;
    background: #111827;
}}
main {{
    max-width: 1200px;
    margin: 30px auto;
    padding: 20px;
}}
.card {{
    background: #111827;
    border-radius: 18px;
    padding: 24px;
    margin-bottom: 24px;
}}
textarea {{
    width: 100%;
    padding: 12px;
    border-radius: 10px;
    border: none;
    margin-top: 8px;
    margin-bottom: 16px;
    background: #1f2937;
    color: white;
    font-size: 15px;
}}
button {{
    background: #facc15;
    color: #111827;
    border: none;
    padding: 14px 22px;
    border-radius: 12px;
    font-weight: bold;
    cursor: pointer;
}}
.result {{
    border: 1px solid #374151;
    border-radius: 16px;
    padding: 20px;
    margin-top: 18px;
    background: #020617;
}}
.rank {{
    color: #facc15;
    font-size: 22px;
    font-weight: bold;
}}
.tag {{
    display: inline-block;
    background: #1f2937;
    padding: 6px 10px;
    border-radius: 999px;
    margin: 4px;
}}
table {{
    width: 100%;
    border-collapse: collapse;
    margin-top: 20px;
}}
th, td {{
    border-bottom: 1px solid #334155;
    padding: 10px;
    text-align: center;
}}
th {{
    background: #1e293b;
    color: #facc15;
}}
.chart-box {{
    height: 340px;
    margin-top: 20px;
}}
.progress-bg {{
    background: #1f2937;
    border-radius: 999px;
    overflow: hidden;
    height: 18px;
    margin: 8px 0 16px;
}}
.progress-fill {{
    background: #facc15;
    height: 100%;
}}
.reason-grid {{
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 12px;
    margin-top: 16px;
}}
.reason-box {{
    background: #1f2937;
    border-radius: 14px;
    padding: 14px;
    text-align: center;
}}
.reason-box strong {{
    color: #facc15;
    font-size: 22px;
}}
.small {{
    color: #9ca3af;
}}
</style>
</head>

<body>
<header>
    <h1>TFT 데이터 기반 덱 추천기</h1>
    <p>기물, 아이템, 시너지를 입력하면 실제 경기 데이터를 바탕으로 추천 덱을 계산합니다.</p>
</header>

<main>
    <section class="card">
        <h2>현재 상황 입력</h2>

        <label>보유 기물</label>
        <textarea id="unitsInput" rows="3" placeholder="예: 블리츠크랭크, 쉔, 진"></textarea>

        <label>보유 아이템</label>
        <textarea id="itemsInput" rows="2" placeholder="예: 구인수의 격노검, 라바돈의 죽음모자"></textarea>

        <label>현재 시너지</label>
        <textarea id="traitsInput" rows="2" placeholder="예: 우주 그루브 3, 선봉대 2"></textarea>

        <button onclick="recommendDecks()">추천 받기</button>
    </section>

    <section class="card">
        <h2>추천 점수 그래프</h2>
        <div class="chart-box"><canvas id="scoreChart"></canvas></div>
    </section>

    <section class="card">
        <h2>1위 덱 적합도 분석</h2>
        <div class="chart-box"><canvas id="detailChart"></canvas></div>
    </section>

    <section class="card">
        <h2>덱 비교표</h2>
        <div id="tableArea" class="small">입력 후 추천 받기를 눌러주세요.</div>
    </section>

    <section class="card">
        <h2>상세 추천 결과</h2>
        <div id="results" class="small">입력 후 추천 받기를 눌러주세요.</div>
    </section>
</main>

<script>
const comps = {json.dumps(data, ensure_ascii=False)};
let scoreChart = null;
let detailChart = null;

function splitInput(text) {{
    return text.split(",").map(x => x.trim()).filter(x => x.length > 0);
}}

function splitList(text) {{
    if (!text || text === "nan") return [];
    return text.split(",").map(x => x.trim()).filter(x => x.length > 0);
}}

function matchScore(current, target) {{
    if (target.length === 0) return 0;
    let count = 0;
    for (const x of current) {{
        if (target.includes(x)) count++;
    }}
    return count / target.length * 100;
}}

function progressBar(value) {{
    const safe = Math.max(0, Math.min(100, value));
    return `
        <div class="progress-bg">
            <div class="progress-fill" style="width:${{safe}}%"></div>
        </div>
    `;
}}

function makeItemRecommend(r, currentItems) {{
    if (currentItems.length === 0) return "<p class='small'>입력된 아이템이 없습니다.</p>";

    let carry = r.main_carry || "메인 캐리";
    let tank = r.main_tank || "메인 탱커";

    let html = "";
    currentItems.forEach((item, i) => {{
        const target = i % 2 === 0 ? carry : tank;
        html += `<span class="tag">${{item}} → ${{target}}</span>`;
    }});

    return html;
}}

function makeTraitStatus(r, currentTraits) {{
    const targetTraits = r.traits.slice(0, 6);
    let html = "";

    targetTraits.forEach(t => {{
        const traitName = t.replace(/[0-9]/g, "").trim();
        const matched = currentTraits.some(c => c.includes(traitName));
        html += `<span class="tag">${{matched ? "✅" : "⬜"}} ${{t}}</span>`;
    }});

    return html || "<p class='small'>핵심 시너지 정보가 없습니다.</p>";
}}

function drawCharts(top) {{
    const labels = top.map((_, i) => (i + 1) + "위");

    if (scoreChart) scoreChart.destroy();
    if (detailChart) detailChart.destroy();

    scoreChart = new Chart(document.getElementById("scoreChart"), {{
        type: "bar",
        data: {{
            labels,
            datasets: [{{
                label: "추천 점수",
                data: top.map(x => x.finalScore)
            }}]
        }},
        options: {{
            responsive: true,
            maintainAspectRatio: false,
            scales: {{
                y: {{ beginAtZero: true }}
            }}
        }}
    }});

    const best = top[0];

    detailChart = new Chart(document.getElementById("detailChart"), {{
        type: "bar",
        data: {{
            labels: ["기물", "핵심 기물", "아이템", "시너지", "덱 통계"],
            datasets: [{{
                label: "적합도",
                data: [best.unitScore, best.coreScore, best.itemScore, best.traitScore, best.metaScore]
            }}]
        }},
        options: {{
            responsive: true,
            maintainAspectRatio: false,
            scales: {{
                y: {{ beginAtZero: true, max: 100 }}
            }}
        }}
    }});
}}

function makeTable(top) {{
    let html = `
    <table>
        <thead>
            <tr>
                <th>순위</th>
                <th>추천 점수</th>
                <th>완성도</th>
                <th>메인 캐리</th>
                <th>메인 탱커</th>
                <th>평균 등수</th>
                <th>TOP4률</th>
                <th>1등률</th>
                <th>표본</th>
            </tr>
        </thead>
        <tbody>
    `;

    top.forEach((r, i) => {{
        html += `
        <tr>
            <td>${{i + 1}}위</td>
            <td>${{r.finalScore.toFixed(2)}}</td>
            <td>${{r.completion.toFixed(1)}}%</td>
            <td>${{r.main_carry}}</td>
            <td>${{r.main_tank}}</td>
            <td>${{r.avg_place}}</td>
            <td>${{r.top4_rate}}%</td>
            <td>${{r.win_rate}}%</td>
            <td>${{r.games}}</td>
        </tr>
        `;
    }});

    html += "</tbody></table>";
    return html;
}}

function recommendDecks() {{
    const currentUnits = splitInput(document.getElementById("unitsInput").value);
    const currentItems = splitInput(document.getElementById("itemsInput").value);
    const currentTraits = splitInput(document.getElementById("traitsInput").value);

    const scored = comps.map(comp => {{
        const units = splitList(comp.units);
        const coreUnits = splitList(comp.core_units);
        const items = splitList(comp.core_items);
        const traits = splitList(comp.core_traits);

        const unitScore = matchScore(currentUnits, units);
        const coreScore = matchScore(currentUnits, coreUnits);
        const itemScore = matchScore(currentItems, items);
        const traitScore = matchScore(currentTraits, traits);
        const metaScore = Math.min(comp.meta_score, 220) / 220 * 100;

        const finalScore =
            unitScore * 0.30 +
            coreScore * 0.25 +
            traitScore * 0.20 +
            itemScore * 0.15 +
            metaScore * 0.10;

        const missing = units.filter(u => !currentUnits.includes(u)).slice(0, 6);
        const matched = units.filter(u => currentUnits.includes(u));
        const completion = units.length === 0 ? 0 : matched.length / units.length * 100;

        return {{
            ...comp,
            finalScore,
            units,
            items,
            traits,
            missing,
            matched,
            unitScore,
            coreScore,
            itemScore,
            traitScore,
            metaScore,
            completion
        }};
    }});

    scored.sort((a, b) => b.finalScore - a.finalScore);
    const top = scored.slice(0, 5);

    drawCharts(top);
    document.getElementById("tableArea").innerHTML = makeTable(top);

    const box = document.getElementById("results");
    box.innerHTML = "";

    top.forEach((r, index) => {{
        const div = document.createElement("div");
        div.className = "result";

        div.innerHTML = `
            <div class="rank">${{index + 1}}위 추천 덱 / 점수: ${{r.finalScore.toFixed(2)}}</div>

            <h3>덱 완성도: ${{r.completion.toFixed(1)}}%</h3>
            ${{progressBar(r.completion)}}

            <div class="reason-grid">
                <div class="reason-box"><p>기물</p><strong>${{r.unitScore.toFixed(0)}}%</strong></div>
                <div class="reason-box"><p>핵심 기물</p><strong>${{r.coreScore.toFixed(0)}}%</strong></div>
                <div class="reason-box"><p>아이템</p><strong>${{r.itemScore.toFixed(0)}}%</strong></div>
                <div class="reason-box"><p>시너지</p><strong>${{r.traitScore.toFixed(0)}}%</strong></div>
                <div class="reason-box"><p>통계</p><strong>${{r.metaScore.toFixed(0)}}%</strong></div>
            </div>

            <p><b>메인 캐리:</b> ${{r.main_carry}} / <b>메인 탱커:</b> ${{r.main_tank}}</p>

            <p><b>완성 덱</b></p>
            ${{r.units.map(x => `<span class="tag">${{x}}</span>`).join("")}}

            <p><b>부족한 기물</b></p>
            ${{r.missing.map(x => `<span class="tag">${{x}}</span>`).join("")}}

            <p><b>아이템 착용 추천</b></p>
            ${{makeItemRecommend(r, currentItems)}}

            <p><b>시너지 활성화 현황</b></p>
            ${{makeTraitStatus(r, currentTraits)}}

            <p><b>추천 이유</b></p>
            <ul>
                <li>현재 기물 ${{r.matched.length}}명이 추천 덱과 일치합니다.</li>
                <li>덱 완성도는 ${{r.completion.toFixed(1)}}%입니다.</li>
                <li>아이템 적합도는 ${{r.itemScore.toFixed(1)}}점입니다.</li>
                <li>시너지 적합도는 ${{r.traitScore.toFixed(1)}}점입니다.</li>
                <li>평균 등수 ${{r.avg_place}}, TOP4률 ${{r.top4_rate}}%, 1등률 ${{r.win_rate}}% 데이터를 반영했습니다.</li>
            </ul>
        `;

        box.appendChild(div);
    }});
}}
</script>

</body>
</html>
"""

with open(OUTPUT, "w", encoding="utf-8") as f:
    f.write(html)

print("덱 추천기 사이트 생성 완료!")
print(OUTPUT)