# 🏅 Tokyo 2021 Olympics — Medal Efficiency Dashboard

> **Which countries _truly_ won the Olympics?**  
> Beyond raw medal counts, this project reveals which nations punched above their weight — analyzing medal efficiency against athletes sent, population, and GDP.

![Python](https://img.shields.io/badge/Python-3.9+-3776AB?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.30+-FF4B4B?logo=streamlit&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-5.0+-3F4F75?logo=plotly&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)

---

## 🎯 The Problem

Traditional Olympic medal tables reward countries that send the most athletes. The USA topped Tokyo 2021 with 113 medals — but they also sent 600+ athletes. Meanwhile, smaller nations like Bermuda and San Marino won medals with tiny delegations.

**This project asks:** If we normalize for team size, population, and economic power, who are the _real_ champions?

---

## 📊 Key Metrics

| Metric | What It Reveals |
|--------|----------------|
| **Medals per Athlete** | How efficiently a country converts athletes into medals |
| **Medals per Million Population** | Which small nations punch above their weight |
| **Medals per $B GDP** | Whether richer countries are simply "buying" medals |
| **Weighted Medal Score** | Gold-weighted performance (Gold=3, Silver=2, Bronze=1) |
| **Gold Percentage** | Dominance — what share of a country's medals are gold |

---

## 🖥️ Dashboard Features

- **Key Findings** — Auto-generated narrative insights that update with filters
- **Traditional vs Efficiency** — Side-by-side comparison showing how rankings flip
- **Interactive Scatter Plots** — Explore athletes vs medals with bubble size = population
- **Efficiency Rankings** — Switchable metric with top 15 horizontal bar chart
- **Efficiency Matrix** — Two-dimensional scatter (per-capita vs per-GDP) with quadrant analysis
- **Country Deep Dive** — Select any country for detailed metrics, rankings, and medal donut chart
- **Country Comparison** — Radar chart comparing 2-3 countries across all efficiency metrics
- **Medal Treemap** — Hierarchical view colored by efficiency
- **Downloadable Data** — Export filtered dataset as CSV

---

## 🗂️ Project Structure

```
├── Tokyo_Olympics_2021_Medal_Efficiency_Project.ipynb   # Full analysis notebook
├── dashboard.py                                         # Streamlit dashboard
├── olympics_final_analysis.csv                          # Cleaned & enriched dataset
├── requirements.txt                                     # Python dependencies
├── test_project.py                                      # Data validation tests
├── data/                                                # Original datasets
│   ├── Athletes.csv
│   ├── Coaches.csv
│   ├── EntriesGender.csv
│   ├── Medals.csv
│   └── Teams.csv
└── README.md
```

---

## 🔧 Setup & Installation

**1. Clone the repository**
```bash
git clone https://github.com/Hrish52/Tokyo-Olympics-2021-Analytics.git
cd Tokyo-Olympics-2021-Analytics
```

**2. Install dependencies**
```bash
pip install -r requirements.txt
```

**3. Run the dashboard**
```bash
streamlit run dashboard.py
```

The dashboard opens at `http://localhost:8501`

---

## 📓 Analysis Notebook

The Jupyter notebook walks through the full analysis pipeline:

| Phase | Description |
|-------|-------------|
| **Phase 1** | Data loading & exploration — understanding 5 datasets across 11,000+ athletes |
| **Phase 2** | Data cleaning & merging — standardizing country names via ISO codes, joining GDP & population data from World Bank |
| **Phase 3** | Feature engineering — calculating efficiency metrics, weighted scores, country/GDP categories |
| **Phase 4** | Dashboard development — building the interactive Streamlit app with Plotly |
| **Phase 5** | Testing — data validation, metric sanity checks, edge cases, dashboard readiness |

---

## 📈 Data Sources

| Dataset | Source |
|---------|--------|
| Olympics (Athletes, Coaches, Medals, Teams, EntriesGender) | [Tokyo 2021 Olympics Dataset](https://github.com/Hrish52/Tokyo-Olympics-2021-Analytics/tree/main/Data) |
| GDP (2021) | [World Bank GDP Data](https://raw.githubusercontent.com/datasets/gdp/master/data/gdp.csv) |
| Population (2021) | [World Bank Population Data](https://raw.githubusercontent.com/datasets/population/master/data/population.csv) |
| Cuba, Venezuela, Taiwan | IMF World Economic Outlook & UN Population Estimates |

---

## 💡 Key Findings

- **The USA** topped the medal table with 113 medals but drops significantly in per-athlete efficiency — team size does most of the heavy lifting
- **Small nations** like Bermuda, San Marino, and Grenada rank among the highest in per-capita efficiency
- **Jamaica** converts roughly 1 in every 12 athletes into a medallist — far above the global average
- **The efficiency leaderboard** looks nothing like the traditional medal table — proving that raw counts hide the real story

---

## 🛠️ Tech Stack

- **Python 3.9+** — Core language
- **Pandas** — Data manipulation & cleaning
- **Plotly** — Interactive visualizations
- **Streamlit** — Dashboard framework

---

## 📜 License

This project is open source under the [MIT License](LICENSE).

---

<p align="center">
  <b>Built as a data analytics portfolio project</b><br>
  <em>Exploring what "winning" really means at the Olympics</em>
</p>
