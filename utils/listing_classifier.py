"""
Utility module for classifying listings as FBA or Merchant.
This module contains functions to separate Amazon listings into FBA and Merchant categories
based on data from multiple reports.
"""

def classify_listings(all_listings_df, fba_inventory_df=None):
    """
    Classifies listings as either FBA or Merchant based on multiple data sources.
    
    Classification logic:
    1. All SKUs from FBA inventory report are considered FBA
    2. SKUs from All Listings with fulfillment-channel=AMAZON_NA are added to FBA set
    3. Remaining SKUs from All Listings are classified as Merchant
    
    Args:
        all_listings_df (pandas.DataFrame): DataFrame containing the all_listings_report
                                           with columns: 'seller-sku', 'fulfillment-channel'
        fba_inventory_df (pandas.DataFrame, optional): DataFrame containing the FBA inventory 
                                                      report with column: 'sku'
                                                      
    Returns:
        dict: A dictionary with two keys:
              - 'fba_skus': set of SKUs classified as FBA
              - 'merchant_skus': set of SKUs classified as Merchant
    
    Example:
        >>> classification = classify_listings(all_listings_df, fba_inventory_df)
        >>> print(f"FBA count: {len(classification['fba_skus'])}")
        >>> print(f"Merchant count: {len(classification['merchant_skus'])}")
    """
    # Convert column names to lowercase if they aren't already
    all_listings_df.columns = all_listings_df.columns.str.lower()
    
    # Extract needed columns for clarity
    all_sku_col = 'seller-sku'
    all_channel_col = 'fulfillment-channel'
    
    # Verify required columns exist in all_listings_df
    required_all_cols = [all_sku_col]
    for col in required_all_cols:
        if col not in all_listings_df.columns:
            raise KeyError(f"Required column '{col}' not found in all_listings_report DataFrame")
    
    # Optional check for fulfillment-channel column
    has_channel_col = all_channel_col in all_listings_df.columns
    
    # Sanitize data - strip whitespace from SKU fields
    if all_listings_df[all_sku_col].dtype == 'object':  # Check if column is string type
        all_listings_df[all_sku_col] = all_listings_df[all_sku_col].fillna('').str.strip()
    
    # Get all unique SKUs from all_listings_df
    all_skus = set(all_listings_df[all_sku_col].unique())
    
    # Initialize the FBA SKUs set
    fba_skus = set()
    
    # Step 1: Add SKUs from FBA inventory report if provided
    if fba_inventory_df is not None:
        fba_inventory_df.columns = fba_inventory_df.columns.str.lower()
        fba_sku_col = 'sku'
        
        if fba_sku_col not in fba_inventory_df.columns:
            raise KeyError(f"Required column '{fba_sku_col}' not found in FBA inventory DataFrame")
        
        # Sanitize data
        if fba_inventory_df[fba_sku_col].dtype == 'object':
            fba_inventory_df[fba_sku_col] = fba_inventory_df[fba_sku_col].fillna('').str.strip()
            
        # Add all SKUs from FBA inventory to the fba_skus set
        fba_skus.update(fba_inventory_df[fba_sku_col].unique())
    
    # Step 2: Add SKUs from all_listings with fulfillment-channel = AMAZON_NA
    if has_channel_col:
        amazon_na_skus = all_listings_df[
            all_listings_df[all_channel_col].str.upper() == 'AMAZON_NA'
        ][all_sku_col].unique()
        
        fba_skus.update(amazon_na_skus)
    
    # Step 3: Get merchant SKUs by subtracting FBA SKUs from all SKUs
    merchant_skus = all_skus - fba_skus
    
    # Return dictionary with both sets
    return {
        'fba_skus': fba_skus,
        'merchant_skus': merchant_skus
    }

def get_inconsistent_skus(all_listings_df, fba_inventory_df):
    """
    Identifies SKUs with potential inconsistencies between reports.
    
    Finds SKUs that are marked as AMAZON_NA in all_listings_df but 
    are not present in the fba_inventory_df.
    
    Args:
        all_listings_df (pandas.DataFrame): DataFrame containing the all_listings_report
                                           with columns: 'seller-sku', 'fulfillment-channel'
        fba_inventory_df (pandas.DataFrame): DataFrame containing the FBA inventory 
                                            report with column: 'sku'
                                            
    Returns:
        set: Set of SKUs with inconsistent fulfillment data
    
    Example:
        >>> inconsistencies = get_inconsistent_skus(all_listings_df, fba_inventory_df)
        >>> print(f"Found {len(inconsistencies)} inconsistent SKUs")
    """
    # Convert column names to lowercase if they aren't already
    all_listings_df.columns = all_listings_df.columns.str.lower()
    fba_inventory_df.columns = fba_inventory_df.columns.str.lower()
    
    # Extract needed columns for clarity
    all_sku_col = 'seller-sku'
    all_channel_col = 'fulfillment-channel'
    fba_sku_col = 'sku'
    
    # Verify required columns exist
    if all_sku_col not in all_listings_df.columns:
        raise KeyError(f"Required column '{all_sku_col}' not found in all_listings_report DataFrame")
        
    if all_channel_col not in all_listings_df.columns:
        raise KeyError(f"Required column '{all_channel_col}' not found in all_listings_report DataFrame")
        
    if fba_sku_col not in fba_inventory_df.columns:
        raise KeyError(f"Required column '{fba_sku_col}' not found in FBA inventory DataFrame")
    
    # Sanitize data
    if all_listings_df[all_sku_col].dtype == 'object':
        all_listings_df[all_sku_col] = all_listings_df[all_sku_col].fillna('').str.strip()
        
    if fba_inventory_df[fba_sku_col].dtype == 'object':
        fba_inventory_df[fba_sku_col] = fba_inventory_df[fba_sku_col].fillna('').str.strip()
    
    # Get set of SKUs from FBA inventory
    fba_skus = set(fba_inventory_df[fba_sku_col].unique())
    
    # Find SKUs marked as AMAZON_NA but not in FBA inventory
    amazon_na_skus = set(all_listings_df[
        all_listings_df[all_channel_col].str.upper() == 'AMAZON_NA'
    ][all_sku_col].unique())
    
    # Return the inconsistencies
    return amazon_na_skus - fba_skus 