from scripts import data_normalization
import pandas as pd
import ecbdata as ecb

def load_inflation_rate():
    """
    Loads ECB inflation rate series and resamples monthly if necessary,
    interpolating missing months linearly.
    """

    # Step 1: Get Data
    df_inf = ecb.ecbdata.get_series('ICP.M.U2.N.000000.4.ANR', start='2021-01')

    # Step 2: Convert TIME_PERIOD to datetime
    df_inf['Order_Month'] = pd.to_datetime(df_inf['TIME_PERIOD'], errors='coerce')

    # Step 3: Select only relevant columns
    df_inf_clean = df_inf[['Order_Month', 'OBS_VALUE']].rename(columns={'OBS_VALUE': 'ECB_Inflation'})

    # Step 4: Drop duplicates and invalid dates
    df_inf_clean = df_inf_clean.drop_duplicates(subset='Order_Month').dropna(subset=['Order_Month'])

    # Step 5: Sort
    df_inf_clean = df_inf_clean.sort_values('Order_Month')

    # Step 6: Resample monthly
    df_monthly = data_normalization.resample_external(
        df_inf_clean,
        date_col='Order_Month',
        value_cols=['ECB_Inflation'],
        method='linear'
    )

    return df_monthly


def load_interest_rate():
    """
    Loads ECB interest rate series and resamples monthly if necessary,
    interpolating missing months linearly.
    """

    # Step 1: Get Data
    df_int = ecb.ecbdata.get_series('IRS.M.FI.L.L40.CI.0000.EUR.N.Z', start='2021-01')

    # Step 2: Convert TIME_PERIOD to datetime
    df_int['Order_Month'] = pd.to_datetime(df_int['TIME_PERIOD'], errors='coerce')

    # Step 3: Select only relevant columns
    df_int_clean = df_int[['Order_Month', 'OBS_VALUE']].rename(columns={'OBS_VALUE': 'ECB_Interest_Rate'})

    # Step 4: Drop duplicates and invalid dates
    df_int_clean = df_int_clean.drop_duplicates(subset='Order_Month').dropna(subset=['Order_Month'])

    # Step 5: Sort
    df_int_clean = df_int_clean.sort_values('Order_Month')

    # Step 6: Resample monthly
    df_monthly = data_normalization.resample_external(
        df_int_clean,
        date_col='Order_Month',
        value_cols=['ECB_Interest_Rate'],
        method='linear'
    )

    return df_monthly
