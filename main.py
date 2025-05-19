import pandas as pd
import os
from utils.template_update_generator import preper_new_template_csv
import numpy as np
from utils.forecasting import generate_wma_forecast
import traceback

# Read constants from 'config.csv' and map 'const name' to 'column name'
config_file_path = './data/config.csv'
try:
    config_df = pd.read_csv(config_file_path, index_col='const name')
    config = config_df['column name'].to_dict()
except FileNotFoundError:
    print(f"Config file not found at '{config_file_path}'.")
    exit(1)
except Exception as e:
    print(f"Error reading config file: {e}")
    exit(1)

# List of required constants
required_constants = {
    'PRICE',
    'SELLER_SKU',
    'SKU',
    'AVAILABLE',
    'INBOUND_QUANTITY',
    'UNITS_ORDERED',
    'UNITS_ORDERED_B2B',
    'ASIN',
    'INV',
    'INBOUND',
    'MERCHANT_SKU',
    'C30',
    'C60',
    'C90',
    'C12M',
    'C2YR',
    'SHP',
    'MERCHANT_SKU_W',
    'SHIPPED_W',
    'FBA_SKU',
    'M_SKU',
    'M_30',
    'M_12M',
    'WMA_FORECAST',
    'REC_SHIP'
}

# Initialize constants from config, converting to lower case
constants = {}
missing_constants = []
for const in required_constants:
    if const in config:
        constants[const] = config[const].lower()
    else:
        missing_constants.append(const)

if missing_constants:
    print(f"Missing constants in config file: {', '.join(missing_constants)}")
    exit(1)

# Unpack constants for easy access
PRICE = constants['PRICE']
SELLER_SKU = constants['SELLER_SKU']
SKU = constants['SKU']
AVAILABLE = constants['AVAILABLE']
INBOUND_QUANTITY = constants['INBOUND_QUANTITY']
UNITS_ORDERED = constants['UNITS_ORDERED']
UNITS_ORDERED_B2B = constants['UNITS_ORDERED_B2B']
ASIN = constants['ASIN']
INV = constants['INV']
INBOUND = constants['INBOUND']
MERCHANT_SKU = constants['MERCHANT_SKU']
C30 = constants['C30']
C60 = constants['C60']
C90 = constants['C90']
C12M = constants['C12M']
C2YR = constants['C2YR']
SHP = constants['SHP']
MERCHANT_SKU_W = constants['MERCHANT_SKU_W']
SHIPPED_W = constants['SHIPPED_W']
FBA_SKU = constants['FBA_SKU']
M_SKU = constants['M_SKU']
M_30 = constants['M_30']
M_12M = constants['M_12M']
WMA_FORECAST_COL = constants['WMA_FORECAST']
REC_SHIP = constants['REC_SHIP']

def columns_to_lower_case(df):
    """
    Convert all column names in a DataFrame to lower case.
    """
    df.columns = df.columns.str.lower()
    return df

def create_data_frame_from_file(directory):
    """
    Reads files from the specified directory and returns a DataFrame.
    For '1_W', '2_W', '3_W', '4_W' directories, combines multiple files.
    Supports CSV, TXT, and TSV files.
    """
    base_dir_name = os.path.basename(os.path.normpath(directory))
    is_weekly_data = base_dir_name in ['1_W', '2_W', '3_W', '4_W']

    try:
        files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f)) and f != '.gitkeep' and f != '.DS_Store']
    except FileNotFoundError:
        print(f"Directory '{directory}' not found.")
        return None

    if not files:
        if is_weekly_data:
            print(f"Folder '{directory}' is empty, column {directory.split('/')[-1]} will be empty in the final report")
            return pd.DataFrame(columns=[MERCHANT_SKU_W, SHIPPED_W])
        else:
            raise ValueError(f"No valid files found in directory '{directory}'")

    if is_weekly_data:
        combined_df = pd.DataFrame(columns=[MERCHANT_SKU_W, SHIPPED_W])
        for file in files:
            file_path = os.path.join(directory, file)
            df = read_file(file_path, skip_lines=7)
            if df is not None:
                df = df[[MERCHANT_SKU_W, SHIPPED_W]]
                combined_df = pd.concat([combined_df, df], ignore_index=True)

        # Group by MERCHANT_SKU_W and sum SHIPPED_W
        combined_df = combined_df.groupby(MERCHANT_SKU_W, as_index=False)[SHIPPED_W].sum()
        return columns_to_lower_case(combined_df)
    else:
        if len(files) > 1:
            raise ValueError(f"More than one valid file found in directory '{directory}'")
        file_path = os.path.join(directory, files[0])
        return read_file(file_path)

def read_file(file_path, skip_lines=0):
    """
    Reads a file and returns a DataFrame.
    """
    file_extension = os.path.splitext(file_path)[1].lower()
    
    try:
        if file_extension == '.csv':
            df = pd.read_csv(file_path, encoding='utf-8', skiprows=skip_lines)
        elif file_extension in ['.txt', '.tsv']:
            df = pd.read_csv(file_path, sep='\t', encoding='utf-8', skiprows=skip_lines)
        else:
            raise ValueError(f"Unsupported file extension '{file_extension}' in file '{file_path}'")
    except UnicodeDecodeError:
        try:
            if file_extension == '.csv':
                df = pd.read_csv(file_path, encoding='ISO-8859-1', skiprows=skip_lines)
            elif file_extension in ['.txt', '.tsv']:
                df = pd.read_csv(file_path, sep='\t', encoding='ISO-8859-1', skiprows=skip_lines)
        except Exception as e:
            print(f"Failed to read file '{file_path}': {e}")
            return None
    except Exception as e:
        print(f"Failed to read file '{file_path}': {e}")
        return None

    return columns_to_lower_case(df)

def create_data_frames_from_directories(directory):
    """
    Reads files from subdirectories of the specified directory and creates a dictionary of DataFrames.
    Each subdirectory is expected to contain one file.
    """
    data_frames = {}

    try:
        subdirectories = os.listdir(directory)
    except FileNotFoundError:
        print(f"Directory '{directory}' not found.")
        raise FileNotFoundError(f"Directory '{directory}' not found.")

    for subdir in subdirectories:
        subdir_path = os.path.join(directory, subdir)
        if os.path.isdir(subdir_path):
            try:
                df = create_data_frame_from_file(subdir_path)
                if df is not None:
                    data_frames[subdir] = df
            except ValueError as e:
                print(f"Error in directory '{subdir_path}': {e}")
                raise e
            except Exception as e:
                print(f"An error occurred while processing directory '{subdir_path}': {e}")
                raise e

    return data_frames

def update_template_with_price_data(template_df, all_listings_report_df):
    """
    Updates the 'PRICE' column in the template DataFrame using data from the 'all_listings_report_df'.
    If FBA_SKU is '-', it tries to find the price using the M_SKU.
    """
    # Check if required columns exist
    if SELLER_SKU not in all_listings_report_df.columns or PRICE not in all_listings_report_df.columns:
        raise KeyError(f"Required columns '{SELLER_SKU}' or '{PRICE}' not found in 'all_listings_report_df'.")

    if FBA_SKU not in template_df.columns or M_SKU not in template_df.columns:
        raise KeyError(f"Required columns '{FBA_SKU}' or '{M_SKU}' not found in 'template_df'.")

    # Create a mapping from SELLER_SKU to PRICE
    # Ensure index is string type for reliable lookup
    all_listings_report_df[SELLER_SKU] = all_listings_report_df[SELLER_SKU].astype(str)
    price_map = all_listings_report_df.set_index(SELLER_SKU)[PRICE].to_dict()

    # Define a function to get the price based on FBA_SKU or M_SKU
    def get_price(row):
        fba_sku = str(row[FBA_SKU]).strip()
        m_sku = str(row[M_SKU]).strip() # Renamed variable for clarity

        # Default price if not found
        price_to_set = np.nan

        # Try FBA_SKU first (unless it's '-')
        if fba_sku != '-' and fba_sku in price_map:
            price_to_set = price_map[fba_sku]
        # If FBA_SKU is '-', try the single M_SKU
        elif fba_sku == '-' and pd.notna(m_sku) and m_sku != '' and m_sku in price_map:
            price_to_set = price_map[m_sku]
        # As a fallback, if FBA SKU exists but wasn't found initially (e.g., data type issues resolved by map creation)
        elif fba_sku != '-' and fba_sku in price_map:
            price_to_set = price_map[fba_sku]

        return price_to_set

    # Apply the function to update the PRICE column
    template_df[PRICE] = template_df.apply(get_price, axis=1)

    # Optional: Print SKUs that were not found in the price_map (might need adjustment based on new logic)
    # Consider how to report missing SKUs now (e.g., rows where PRICE is still NaN)
    missing_price_rows = template_df[template_df[PRICE].isnull()]
    if not missing_price_rows.empty:
        print(f"Could not find price for {len(missing_price_rows)} rows. Example FBA/M SKUs:")
        print(missing_price_rows[[FBA_SKU, M_SKU]].head())

    return template_df

def update_template_with_availability_data(template_df, FBA_inventory_report_df, restock_report_df):
    """
    Updates the 'INV' column in the template DataFrame using availability data from FBA inventory and restock reports.
    """
    # Check if required columns exist in the data frames
    required_columns_fba = [SKU, AVAILABLE]
    required_columns_restock = [MERCHANT_SKU, AVAILABLE]
    required_columns_template = [FBA_SKU]

    for col in required_columns_fba:
        if col not in FBA_inventory_report_df.columns:
            raise KeyError(f"Column '{col}' not found in 'FBA_inventory_report_df'.")

    for col in required_columns_restock:
        if col not in restock_report_df.columns:
            raise KeyError(f"Column '{col}' not found in 'restock_report_df'.")

    for col in required_columns_template:
        if col not in template_df.columns:
            raise KeyError(f"Column '{col}' not found in 'template_df'.")

    # Create mappings of SKU to available quantity
    FBA_available_map = FBA_inventory_report_df.set_index(SKU)[AVAILABLE].to_dict()
    restock_available_map = restock_report_df.set_index(MERCHANT_SKU)[AVAILABLE].to_dict()

    # Update the 'INV' column in template_df
    def get_inventory(sku):
        if sku in FBA_available_map and FBA_available_map[sku] > 0:
            return FBA_available_map[sku]
        elif sku in restock_available_map and restock_available_map[sku] > 0:
            return restock_available_map[sku]
        else:
            return 0

    template_df[INV] = template_df[FBA_SKU].apply(get_inventory)

    return template_df

def update_template_with_inbound_quantity_data(template_df, FBA_inventory_report_df, restock_report_df):
    """
    Updates the 'INBOUND' column in the template DataFrame using inbound quantity data from FBA inventory and restock reports.
    """
    # Check for duplicates in SKU columns
    if FBA_inventory_report_df[SKU].duplicated().any():
        duplicates = FBA_inventory_report_df[FBA_inventory_report_df[SKU].duplicated()][SKU].unique()
        print(f"FBA_inventory_report_df has duplicates in the '{SKU}' column: {duplicates}")

    if restock_report_df[MERCHANT_SKU].duplicated().any():
        duplicates = restock_report_df[restock_report_df[MERCHANT_SKU].duplicated()][MERCHANT_SKU].unique()
        print(f"restock_report_df has duplicates in the '{MERCHANT_SKU}' column: {duplicates}")

    # Check if required columns exist
    required_columns_fba = [SKU, INBOUND_QUANTITY]
    required_columns_restock = [MERCHANT_SKU, INBOUND]
    required_columns_template = [FBA_SKU]

    for col in required_columns_fba:
        if col not in FBA_inventory_report_df.columns:
            raise KeyError(f"Column '{col}' not found in 'FBA_inventory_report_df'.")

    for col in required_columns_restock:
        if col not in restock_report_df.columns:
            raise KeyError(f"Column '{col}' not found in 'restock_report_df'.")

    for col in required_columns_template:
        if col not in template_df.columns:
            raise KeyError(f"Column '{col}' not found in 'template_df'.")

    # Create mappings of SKU to inbound quantity
    FBA_inbound_map = FBA_inventory_report_df.set_index(SKU)[INBOUND_QUANTITY].to_dict()
    restock_inbound_map = restock_report_df.set_index(MERCHANT_SKU)[INBOUND].to_dict()

    # Update the 'INBOUND' column in template_df
    def get_inbound_quantity(sku):
        if sku in FBA_inbound_map and FBA_inbound_map[sku] > 0:
            return FBA_inbound_map[sku]
        elif sku in restock_inbound_map and restock_inbound_map[sku] > 0:
            return restock_inbound_map[sku]
        else:
            return 0

    template_df[INBOUND] = template_df[FBA_SKU].apply(get_inbound_quantity)

    return template_df

def sales_to_dict(sales_report_df):
    """
    Converts sales data into a dictionary mapping SKU to total units ordered.
    """
    # Check if required columns exist
    required_columns = [SKU, UNITS_ORDERED, UNITS_ORDERED_B2B]
    for col in required_columns:
        if col not in sales_report_df.columns:
            raise KeyError(f"Column '{col}' not found in 'sales_report_df'.")

    # Convert columns to numeric, handling commas and missing values
    sales_report_df[UNITS_ORDERED] = pd.to_numeric(sales_report_df[UNITS_ORDERED].astype(str).str.replace(',', ''), errors='coerce').fillna(0)
    sales_report_df[UNITS_ORDERED_B2B] = pd.to_numeric(sales_report_df[UNITS_ORDERED_B2B].astype(str).str.replace(',', ''), errors='coerce').fillna(0)

    # Calculate total units ordered per SKU
    sales_data = {}
    for index, row in sales_report_df.iterrows():
        sku = row[SKU]
        units_ordered = row[UNITS_ORDERED]
        units_ordered_b2b = row[UNITS_ORDERED_B2B]
        total_units_ordered = units_ordered + units_ordered_b2b
        if sku in sales_data:
            sales_data[sku] = max(sales_data[sku], total_units_ordered)
        else:
            sales_data[sku] = total_units_ordered

    return sales_data

def update_template_with_sales_data(template_df, df_30, df_60, df_90, df_12_m, df_2yr):
    """
    Updates the template DataFrame with sales data for 30, 60, 90 days, and 12 months.
    Also processes merchant SKU sales for M_30 and M_12M columns.
    """
    # Generate sales data dictionaries
    sales_30 = sales_to_dict(df_30)
    sales_60 = sales_to_dict(df_60)
    sales_90 = sales_to_dict(df_90)
    sales_12_m = sales_to_dict(df_12_m)
    sales_2yr = sales_to_dict(df_2yr)

    # Update the template DataFrame with FBA SKU sales
    template_df[C30] = template_df[FBA_SKU].map(sales_30).fillna(0)
    template_df[C60] = template_df[FBA_SKU].map(sales_60).fillna(0)
    template_df[C90] = template_df[FBA_SKU].map(sales_90).fillna(0)
    template_df[C12M] = template_df[FBA_SKU].map(sales_12_m).fillna(0)
    template_df[C2YR] = template_df[FBA_SKU].map(sales_2yr).fillna(0)
    
    # Process merchant SKU sales
    def get_merchant_sales(merchant_sku_str, sales_dict):
        if pd.isna(merchant_sku_str) or merchant_sku_str == '':
            return 0
        # Split merchant SKUs by comma and remove whitespace
        merchant_skus = [sku.strip() for sku in str(merchant_sku_str).split(',')]
        # Sum up sales for all merchant SKUs
        total_sales = sum(sales_dict.get(sku, 0) for sku in merchant_skus)
        return total_sales

    # Update merchant sales columns
    template_df[M_30] = template_df[M_SKU].apply(lambda x: get_merchant_sales(x, sales_30))
    template_df[M_12M] = template_df[M_SKU].apply(lambda x: get_merchant_sales(x, sales_12_m))
    
    return template_df

def pre_clean(template_df):
    """
    Performs pre-cleaning steps on the template DataFrame.
    """
    # Strip whitespace from ASIN column
    if ASIN in template_df.columns:
        template_df[ASIN] = template_df[ASIN].str.strip()
    else:
        raise KeyError(f"Column '{ASIN}' not found in 'template_df'.")

    # Clear the columns that will be updated
    columns_to_clear = [PRICE, INV, INBOUND, C30, C60, C90, C12M, SHP, '1_w', '2_w', '3_w', '4_w', M_30, M_12M]
    for col in columns_to_clear:
        if col in template_df.columns:
            template_df[col] = ''
        else:
            # Optionally, add the column if it doesn't exist
            template_df[col] = ''

    return template_df

def print_data_frame_headers(data_frames):
    """
    Prints the column names of each DataFrame in the provided dictionary.
    """
    for name, df in data_frames.items():
        print(f"Column names for '{name}':")
        print(df.columns.tolist())
        print("\n")

def update_template_with_last_shipments_data(template_df, df_1_W, df_2_W, df_3_W, df_4_W):
    """
    Updates the template DataFrame with the last shipments data from the given DataFrames.
    """
    # Check if required columns exist
    required_columns = [MERCHANT_SKU_W, SHIPPED_W]
    for df, week in zip([df_1_W, df_2_W, df_3_W, df_4_W], ['1_w', '2_w', '3_w', '4_w']):
        for col in required_columns:
            if col not in df.columns:
                raise KeyError(f"Column '{col}' not found in data for '{week}'.")

    # Create mappings from MERCHANT_SKU_W to SHIPPED_W
    last_shipped_map_1_w = df_1_W.set_index(MERCHANT_SKU_W)[SHIPPED_W].to_dict()
    last_shipped_map_2_w = df_2_W.set_index(MERCHANT_SKU_W)[SHIPPED_W].to_dict()
    last_shipped_map_3_w = df_3_W.set_index(MERCHANT_SKU_W)[SHIPPED_W].to_dict()
    last_shipped_map_4_w = df_4_W.set_index(MERCHANT_SKU_W)[SHIPPED_W].to_dict()

    # Update the template DataFrame
    template_df['1_w'] = template_df[FBA_SKU].map(last_shipped_map_1_w).fillna('')
    template_df['2_w'] = template_df[FBA_SKU].map(last_shipped_map_2_w).fillna('')
    template_df['3_w'] = template_df[FBA_SKU].map(last_shipped_map_3_w).fillna('')
    template_df['4_w'] = template_df[FBA_SKU].map(last_shipped_map_4_w).fillna('')

    return template_df

def update_template_with_forecast(template_df, wma_forecast_dict):
    """
    Updates the template DataFrame with the WMA forecast data.
    """
    # Verify the forecast column exists
    if WMA_FORECAST_COL not in template_df.columns:
        return template_df
    
    for index, row in template_df.iterrows():
        try:
            if row[FBA_SKU] == '-':
                if row[M_SKU] in wma_forecast_dict:
                    template_df.at[index, WMA_FORECAST_COL] = wma_forecast_dict[row[M_SKU]]
            else:
                if row[FBA_SKU] in wma_forecast_dict:
                    template_df.at[index, WMA_FORECAST_COL] = wma_forecast_dict[row[FBA_SKU]]
        except Exception as e:
            template_df.at[index, WMA_FORECAST_COL] = 0
            
    return template_df

def calculate_recommended_shipment(template_df):
    """
    Calculates recommended shipment quantity based on:
    REC_SHIP = max(0, WMA_FORECAST - (INBOUND + INV))
    If 1_w column contains a value greater than INBOUND, add it to INBOUND as it represents
    additional shipments not yet captured in the inbound report.
    Empty values in 1_w will remain empty.
    
    Args:
        template_df (pd.DataFrame): Template DataFrame with required columns
        
    Returns:
        pd.DataFrame: Updated template DataFrame with REC_SHIP column
    """
    try:
        # Ensure all required columns exist
        required_cols = [INBOUND, INV, WMA_FORECAST_COL]
        for col in required_cols:
            if col not in template_df.columns:
                raise KeyError(f"Required column '{col}' not found in template DataFrame")
        
        # Convert columns to numeric if they aren't already
        template_df[INBOUND] = pd.to_numeric(template_df[INBOUND], errors='coerce').fillna(0)
        template_df[INV] = pd.to_numeric(template_df[INV], errors='coerce').fillna(0)
        template_df[WMA_FORECAST_COL] = pd.to_numeric(template_df[WMA_FORECAST_COL], errors='coerce').fillna(0)
        
        # Check if 1_w column exists
        if '1_w' in template_df.columns:
            # Create a copy of 1_w to preserve original values
            original_1w = template_df['1_w'].copy()
            
            # Convert 1_w to numeric for calculation, but don't fillna yet
            numeric_1w = pd.to_numeric(template_df['1_w'], errors='coerce')
            
            # Define a function to calculate REC_SHIP considering 1_w
            def calculate_rec_ship(row):
                # If 1_w is empty or not numeric, use just INBOUND
                if pd.isna(numeric_1w[row.name]) or original_1w[row.name] == '':
                    return max(0, row[WMA_FORECAST_COL] - (row[INBOUND] + row[INV]))
                else:
                    # If 1_w has numeric value and is greater than INBOUND, add it to INBOUND
                    one_w_value = numeric_1w[row.name]
                    if one_w_value > row[INBOUND]:
                        return max(0, row[WMA_FORECAST_COL] - ((row[INBOUND] + one_w_value) + row[INV]))
                    else:
                        return max(0, row[WMA_FORECAST_COL] - (row[INBOUND] + row[INV]))
            
            # Apply the function
            template_df[REC_SHIP] = template_df.apply(calculate_rec_ship, axis=1)
        else:
            # Original calculation if 1_w doesn't exist
            template_df[REC_SHIP] = template_df.apply(
                lambda row: max(0, row[WMA_FORECAST_COL] - (row[INBOUND] + row[INV])),
                axis=1
            )
        
        return template_df
        
    except Exception as e:
        print(f"Error calculating recommended shipment: {e}")
        traceback.print_exc()
        raise e

def main():
    """
    Main function to orchestrate the data processing and updating the template DataFrame.
    """
    print("Starting the program")

    # Create data frames from directories
    data_frames = create_data_frames_from_directories('amazon exports')

    try:
        preper_new_template_csv(data_frames['all_listings_report'], data_frames['FBA_Inventory'])
    except Exception as e:
        print(f'error in preper_new_template_csv {e}')
        raise e     

    # Check if 'template.csv' exists
    template_file_path = './data/template.csv'
    try:
        template_df = pd.read_csv(template_file_path)
    except FileNotFoundError:
        print(f"Template file not found at '{template_file_path}'.")
        raise FileNotFoundError(f"Template file not found at '{template_file_path}'.")  
    except Exception as e:
        print(f"Error reading template file: {e}")
        raise  e

    # Convert template columns to lower case
    template_df = columns_to_lower_case(template_df)

    try:
        print('Processing reports data')
        # Update template with price data
        if 'all_listings_report' in data_frames:
            template_df = update_template_with_price_data(template_df, data_frames['all_listings_report'])
        else:
            print("Data frame for 'all_listings_report' not found.")

        # Update template with availability data
        if 'FBA_Inventory' in data_frames and 'restock_report' in data_frames:
            template_df = update_template_with_availability_data(template_df, data_frames['FBA_Inventory'], data_frames['restock_report'])
        else:
            print("Data frames for 'FBA_Inventory' or 'restock_report' not found.")

        # Update template with inbound quantity data
        if 'FBA_Inventory' in data_frames and 'restock_report' in data_frames:
            template_df = update_template_with_inbound_quantity_data(template_df, data_frames['FBA_Inventory'], data_frames['restock_report'])
        else:
            print("Data frames for 'FBA_Inventory' or 'restock_report' not found.")

        # Update template with sales data
        if all(key in data_frames for key in ['30d', '60d', '90d', '12m', '2yr']):
            template_df = update_template_with_sales_data(template_df, data_frames['30d'], data_frames['60d'], data_frames['90d'], data_frames['12m'], data_frames['2yr'])
        else:
            print("One or more sales data frames ('30d', '60d', '90d', '12m', '2yr') not found.")

        # Update template with last shipments data
        if all(key in data_frames for key in ['1_W', '2_W', '3_W', '4_W']):
            template_df = update_template_with_last_shipments_data(template_df, data_frames['1_W'], data_frames['2_W'], data_frames['3_W'], data_frames['4_W'])
        else:
            print("One or more shipment data frames ('1_W', '2_W', '3_W', '4_W') not found.")

        # Generate WMA forecast using the previously created function
        try:
            print('Calculating WMA forecast...')
            wma_forecast_dict = generate_wma_forecast(
                data_frames['all_listings_report'],
                data_frames['30d'],
                data_frames['60d'],
                data_frames['90d'],
                data_frames.get('12m'), # Use .get() to handle potentially missing keys gracefully
                data_frames.get('2yr'),  # Use .get() for safety
                sku_col_listings=SELLER_SKU,  # SKU column in all_listings_report
                sku_col_sales=SKU,           # SKU column in sales reports
                units_col=UNITS_ORDERED      # Units ordered column name
            )

            # Check if forecast generation was successful before proceeding
            if not wma_forecast_dict:
                print("WMA forecast dictionary is empty. Skipping forecast update and subsequent steps.")
            else:
                template_df = update_template_with_forecast(template_df, wma_forecast_dict)
                
                # Calculate recommended shipment quantity
                print('Calculating recommended shipment quantities...')
                template_df = calculate_recommended_shipment(template_df)
                
                # Sort the DataFrame by multiple columns
                print('Sorting results...')
                template_df = template_df.sort_values(
                    by=[REC_SHIP, C30, M_30],  # Changed order: REC_SHIP, C30, M_30
                    ascending=[False, False, False],
                    na_position='last'
                )

                # Save the result
                output_file_path = './results/result.csv'
                os.makedirs(os.path.dirname(output_file_path), exist_ok=True)
                template_df.to_csv(output_file_path, index=False)
                print(f"Data processing completed, results saved to '{output_file_path}'")

        except Exception as e:
            print(f"Error generating WMA forecast or calculating recommended shipment: {e}")
            traceback.print_exc()

    except KeyError as e:
        print(f"Error with column name:\n{e}.\n\nPlease check your './data/config.csv' for this constant name.\n")
        # Optionally, print all data frame column names for debugging
        print("All data frame column names for debugging:")
        print_data_frame_headers(data_frames)
        raise e
    except Exception as e:
        print(f"An unexpected error occurred:\n{e}")
        raise  e

if __name__ == "__main__":
    main()
