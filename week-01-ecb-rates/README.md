# Week 1: ECB Policy Rates vs. Eurozone Inflation

## Question

How have ECB policy rates and Eurozone inflation moved together (or diverged) since 2000, and how far does the ECB's rate typically lag behind inflation?

## Data

- **ECB Deposit Facility Rate** (daily, %) — FRED series [`ECBDFR`](https://fred.stlouisfed.org/series/ECBDFR)
- **Euro Area HICP, All Items** (monthly, index level) — FRED series [`CP0000EZ19M086NEST`](https://fred.stlouisfed.org/series/CP0000EZ19M086NEST)

Both series are pulled from FRED's public CSV download endpoint (`https://fred.stlouisfed.org/graph/fredgraph.csv?id=<series_id>`), which doesn't require an API key.

Note: `CP0000EZ19M086NEST` is the HICP **index level** (e.g. 103.66), not year-on-year inflation. `analysis.py` calculates year-on-year inflation itself from the index (the % change vs. the same month 12 months earlier).

## Methodology

1. `data_pull.py` downloads both raw series from FRED and saves them to `data/` as CSVs, untouched.
2. `analysis.py`:
   - Resamples the daily policy rate to monthly (rate as of the 1st of each month).
   - Computes year-on-year HICP inflation from the index level (`pct_change(12) * 100`).
   - Merges both series on date (inner join), forward-fills any small gaps, and trims the data to 2000-01-01 onward.
   - Plots both series on one chart with two y-axes and saves it as `chart.png`.
   - Computes a lag statistic: for lags of 0–24 months, it correlates today's policy rate with inflation from that many months earlier, and reports the lag with the strongest correlation.

## Results

- **Lag statistic:** the strongest correlation (0.68) is at an **18-month lag** — today's ECB policy rate lines up most closely with inflation from about a year and a half earlier.
- **Chart:** `chart.png` — ECB Deposit Facility Rate (blue, left axis) vs. Eurozone HICP inflation year-on-year (red, right axis), 2000–present, with a dashed line marking the ECB's 2% inflation target.

## What I learned

Inflation and the policy rate move together, but with a real delay — the ECB doesn't react instantly. The clearest example is 2021–2023: inflation shot up first (peaking near 10% in late 2022), and the ECB didn't start raising rates meaningfully until mid-2022, only catching up to a peak rate in 2023, well after inflation had already started falling. Correlating today's rate against past inflation at different lags is a simple way to estimate that delay (~18 months here) without needing to manually identify every peak and cut by eye.

## Tools

Python 3, `pandas`, `requests`, `matplotlib`.
