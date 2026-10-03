# 📊 Retail Sales Insights Dashboard

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-app-FF4B4B?logo=streamlit&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-charts-3F4F75?logo=plotly&logoColor=white)

An interactive **Streamlit** dashboard that turns raw retail sales data into clear business insights for managers. You can filter by date, city and category, and every chart, KPI and written insight updates instantly.

## ✨ Features

- **KPI cards:** revenue, orders, average order value and average discount, each with % change against the previous period
- **Monthly revenue trend** with a 3-month moving average
- **Revenue by city** and **category mix** (donut chart)
- **City × category heatmap** that shows where each category sells best
- **Top 10 products** by revenue and units sold
- **Discount impact analysis:** does discounting actually increase order value?
- **Auto-generated "Key insights"** written in plain English from the filtered data
- **Upload your own CSV**, or use the built-in demo dataset (about 27,000 orders across 7 Pakistani cities, 2024–2025)
- **Download** the filtered data as CSV

## 🔎 Sample insights (demo data, all filters)

- **Karachi** is the top city with **PKR 309M** (26% of revenue)
- **Electronics** drives **72%** of revenue, with **Laptops** as the best-selling product
- The **best month was November 2025**, driven by the 11.11 and year-end sales
- Revenue in the last 3 months is **+33%** versus the first 3 months

## 🚀 Run it

```bash
git clone https://github.com/khizercheema78/retail-sales-insights-dashboard.git
cd retail-sales-insights-dashboard
pip install -r requirements.txt
streamlit run app.py
```

The dashboard opens at http://localhost:8501.

### Using your own data

Upload a CSV from the sidebar with these columns:

`order_date, city, category, product, quantity, unit_price, discount, revenue`

## 🧰 Tech stack

Python · Streamlit · Plotly Express · pandas · NumPy

## 🔭 Next steps

- Sales forecasting with Prophet / ARIMA
- Customer cohort and retention analysis
- Deploy on Streamlit Community Cloud
