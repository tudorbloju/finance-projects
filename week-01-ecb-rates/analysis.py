"""
analysis.py

Takes the raw CSVs saved by data_pull.py and:
1. Cleans them (parses dates, resamples to a common monthly frequency)
2. Merges them into one dataframe on date
3. Plots both series on one chart (two y-axes) and saves it as chart.png
4. Calculates one lag statistic: which lag (in months) gives the strongest
   correlation between inflation and the policy rate
5. Prints a plain-language summary of what the numbers show

Run this after data_pull.py.
"""

import pandas as pd
import matplotlib.pyplot as plt

RAW_RATE_PATH = "data/ecb_deposit_rate_raw.csv"
RAW_HICP_PATH = "data/hicp_index_raw.csv"
CLEAN_DATA_PATH = "data/ecb_rates_and_inflation.csv"
CHART_PATH = "chart.png"

# We only look at data from this date onward, per the project brief
# ("since around 2000"). Earlier data exists but is patchier.
COMMON_START_DATE = "2000-01-01"


def load_and_clean_data() -> pd.DataFrame:
    """Load the two raw CSVs, clean them, and merge into one dataframe."""

    # --- ECB Deposit Facility Rate ---------------------------------------
    # This series is published daily (the rate is repeated every calendar
    # day until the ECB changes it). We only need one value per month, so
    # we "resample" it down to monthly: for each calendar month, keep the
    # rate as of the first day of that month.
    rate = pd.read_csv(RAW_RATE_PATH, parse_dates=["observation_date"])
    rate = rate.set_index("observation_date").rename(columns={"ECBDFR": "policy_rate"})
    rate = rate.resample("MS").first()  # "MS" = Month Start frequency

    # --- Euro area HICP (inflation) ---------------------------------------
    # This FRED series is the HICP INDEX LEVEL (e.g. 100.42), not inflation
    # itself. Year-on-year inflation is "how much higher is the index than
    # it was 12 months ago, in percent". pct_change(12) does exactly that:
    # it compares each row to the row 12 months earlier.
    hicp = pd.read_csv(RAW_HICP_PATH, parse_dates=["observation_date"])
    hicp = hicp.set_index("observation_date").rename(
        columns={"CP0000EZ19M086NEST": "hicp_index"}
    )
    hicp["inflation_yoy"] = hicp["hicp_index"].pct_change(12) * 100

    # --- Merge on date ------------------------------------------------
    # join() lines up the two dataframes by their date index. "inner" only
    # keeps dates present in both series, which naturally drops the leading
    # rows of HICP that have no inflation value yet (first 12 months) and
    # any dates one series has that the other doesn't.
    df = rate.join(hicp[["inflation_yoy"]], how="inner")

    # Any remaining gaps (e.g. a single missing month) are filled by
    # carrying the last known value forward -- reasonable for both a
    # policy rate (unchanged until the ECB acts) and inflation (we assume
    # no data means "no reported change").
    df = df.asfreq("MS").ffill()

    # Trim to our common start date and drop any rows still missing data
    df = df.loc[COMMON_START_DATE:].dropna()

    return df


def plot_chart(df: pd.DataFrame) -> None:
    """Plot policy rate and inflation on one chart with two y-axes."""

    fig, ax_rate = plt.subplots(figsize=(11, 6))

    # Left axis: policy rate
    ax_rate.plot(df.index, df["policy_rate"], color="tab:blue", label="ECB Deposit Facility Rate")
    ax_rate.set_ylabel("Policy rate (%)", color="tab:blue")
    ax_rate.tick_params(axis="y", labelcolor="tab:blue")
    ax_rate.set_xlabel("Year")

    # twinx() creates a second y-axis that shares the same x-axis (dates),
    # which is how we get two different scales on one chart.
    ax_inflation = ax_rate.twinx()
    ax_inflation.plot(df.index, df["inflation_yoy"], color="tab:red", label="HICP Inflation (YoY)")
    ax_inflation.set_ylabel("Inflation, year-on-year (%)", color="tab:red")
    ax_inflation.tick_params(axis="y", labelcolor="tab:red")

    # ECB's inflation target line, for visual reference
    ax_inflation.axhline(2.0, color="gray", linestyle="--", linewidth=1, alpha=0.6)

    # Each axis tracks its own line's label separately, so to get one combined
    # legend we grab the handles/labels from both axes and merge them here.
    lines_rate, labels_rate = ax_rate.get_legend_handles_labels()
    lines_inflation, labels_inflation = ax_inflation.get_legend_handles_labels()
    ax_rate.legend(lines_rate + lines_inflation, labels_rate + labels_inflation, loc="upper left")

    plt.title("ECB Policy Rate vs. Eurozone Inflation (2000-present)")
    fig.tight_layout()
    fig.savefig(CHART_PATH, dpi=150)
    print(f"Saved chart -> {CHART_PATH}")


def compute_lag_statistic(df: pd.DataFrame) -> int:
    """
    Find which lag (in months) gives the strongest correlation between
    TODAY's policy rate and PAST inflation.

    The idea: the ECB sets rates in response to inflation it has already
    seen, and it takes time for a rate decision to happen and show up in
    the data. So we ask: "is today's rate more correlated with inflation
    from 1 month ago? 6 months ago? 18 months ago?" -- and see which lag
    fits best. That best-fitting lag is our estimate of how far behind
    the ECB's rate trails inflation.
    """
    best_lag = None
    best_corr = -2  # correlation is always between -1 and 1, so -2 is a safe starting point

    for lag in range(0, 25):  # test lags of 0 to 24 months
        # shift(lag) moves each inflation value forward by `lag` months, so
        # shifted_inflation[t] = inflation_yoy[t - lag] ("what inflation was
        # `lag` months before this row"). Correlating that with today's
        # policy rate checks how well past inflation predicts today's rate.
        shifted_inflation = df["inflation_yoy"].shift(lag)
        correlation = df["policy_rate"].corr(shifted_inflation)

        if correlation > best_corr:
            best_corr = correlation
            best_lag = lag

    print(f"\nStrongest correlation is at an {best_lag}-month lag (correlation = {best_corr:.2f})")
    print(f"This means today's policy rate lines up most closely with inflation from {best_lag} months earlier --")
    print("a rough estimate of how long it takes the ECB's rate to catch up with inflation.")

    return best_lag


if __name__ == "__main__":
    data = load_and_clean_data()
    data.to_csv(CLEAN_DATA_PATH)
    print(f"Saved cleaned, merged data -> {CLEAN_DATA_PATH} ({len(data)} monthly rows)")

    plot_chart(data)
    compute_lag_statistic(data)
