from scripts import data_normalization
import pandas as pd
import faostat as fs

# Load Agricultural Data (Food Price Index)
def load_food_price_index(code):
    """
    Loads and processes Food Price Index data from FAO/Stat,
    ensures monthly time series, and fills missing months via linear interpolation.

    Args:
        code: Dataset code for FAO.Stat.

    Returns:
        DataFrame with monthly Food Price Index.
    """

    # Step 0: Prepare Filtering Criteria
    filter = {
        'area': '67',
        'element': [6120],
        'item': '23013',
        'year': [2021, 2022, 2023, 2024, 2025]
    }

    # Step 1: Get Data
    df_fpi = fs.get_data_df(code, pars=filter, strval=False)

    # Step 2: Create 'Order Month' column from Year + Month number
    df_fpi['month'] = df_fpi['Months Code'].astype(str).str[-2:].astype(int)  # Extract month number
    df_fpi['Order_Month'] = pd.to_datetime(
        df_fpi['Year'].astype(str) + '-' + df_fpi['month'].astype(str).str.zfill(2),
        errors='coerce'
    )

    # Step 3: Clean data
    df_fpi_clean = df_fpi[['Order_Month', 'Value']].copy()
    df_fpi_clean.rename(columns={'Value': 'Food_Price_Index'}, inplace=True)

    # Step 4: Drop duplicates and invalid dates
    df_fpi_clean = df_fpi_clean.drop_duplicates(subset='Order_Month')
    df_fpi_clean = df_fpi_clean.dropna(subset=['Order_Month']).sort_values('Order_Month')

    # Step 5: Resample monthly and interpolate missing values
    df_monthly = data_normalization.resample_external(
        df_fpi_clean,
        date_col='Order_Month',
        value_cols=['Food_Price_Index'],
        method='linear'
    )

    return df_monthly
