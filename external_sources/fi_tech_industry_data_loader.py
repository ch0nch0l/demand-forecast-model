from scripts import data_normalization
import pandas as pd

def load_purchase_index(filepath):
    """
    Loads and processes the Purchase Manager Index (PMI) data from CSV.
    Converts it to monthly format using the shared resampling utility.
    """

    # Step 1: Read CSV file safely
    df = pd.read_csv(
        filepath,
        sep=';',          # Finnish CSVs often use semicolons
        quotechar='"',
        decimal=',',      # European format uses comma as decimal
        encoding='utf-8-sig'
    )

    # Step 2: Clean up and rename columns
    df.columns = df.columns.str.strip()
    
    # Step 3: Select and rename relevant columns
    df_pmi = df[['Kuukausi', 'Euroalue']].copy()
    df_pmi.rename(columns={'Kuukausi': 'Order_Month', 'Euroalue': 'Purchase_Index'}, inplace=True)

    # Step 4: Convert Order_Month to datetime
    # Format: "YYYY.MM" or sometimes "YYYY-M"
    df_pmi['Order_Month'] = pd.to_datetime(df_pmi['Order_Month'], format='%Y.%m', errors='coerce')

    # Step 5: Convert to numeric
    df_pmi['Purchase_Index'] = pd.to_numeric(df_pmi['Purchase_Index'], errors='coerce')

    # Step 6: Drop missing and use the common resampler
    df_pmi = df_pmi.dropna(subset=['Order_Month', 'Purchase_Index'])
    df_monthly = data_normalization.resample_external(df_pmi, date_col='Order_Month', value_cols=['Purchase_Index'])
    
    return df_monthly


def load_value_of_new_order(filepath):
    """
    Loads and processes 'Value of New Orders' data (quarterly) and converts it
    into monthly time series via linear interpolation.

    Args:
        filepath: path to the CSV file from the Technology Industries of Finland.

    Returns:
        DataFrame with monthly data.
    """

    # Step 1: Read CSV safely
    df = pd.read_csv(
        filepath,
        sep=';',
        quotechar='"',
        decimal=',',
        encoding='utf-8-sig'
    )

    # Step 2: Clean column names and remove whitespace
    df.columns = df.columns.str.strip()

    # Step 3: Fix Quarter column name and clean spaces (e.g., '2010 Q1' -> '2010Q1')
    if 'Quarter' not in df.columns:
        # Sometimes the column might be lowercase or misspelled
        df.rename(columns={col: 'Quarter' for col in df.columns if 'quarter' in col.lower()}, inplace=True)
    
    df['Quarter'] = df['Quarter'].str.replace(' ', '')

    # Step 4: Convert Quarter strings to timestamps (e.g., 2010Q1 → 2010-01-01)
    df['Order_Month'] = pd.PeriodIndex(df['Quarter'], freq='Q').to_timestamp()

    # Step 5: Clean numeric data — fix possible thousand separators, spaces, etc.
    numeric_cols = ['Export', 'Domestic', 'Combined']
    for col in numeric_cols:
        df[col] = (
            df[col]
            .astype(str)
            .str.replace('\t', '')       # remove tab separators
            .str.replace(' ', '')        # remove spaces
            .str.replace(',', '.')       # fix commas if used as decimal separators
        )
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # Step 6: Drop invalid rows
    df = df.dropna(subset=['Order_Month'])

    # Step 7: Use shared resampling function to interpolate monthly
    df_monthly = data_normalization.resample_external(
        df[['Order_Month', 'Export', 'Domestic', 'Combined']],
        date_col='Order_Month',
        value_cols=['Combined'],
        method='linear'
    )

    # Step 8: Rename the column for clarity
    df_monthly.rename(columns={
        'Export': 'Export_Value',
        'Domestic': 'Domestic_Value',
        'Combined': 'Total_New_Orders_Value'
    }, inplace=True)

    return df_monthly


def load_steel_price(filepath):
    """
    Loads and processes steel price data (monthly) and ensures all dates are
    properly set for monthly time series. Handles conversion and resampling
    like the 'Value of New Orders' function.

    Args:
        filepath: path to the CSV file.

    Returns:
        DataFrame with monthly steel price data.
    """
    import pandas as pd

    # Step 1: Read CSV safely
    df = pd.read_csv(
        filepath,
        sep=';',
        quotechar='"',
        decimal=',',
        encoding='utf-8-sig'  # handles BOM if present
    )

    # Step 2: Clean column names
    df.columns = df.columns.str.strip()

    # Step 3: Select relevant columns
    df_euro = df[['Kuukausi', 'Euro area']].copy()

    # Step 4: Convert Kuukausi to datetime
    df_euro['Order_Month'] = pd.to_datetime(df_euro['Kuukausi'], format='%Y.%m', errors='coerce')
    df_euro.rename(columns={'Euro area': 'Steel_Price'}, inplace=True)

    # Step 5: Drop rows with invalid dates
    df_euro = df_euro.dropna(subset=['Order_Month'])

    # Step 6: Resample to monthly if necessary (fill missing months using linear interpolation)
    df_monthly = data_normalization.resample_external(
        df_euro[['Order_Month', 'Steel_Price']],
        date_col='Order_Month',
        value_cols=['Steel_Price'],
        method='linear'
    )

    return df_monthly
