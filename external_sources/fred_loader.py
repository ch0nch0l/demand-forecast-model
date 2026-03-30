from scripts import data_normalization
import requests
import pandas as pd

def load_fred_series(series_id, api_key):

    # TODO: Update start & End date
    url = f"https://api.stlouisfed.org/fred/series/observations"
    params = {
        "series_id": series_id,
        "api_key": api_key,
        "file_type": "json",
        "observation_start": "2021-01-01",
        "observation_end": "2024-12-31",
        "frequency": "m"
    }

    response = requests.get(url, params=params)
    data = response.json()

    if 'observations' not in data:
        raise KeyError("FRED API response missing 'observations' key")

    df = pd.DataFrame(data['observations'])
    df['Order_Month'] = pd.to_datetime(df['date'])
    df['Value'] = pd.to_numeric(df['value'], errors='coerce')

    df_monthly = data_normalization.resample_external(df, date_col='Order_Month', value_cols=['Value'])
    df_monthly.rename(columns={'Value': f"{series_id}_Value"}, inplace=True)
    return df_monthly