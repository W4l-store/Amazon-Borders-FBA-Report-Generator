import pandas as pd
from utils.helpers import a_ph, retrieve_B_sku_mapping, retrieve_BS_sku_mapping
from utils.update_resources import update_resources
from utils.fba_merchant_mapping import create_fba_merchant_mapping
from utils.listing_classifier import classify_listings


def preper_new_template_csv(all_listings_report, fba_inventory_report):
    """
    Prepare a new template CSV file based on the all listings report.
    This function updates SKU mappings, creates a new template, and identifies potential unmapped borders.
    
    Args:
        all_listings_report (pd.DataFrame): The all listings report data.
        fba_inventory_report (pd.DataFrame): The FBA inventory report data.
    
    Raises:
        Exception: If any step in the process fails.
    """
 
    # Step 1: Update SKU mapping data
    try:
        print("Retrieving current SKU mapping data")
        update_resources()
        print("SKU mapping data successfully updated")
    except Exception as e:
        print(f"Error retrieving current SKU mapping data: {e}")
        raise 

    # Step 2: Create new template CSV
    try:
        print("Creating new template CSV")
        create_new_template_csv(all_listings_report, fba_inventory_report)
        print("New template CSV successfully created")
    except Exception as e:
        print(f"Error creating new template CSV: {e}")
        raise e

    # Step 3: Identify potential unmapped borders
    try:    
        print("Checking for potential unmapped borders")
        potential_not_mapped_borders = get_potential_not_mapped_borders(all_listings_report)
        
        if len(potential_not_mapped_borders) == 0:
            print("No potential unmapped borders found")
        else:
            # Save potential unmapped borders to a CSV file
            num_unmapped = len(potential_not_mapped_borders)
            print(f"Found {num_unmapped} potential unmapped borders")
            
            output_path = a_ph('/results/potential_not_mapped_borders.csv')
            potential_not_mapped_borders.to_csv(output_path, index=False)
            print(f"Potential unmapped borders saved to: {output_path}")
            print("Please review and update the SKU mapping for listings in the CSV file")
    except Exception as e:
        print(f"Error checking for potential unmapped borders: {e}")
        raise e

    print("New template CSV preparation completed successfully")


def create_new_template_csv(all_listings_report, fba_inventory_report):
    """
    Create a new template CSV file based on the all listings report and FBA inventory report.
    
    Args:
        all_listings_report (pd.DataFrame): The all listings report data.
        fba_inventory_report (pd.DataFrame): The FBA inventory report data.
    """
    # Define the initial columns for the template
    initial_columns = ['Title', 'ASIN', 'WMA forecast', 'Rec Ship', 'SHP', 'N_Price', 'Price', '1_W', '2_W', '3_W', '4_W', 'Inbound', 'Inv', '30', '60', '90', '12m', '2yr', 'M_30', 'M_12m', 'Parts__Num', 'FBA_SKU', 'M_SKU', 'Status']
    
    # Create a new DataFrame with the initial columns
    new_template_df = pd.DataFrame(columns=initial_columns)
    
    # Get all borders listings without filtering by fulfillment channel
    borders_listings = get_borders_listings_from_all_listings_report(all_listings_report)
    
    # Classify listings as FBA or Merchant
    classification = classify_listings(all_listings_report, fba_inventory_report)
    fba_skus = classification['fba_skus']
    merchant_skus = classification['merchant_skus']
    
    # Create FBA to Merchant SKU mapping
    fba_merchant_mapping = create_fba_merchant_mapping(all_listings_report, fba_inventory_report)
    
    # PART 1: Add FBA listings to template
    fba_template = add_fba_listings_to_template(borders_listings, fba_skus, fba_merchant_mapping, initial_columns)
    
    # PART 2: Add standalone FBM listings to template
    template_with_fbm = add_fbm_listings_to_template(borders_listings, merchant_skus, fba_template, fba_merchant_mapping)
    
    # PART 3: Add Parts__Num mapping after both FBA and FBM listings are added
    final_template = add_parts_num_mapping(template_with_fbm, fba_merchant_mapping)
    
    # Save the updated template to a CSV file
    final_template.to_csv(a_ph('/data/template.csv'), index=False)


def add_fba_listings_to_template(borders_listings, fba_skus, fba_merchant_mapping, initial_columns):
    """
    Add FBA listings to the template.
    
    Args:
        borders_listings (pd.DataFrame): The borders listings data.
        fba_skus (set): Set of SKUs classified as FBA.
        fba_merchant_mapping (dict): Mapping of FBA SKUs to Merchant SKUs.
        initial_columns (list): List of columns for the template.
        
    Returns:
        pd.DataFrame: Template with FBA listings added.
    """
    # Create a new DataFrame with the initial columns
    fba_template = pd.DataFrame(columns=initial_columns)
    
    # Filter borders_listings to only include FBA SKUs
    if 'SKU' in borders_listings.columns:
        fba_borders = borders_listings[borders_listings['SKU'].isin(fba_skus)].copy()
        
        # Fill fba_template with data from fba_borders for the required columns
        for col in ['Title', 'ASIN', 'Parts__Num', 'Status']:
            if col in fba_borders.columns:
                fba_template[col] = fba_borders[col]
        
        # Map the SKU column to FBA_SKU
        fba_template['FBA_SKU'] = fba_borders['SKU']
        
        # Add M_SKU column with merchant SKUs from the mapping
        fba_template['M_SKU'] = fba_template['FBA_SKU'].apply(
            lambda fba_sku: ', '.join(fba_merchant_mapping.get(fba_sku, [])) if fba_sku in fba_merchant_mapping else ''
        )
    
    return fba_template


def add_fbm_listings_to_template(borders_listings, merchant_skus, fba_template, fba_merchant_mapping):
    """
    Add standalone FBM (Merchant) listings to the template.
    These are border listings that only exist as merchant fulfilled, without FBA counterparts.
    
    Args:
        borders_listings (pd.DataFrame): The borders listings data
        merchant_skus (set): Set of SKUs classified as Merchant
        fba_template (pd.DataFrame): Template with FBA listings already added
        fba_merchant_mapping (dict): Mapping of FBA SKUs to Merchant SKUs
        
    Returns:
        pd.DataFrame: Template with both FBA and standalone FBM listings
    """
    # Get all merchant SKUs that are mapped to FBA SKUs
    mapped_merchant_skus = set()
    for fba_sku, m_skus in fba_merchant_mapping.items():
        mapped_merchant_skus.update(m_skus)
    
    # Get standalone merchant SKUs (those not mapped to any FBA SKU)
    standalone_merchant_skus = merchant_skus - mapped_merchant_skus
    
    # Filter borders_listings to get only standalone merchant listings
    standalone_merchant_borders = borders_listings[
        borders_listings['SKU'].isin(standalone_merchant_skus)
    ].copy()
    
    # If no standalone merchant listings found, return the original template
    if len(standalone_merchant_borders) == 0:
        return fba_template
        
    # Create DataFrame for standalone merchant listings
    merchant_template = pd.DataFrame(columns=fba_template.columns)
    
    # Copy relevant columns from standalone_merchant_borders
    for col in ['Title', 'ASIN', 'Status']:
        if col in standalone_merchant_borders.columns:
            merchant_template[col] = standalone_merchant_borders[col]
    
    # Set FBA_SKU to "-" for standalone merchant listings
    merchant_template['FBA_SKU'] = "-"
    
    # Set M_SKU to the merchant SKU
    merchant_template['M_SKU'] = standalone_merchant_borders['SKU']
    
    # Combine FBA template with merchant template
    final_template = pd.concat([fba_template, merchant_template], ignore_index=True)
    
    return final_template


def add_parts_num_mapping(template_df, fba_merchant_mapping):
    """
    Add Parts__Num mapping to the template after both FBA and FBM listings are added.
    Maps Parts__Num based on either FBA SKU or its corresponding merchant SKUs.
    
    Args:
        template_df (pd.DataFrame): Template with both FBA and merchant SKUs
        fba_merchant_mapping (dict): Mapping between FBA and merchant SKUs
        
    Returns:
        pd.DataFrame: Template with Parts__Num mapping added
    """
    amazon_sku_to_B_sku = retrieve_B_sku_mapping()
    
    # Create a copy to avoid modifying the original
    result_df = template_df.copy()
    
    # Iterate through each row in the template
    for idx, row in result_df.iterrows():
        fba_sku = row['FBA_SKU']
        merchant_skus = row['M_SKU'].split(', ') if row['M_SKU'] else []
        
        # First try to map using FBA SKU
        if fba_sku in amazon_sku_to_B_sku:
            result_df.at[idx, 'Parts__Num'] = amazon_sku_to_B_sku[fba_sku]
            continue
            
        # If no FBA mapping, try merchant SKUs
        mapped = False
        for m_sku in merchant_skus:
            if m_sku and m_sku in amazon_sku_to_B_sku:
                result_df.at[idx, 'Parts__Num'] = amazon_sku_to_B_sku[m_sku]
                mapped = True
                break
                
        # If no mapping found at all
        if not mapped:
            result_df.at[idx, 'Parts__Num'] = "UNMAPPED_BORDER"
    
    return result_df


def get_borders_listings_from_all_listings_report(all_listings_report_df):
    """
    Filter and process the all listings report to get borders listings.
    This function includes both mapped borders and listings with 'Border' in the title,
    without filtering by fulfillment channel.
    """
    config = read_config()
    
    # Get the column names from config
    seller_sku_col = config.get('SELLER_SKU', 'seller-sku').lower()
    asin_col = config.get('ASIN1', 'asin1').lower()
    title_col = config.get('ITEM_NAME', 'item-name').lower()
    status_col = config.get('STATUS', 'status').lower()

    # Get the B_SKU mapping
    amazon_sku_to_B_sku = retrieve_B_sku_mapping()

    # Filter the inventory report to include:
    # 1. Items that are in the B_SKU mapping
    mapped_borders = all_listings_report_df[all_listings_report_df[seller_sku_col].isin(amazon_sku_to_B_sku.keys())].copy()
    
    # 2. Items that have 'Border' in the title (without fulfillment channel filter)
    title_borders = all_listings_report_df[
        (all_listings_report_df[title_col].str.contains('Border', case=False, na=False)) &
        (~all_listings_report_df[seller_sku_col].isin(amazon_sku_to_B_sku.keys()))
    ].copy()
    
    # Combine both sets of borders
    filtered_df = pd.concat([mapped_borders, title_borders], ignore_index=True)
    
    # Rename columns to match the template
    filtered_df = filtered_df.rename(columns={title_col: 'Title', asin_col: 'ASIN', seller_sku_col: 'SKU', status_col: 'Status'})
    
    # Sort A to Z by title
    filtered_df = filtered_df.sort_values(by='Title', ascending=True).copy()
    
    # Remove duplicates if any
    filtered_df = filtered_df.drop_duplicates(subset=['SKU'], keep='first')
    
    return filtered_df


def get_potential_not_mapped_borders(all_listings_report_df):
    """
    Get listings that potentially could be not mapped borders.
    """
    config = read_config()
    amazon_sku_to_BS_sku = retrieve_BS_sku_mapping()
    amazon_sku_to_B_sku = retrieve_B_sku_mapping()
    
    # Get the column names from config
    seller_sku_col = config.get('SELLER_SKU', 'seller-sku').lower()
    title_col = config.get('ITEM_NAME', 'item-name').lower()
    price_col = config.get('PRICE', 'price').lower()
    fulfillment_col = config.get('FULFILLMENT_CHANNEL', 'fulfillment-channel').lower()
    
    # Filter the dataframe
    filtered_df = all_listings_report_df[
        (
            all_listings_report_df[title_col].str.contains('Border', case=False, na=False) |
            (all_listings_report_df[price_col].astype(float).between(6, 20))
        ) &
        (all_listings_report_df[fulfillment_col] == 'AMAZON_NA') &
        (~all_listings_report_df[seller_sku_col].isin(amazon_sku_to_BS_sku.keys())) &
        (~all_listings_report_df[seller_sku_col].isin(amazon_sku_to_B_sku.keys()))
    ]
    return filtered_df


def read_config():
    """
    Read the configuration file and return it as a dictionary.
    """
    config_file_path = a_ph('/data/config.csv')
    try:
        config_df = pd.read_csv(config_file_path, index_col='const name')
        return config_df['column name'].to_dict()
    except FileNotFoundError:
        print(f"Config file not found at '{config_file_path}'.")
        raise
    except Exception as e:
        print(f"Error reading config file: {e}")
        raise


    




