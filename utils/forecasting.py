import pandas as pd
import numpy as np
import traceback # For detailed error logging

# --- Configurable Weights for WMA ---
# These weights determine the influence of different sales periods on the forecast.
# The current setting (3, 2, 1) gives the most importance to the most recent month (M1).
# M1: Sales from the last 30 days.
# M2: Sales from 31-60 days ago.
# M3: Sales from 61-90 days ago.
# Consider adjusting these weights based on how responsive you want the forecast to be
# versus how much stability you prefer. Higher M1 weight = more responsive to recent trends.
WMA_WEIGHT_M1 = 3 # Weight for the last 30 days (most recent)
WMA_WEIGHT_M2 = 2 # Weight for the period 30-60 days ago
WMA_WEIGHT_M3 = 1 # Weight for the period 60-90 days ago

# --- Check total weight ---
WEIGHT_SUM = WMA_WEIGHT_M1 + WMA_WEIGHT_M2 + WMA_WEIGHT_M3
if WEIGHT_SUM <= 0:
    raise ValueError(f"Sum of WMA weights ({WEIGHT_SUM}) must be positive.")
# ------------------------------------

def _clean_sales_data(df, sku_col, units_col, period_suffix):
    """Internal helper to clean and prepare sales data for a period."""
    if df is None or df.empty:
        print(f"Warning: DataFrame for period {period_suffix} is None or empty.")
        # Return an empty DataFrame with the expected column, indexed by sku_col if possible
        # If sku_col itself is missing, we can't set it as index.
        cols = [f'{units_col}_{period_suffix}']
        idx = pd.Index([], name=sku_col) # Empty index with the correct name
        return pd.DataFrame(columns=cols, index=idx)


    if sku_col not in df.columns or units_col not in df.columns:
         print(f"Warning: Missing '{sku_col}' or '{units_col}' in DataFrame for period {period_suffix}. Returning empty.")
         # Return an empty DataFrame with the expected column, indexed by sku_col if possible
         cols = [f'{units_col}_{period_suffix}']
         idx_name = sku_col if sku_col in df.columns else None # Use sku_col name if it exists
         idx = pd.Index([], name=idx_name)
         return pd.DataFrame(columns=cols, index=idx)

    df_clean = df[[sku_col, units_col]].copy()
    # Ensure units_col is treated as string before replacing commas
    df_clean[units_col] = df_clean[units_col].astype(str).str.replace(',', '', regex=False)
    # Convert to numeric, coercing errors, then fill NaNs with 0
    df_clean[units_col] = pd.to_numeric(df_clean[units_col], errors='coerce').fillna(0).astype(float)
    df_clean = df_clean.rename(columns={units_col: f'{units_col}_{period_suffix}'})

    # Aggregate duplicates *before* setting the index
    df_agg = df_clean.groupby(sku_col).sum() # This returns a DataFrame with sku_col as the index
    return df_agg

def generate_wma_forecast(all_listings_df, df_30, df_60, df_90, sku_col_listings, sku_col_sales, units_col):
    """
    Generates a Weighted Moving Average (WMA) forecast for the next month.

    Uses all_listings_df to get the full list of SKUs, ensuring forecasts
    are generated even for items with zero sales in the recent periods.

    Args:
        all_listings_df (pd.DataFrame): DataFrame from the all listings report. Must contain sku_col_listings.
        df_30 (pd.DataFrame | None): DataFrame with sales for the last 30 days.
        df_60 (pd.DataFrame | None): DataFrame with sales for the last 60 days.
        df_90 (pd.DataFrame | None): DataFrame with sales for the last 90 days.
        sku_col_listings (str): Name of the SKU column in all_listings_df.
        sku_col_sales (str): Name of the SKU column in the sales DataFrames (df_30, df_60, df_90).
        units_col (str): Name of the 'units ordered' column in sales DataFrames.

    Returns:
        dict: A dictionary mapping SKU (from sku_col_listings) to its WMA forecast value.
              Returns an empty dictionary if essential inputs are missing or invalid.
    """
    print("Starting WMA forecast generation...")

    # --- Input Validation ---
    if not isinstance(all_listings_df, pd.DataFrame) or all_listings_df.empty:
        print("Error: all_listings_df is missing, empty, or not a DataFrame.")
        return {}
    if sku_col_listings not in all_listings_df.columns:
        print(f"Error: SKU column '{sku_col_listings}' not found in all_listings_df.")
        return {}
    # Check if any sales dataframes are provided. If not, WMA will be 0, which might be acceptable.
    if df_30 is None and df_60 is None and df_90 is None:
         print("Warning: All sales DataFrames (30d, 60d, 90d) are None. Forecast will be zero for all items.")
         # Proceed, but expect zero forecast.

    # Weights are checked globally at the start of the script.

    try:
        # 1. Get the full list of unique SKUs from the all_listings report
        # Drop duplicates and handle potential NaN SKUs before setting index
        all_skus = all_listings_df[sku_col_listings].dropna().unique()
        if len(all_skus) == 0:
             print("Error: No valid SKUs found in the all_listings_df after dropping NA.")
             return {}
        print(f"Found {len(all_skus)} unique SKUs in all_listings_df.")

        # Create a base DataFrame indexed by all unique SKUs
        forecast_base = pd.DataFrame(index=pd.Index(all_skus, name=sku_col_listings))

        # 2. Clean and prepare sales data for each period
        # Pass the correct SKU column name for sales data
        sales_30 = _clean_sales_data(df_30, sku_col_sales, units_col, '30d')
        sales_60 = _clean_sales_data(df_60, sku_col_sales, units_col, '60d')
        sales_90 = _clean_sales_data(df_90, sku_col_sales, units_col, '90d')

        # Check if cleaning resulted in non-empty DataFrames before joining
        valid_sales_dfs = [df for df in [sales_90, sales_60, sales_30] if isinstance(df, pd.DataFrame) and not df.empty]

        # 3. Combine sales data with the forecast base
        # Use left join to keep all SKUs from forecast_base, fill missing sales with 0
        if valid_sales_dfs:
            combined_sales = forecast_base.join(valid_sales_dfs, how='left')
        else:
            # If no valid sales data, create DataFrame with 0s for expected columns
            combined_sales = forecast_base.copy()
            for period in ['90d', '60d', '30d']:
                col_name = f'{units_col}_{period}'
                if col_name not in combined_sales.columns:
                    combined_sales[col_name] = 0.0 # Ensure float type

        combined_sales = combined_sales.fillna(0) # Fill any NaNs resulting from join

        # Check if combined_sales is empty or lost its index
        if combined_sales.empty:
             print("Error: Combined sales data is empty after joining and cleaning.")
             return {}
        if combined_sales.index.name != sku_col_listings:
             print(f"Error: Index name mismatch after join. Expected '{sku_col_listings}', got '{combined_sales.index.name}'.")
             # Attempt to reset index if it helps, or return error
             # combined_sales = combined_sales.reset_index().set_index(sku_col_listings) # Risky if index name is wrong
             return {}


        # 4. Calculate approximate monthly sales (M1, M2, M3)
        units_30d_col = f'{units_col}_30d'
        units_60d_col = f'{units_col}_60d'
        units_90d_col = f'{units_col}_90d'

        # Ensure columns exist, default to 0 Series if not
        s_30 = combined_sales[units_30d_col] if units_30d_col in combined_sales else pd.Series(0.0, index=combined_sales.index)
        s_60 = combined_sales[units_60d_col] if units_60d_col in combined_sales else pd.Series(0.0, index=combined_sales.index)
        s_90 = combined_sales[units_90d_col] if units_90d_col in combined_sales else pd.Series(0.0, index=combined_sales.index)

        # M1: Sales in the last 30 days
        m1 = s_30
        # M2: Sales in the period 31-60 days ago
        m2_calc = s_60 - s_30
        # M3: Sales in the period 61-90 days ago
        m3_calc = s_90 - s_60

        # Ensure calculated monthly sales are not negative
        m2 = m2_calc.clip(lower=0)
        m3 = m3_calc.clip(lower=0)

        # 5. Calculate WMA using configured weights
        # WEIGHT_SUM is pre-calculated and checked globally
        wma_values = (WMA_WEIGHT_M3 * m3 + WMA_WEIGHT_M2 * m2 + WMA_WEIGHT_M1 * m1) / WEIGHT_SUM

        # 6. Round the forecast
        wma_rounded = wma_values.round(2) # Round to 2 decimal places

        # 7. Convert the resulting Series (indexed by SKU) to a dictionary
        forecast_dict = wma_rounded.to_dict()

        print(f"WMA forecast generated successfully for {len(forecast_dict)} SKUs.")
        return forecast_dict

    except Exception as e:
        print(f"Error during WMA forecast generation: {e}")
        traceback.print_exc() # Print detailed traceback for debugging
        return {} # Return empty dict on error 