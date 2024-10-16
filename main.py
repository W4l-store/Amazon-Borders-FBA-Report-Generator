import pandas as pd
import os

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
    'SHP',
    'MERCHANT_SKU_W',
    'SHIPPED_W'
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
SHP = constants['SHP']
MERCHANT_SKU_W = constants['MERCHANT_SKU_W']
SHIPPED_W = constants['SHIPPED_W']

def columns_to_lower_case(df):
    """
    Convert all column names in a DataFrame to lower case.
    """
    df.columns = df.columns.str.lower()
    return df

def create_data_frame_from_file(directory):
    """
    Reads a file from the specified directory and returns a DataFrame.
    Assumes there is only one file in the directory.
    Supports CSV, TXT, and TSV files.
    Skips initial lines depending on the directory name.
    """
    # List files in the directory
    try:
        files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
    except FileNotFoundError:
        print(f"Directory '{directory}' not found.")
        return None

    # Check if there is exactly one file
    if not files:
        raise ValueError(f"No files found in directory '{directory}'")
    if len(files) > 1:
        raise ValueError(f"More than one file found in directory '{directory}'")

    file = files[0]
    file_path = os.path.join(directory, file)
    file_extension = os.path.splitext(file)[1].lower()

    # Determine if we need to skip lines based on directory name
    base_dir_name = os.path.basename(os.path.normpath(directory))
    skip_lines = 7 if base_dir_name in ['1_W', '2_W', '3_W', '4_W'] else 0  # Skip 7 lines to start from the 8th line

    # Try to read the file
    try:
        if file_extension == '.csv':
            data_frame = pd.read_csv(file_path, encoding='utf-8', skiprows=skip_lines)
        elif file_extension in ['.txt', '.tsv']:
            data_frame = pd.read_csv(file_path, sep='\t', encoding='utf-8', skiprows=skip_lines)
        else:
            raise ValueError(f"Unsupported file extension '{file_extension}' in file '{file}'")
    except UnicodeDecodeError:
        # Try with a different encoding
        try:
            if file_extension == '.csv':
                data_frame = pd.read_csv(file_path, encoding='ISO-8859-1', skiprows=skip_lines)
            elif file_extension in ['.txt', '.tsv']:
                data_frame = pd.read_csv(file_path, sep='\t', encoding='ISO-8859-1', skiprows=skip_lines)
        except Exception as e:
            print(f"Failed to read file '{file}' in directory '{directory}': {e}")
            raise e
    except Exception as e:
        print(f"Failed to read file '{file}' in directory '{directory}': {e}")
        raise e

    # Convert columns to lower case
    return columns_to_lower_case(data_frame)

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
        return data_frames

    for subdir in subdirectories:
        subdir_path = os.path.join(directory, subdir)
        if os.path.isdir(subdir_path):
            try:
                df = create_data_frame_from_file(subdir_path)
                if df is not None:
                    data_frames[subdir] = df
            except ValueError as e:
                print(f"Skipping directory '{subdir_path}': {e}")
            except Exception as e:
                print(f"An error occurred while processing directory '{subdir_path}': {e}")

    return data_frames

def update_template_with_price_data(template_df, all_listings_report_df):
    """
    Updates the 'PRICE' column in the template DataFrame using data from the 'all_listings_report_df'.
    """
    # Check if required columns exist
    if SELLER_SKU not in all_listings_report_df.columns or PRICE not in all_listings_report_df.columns:
        raise KeyError(f"Required columns '{SELLER_SKU}' or '{PRICE}' not found in 'all_listings_report_df'.")

    if SKU not in template_df.columns:
        raise KeyError(f"Column '{SKU}' not found in 'template_df'.")

    # Create a mapping from SELLER_SKU to PRICE
    price_map = all_listings_report_df.set_index(SELLER_SKU)[PRICE].to_dict()

    # Update the PRICE column in template_df using the mapping
    template_df[PRICE] = template_df[SKU].map(price_map)

    # Optional: Print SKUs that were not found in the price_map
    missing_skus = template_df[template_df[PRICE].isnull()][SKU].unique()
    if len(missing_skus) > 0:
        print(f"SKUs not found in all_listings_report: {missing_skus}")

    return template_df

def update_template_with_availability_data(template_df, FBA_inventory_report_df, restock_report_df):
    """
    Updates the 'INV' column in the template DataFrame using availability data from FBA inventory and restock reports.
    """
    # Check if required columns exist in the data frames
    required_columns_fba = [SKU, AVAILABLE]
    required_columns_restock = [MERCHANT_SKU, AVAILABLE]
    required_columns_template = [SKU]

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

    template_df[INV] = template_df[SKU].apply(get_inventory)

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
    required_columns_template = [SKU]

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

    template_df[INBOUND] = template_df[SKU].apply(get_inbound_quantity)

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

def update_template_with_sales_data(template_df, df_30, df_60, df_90, df_12_m):
    """
    Updates the template DataFrame with sales data for 30, 60, 90 days, and 12 months.
    """
    # Generate sales data dictionaries
    sales_30 = sales_to_dict(df_30)
    sales_60 = sales_to_dict(df_60)
    sales_90 = sales_to_dict(df_90)
    sales_12_m = sales_to_dict(df_12_m)

    # Update the template DataFrame
    template_df[C30] = template_df[SKU].map(sales_30).fillna(0)
    template_df[C60] = template_df[SKU].map(sales_60).fillna(0)
    template_df[C90] = template_df[SKU].map(sales_90).fillna(0)
    template_df[C12M] = template_df[SKU].map(sales_12_m).fillna(0)

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
    columns_to_clear = [PRICE, INV, INBOUND, C30, C60, C90, C12M, SHP, '1_w', '2_w', '3_w', '4_w']
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
    template_df['1_w'] = template_df[SKU].map(last_shipped_map_1_w).fillna('')
    template_df['2_w'] = template_df[SKU].map(last_shipped_map_2_w).fillna('')
    template_df['3_w'] = template_df[SKU].map(last_shipped_map_3_w).fillna('')
    template_df['4_w'] = template_df[SKU].map(last_shipped_map_4_w).fillna('')

    return template_df

def main():
    """
    Main function to orchestrate the data processing and updating the template DataFrame.
    """
    print("Starting the program")

    # Create data frames from directories
    data_frames = create_data_frames_from_directories('amazon exports')

    # Check if 'template.csv' exists
    template_file_path = './data/template.csv'
    try:
        template_df = pd.read_csv(template_file_path)
    except FileNotFoundError:
        print(f"Template file not found at '{template_file_path}'.")
        exit(1)
    except Exception as e:
        print(f"Error reading template file: {e}")
        exit(1)

    # Convert template columns to lower case
    template_df = columns_to_lower_case(template_df)

    try:
        # Pre-clean the template DataFrame
        template_df = pre_clean(template_df)

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
        if all(key in data_frames for key in ['30d', '60d', '90d', '12m']):
            template_df = update_template_with_sales_data(template_df, data_frames['30d'], data_frames['60d'], data_frames['90d'], data_frames['12m'])
        else:
            print("One or more sales data frames ('30d', '60d', '90d', '12m') not found.")

        # Update template with last shipments data
        if all(key in data_frames for key in ['1_W', '2_W', '3_W', '4_W']):
            template_df = update_template_with_last_shipments_data(template_df, data_frames['1_W'], data_frames['2_W'], data_frames['3_W'], data_frames['4_W'])
        else:
            print("One or more shipment data frames ('1_W', '2_W', '3_W', '4_W') not found.")

        # Save the result
        output_file_path = './results/result.csv'
        os.makedirs(os.path.dirname(output_file_path), exist_ok=True)
        template_df.to_csv(output_file_path, index=False)
        print(f"Program finished, results saved to '{output_file_path}'")

    except KeyError as e:
        print(f"Error with column name:\n{e}.\n\nPlease check your './data/config.csv' for this constant name.\n")
        # Optionally, print all data frame column names for debugging
        print("All data frame column names for debugging:")
        print_data_frame_headers(data_frames)
    except Exception as e:
        print(f"An unexpected error occurred:\n{e}")
        raise  # Re-raise the exception for further debugging if necessary

if __name__ == "__main__":
    main()
