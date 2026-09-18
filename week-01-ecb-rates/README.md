# Week 1: ECB Policy Rates vs. Eurozone Inflation

## Question

How have ECB policy rates and Eurozone inflation moved together (or diverged) since 2000, and how far does the ECB's rate typically lag behind inflation?

## Data

- **ECB Deposit Facility Rate** (daily, %) — FRED series [`ECBDFR`](https://fred.stlouisfed.org/series/ECBDFR)
- **Euro Area HICP, All Items** (monthly, index level) — FRED series [`CP0000EZ19M086NEST`](https://fred.stlouisfed.org/series/CP0000EZ19M086NEST)
- **Euro Area HICP, excluding energy and unprocessed food** ("core" inflation, monthly, index level) — FRED series [`00XFUNEZ19M086NEST`](https://fred.stlouisfed.org/series/00XFUNEZ19M086NEST), used in the bonus analysis

All three series are pulled from FRED's public CSV download endpoint (`https://fred.stlouisfed.org/graph/fredgraph.csv?id=<series_id>`), which doesn't require an API key.

Note: both HICP series are **index levels** (e.g. 103.66), not year-on-year inflation. The scripts calculate year-on-year inflation themselves from the index (the % change vs. the same month 12 months earlier).

## Methodology

1. `data_pull.py` downloads all three raw series from FRED and saves them to `data/` as CSVs, untouched.
2. `analysis.py`:
   - Resamples the daily policy rate to monthly (rate as of the 1st of each month).
   - Computes year-on-year HICP inflation from the index level (`pct_change(12) * 100`).
   - Merges both series on date (inner join), forward-fills any small gaps, and trims the data to 2000-01-01 onward.
   - Plots both series on one chart with two y-axes and saves it as `chart.png`.
   - Computes a lag statistic: for lags of 0–24 months, it correlates today's policy rate with inflation from that many months earlier, and reports the lag with the strongest correlation.
   - Supports an optional `--end-year` flag to re-run the same analysis using only data up to a past year (saved separately under `experiments/`, gitignored), to test how stable the finding is over time.
3. `bonus_analysis.py` digs deeper into the same question three ways:
   - Plots the **full correlation-by-lag curve** (0–24 months), not just the single best lag, to show the actual shape behind the headline number.
   - **Splits the data into three ECB eras** (pre-2008 crisis, the 2008–2014 financial/debt-crisis period, and the negative-rate era from mid-2014 onward) and computes the lag curve separately for each, to check whether the relationship is stable across very different monetary regimes.
   - Compares the lag curve for **core inflation** (excluding food & energy) against **headline inflation**, since the ECB pays close attention to core as a less noisy signal.

## Results

- **Lag statistic (full history):** the strongest correlation (0.68) is at an **18-month lag** — today's ECB policy rate lines up most closely with inflation from about a year and a half earlier.
- **Chart:** `chart.png` — ECB Deposit Facility Rate (blue, left axis) vs. Eurozone HICP inflation year-on-year (red, right axis), 2000–present, with a dashed line marking the ECB's 2% inflation target.
- **Full lag curve:** `lag_correlation_curve.png` — correlation rises smoothly from 0.27 at lag 0 to a peak of 0.68 at 18 months, then falls off, confirming 18 months is a genuine peak and not a coincidence of the search range.
- **By ECB era:** `era_comparison.png` — the relationship is *not* stable across eras:
  - Pre-2008 crisis: weak, best lag ≈ 0 months (correlation 0.36)
  - 2008–2014 financial/debt-crisis era: weak and **negative** at longer lags (correlation drops to about **-0.83** by 24 months) — the ECB was cutting rates during this period *despite* still-elevated past inflation, because crisis response dominated over inflation targeting
  - 2014–present (negative-rate era onward): a strong, clean relationship, best lag ≈ 17 months (correlation **0.89**)
- **Core vs. headline inflation:** `core_vs_headline.png` — core inflation's best lag is shorter (12 months, correlation 0.74) than headline's (17 months, correlation 0.70), suggesting the ECB's rate tracks the less noisy core measure slightly faster than the more volatile headline figure.

## What I learned

Inflation and the policy rate move together, but with a real delay — the ECB doesn't react instantly. The clearest example is 2021–2023: inflation shot up first (peaking near 10% in late 2022), and the ECB didn't start raising rates meaningfully until mid-2022, only catching up to a peak rate in 2023, well after inflation had already started falling. Correlating today's rate against past inflation at different lags is a simple way to estimate that delay (~18 months here) without needing to manually identify every peak and cut by eye.

The single "18-month lag" headline number is convenient, but it hides a lot: splitting the data by era shows this relationship has actually changed dramatically over time. Before 2008 and during the 2008–2014 crisis years, the rate barely tracked past inflation at all — the ECB was reacting mostly to the financial and sovereign debt crises, not inflation. The strong 18-month relationship in the full-history number is really being driven by the 2014-onward period, and especially by the 2022 inflation shock. So the honest takeaway isn't "the ECB always takes 18 months to react to inflation" — it's "in the current monetary regime, and especially around the recent inflation shock, the ECB's rate has tracked inflation from about a year and a half earlier, much more closely than in prior eras."

## Tools

Python 3, `pandas`, `requests`, `matplotlib`.
