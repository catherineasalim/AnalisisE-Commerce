import os

import folium
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import numpy as np
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="E-Commerce Dashboard", page_icon="🛒", layout="wide")

# ------------------------------------------------------------------ style
HIGHLIGHT = "#2a78d6"
ACCENT = "#eb6834"
MUTED = "#c9c8c2"
TEXT = "#52514e"
GRID = "#ececea"

plt.rcParams.update({
    "figure.facecolor": "white", "axes.facecolor": "white",
    "axes.spines.top": False, "axes.spines.right": False, "axes.spines.left": False,
    "axes.edgecolor": "#d6d6d2", "axes.titleweight": "bold", "axes.titlesize": 12,
    "axes.titlecolor": "#1f2937", "axes.titlepad": 12, "axes.labelcolor": TEXT, "axes.labelsize": 10,
    "xtick.color": TEXT, "ytick.color": TEXT, "xtick.labelsize": 9, "ytick.labelsize": 9,
    "ytick.left": False, "font.size": 10,
})

st.markdown("""
<style>
.block-container {padding-top: 3.4rem; padding-bottom: 2rem; max-width: 1300px;}

.hero {
    background: linear-gradient(120deg, #1d5fae 0%, #2a78d6 55%, #4b93e6 100%);
    border-radius: 18px; padding: 26px 32px; color: white; margin-bottom: 1.4rem;
    box-shadow: 0 6px 18px rgba(42, 120, 214, .18);
}
.hero h1 {color: white; font-size: 1.85rem; font-weight: 700; margin: 0 0 4px 0; padding: 0;}
.hero p {color: rgba(255,255,255,.88); margin: 0; font-size: .95rem;}
.hero .chip {
    display: inline-block; background: rgba(255,255,255,.18); border-radius: 999px;
    padding: 3px 12px; margin: 12px 6px 0 0; font-size: .8rem; color: white;
}

[data-testid="stMetric"] {
    background: #ffffff; border: 1px solid #e7e9ee; border-radius: 14px;
    padding: 16px 20px; box-shadow: 0 1px 3px rgba(16, 24, 40, .06);
    min-height: 124px; display: flex; flex-direction: column; justify-content: center;
}
[data-testid="stMetricLabel"] p {font-size: .82rem; color: #6b7280; font-weight: 600;}
[data-testid="stMetricValue"] {font-size: 1.65rem; font-weight: 700; color: #1f2937;}

.stTabs [data-baseweb="tab-list"] {gap: 6px; border-bottom: 1px solid #e7e9ee;}
.stTabs [data-baseweb="tab"] {padding: 10px 16px; border-radius: 10px 10px 0 0; font-weight: 600;}

.section-title {font-size: 1.15rem; font-weight: 700; color: #1f2937; margin: .6rem 0 .2rem 0;}
.section-sub {font-size: .88rem; color: #6b7280; margin-bottom: .8rem;}

[data-testid="stSidebar"] {background: #f5f7fa; border-right: 1px solid #e7e9ee;}
footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


def brl(x, pos=None):
    if abs(x) >= 1e6:
        return f"R$ {x/1e6:.1f} jt"
    if abs(x) >= 1e3:
        return f"R$ {x/1e3:.0f} rb"
    return f"R$ {x:.0f}"


def section(title, subtitle=""):
    st.markdown(f"<div class='section-title'>{title}</div>"
                + (f"<div class='section-sub'>{subtitle}</div>" if subtitle else ""), unsafe_allow_html=True)


def show(fig):
    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)


# ------------------------------------------------------------------ data helpers
@st.cache_data
def load_data():
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "main_data.csv")
    df = pd.read_csv(path, parse_dates=["order_purchase_timestamp", "order_delivered_customer_date",
                                        "order_estimated_delivery_date"])
    return df


def create_monthly_df(df):
    monthly = (df.resample("ME", on="order_purchase_timestamp")
               .agg(order_count=("order_id", "nunique"), revenue=("price", "sum")))
    monthly.index = monthly.index.strftime("%Y-%m")
    return monthly


def create_category_df(df):
    cat = (df.groupby("product_category")
           .agg(revenue=("price", "sum"), items_sold=("order_item_id", "count"))
           .sort_values("revenue", ascending=False))
    cat["share_%"] = cat["revenue"] / cat["revenue"].sum() * 100
    return cat


def create_order_level_df(df):
    return df.drop_duplicates("order_id")


def create_state_df(order_df, df):
    state = (order_df.groupby("customer_state")
             .agg(order_count=("order_id", "nunique"), late_rate=("is_late", "mean"),
                  avg_delivery_days=("delivery_days", "mean"), avg_review=("review_score", "mean"),
                  lat=("lat", "median"), lng=("lng", "median")))
    state["late_rate"] *= 100
    state["revenue"] = df.groupby("customer_state")["price"].sum()
    return state.sort_values("late_rate", ascending=False)


def create_rfm_df(df):
    snapshot = df["order_purchase_timestamp"].max() + pd.Timedelta(days=1)
    rfm = (df.groupby("customer_unique_id")
           .agg(last_purchase=("order_purchase_timestamp", "max"),
                frequency=("order_id", "nunique"), monetary=("price", "sum")))
    rfm["recency"] = (snapshot - rfm["last_purchase"]).dt.days
    rfm["R_score"] = pd.qcut(rfm["recency"].rank(method="first"), 5, labels=[5, 4, 3, 2, 1]).astype(int)
    rfm["M_score"] = pd.qcut(rfm["monetary"].rank(method="first"), 5, labels=[1, 2, 3, 4, 5]).astype(int)
    rfm["F_score"] = pd.cut(rfm["frequency"], bins=[0, 1, 2, np.inf], labels=[1, 3, 5]).astype(int)

    conditions = [
        (rfm["F_score"] >= 3) & (rfm["R_score"] >= 4),
        rfm["F_score"] >= 3,
        (rfm["R_score"] >= 4) & (rfm["M_score"] >= 4),
        rfm["R_score"] >= 4,
        (rfm["R_score"] <= 2) & (rfm["M_score"] >= 4),
        rfm["R_score"] <= 2,
    ]
    choices = ["Champions", "Loyal Customers", "New Big Spenders", "New Customers",
               "At Risk (High Value)", "Hibernating"]
    rfm["segment"] = np.select(conditions, choices, default="Need Attention")
    return rfm


# ------------------------------------------------------------------ sidebar
all_df = load_data()
min_date = all_df["order_purchase_timestamp"].min().date()
max_date = all_df["order_purchase_timestamp"].max().date()

with st.sidebar:
    st.markdown("## 🛒 Olist E-Commerce")
    st.caption("Pesanan *delivered*, Jan 2017 – Agu 2018")
    st.divider()
    date_range = st.date_input("Rentang waktu pembelian", value=[min_date, max_date],
                               min_value=min_date, max_value=max_date)
    states = sorted(all_df["customer_state"].dropna().unique())
    selected_states = st.multiselect("Negara bagian (state) pelanggan", states,
                                     placeholder="Semua state")
    

if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date, end_date = min_date, max_date

main_df = all_df[(all_df["order_purchase_timestamp"].dt.date >= start_date) &
                 (all_df["order_purchase_timestamp"].dt.date <= end_date)]
if selected_states:
    main_df = main_df[main_df["customer_state"].isin(selected_states)]

if main_df.empty:
    st.warning("Tidak ada data untuk filter yang dipilih. Silakan ubah rentang waktu atau state.")
    st.stop()

order_df = create_order_level_df(main_df)

# ------------------------------------------------------------------ header & KPI
state_label = ", ".join(selected_states) if selected_states else "Seluruh state"
st.markdown(f"""
<div class="hero">
  <h1>Dashboard Analisis E-Commerce Brasil</h1>
  <p>Ringkasan penjualan, kategori produk, pengiriman, dan segmentasi pelanggan Olist.</p>
  <span class="chip">📅 {start_date:%d %b %Y} – {end_date:%d %b %Y}</span>
  <span class="chip">📍 {state_label}</span>
</div>
""", unsafe_allow_html=True)

k1, k2, k3, k4 = st.columns(4)
k1.metric("🧾 Total pesanan", f"{order_df['order_id'].nunique():,}")
k2.metric("💰 Revenue", f"R$ {main_df['price'].sum():,.0f}")
k3.metric("⭐ Rata-rata Skor Review", f"{order_df['review_score'].mean():.2f} / 5")
k4.metric("⏱️ Pesanan terlambat", f"{order_df['is_late'].mean()*100:.1f}%")

st.write("")
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📈 Tren Penjualan", "📦 Kategori Produk",
                                        "🚚 Pengiriman & Kepuasan", "👥 Segmentasi RFM", "🗺️ Peta"])

# ------------------------------------------------------------------ tab 1: trend (Pertanyaan 1)
with tab1:
    monthly = create_monthly_df(main_df)
    ytd = main_df[main_df["order_purchase_timestamp"].dt.month <= 8].groupby(
        main_df["order_purchase_timestamp"].dt.year)["price"].sum()

    c1, c2, c3 = st.columns(3)
    if {2017, 2018}.issubset(ytd.index) and ytd[2017] > 0:
        growth = (ytd[2018] / ytd[2017] - 1) * 100
        c1.metric("Revenue Jan–Agu 2017", brl(ytd[2017]))
        c2.metric("Revenue Jan–Agu 2018", brl(ytd[2018]), f"{growth:+.1f}% YoY")
    else:
        c1.metric("Revenue Jan–Agu 2017", "–")
        c2.metric("Revenue Jan–Agu 2018", "–")
    c3.metric("Bulan dengan revenue tertinggi", monthly["revenue"].idxmax())

    with st.container(border=True):
        h1, h2 = st.columns([3, 2])
        with h1:
            section("Tren jumlah pesanan & revenue bulanan")
        with h2:
            metric = st.radio("Tampilkan", ["Revenue", "Jumlah pesanan"], horizontal=True,
                              label_visibility="collapsed")
        col = "revenue" if metric == "Revenue" else "order_count"
        y = monthly[col].values
        x = np.arange(len(monthly))
        peak = int(y.argmax())

        fig, ax = plt.subplots(figsize=(12, 4.2))
        ax.fill_between(x, y, color=HIGHLIGHT, alpha=0.08)
        ax.plot(x, y, color=HIGHLIGHT, linewidth=2.2, marker="o", markersize=4)
        ax.scatter(x[peak], y[peak], s=90, color=ACCENT, zorder=3, edgecolor="white", linewidth=2)
        label = brl(y[peak]) if col == "revenue" else f"{y[peak]:,.0f} pesanan"
        ax.annotate(f"Puncak {monthly.index[peak]}\n{label}", (x[peak], y[peak]), xytext=(10, -5),
                    textcoords="offset points", fontsize=9, color=TEXT)
        ax.set_xticks(x)
        ax.set_xticklabels(monthly.index, rotation=45, ha="right")
        ax.set_ylim(0, y.max() * 1.2)
        ax.yaxis.set_major_formatter(mtick.FuncFormatter(brl) if col == "revenue"
                                     else mtick.StrMethodFormatter("{x:,.0f}"))
        ax.set_ylabel(metric)
        ax.grid(axis="y", color=GRID)
        show(fig)

    st.info("💡 Revenue memuncak pada November 2017 (Black Friday) lalu mendatar sepanjang 2018 — "
            "siapkan kapasitas puncak November dan promo untuk memecah *plateau*.")

# ------------------------------------------------------------------ tab 2: category (Pertanyaan 2)
with tab2:
    cat = create_category_df(main_df)

    c1, c2 = st.columns([1, 2])
    with c2:
        with st.container(border=True, height=124):
            n = st.slider("Jumlah kategori ditampilkan", 5, 15, 10)
    with c1:
        st.metric(f"Kontribusi {n} kategori teratas thd revenue",
                  f"{cat['share_%'].head(n).sum():.1f}%")

    section("Kategori produk dengan revenue terbesar & terkecil")
    c1, c2 = st.columns(2)
    fig_h = 0.42 * n + 1.6

    with c1:
        with st.container(border=True):
            top = cat.head(n).iloc[::-1]
            fig, ax = plt.subplots(figsize=(6, fig_h))
            colors = [MUTED] * (n - 3) + [HIGHLIGHT] * 3
            ax.barh(top.index, top["revenue"], color=colors[-len(top):], height=0.65)
            for i, (v, s) in enumerate(zip(top["revenue"], top["share_%"])):
                ax.text(v, i, f"  {brl(v)} ({s:.1f}%)", va="center", fontsize=9, color=TEXT)
            ax.set_xlim(0, top["revenue"].max() * 1.5)
            ax.xaxis.set_major_formatter(mtick.FuncFormatter(brl))
            ax.xaxis.set_major_locator(mtick.MaxNLocator(4))
            ax.set_title(f"{n} kategori teratas", loc="left")
            ax.set_xlabel("Revenue (BRL)")
            ax.grid(axis="x", color=GRID)
            ax.set_axisbelow(True)
            show(fig)

    with c2:
        with st.container(border=True):
            bottom = cat.tail(n).iloc[::-1]
            fig, ax = plt.subplots(figsize=(6, fig_h))
            ax.barh(bottom.index, bottom["revenue"], color=ACCENT, height=0.65)
            for i, (v, q) in enumerate(zip(bottom["revenue"], bottom["items_sold"])):
                ax.text(v, i, f"  R$ {v:,.0f} ({q} item)", va="center", fontsize=9, color=TEXT)
            ax.set_xlim(0, bottom["revenue"].max() * 1.6)
            ax.xaxis.set_major_locator(mtick.MaxNLocator(4))
            ax.set_title(f"{n} kategori terbawah", loc="left")
            ax.set_xlabel("Revenue (BRL)")
            ax.grid(axis="x", color=GRID)
            ax.set_axisbelow(True)
            show(fig)

# ------------------------------------------------------------------ tab 3: delivery (Pertanyaan 3)
with tab3:
    lr = order_df.groupby("is_late")["review_score"].mean()
    lr.index = lr.index.map({False: "Tepat waktu", True: "Terlambat"})
    state = create_state_df(order_df, main_df)
    overall = order_df["is_late"].mean() * 100

    c1, c2 = st.columns([1, 2])
    with c2:
        with st.container(border=True, height=124):
            min_orders = st.slider("Minimal jumlah pesanan per state", 0, 1000, 300, step=50)
    with c1:
        st.metric("Rata-rata nasional pesanan terlambat", f"{overall:.1f}%")

    section("Dampak keterlambatan pengiriman terhadap skor review")
    c1, c2 = st.columns(2)
    with c1:
        with st.container(border=True):
            fig, ax = plt.subplots(figsize=(6, 4.6))
            bar_colors = [HIGHLIGHT if i == "Tepat waktu" else ACCENT for i in lr.index]
            bars = ax.bar(lr.index, lr.values, color=bar_colors, width=0.5)
            for b, v in zip(bars, lr.values):
                ax.text(b.get_x() + b.get_width() / 2, v + 0.06, f"{v:.2f}", ha="center",
                        fontweight="bold", fontsize=12, color=TEXT)
            ax.set_ylim(0, 5)
            ax.set_ylabel("Rata-rata skor review (1–5)")
            ax.set_title("Rata-rata skor review", loc="left")
            ax.grid(axis="y", color=GRID)
            ax.set_axisbelow(True)
            show(fig)

    with c2:
        with st.container(border=True):
            st_top = state[state["order_count"] >= min_orders].head(10).iloc[::-1]
            if st_top.empty:
                st.write("Tidak ada state yang memenuhi batas minimal pesanan.")
            else:
                fig, ax = plt.subplots(figsize=(6, 4.6))
                ax.barh(st_top.index, st_top["late_rate"], color=ACCENT, height=0.65)
                ax.axvline(overall, color=TEXT, linestyle="--", linewidth=1)
                ax.text(overall, len(st_top) - 0.4, f" rata-rata {overall:.1f}%", fontsize=9, color=TEXT)
                for i, (v, d) in enumerate(zip(st_top["late_rate"], st_top["avg_delivery_days"])):
                    ax.text(v, i, f"  {v:.1f}% (±{d:.0f} hari)", va="center", fontsize=9, color=TEXT)
                ax.set_xlim(0, st_top["late_rate"].max() * 1.5)
                ax.xaxis.set_major_formatter(mtick.PercentFormatter())
                ax.set_title("Top 10 state dengan Pesanan terlambat Tertinggi", loc="left")
                ax.set_xlabel("Persentase pesanan terlambat")
                show(fig)

    with st.container(border=True):
        section("Binning Lama Pengiriman vs Skor Review")
        bins = [0, 7, 14, 21, 30, np.inf]
        labels = ["≤7 hari", "8–14 hari", "15–21 hari", "22–30 hari", ">30 hari"]
        tmp = order_df.assign(delivery_bin=pd.cut(order_df["delivery_days"], bins=bins, labels=labels))
        bin_sum = tmp.groupby("delivery_bin", observed=False).agg(
            avg_review=("review_score", "mean"), orders=("order_id", "nunique"))
        fig, ax = plt.subplots(figsize=(12, 3.8))
        colors = [HIGHLIGHT, HIGHLIGHT, MUTED, ACCENT, ACCENT]
        bars = ax.bar(bin_sum.index.astype(str), bin_sum["avg_review"].fillna(0), color=colors, width=0.55)
        for b, v, o in zip(bars, bin_sum["avg_review"], bin_sum["orders"]):
            if pd.notna(v):
                ax.text(b.get_x() + b.get_width() / 2, v + 0.06, f"{v:.2f}  ({o:,} pesanan)", ha="center",
                        fontsize=9, color=TEXT)
        ax.set_ylim(0, 5)
        ax.set_ylabel("Rata-rata skor review")
        ax.set_xlabel("Lama pengiriman")
        ax.grid(axis="y", color=GRID)
        ax.set_axisbelow(True)
        show(fig)

# ------------------------------------------------------------------ tab 4: RFM
with tab4:
    rfm = create_rfm_df(main_df)
    c1, c2, c3 = st.columns(3)
    c1.metric("Rata-rata recency", f"{rfm['recency'].mean():.0f} hari")
    c2.metric("Rata-rata frequency", f"{rfm['frequency'].mean():.2f} pesanan")
    c3.metric("Rata-rata monetary", f"R$ {rfm['monetary'].mean():,.2f}")

    with st.container(border=True):
        section("Segmentasi pelanggan dengan RFM Analysis", "Biru = segmen prioritas retensi")
        seg = (rfm.groupby("segment").agg(customers=("recency", "size"), avg_monetary=("monetary", "mean"))
               .sort_values("customers"))
        seg["pct"] = seg["customers"] / seg["customers"].sum() * 100
        priority = {"At Risk (High Value)", "Champions", "Loyal Customers"}
        fig, ax = plt.subplots(figsize=(12, 4.4))
        ax.barh(seg.index, seg["customers"], color=[HIGHLIGHT if s in priority else MUTED for s in seg.index],
                height=0.65)
        for i, (nn, p, m) in enumerate(zip(seg["customers"], seg["pct"], seg["avg_monetary"])):
            ax.text(nn, i, f"  {nn:,} ({p:.1f}%) · rata-rata R$ {m:,.0f}", va="center", fontsize=9, color=TEXT)
        ax.set_xlim(0, seg["customers"].max() * 1.6)
        ax.set_xlabel("Jumlah pelanggan")
        ax.grid(axis="x", color=GRID)
        ax.set_axisbelow(True)
        show(fig)

    with st.container(border=True):
        section("10 pelanggan dengan monetary tertinggi")
                
        st.dataframe(rfm.sort_values("monetary", ascending=False).head(10)[
                    ["recency", "frequency", "monetary", "R_score", "F_score", "M_score", "segment"]].round(2),
                    height=318,
                    use_container_width=True
            )
    
        
        

# ------------------------------------------------------------------ tab 5: map
with tab5:
    state = create_state_df(order_df, main_df).dropna(subset=["lat", "lng"])
    overall = order_df["is_late"].mean() * 100

    with st.container(border=True):
        section(
            "Revenue & keterlambatan per state",
            f"Ukuran lingkaran = revenue ·\n"
            f"🟠 Keterlambatan di atas rata-rata · "
            f"🔵 Di bawah/sama dengan rata-rata"
        )
        m = folium.Map(location=[-14.5, -52], zoom_start=4, tiles="Esri.WorldGrayCanvas")
        max_rev = state["revenue"].max()
        for name, r in state.iterrows():
            color = ACCENT if r["late_rate"] > overall else HIGHLIGHT
            folium.CircleMarker(
                location=[r["lat"], r["lng"]], radius=5 + 30 * np.sqrt(r["revenue"] / max_rev),
                color=color, fill=True, fill_color=color, fill_opacity=0.55, weight=1,
                tooltip=(f"<b>{name}</b><br>Revenue: R$ {r['revenue']:,.0f}<br>Pesanan: {r['order_count']:,}<br>"
                         f"Terlambat: {r['late_rate']:.1f}%<br>Rata-rata kirim: {r['avg_delivery_days']:.1f} hari<br>"
                         f"Skor review: {r['avg_review']:.2f}"),
            ).add_to(m)
        map_html = m.get_root().render()
        if hasattr(st, "iframe"):          # Streamlit versi baru
            st.iframe(map_html, height=520)
        else:                              # Streamlit versi lama
            components.html(map_html, height=520)

    with st.container(border=True):
        section("Ringkasan per state")
        st.dataframe(state[["order_count", "revenue", "late_rate", "avg_delivery_days", "avg_review"]]
                     .sort_values("revenue", ascending=False).round(2))

st.divider()
