# Task 3: builds dashboard_preview.png and dashboard.pdf from cleaned_data.csv
import pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mp

df = pd.read_csv("cleaned_data.csv", parse_dates=["order_date"])
BG, CARD, TX, MU = "#f4f6fa", "#ffffff", "#1b2430", "#667085"
BLUE, ORG, GRN, PUR, RED = "#2f6fdd", "#f08a24", "#2e9d6b", "#8e5bd6", "#d64f5e"

fig = plt.figure(figsize=(14, 11), facecolor=BG)
gs = fig.add_gridspec(4, 4, height_ratios=[0.55, 1.2, 1.2, 1.2], hspace=0.55, wspace=0.5,
                      left=0.10, right=0.97, top=0.88, bottom=0.05)
fig.text(0.10, 0.945, "Sales Dashboard 2025", fontsize=24, fontweight="bold", color=TX)
fig.text(0.10, 0.915, "200 orders · 7 cities · 5 products · Jan–Dec 2025", fontsize=12, color=MU)

# KPI cards
kpis = [("TOTAL REVENUE", f"₹{df.amount.sum()/1e5:.1f}L", BLUE),
        ("ORDERS", f"{len(df)}", GRN),
        ("AVG ORDER VALUE", f"₹{df.amount.mean():,.0f}", ORG),
        ("AVG RATING", f"{df.rating.mean():.2f} / 5", PUR)]
for i, (t, v, c) in enumerate(kpis):
    ax = fig.add_subplot(gs[0, i]); ax.axis("off")
    ax.add_patch(mp.FancyBboxPatch((0, 0), 1, 1, boxstyle="round,pad=0.0,rounding_size=0.08",
                 fc=CARD, ec="#e3e8ef", transform=ax.transAxes))
    ax.add_patch(mp.Rectangle((0, 0.05), 0.02, 0.9, fc=c, transform=ax.transAxes))
    ax.text(0.08, 0.68, t, fontsize=10, color=MU, fontweight="bold", transform=ax.transAxes)
    ax.text(0.08, 0.2, v, fontsize=22, color=TX, fontweight="bold", transform=ax.transAxes)

def card(ax, title):
    ax.set_facecolor(CARD)
    for s in ax.spines.values(): s.set_color("#e3e8ef")
    ax.set_title(title, fontsize=11, loc="left", color=MU, fontweight="bold")
    ax.tick_params(colors=MU, labelsize=9)

# Monthly revenue
m = df.groupby(df.order_date.dt.month).amount.sum() / 1e5
ax = fig.add_subplot(gs[1, :]); card(ax, "MONTHLY REVENUE (₹ LAKH)")
ax.plot(["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"], m.values, marker="o", color=BLUE, lw=2.5)
ax.fill_between(range(12), m.values, alpha=0.12, color=BLUE); ax.grid(alpha=.25)
for i in (m.idxmax()-1, m.idxmin()-1):
    ax.annotate(f"{m.values[i]:.1f}", (i, m.values[i]), textcoords="offset points", xytext=(0, 8), ha="center", fontsize=9, color=TX)

# Product revenue / city revenue
p = (df.groupby("product").amount.sum() / 1e5).sort_values()
ax = fig.add_subplot(gs[2, :2]); card(ax, "REVENUE BY PRODUCT (₹ LAKH)")
ax.barh(p.index, p.values, color=BLUE); ax.bar_label(ax.containers[0], fmt="%.1f", padding=3, fontsize=9)
c = (df.groupby("city").amount.sum() / 1e5).sort_values()
ax = fig.add_subplot(gs[2, 2:]); card(ax, "REVENUE BY CITY (₹ LAKH)")
ax.barh(c.index, c.values, color=GRN); ax.bar_label(ax.containers[0], fmt="%.1f", padding=3, fontsize=9)

# Rating by product, payment share, age group
r = df.groupby("product").rating.mean().sort_values()
ax = fig.add_subplot(gs[3, :2]); card(ax, "AVG RATING BY PRODUCT")
ax.barh(r.index, r.values, color=[RED if v < 3 else ORG for v in r.values]); ax.set_xlim(0, 5)
ax.bar_label(ax.containers[0], fmt="%.1f", padding=3, fontsize=9)
pm = df.payment_method.value_counts()
ax = fig.add_subplot(gs[3, 2]); card(ax, "PAYMENT METHODS")
ax.pie(pm, labels=pm.index, autopct="%1.0f%%", startangle=90, textprops={"fontsize": 8},
       colors=[BLUE, ORG, GRN, PUR]); 
ag = df.groupby(pd.cut(df.age, [17, 30, 45, 60, 70], labels=["18-30", "31-45", "46-60", "61+"]), observed=True).amount.mean() / 1e3
ax = fig.add_subplot(gs[3, 3]); card(ax, "AVG ORDER BY AGE (₹K)")
ax.bar(ag.index.astype(str), ag.values, color=PUR); ax.bar_label(ax.containers[0], fmt="%.0f", padding=2, fontsize=9); ax.set_ylim(0, 52)

fig.savefig("dashboard_preview.png", dpi=130, facecolor=BG)
fig.savefig("dashboard.pdf", facecolor=BG)
print("saved")
