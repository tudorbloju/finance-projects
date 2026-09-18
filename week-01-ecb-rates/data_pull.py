"""
data_pull.py

Downloads two raw time series from FRED (the St. Louis Fed's public data
website) and saves them as CSV files. This script does NOT clean or merge
anything -- that happens in analysis.py. Keeping "download" and "process"
separate means we always have the original, untouched data saved locally,
so we can re-run the analysis without hitting the internet again.

Series downloaded:
1. ECBDFR  - ECB Deposit Facility Rate (daily, in %)
2. CP0000EZ19M086NEST - Euro area Harmonised Index of Consumer Prices,
   all items (monthly, index level, NOT year-on-year inflation yet --
   we calculate the year-on-year % change ourselves in analysis.py)
3. 00XFUNEZ19M086NEST - Euro area HICP excluding energy and unprocessed
   food (monthly, index level) -- this is "core inflation", used in
   bonus_analysis.py to see if the ECB reacts differently to core vs.
   headline inflation

Source: FRED (https://fred.stlouisfed.org), series pages:
- https://fred.stlouisfed.org/series/ECBDFR
- https://fred.stlouisfed.org/series/CP0000EZ19M086NEST
- https://fred.stlouisfed.org/series/00XFUNEZ19M086NEST
"""

import requests

# FRED lets you download any series as a CSV directly from this URL pattern,
# without needing an API key. We just swap in the series ID ("id=...").
FRED_CSV_URL = "https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}"

# The two series we need, and the filename we want to save each one as.
SERIES_TO_DOWNLOAD = {
    "ECBDFR": "data/ecb_deposit_rate_raw.csv",
    "CP0000EZ19M086NEST": "data/hicp_index_raw.csv",
    "00XFUNEZ19M086NEST": "data/core_hicp_index_raw.csv",
}


def download_series(series_id: str, output_path: str) -> None:
    """Download one FRED series and save it to output_path as a CSV."""
    url = FRED_CSV_URL.format(series_id=series_id)

    # timeout=30 stops the request from hanging forever if FRED is slow/down
    response = requests.get(url, timeout=30)

    # raise_for_status() throws an error if the download failed (e.g. 404),
    # instead of silently saving an error page as if it were data
    response.raise_for_status()

    with open(output_path, "w") as f:
        f.write(response.text)

    print(f"Saved {series_id} -> {output_path}")


if __name__ == "__main__":
    for series_id, output_path in SERIES_TO_DOWNLOAD.items():
        download_series(series_id, output_path)
