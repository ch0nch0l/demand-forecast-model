import pandas as pd
import eurostat as es
from scripts import data_normalization  # import resample_external

def load_electricity_price(start_year=2015, end_year=2025):
    """
    Fetches and preprocesses Eurostat electricity price index data for Finland.
    Handles duplicate months before resampling.
    """

    filter_pars = {'StartPeriod': start_year, 'EndPeriod': end_year, 'currency': 'EUR', 'geo': ['FI']}
    df_raw = es.get_data_df('NRG_PC_205', filter_pars=filter_pars)

    df_melted = df_raw.melt(
        id_vars=['freq', 'product', 'nrg_cons', 'unit', 'tax', 'currency', 'geo\\TIME_PERIOD'],
        var_name='Half_Year',
        value_name='Price'
    )

    def parse_half_year(hy):
        try:
            year, part = hy.split('-')
            month = '01' if part.upper() == 'S1' else '07'
            return pd.to_datetime(f"{year}-{month}")
        except:
            return pd.NaT

    df_melted['Order_Month'] = df_melted['Half_Year'].apply(parse_half_year)
    df_filtered = df_melted[df_melted['tax'] == 'I_TAX'].copy()
    df_filtered['Price'] = pd.to_numeric(df_filtered['Price'], errors='coerce')

    # Keep only relevant columns and drop NaT
    df_filtered = df_filtered[['Order_Month', 'Price']].dropna()

    # **Handle duplicates by grouping and taking the mean**
    df_filtered = df_filtered.groupby('Order_Month', as_index=False).mean()

    # ✅ Resample monthly using shared utility
    df_monthly = data_normalization.resample_external(
        df_filtered,
        date_col='Order_Month',
        value_cols=['Price'],
        method='linear'
    )

    df_monthly.rename(columns={'Price': 'Electricity_Price'}, inplace=True)

    return df_monthly

