import pandas as pd
from utils.helpers import a_ph, retrieve_B_sku_mapping, retrieve_BS_sku_mapping
from utils.update_resources import update_resources


def preper_new_template_csv(all_listings_report):
    """
    Prepare a new template CSV file based on the all listings report.
    This function updates SKU mappings, creates a new template, and identifies potential unmapped borders.
    
    Args:
        all_listings_report (pd.DataFrame): The all listings report data.
    
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
        create_new_template_csv(all_listings_report)
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


def create_new_template_csv(all_listings_report):
    """
    Create a new template CSV file based on the all listings report.
    """
    # Define the initial columns for the template
    initial_columns = ['id', 'Title', 'ASIN', 'SHP', 'N_Price', 'Price', '1_W', '2_W', '3_W', '4_W', 'Inbound', 'Inv', '30', '60', '90', '12m', '2000-2025', 'Parts__Num', 'SKU']
    
    # Create a new DataFrame with the initial columns
    new_template_df = pd.DataFrame(columns=initial_columns)
    
    # Get the borders listings
    borders_listings = get_borders_listings_from_all_listings_report(all_listings_report)
    
    # Fill new_template_df with data from borders_listings only for the required columns
    for col in ['Title', 'ASIN', 'Parts__Num', 'SKU']:
        if col in borders_listings.columns:
            new_template_df[col] = borders_listings[col]
    
    # Fill the id column with sequential numbers
    new_template_df['id'] = range(1, len(new_template_df) + 1)
    
    # Save the updated template to a CSV file
    new_template_df.to_csv(a_ph('/data/template.csv'), index=False)




def get_borders_listings_from_all_listings_report(all_listings_report_df):
    """
    Filter and process the all listings report to get borders listings.
    """
    config = read_config()
    
    # Get the column names from config
    seller_sku_col = config.get('SELLER_SKU', 'seller-sku').lower()
    asin_col = config.get('ASIN', 'asin').lower()
    title_col = config.get('ITEM_NAME', 'item-name').lower()
    status_col = config.get('STATUS', 'status').lower()

    # Get the B_SKU mapping
    amazon_sku_to_B_sku = retrieve_B_sku_mapping()

    # Filter the FBA inventory report
    filtered_df = all_listings_report_df[all_listings_report_df[seller_sku_col].isin(amazon_sku_to_B_sku.keys())].copy()
    filtered_df = filtered_df[filtered_df[status_col] == 'Active'].copy()

    # Fill Parts__Num column with the B_SKU
    filtered_df.loc[:, 'Parts__Num'] = filtered_df[seller_sku_col].map(amazon_sku_to_B_sku)
    
    # Rename columns to match the template
    filtered_df = filtered_df.rename(columns={title_col: 'Title', asin_col: 'ASIN', seller_sku_col: 'SKU'})
    
    # Sort A to Z by title
    filtered_df = filtered_df.sort_values(by='Title', ascending=True).copy()
    
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
            (all_listings_report_df[price_col].astype(float).between(17, 20))
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


    




