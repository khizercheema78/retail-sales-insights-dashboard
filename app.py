"""
Retail Sales Insights Dashboard (Streamlit + Plotly)
----------------------------------------------------
An interactive dashboard that turns raw sales data into business insights:
KPIs, monthly trend, city and category performance, top products,
discount impact and an automatically written "key insights" summary.

Uses a seeded synthetic dataset (2 years, 7 Pakistani cities) generated
on first run, or your own CSV with the same columns.

Run:  streamlit run app.py
"""
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Retail Sales Insights", page_icon="📊", layout="wide")

CITIES = ["Lahore", "Karachi", "Islamabad", "Sialkot", "Faisalabad", "Multan", "Peshawar"]
PRODUCTS = {
    "Electronics": {"Smartphone": 65000, "Earbuds": 6500, "Laptop": 185000, "Smartwatch": 18000},
    "Fashion": {"Kurta": 4500, "Sneakers": 9000, "Lawn Suit": 7500, "Jacket": 12000},
    "Home": {"Air Fryer": 28000, "Bedsheet Set": 6000, "Water Dispenser": 42000, "Lamp": 3500},
    "Beauty": {"Perfume": 8500, "Skincare Kit": 5200, "Hair Dryer": 7800, "Makeup Set": 6400},
}
REQUIRED = ["order_date", "city", "category", "product", "quantity", "unit_price", "discount", "revenue"]


@st.cache_data
def generate_data(seed: int = 11) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    dates = pd.date_range("2024-01-01", "2025-12-31", freq="D")
    rows = []
    for d in dates:
        # Seasonality: Eid / wedding season and 11.11 / year-end sales bumps
        season = 1.0 + 0.35 * (d.month in (3, 4, 6)) + 0.5 * (d.month in (11, 12))
        trend = 1.0 + 0.25 * (d - dates[0]).days / len(dates)
        for _ in range(rng.poisson(28 * season * trend)):
            cat = rng.choice(list(PRODUCTS), p=[0.3, 0.32, 0.2, 0.18])
            prod = rng.choice(list(PRODUCTS[cat]))
            price = PRODUCTS[cat][prod] * rng.uniform(0.9, 1.1)
            qty = int(rng.choice([1, 1, 1, 2, 2, 3]))
            disc = float(rng.choice([0, 0, 0.05, 0.1, 0.15, 0.25]))
            rows.append((d, rng.choice(CITIES, p=[.24, .26, .13, .09, .12, .08, .08]),
                         cat, prod, qty, round(price, 0), disc))
    df = pd.DataFrame(rows, columns=REQUIRED[:-1])
    df["revenue"] = (df["quantity"] * df["unit_price"] * (1 - df["discount"])).round(0)
    return df


def load_data() -> pd.DataFrame:
    up = st.sidebar.file_uploader("Upload your own sales CSV (optional)", type="csv")
    if up is not None:
        df = pd.read_csv(up)
        missing = set(REQUIRED) - set(df.columns)
        if missing:
            st.sidebar.error(f"Missing columns: {', '.join(sorted(missing))}. Using demo data.")
            return generate_data()
        return df
    return generate_data()


def fmt_pkr(x: float) -> str:
    if x >= 1e9:
        return f"PKR {x / 1e9:,.2f}B"
    return f"PKR {x / 1e6:,.1f}M" if x >= 1e6 else f"PKR {x:,.0f}"


df = load_data()
df["order_date"] = pd.to_datetime(df["order_date"])

# ---------------- Sidebar filters ----------------
st.sidebar.header("Filters")
min_d, max_d = df["order_date"].min().date(), df["order_date"].max().date()
date_range = st.sidebar.date_input("Date range", (min_d, max_d), min_value=min_d, max_value=max_d)
cities = st.sidebar.multiselect("City", sorted(df["city"].unique()), default=sorted(df["city"].unique()))
cats = st.sidebar.multiselect("Category", sorted(df["category"].unique()), default=sorted(df["category"].unique()))

start, end = (date_range if len(date_range) == 2 else (min_d, max_d))
f = df[(df["order_date"].dt.date.between(start, end)) & df["city"].isin(cities) & df["category"].isin(cats)]

st.title("📊 Retail Sales Insights Dashboard")
st.caption("Interactive analysis of sales performance across cities, categories and time.")

if f.empty:
    st.warning("No data for the selected filters.")
    st.stop()

# ---------------- KPIs with period-over-period change ----------------
period = (pd.Timestamp(end) - pd.Timestamp(start)).days + 1
prev = df[(df["order_date"] >= pd.Timestamp(start) - pd.Timedelta(days=period))
          & (df["order_date"] < pd.Timestamp(start))
          & df["city"].isin(cities) & df["category"].isin(cats)]


def delta(cur, old):
    return f"{(cur - old) / old:+.1%}" if old else None


c1, c2, c3, c4 = st.columns(4)
rev, orders = f["revenue"].sum(), len(f)
c1.metric("Revenue", fmt_pkr(rev), delta(rev, prev["revenue"].sum()))
c2.metric("Orders", f"{orders:,}", delta(orders, len(prev)))
c3.metric("Avg order value", fmt_pkr(rev / orders), delta(rev / orders, prev["revenue"].sum() / max(len(prev), 1)))
c4.metric("Avg discount", f"{f['discount'].mean():.1%}")

# ---------------- Trend ----------------
monthly = f.set_index("order_date").resample("MS")["revenue"].sum().reset_index()
monthly["3-month avg"] = monthly["revenue"].rolling(3, min_periods=1).mean()
fig = px.line(monthly, x="order_date", y=["revenue", "3-month avg"], markers=True,
              title="Monthly revenue trend", labels={"value": "Revenue (PKR)", "order_date": ""})
st.plotly_chart(fig, width="stretch")

# ---------------- City & category ----------------
left, right = st.columns(2)
by_city = f.groupby("city", as_index=False)["revenue"].sum().sort_values("revenue")
left.plotly_chart(px.bar(by_city, x="revenue", y="city", orientation="h", title="Revenue by city"),
                  width="stretch")
by_cat = f.groupby("category", as_index=False)["revenue"].sum()
right.plotly_chart(px.pie(by_cat, names="category", values="revenue", hole=0.5, title="Category mix"),
                   width="stretch")

# ---------------- Heatmap & top products ----------------
left, right = st.columns(2)
heat = f.pivot_table(index="city", columns="category", values="revenue", aggfunc="sum")
left.plotly_chart(px.imshow(heat, text_auto=".2s", aspect="auto", color_continuous_scale="Blues",
                            title="City × category revenue"), width="stretch")
top = (f.groupby("product", as_index=False).agg(revenue=("revenue", "sum"), units=("quantity", "sum"))
       .sort_values("revenue", ascending=False).head(10))
right.plotly_chart(px.bar(top, x="product", y="revenue", hover_data=["units"], title="Top 10 products"),
                   width="stretch")

# ---------------- Discount impact ----------------
disc = f.groupby("discount", as_index=False).agg(orders=("revenue", "size"), avg_units=("quantity", "mean"),
                                                avg_order_value=("revenue", "mean"))
disc["discount"] = (disc["discount"] * 100).astype(int).astype(str) + "%"
st.plotly_chart(px.bar(disc, x="discount", y="avg_order_value", color="avg_units",
                       title="Does discounting pay off? Avg order value by discount level"),
                width="stretch")

# ---------------- Auto-generated insights ----------------
st.subheader("🔎 Key insights")
best_city = by_city.iloc[-1]
best_cat = by_cat.sort_values("revenue").iloc[-1]
best_month = monthly.loc[monthly["revenue"].idxmax()]
growth = (monthly["revenue"].iloc[-3:].mean() / monthly["revenue"].iloc[:3].mean() - 1) if len(monthly) >= 6 else None
insights = [
    f"**{best_city.city}** is the top city with {fmt_pkr(best_city.revenue)} "
    f"({best_city.revenue / rev:.0%} of revenue).",
    f"**{best_cat.category}** leads the category mix at {best_cat.revenue / rev:.0%} of revenue.",
    f"The best month was **{best_month.order_date:%B %Y}** ({fmt_pkr(best_month.revenue)}).",
    f"**{top.iloc[0]['product']}** is the best-selling product by revenue.",
]
if growth is not None:
    insights.append(f"Revenue in the last 3 months is **{growth:+.0%}** versus the first 3 months of the period.")
for line in insights:
    st.markdown(f"- {line}")

with st.expander("View filtered data"):
    st.dataframe(f.sort_values("order_date", ascending=False), width="stretch")
    st.download_button("Download CSV", f.to_csv(index=False), "filtered_sales.csv", "text/csv")
