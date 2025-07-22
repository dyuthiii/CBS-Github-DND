# -*- coding: utf-8 -*-
"""
Created on Tue Jun 10 15:14:24 2025

@author: dnd2129
"""
import pandas as pd
import numpy as np
from openpyxl import Workbook
import re

#Numerical descriptives fn
def fn_descriptives(df): 
    num_describe = df.describe()      # Descriptive stats (numerical vars only)
    cat_describe = df.describe(include='object')  # Categorical column stats
    #missing values
    df_null = df.isnull().sum().sort_values(ascending=False)
    #cor matrix
    correlation_matrix = df.corr(numeric_only=True)
    return num_describe, cat_describe, df_null, correlation_matrix

#categorical var counts dictionary
def cat_counts(df):
    col_counts = {}
    for col in df.select_dtypes(include='object'):
        col_counts[col] = df[col].value_counts()
    return col_counts

def sanitize_sheet_name(name):
    # Replace invalid characters with underscore and truncate to 31 characters
    return re.sub(r'[\\/*?:\[\]]', '_', name)[:31]

def write_vars_to_excel(filename, variables):
    file_path = filename 
    with pd.ExcelWriter(file_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
        for sheet_name, data in variables.items():
            sheet_name_clean = sanitize_sheet_name(sheet_name)
            if isinstance(data, pd.DataFrame):
                df = data
                df.to_excel(writer, sheet_name=sheet_name_clean, index=True)
            elif isinstance(data, pd.Series):
                df = data.to_frame(name='Count')
                df.index.name = sheet_name
                df.to_excel(writer, sheet_name=sheet_name_clean)
            elif isinstance(data, dict):
                for sub_sheet_name, series in data.items():
                    sub_sheet_name_clean = sanitize_sheet_name(sub_sheet_name)
                    sub_df = series.to_frame(name='Count')
                    sub_df.index.name = sub_sheet_name
                    sub_df.to_excel(writer, sheet_name=sub_sheet_name_clean)
            else:
                df = pd.DataFrame(data)
                df.to_excel(writer, sheet_name=sheet_name_clean, index=True)
