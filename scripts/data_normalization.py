import pandas as pd


# Filter to Cylinder Products
def filter_products(df_erp, productgroup_path):
    """
    Filters ERP data to include only cylinder-related product groups
    using mapping from productgroup.xlsx.
    """
    try:
        product_groups = pd.read_excel(productgroup_path, sheet_name='prod_group', dtype={'Product_Item_Group': str})
        # Filter rows containing 'cylinder' keywords (case-insensitive)
        cyl_groups = product_groups[
            product_groups['Name_in_English'].str.contains('cylinder', case=False, na=False)
        ]['Product_Item_Group'].unique()

        df_filtered = df_erp[df_erp['Product_Item_Group'].isin(cyl_groups)]
        print(f"✅ Filtered ERP data to {len(df_filtered)} cylinder records (from {len(df_erp)} total).")
        return df_filtered
    except Exception as e:
        print(f"⚠️ Could not filter cylinder data: {e}")
        return df_erp

def aggregate_orders(df):
    df['Order_Date'] = pd.to_datetime(df['Order_Date'], dayfirst=True, errors='coerce')
    df['Order_Month'] = df['Order_Date'].dt.to_period('M').dt.to_timestamp()
    df = df.groupby(['Customer_Number', 'Product_Item_Group', 'Order_Month']) \
        .agg({'Ordered_Quantity': 'sum', 'Unit_Price': 'mean', 'Order_Amount': 'sum'}) \
        .reset_index()
    df.rename(columns={
        'Ordered_Quantity': 'Actual_Quantity',
        'Total_Amount': 'Revenue',
        'Unit_Price': 'Price'
    }, inplace=True)
    return df

# Check for missing values in each column
def check_missing_value(df):    
    missing_report = df.isnull().sum()
    print("Missing values per column:\n", missing_report)

# Check for duplicate rows
def handle_duplicate_value(df):  
    duplicates = df.duplicated().sum()
    print(f"Number of duplicate rows: {duplicates}")

    # Optionally, drop duplicates
    df = df.drop_duplicates()
    return df

# Describe numeric columns to spot outliers
def display_outliers(df):   
    print(df[['Ordered_Quantity', 'Order_Amount', 'Unit_Price']].describe())

    # Find unusually large orders
    outliers = df[df['Ordered_Quantity'] > df['Ordered_Quantity'].quantile(0.99)]
    print("Potential outliers:\n", outliers)

# Convert date columns to datetime
def standardize_data(df):   
    date_cols = ['Order_Date', 'Planned_Delivery_Date', 'Confirmed_Delivery_Date',
                'Original_Delivery_Date', 'Last_Delivery_Date']
    for col in date_cols:
        df[col] = pd.to_datetime(df[col], errors='coerce')

    # Standardize categorical columns (e.g., Status)
    df['Status'] = df['Status'].str.strip().str.lower()

    df['Product_Item_Group'] = df['Product_Item_Group'].astype(str)

    return df

# Example: Join with product master data
def prepare_clean_data(df):
    product_master = pd.read_excel("data/raw/ProductGroups.xlsx", sheet_name='prod_group', dtype={'Product_Item_Group': str})
    df = df.merge(product_master, on="Product_Item_Group", how="left")
    df.to_excel("data/raw/cleaned/erp_order_data_cleaned.xlsx", sheet_name="all_orders", index=False)
    return df


# External Data Resampling (Monthly)
def resample_external(df, date_col='Order_Month', value_cols=None, method='linear'):
    """
    Resample any external dataset to monthly frequency.
    - Converts to datetime index.
    - Handles missing months.
    - Interpolates or forward-fills values.
    
    Args:
        df: input DataFrame
        date_col: column containing dates
        value_cols: list of columns to resample (defaults to all numeric)
        method: 'linear' or 'ffill'
    """
    df = df.copy()
    df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
    df = df.dropna(subset=[date_col]).sort_values(date_col)
    df = df.set_index(date_col)

    # Choose value columns
    if value_cols is None:
        value_cols = df.select_dtypes(include='number').columns.tolist()

    # Resample and interpolate
    df_resampled = df[value_cols].resample('MS').interpolate(method=method)

    df_resampled = df_resampled.reset_index()
    return df_resampled