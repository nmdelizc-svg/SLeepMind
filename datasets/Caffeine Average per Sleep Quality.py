import pandas as pd
import matplotlib.pyplot as plt

# ==========================
# LOAD DATA
# ==========================
df = pd.read_csv("combined_external_sleepmind.csv")

# ==========================
# PREPARE DATA
# ==========================
# Group by sleep_quality and calculate mean caffeine
caffeine_means = df.groupby("sleep_quality")["caffeine"].mean().sort_values()

# ==========================
# SLEEPMIND STYLE FUNCTION
# ==========================
def sleepmind_style(ax, title):
    ax.set_facecolor("#0E0F23")
    ax.figure.set_facecolor("#0E0F23")

    for spine in ax.spines.values():
        spine.set_color("#29D3D3")

    ax.tick_params(colors="white", labelsize=11)
    ax.title.set_color("#29D3D3")
    ax.xaxis.label.set_color("#F5F5F5")
    ax.yaxis.label.set_color("#F5F5F5")
    ax.grid(True, linestyle="--", alpha=0.25)
    ax.set_title(title, fontsize=18, pad=15)

# ==========================
# BAR CHART
# ==========================
fig, ax = plt.subplots(figsize=(9, 6))

bars = ax.bar(
    caffeine_means.index,
    caffeine_means.values,
    color="#29D3D3",
    edgecolor="white",
    linewidth=1.5
)

# Labels
ax.set_xlabel("Sleep Quality Category")
ax.set_ylabel("Average Caffeine Level")
sleepmind_style(ax, "Average Caffeine Consumption per Sleep Quality")

# Add values above bars
for bar in bars:
    height = bar.get_height()
    ax.text(
        bar.get_x() + bar.get_width()/2,
        height + 0.1,
        f"{height:.1f}",
        ha="center",
        va="bottom",
        color="white",
        fontsize=12
    )

plt.tight_layout()
plt.show()
