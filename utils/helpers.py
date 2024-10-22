import os
import pandas as pd

def a_ph(relative_path):
    
    root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Join the root path with the relative path, removing any leading '/'
    return os.path.join(root_path, relative_path.lstrip('/'))


def retrieve_BS_sku_mapping(region = "US", statuses_allowed=['Active', 'Inactive','Incomplete']):

    allowed_values = ["PL", "FR", "SE", "US", "NL", "UK", "MX", "CA", "BE", "ES", "IT", "DE"]
    if region not in allowed_values:
        raise ValueError(f"Invalid region '{region}'. Allowed values are {allowed_values}.")
    
    status_column = f'status_{region}'
    fulfillment = f'fulfillment_{region}'



    source_df = pd.read_csv(a_ph('/data/amazon/amz_sku_mapping.csv'), dtype=str)
    
    # filter the empty status columns
    source_df = source_df[source_df[status_column].notna()]
    source_df = source_df[source_df[status_column] != '']
    source_df = source_df[source_df[status_column].isin(statuses_allowed)]
    # filter the BS_SKU columns from nan and empty values
    source_df = source_df[source_df['BS_SKU'].notna()]
    source_df = source_df[source_df['BS_SKU'] != '']
    # filter the fulfillment column to only "DEFAULT" values
    source_df = source_df[source_df[fulfillment] == 'DEFAULT']

    # to dict map
    amazon_sku_to_BS_sku = dict(zip(source_df['seller_sku'], source_df['BS_SKU']))
    
    return amazon_sku_to_BS_sku

def retrieve_B_sku_mapping(region = "US", statuses_allowed=['Active', 'Inactive','Incomplete']):

    allowed_values = ["PL", "FR", "SE", "US", "NL", "UK", "MX", "CA", "BE", "ES", "IT", "DE"]
    if region not in allowed_values:
        raise ValueError(f"Invalid region '{region}'. Allowed values are {allowed_values}.")
    
    status_column = f'status_{region}'
    fulfillment = f'fulfillment_{region}'


    
    source_df = pd.read_csv(a_ph('/data/amazon/amz_sku_mapping.csv'), dtype=str)
    
    # filter the empty status columns
    source_df = source_df[source_df[status_column].notna()]
    source_df = source_df[source_df[status_column] != '']
    source_df = source_df[source_df[status_column].isin(statuses_allowed)]
    # filter the BS_SKU columns from nan and empty values
    source_df = source_df[source_df['B_SKU'].notna()]
    source_df = source_df[source_df['B_SKU'] != '']
    # filter the fulfillment column to only "AMAZON_NA" values
    source_df = source_df[source_df[fulfillment] == 'AMAZON_NA']

    # to dict map
    amazon_sku_to_B_sku = dict(zip(source_df['seller_sku'], source_df['B_SKU']))
    
    return amazon_sku_to_B_sku