import pandas as pd
import json
import shutil
import re

PAGES = [
    ("units.html", "unit_tier_kr.csv", "unit_kr", "기물"),
    ("items.html", "item_tier_kr.csv", "item_kr", "아이템"),
    ("traits.html", "trait_tier_kr.csv", "trait_kr", "시너지"),
]

def make_chart_block(csv_file, name_col, title):
    df = pd.read_csv(csv_file)

    pick = df.sort_values("pick_rate", ascending=False).head(15)
    avg = df.sort_values("avg_place", ascending=True).head(15)
    win = df.sort_values("win_rate", ascending=False).head(15)
    scatter = df[df["games"] >= 100]

    data = {
        "pickLabels": pick[name_col].tolist(),
        "pickValues": pick["pick_rate"].tolist(),
        "avgLabels": avg[name_col].tolist(),
        "avgValues": avg["avg_place"].tolist(),
        "winLabels": win[name_col].tolist(),
        "winValues": win["win_rate"].tolist(),
        "scatterValues": [
            {
                "x": float(row["pick_rate"]),
                "y": float(row["avg_place"]),
                "name": str(row[name_col])
            }
            for _, row in scatter.iterrows()
        ],
        "maxPick": float(pick["pick_rate"].max()) + 10,
        "maxWin": float(win["win_rate"].max()) + 10
    }

    return f"""
<!-- CHARTS_START -->
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

<style>
.chart-grid {{
    display: grid;
    grid-template-columns: 1fr;
    gap: 32px;
    margin-bottom: 40px;
}}

.chart-card {{
    background: #111827;
    padding: 24px;
    border-radius: 18px;
}}

.chart-card h2 {{
    color: #facc15;
}}

.chart-box {{
    position: relative;
    height: 720px;
    width: 100%;
}}

.scatter-box {{
    position: relative;
    height: 560px;
    width: 100%;
}}
</style>

<div class="chart-grid">
    <div class="chart-card">
        <h2>{title} 채용률 TOP 15</h2>
        <div class="chart-box">
            <canvas id="pickChart"></canvas>
        </div>
    </div>

    <div class="chart-card">
        <h2>{title} 평균 등수 TOP 15</h2>
        <div class="chart-box">
            <canvas id="avgChart"></canvas>
        </div>
    </div>

    <div class="chart-card">
        <h2>{title} 승률 TOP 15</h2>
        <div class="chart-box">
            <canvas id="winChart"></canvas>
        </div>
    </div>

    <div class="chart-card">
        <h2>{title} 채용률 vs 평균 등수</h2>
        <div class="scatter-box">
            <canvas id="scatterChart"></canvas>
        </div>
    </div>
</div>

<script>
const chartData = {json.dumps(data, ensure_ascii=False)};

new Chart(document.getElementById("pickChart"), {{
    type: "bar",
    data: {{
        labels: chartData.pickLabels,
        datasets: [{{
            label: "채용률 (%)",
            data: chartData.pickValues
        }}]
    }},
    options: {{
        responsive: true,
        maintainAspectRatio: false,
        indexAxis: "y",
        scales: {{
            x: {{
                beginAtZero: true,
                suggestedMax: chartData.maxPick,
                title: {{
                    display: true,
                    text: "채용률 (%)"
                }}
            }},
            y: {{
                ticks: {{
                    autoSkip: false
                }}
            }}
        }}
    }}
}});

new Chart(document.getElementById("avgChart"), {{
    type: "bar",
    data: {{
        labels: chartData.avgLabels,
        datasets: [{{
            label: "평균 등수",
            data: chartData.avgValues
        }}]
    }},
    options: {{
        responsive: true,
        maintainAspectRatio: false,
        indexAxis: "y",
        scales: {{
            x: {{
                beginAtZero: true,
                suggestedMax: 8,
                title: {{
                    display: true,
                    text: "평균 등수"
                }}
            }},
            y: {{
                ticks: {{
                    autoSkip: false
                }}
            }}
        }}
    }}
}});

new Chart(document.getElementById("winChart"), {{
    type: "bar",
    data: {{
        labels: chartData.winLabels,
        datasets: [{{
            label: "1등률 (%)",
            data: chartData.winValues
        }}]
    }},
    options: {{
        responsive: true,
        maintainAspectRatio: false,
        indexAxis: "y",
        scales: {{
            x: {{
                beginAtZero: true,
                suggestedMax: chartData.maxWin,
                title: {{
                    display: true,
                    text: "1등률 (%)"
                }}
            }},
            y: {{
                ticks: {{
                    autoSkip: false
                }}
            }}
        }}
    }}
}});

new Chart(document.getElementById("scatterChart"), {{
    type: "scatter",
    data: {{
        datasets: [{{
            label: "채용률 vs 평균 등수",
            data: chartData.scatterValues
        }}]
    }},
    options: {{
        responsive: true,
        maintainAspectRatio: false,
        parsing: false,
        plugins: {{
            tooltip: {{
                callbacks: {{
                    label: function(context) {{
                        const p = context.raw;
                        return p.name + " / 채용률: " + p.x + "% / 평균 등수: " + p.y;
                    }}
                }}
            }}
        }},
        scales: {{
            x: {{
                beginAtZero: true,
                title: {{
                    display: true,
                    text: "채용률 (%)"
                }}
            }},
            y: {{
                beginAtZero: true,
                suggestedMax: 8,
                title: {{
                    display: true,
                    text: "평균 등수"
                }}
            }}
        }}
    }}
}});
</script>
<!-- CHARTS_END -->
"""

for html_file, csv_file, name_col, title in PAGES:
    path = "site/" + html_file

    with open(path, "r", encoding="utf-8") as f:
        html = f.read()

    html = re.sub(
        r"<!-- CHARTS_START -->.*?<!-- CHARTS_END -->",
        "",
        html,
        flags=re.DOTALL
    )

    chart_block = make_chart_block(csv_file, name_col, title)

    html = html.replace("<main>", "<main>\n" + chart_block)

    with open(path, "w", encoding="utf-8") as f:
        f.write(html)

    shutil.copy(path, html_file)

print("그래프 재삽입 완료!")