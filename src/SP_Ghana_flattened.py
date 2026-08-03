# -*- coding: utf-8 -*-
"""
Created on Thu Nov 21 22:18:01 2024


@author: Abigail Gitonga
"""


#%% Code to extract data from API

import requests
import pandas as pd


class Items:
    url = 'https://earth-search.aws.element84.com/v1/search'

    def __init__(self, url=url):
        """Initialize the Items class.
        
        Keyword arguments:
        url -- images catalog API.
        """
        self.url = url

    def get_data(
            self, 
            bbox, 
            fields, 
            datetime, 
            limit=350, 
            ids=None, 
            #limit=None
            ):
        """Return the item parameters listed from the feature collection.
        
        Keyword arguments:
        bbox -- bounding box coordinates
        fields -- fields of interest to be specified
        datetime -- date interval for API request
        limit -- API call limit
        """
        params = {
            "bbox": bbox,
            "fields": ",".join(fields),
            "datetime": datetime,
            "limit": limit
        }       
        if ids:
            params["ids"] = ids     
        print("Sending request with params:", params)
            
        response = requests.get(self.url, params=params)
        """ Return response from GET request to STAC API"""
        response_code = response.status_code 
        if response_code == 200:
            data = response.json()
            return data
        else:
            print(f'Error {response_code}: {response.text}')
            return None
        
    def flatten_data(self, data, record_path='features'):
        """ Flatten nested data return data frame.
        
         Keyword arguments:
         data -- JSON response from get_data method
         record_path -- nested dictionary key 
        """
        if record_path in data:
            df = pd.json_normalize(data[record_path], errors='ignore')
            return df
        else:
            print(f"Key '{record_path}' not found. Returning empty DataFrame.")
            return pd.DataFrame()
        
#%% Testing API call and initialisation of class
if __name__ == "__main__":
    # Example usage / smoke test — runs only when this file is executed directly,
    # not when imported by the analysis notebook.
    bbox = "-3.24437008301, 4.71046214438, 1.0601216976, 11.0983409693"  # Ghana
    fields = [
        'properties.eo:cloud_cover',
        'properties.datetime',
        'geometry.coordinates',
        'properties.platform',
        'id'
    ]
    datetime = "2023-01-01T00:00:00Z/2023-12-31T23:59:59Z"

    # class instance
    items = Items()
    # get json version of data
    json_items = items.get_data(bbox, fields, datetime)
    # flattening response
    flattened_df = items.flatten_data(json_items)

    # checking response
    print(flattened_df.head())
    # checking length of response
    print(len(flattened_df))
