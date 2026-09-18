# Week 1: ECB Policy Rates vs. Eurozone Inflation

## Question

Do ECB policy rates and Eurozone inflation move together since 2000? And how big is the delay between them?

## Data

- ECB Deposit Facility Rate (daily, %): FRED series [`ECBDFR`](https://fred.stlouisfed.org/series/ECBDFR)
- Euro Area HICP, all items (monthly, index level): FRED series [`CP0000EZ19M086NEST`](https://fred.stlouisfed.org/series/CP0000EZ19M086NEST)
- Euro Area HICP excluding food and energy, i.e. "core" inflation (monthly, index level): FRED series [`00XFUNEZ19M086NEST`](https://fred.stlouisfed.org/series/00XFUNEZ19M086NEST), used in the bonus analysis

All three come from FRED's public CSV download link, no API key needed.

Note: the two HICP series are index levels, not inflation rates. The scripts calculate year-on-year inflation themselves from the index.

## Methodology

1. `data_pull.py` downloads the three raw series and saves them to `data/`, untouched.
2. `analysis.py` cleans and merges the rate and headline inflation, plots them in `chart.png`, and finds the lag (0 to 24 months) where the two series correlate most strongly. It also has a `--end-year` flag to rerun the analysis using only data up to a chosen year.
3. `bonus_analysis.py` goes further:
   - Plots the full correlation curve across all lags, not just the best one.
   - Splits the data into three ECB eras (pre-2008, the 2008-2014 crisis years, and 2014 onward) and checks the lag in each.
   - Compares core inflation against headline inflation.

## Results

- Full history: the strongest correlation (0.68) is at an 18-month lag. Today's rate lines up best with inflation from about a year and a half earlier.
- `chart.png`: rate and inflation plotted together since 2000, with the ECB's 2% target marked.
- `lag_correlation_curve.png`: correlation rises from 0.27 at lag 0 up to 0.68 at 18 months, then falls. That confirms 18 months is a real peak, not a fluke.
- `era_comparison.png`: the relationship changes a lot by era.
  - Pre-2008: weak, best lag close to 0 months (correlation 0.36)
  - 2008-2014 crisis years: weak, and turns negative at longer lags (down to about -0.83). The ECB was cutting rates because of the crisis, not because of inflation.
  - 2014 onward: strong, best lag 17 months (correlation 0.89)
- `core_vs_headline.png`: core inflation's best lag is shorter (12 months, correlation 0.74) than headline's (17 months, correlation 0.70). The ECB seems to track core inflation a bit faster.

## What I learned

The rate and inflation move together, but with a real delay. The clearest example is 2021-2023: inflation shot up first, peaking near 10% in late 2022, and the ECB didn't really start hiking until mid-2022, only reaching its peak rate in 2023.

The 18-month number sounds like a fixed rule, but it isn't. Splitting the data by era shows the relationship was weak before 2014. The strong result is mostly driven by the recent cycle, especially the 2022 inflation shock. So the honest conclusion isn't "the ECB always takes 18 months to react." It's "in the current cycle, the ECB's rate has tracked inflation from about 18 months earlier, much more closely than in past cycles."

## Tools

Python 3, pandas, requests, matplotlib.
