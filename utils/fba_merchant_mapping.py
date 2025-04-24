"""
Utility module for mapping FBA listings to Merchant listings.
This module contains functions to create a mapping between FBA SKUs and their 
corresponding Merchant SKUs based on the same ASIN.
"""

import json
import pandas as pd
import os
from .listing_classifier import classify_listings, get_inconsistent_skus

def create_fba_merchant_mapping(all_listings_df, fba_inventory_df):
    """
    Creates a mapping between FBA SKUs and Merchant SKUs based on ASIN.
    
    The function identifies FBA SKUs using the classifier and creates mapping
    based on the all_listings_report data.
    
    Args:
        all_listings_df (pandas.DataFrame): DataFrame containing the all_listings_report
                                           with columns: 'seller-sku', 'asin1'
        fba_inventory_df (pandas.DataFrame): DataFrame containing the FBA inventory report,
                                           used only for classification
    
    Returns:
        dict: A dictionary mapping FBA SKUs to lists of corresponding Merchant SKUs
              {FBA_SKU: [MERCHANT_SKU1, MERCHANT_SKU2, ...]}
    """
    # Convert column names to lowercase if they aren't already
    all_listings_df.columns = all_listings_df.columns.str.lower()
    
    # Extract needed columns for clarity
    all_sku_col = 'seller-sku'
    all_asin_col = 'asin1'
    
    # Verify required columns exist in all_listings_df
    required_all_cols = [all_sku_col, all_asin_col]
    for col in required_all_cols:
        if col not in all_listings_df.columns:
            raise KeyError(f"Required column '{col}' not found in all_listings_report DataFrame")
    
    # Sanitize data - strip whitespace from all text fields
    for col in [all_sku_col, all_asin_col]:
        if all_listings_df[col].dtype == 'object':  # Check if column is string type
            all_listings_df[col] = all_listings_df[col].fillna('').str.strip()
    
    # Use the classifier to get FBA and Merchant SKUs
    classification = classify_listings(all_listings_df, fba_inventory_df)
    fba_skus = classification['fba_skus']
    merchant_skus = classification['merchant_skus']
    
    # Check for inconsistencies
    inconsistent_skus = get_inconsistent_skus(all_listings_df, fba_inventory_df)
    
    # Create a dictionary mapping FBA SKUs to their ASINs using all_listings_df
    fba_sku_to_asin = {}
    fba_listings = all_listings_df[all_listings_df[all_sku_col].isin(fba_skus)]
    for _, row in fba_listings.iterrows():
        sku = row[all_sku_col]
        asin = row[all_asin_col]
        if isinstance(asin, str) and asin.strip():
            fba_sku_to_asin[sku] = asin.lower()

    # Save the fba_sku_to_asin mapping to a file
    with open('fba_sku_to_asin.json', 'w') as f:
        json.dump(fba_sku_to_asin, f)
    
    # Get merchant listings using the classification results
    merchant_listings = all_listings_df[all_listings_df[all_sku_col].isin(merchant_skus)]
    
    # Create ASIN to Merchant SKU mapping for faster lookups
    asin_to_merchant = {}
    for _, row in merchant_listings.iterrows():
        asin = row[all_asin_col]
        sku = row[all_sku_col]
        # Skip empty values
        if not isinstance(asin, str) or not asin:
            continue
        asin_lower = asin.lower()
        if asin_lower in asin_to_merchant:
            asin_to_merchant[asin_lower].append(sku)
        else:
            asin_to_merchant[asin_lower] = [sku]
    
    # Create the FBA to merchant mapping
    fba_merchant_mapping = {}
    for fba_sku, asin in fba_sku_to_asin.items():
        if asin in asin_to_merchant:
            fba_merchant_mapping[fba_sku] = asin_to_merchant[asin]
        else:
            fba_merchant_mapping[fba_sku] = []
    
    # Save mapping results to file for testing
    # save_mapping_results(fba_merchant_mapping, fba_skus, merchant_skus, inconsistent_skus, all_listings_df)
    
    return fba_merchant_mapping

def save_mapping_results(fba_merchant_mapping, fba_skus, merchant_skus, inconsistent_skus, all_listings_df=None):
    """
    Save mapping results to files for testing and analysis.
    
    Args:
        fba_merchant_mapping (dict): Dictionary mapping FBA SKUs to Merchant SKUs
        fba_skus (set): Set of FBA SKUs
        merchant_skus (set): Set of Merchant SKUs
        inconsistent_skus (set): Set of inconsistent SKUs (AMAZON_NA but not in inventory)
        all_listings_df (pd.DataFrame, optional): The all listings report DataFrame
    """
    # Create results directory if it doesn't exist
    results_dir = os.path.join(os.getcwd(), 'results')
    if not os.path.exists(results_dir):
        os.makedirs(results_dir)
    
    # Save FBA to Merchant mapping
    mapping_rows = []
    for fba_sku, merchant_skus_list in fba_merchant_mapping.items():
        mapping_rows.append({
            'FBA_SKU': fba_sku,
            'Merchant_SKUs': ', '.join(merchant_skus_list),
            'Merchant_Count': len(merchant_skus_list)
        })
    
    mapping_df = pd.DataFrame(mapping_rows)
    mapping_df.to_csv(os.path.join(results_dir, 'fba_merchant_mapping.csv'), index=False)
    
    # Save inconsistencies
    if inconsistent_skus:
        with open(os.path.join(results_dir, 'inconsistent_skus.txt'), 'w') as f:
            f.write(f"Found {len(inconsistent_skus)} SKUs marked as AMAZON_NA but not in FBA inventory:\n\n")
            for sku in inconsistent_skus:
                f.write(f"{sku}\n")
    
    # Save summary statistics
    with open(os.path.join(results_dir, 'mapping_summary.txt'), 'w') as f:
        f.write("FBA and Merchant Mapping Summary\n")
        f.write("===============================\n\n")
        f.write(f"Total FBA SKUs: {len(fba_skus)}\n")
        f.write(f"Total Merchant SKUs: {len(merchant_skus)}\n")
        f.write(f"FBA SKUs with Merchant mappings: {len([k for k in fba_merchant_mapping if fba_merchant_mapping[k]])}\n")
        f.write(f"Inconsistent SKUs: {len(inconsistent_skus)}\n\n")
        
        # Percentage calculations
        total_skus = len(fba_skus) + len(merchant_skus)
        if total_skus > 0:
            f.write(f"FBA percentage: {len(fba_skus)/total_skus*100:.2f}%\n")
            f.write(f"Merchant percentage: {len(merchant_skus)/total_skus*100:.2f}%\n")
        
        if len(fba_skus) > 0:
            f.write(f"FBA SKUs with mappings: {len([k for k in fba_merchant_mapping if fba_merchant_mapping[k]])/len(fba_skus)*100:.2f}%\n")
            f.write(f"Inconsistent SKUs percentage: {len(inconsistent_skus)/len(fba_skus)*100:.2f}%\n")
    
    # Save filtered versions of All Listings Report if provided
    if all_listings_df is not None:
        all_sku_col = 'seller-sku' if 'seller-sku' in all_listings_df.columns else all_listings_df.columns[0]
        
        # Filter for FBA SKUs
        fba_listings = all_listings_df[all_listings_df[all_sku_col].isin(fba_skus)]
        fba_listings.to_csv(os.path.join(results_dir, 'fba_listings.csv'), index=False)
        
        # Filter for Merchant SKUs
        merchant_listings = all_listings_df[all_listings_df[all_sku_col].isin(merchant_skus)]
        merchant_listings.to_csv(os.path.join(results_dir, 'merchant_listings.csv'), index=False)
        
        # Save inconsistent listings
        if inconsistent_skus:
            inconsistent_listings = all_listings_df[all_listings_df[all_sku_col].isin(inconsistent_skus)]
            inconsistent_listings.to_csv(os.path.join(results_dir, 'inconsistent_listings.csv'), index=False)
        
        with open(os.path.join(results_dir, 'mapping_summary.txt'), 'a') as f:
            f.write(f"\nFiltered Listings Files:\n")
            f.write(f"FBA Listings: {len(fba_listings)} rows saved to fba_listings.csv\n")
            f.write(f"Merchant Listings: {len(merchant_listings)} rows saved to merchant_listings.csv\n")
            if inconsistent_skus:
                f.write(f"Inconsistent Listings: {len(inconsistent_listings)} rows saved to inconsistent_listings.csv\n")
    