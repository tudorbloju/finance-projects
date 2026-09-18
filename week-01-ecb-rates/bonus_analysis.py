"""
bonus_analysis.py

Three extra analyses that build on analysis.py, to dig deeper than the
single "18-month lag" headline number:

1. The full correlation-by-lag curve -- analysis.py only reports the single
   BEST lag, which hides the fact that correlation rises and falls smoothly
   around it. Plotting the whole curve shows that shape.
2. Splitting the analysis by ECB era -- the 2000-present relationship is
   really three very different monetary policy periods stitched together
   (pre-2008 crisis, the low/zero-rate 2008-2014 period, and the
   negative-then-hiking 2014-present period). Computing the lag statistic
   separately for each era shows whether "18 months" is a stable fact or
   an average masking very different behavior.
3. Core inflation vs. headline inflation -- the ECB pays close attention to
   "core" inflation (excluding food and energy, which are volatile for
   reasons that have nothing to do with monetary policy). This checks
   whether the rate lines up differently with core vs. headline inflation.

Run this after data_pull.py and analysis.py. It reuses load_and_clean_data()
and correlation_by_lag() from analysis.py rather than re-implementing the
same cleaning logic twice.
"""

import pandas as pd
import matplotlib.pyplot as plt

from analysis import (
    COMMON_START_DATE,
    load_and_clean_data,
    correlation_by_lag,
)

RAW_CORE_HICP_PATH = "data/core_hicp_index_raw.csv"

LAG_CURVE_CHART_PATH = "lag_correlation_curve.png"
ERA_CHART_PATH = "era_comparison.png"
CORE_VS_HEADLINE_CHART_PATH = "core_vs_headline.png"

# ECB policy eras, used to split the data for part 2.
# - "Pre-2008 crisis": the ECB's first decade, rates moved in a fairly
#   normal range (1%-4.75%).
# - "2008-2014": the financial crisis and Eurozone debt crisis years, rates
#   fell toward zero.
# - "2014-present": the ECB's negative-rate era begins (June 2014) and later
#   the 2022-2023 hiking cycle.
ERAS = {
    "Pre-2008 crisis (2000-2008)": (COMMON_START_DATE, "2008-08-31"),
    "Financial crisis era (2008-2014)": ("2008-09-01", "2014-05-31"),
    "Negative-rate era onward (2014-present)": ("2014-06-01", None),
}


def plot_lag_curve(df: pd.DataFrame) -> None:
    """Part 1: plot the full correlation-by-lag curve, not just the peak."""
    correlations = correlation_by_lag(df["policy_rate"], df["inflation_yoy"])
    best_lag = correlations.idxmax()

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(correlations.index, correlations.values, color="tab:purple", marker="o", markersize=3)

    # Mark the peak (the single number analysis.py reports) on the curve
    ax.scatter([best_lag], [correlations[best_lag]], color="black", zorder=5)
    ax.annotate(
        f"peak: {best_lag} months",
        xy=(best_lag, correlations[best_lag]),
        xytext=(best_lag + 1, correlations[best_lag] - 0.05),
    )

    ax.set_xlabel("Lag (months)")
    ax.set_ylabel("Correlation between policy rate and inflation N months earlier")
    ax.set_title("Correlation by Lag -- Full Curve (2000-present)")
    ax.axhline(0, color="gray", linewidth=0.8)
    fig.tight_layout()
    fig.savefig(LAG_CURVE_CHART_PATH, dpi=150)
    plt.close(fig)
    print(f"Saved chart -> {LAG_CURVE_CHART_PATH}")


def plot_era_comparison(df: pd.DataFrame) -> None:
    """Part 2: compute and plot the lag curve separately for each ECB era."""
    fig, ax = plt.subplots(figsize=(9, 5))

    print("\n--- Lag statistic by ECB era ---")
    for era_name, (start, end) in ERAS.items():
        era_df = df.loc[start:end] if end else df.loc[start:]

        correlations = correlation_by_lag(era_df["policy_rate"], era_df["inflation_yoy"])
        best_lag = correlations.idxmax()
        best_corr = correlations.max()
        print(f"{era_name}: best lag = {best_lag} months (correlation = {best_corr:.2f}, n={len(era_df)} months)")

        ax.plot(correlations.index, correlations.values, marker="o", markersize=3, label=era_name)

    ax.set_xlabel("Lag (months)")
    ax.set_ylabel("Correlation between policy rate and inflation N months earlier")
    ax.set_title("Correlation by Lag, Split by ECB Era")
    ax.axhline(0, color="gray", linewidth=0.8)
    ax.legend()
    fig.tight_layout()
    fig.savefig(ERA_CHART_PATH, dpi=150)
    plt.close(fig)
    print(f"Saved chart -> {ERA_CHART_PATH}")


def load_core_inflation() -> pd.Series:
    """Load the core HICP index and convert it to year-on-year inflation,
    the same way analysis.py does for headline HICP."""
    core = pd.read_csv(RAW_CORE_HICP_PATH, parse_dates=["observation_date"])
    core = core.set_index("observation_date").rename(columns={"00XFUNEZ19M086NEST": "core_hicp_index"})
    core["core_inflation_yoy"] = core["core_hicp_index"].pct_change(12) * 100
    return core["core_inflation_yoy"]


def plot_core_vs_headline(df: pd.DataFrame) -> None:
    """Part 3: compare the lag curve for core inflation vs. headline inflation."""
    core_inflation = load_core_inflation()

    # Add core inflation as a column, aligned by date to the existing dataframe.
    # Core HICP starts a year later than headline HICP, so this join drops
    # a few more early months than analysis.py's headline-only dataframe --
    # that's why headline's best lag here may differ slightly (e.g. 17 vs.
    # 18 months) from what analysis.py reports: same data, marginally
    # different date range.
    combined = df.join(core_inflation, how="inner").dropna()
    print(f"(Using {len(combined)} months common to both series, {combined.index.min().date()} to {combined.index.max().date()})")

    headline_correlations = correlation_by_lag(combined["policy_rate"], combined["inflation_yoy"])
    core_correlations = correlation_by_lag(combined["policy_rate"], combined["core_inflation_yoy"])

    headline_best_lag = headline_correlations.idxmax()
    core_best_lag = core_correlations.idxmax()

    print("\n--- Headline vs. core inflation ---")
    print(f"Headline inflation: best lag = {headline_best_lag} months (correlation = {headline_correlations.max():.2f})")
    print(f"Core inflation:     best lag = {core_best_lag} months (correlation = {core_correlations.max():.2f})")

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(headline_correlations.index, headline_correlations.values, color="tab:red", marker="o", markersize=3, label="Headline HICP inflation")
    ax.plot(core_correlations.index, core_correlations.values, color="tab:orange", marker="o", markersize=3, label="Core HICP inflation (ex. food & energy)")
    ax.set_xlabel("Lag (months)")
    ax.set_ylabel("Correlation between policy rate and inflation N months earlier")
    ax.set_title("Correlation by Lag: Core vs. Headline Inflation (2000-present)")
    ax.axhline(0, color="gray", linewidth=0.8)
    ax.legend()
    fig.tight_layout()
    fig.savefig(CORE_VS_HEADLINE_CHART_PATH, dpi=150)
    plt.close(fig)
    print(f"Saved chart -> {CORE_VS_HEADLINE_CHART_PATH}")


if __name__ == "__main__":
    data = load_and_clean_data()  # full history, same cleaning as analysis.py

    plot_lag_curve(data)
    plot_era_comparison(data)
    plot_core_vs_headline(data)
