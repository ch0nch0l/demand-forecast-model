from external_sources import faostat_loader, eurostat_loader, ecb_loader, fred_loader, fi_tech_industry_data_loader

def load_external_data():    
    # external_dfs = {}
    # external_dfs['Food_Price_Index']       = faostat_loader.load_food_price_index('CP')
    # external_dfs['Electricity_Price']      = eurostat_loader.load_electricity_price()
    # external_dfs['ECB_Inflation']          = ecb_loader.load_inflation_rate()
    # external_dfs['ECB_Interest_Rate']      = ecb_loader.load_interest_rate()
    # external_dfs['FEDFUNDS_Value']         = fred_loader.load_fred_series('FEDFUNDS', '040e22ffb044f5bca5222e505a728a98')
    # external_dfs['Purchase_Index']         = fi_tech_industry_data_loader.load_purchase_index('data/external/purchase_index_data.csv')
    # external_dfs['Total_New_Orders_Value'] = fi_tech_industry_data_loader.load_value_of_new_order('data/external/value_of_new_order.csv')
    # external_dfs['Steel_Price']            = fi_tech_industry_data_loader.load_steel_price('data/external/iron_steel_scrap_price.csv')
    
    df_fpi = faostat_loader.load_food_price_index('CP')
    df_elc = eurostat_loader.load_electricity_price()
    df_inf = ecb_loader.load_inflation_rate()
    df_int = ecb_loader.load_interest_rate()
    df_fred = fred_loader.load_fred_series('FEDFUNDS', '040e22ffb044f5bca5222e505a728a98')
    df_pur = fi_tech_industry_data_loader.load_purchase_index('data/external/purchase_index_data.csv')
    df_val = fi_tech_industry_data_loader.load_value_of_new_order('data/external/value_of_new_order.csv')
    df_stl = fi_tech_industry_data_loader.load_steel_price('data/external/iron_steel_scrap_price.csv')

    # Merge External data
    print("🔗 Merging All external data ...")
    df_external = df_fpi
    df_external = df_external.merge(df_elc, on="Order_Month", how="left")
    df_external = df_external.merge(df_inf, on="Order_Month", how="left")
    df_external = df_external.merge(df_int, on="Order_Month", how="left")
    df_external = df_external.merge(df_fred, on="Order_Month", how="left")
    df_external = df_external.merge(df_pur, on="Order_Month", how="left")
    df_external = df_external.merge(df_val, on="Order_Month", how="left")
    df_external = df_external.merge(df_stl, on="Order_Month", how="left")

    return df_external