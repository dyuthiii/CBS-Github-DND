# -*- coding: utf-8 -*-
"""
Created on Mon Jun 23 11:50:48 2025

@author: dnd2129
"""
import pandas as pd
import re

df = pd.read_excel("Z:/Individual Folders/Dyuthi Dinesh (dnd2129)/Task - Clean Historical Evaluation Data/Task - Clean Historical Evaluation Data/final_course_evals_with UNI.xlsx", 
                   "final_map_with_multiple")

df_multiple = df[df['fixed_name'] == 'multiple']

name_ref_df= pd.read_excel("Z:/Individual Folders/Dyuthi Dinesh (dnd2129)/Task - Clean Historical Evaluation Data/Task - Clean Historical Evaluation Data/final_course_evals_with UNI.xlsx", 
                         "Name-UNI masterlist")
course_to_uni_df= pd.read_csv('Z:/Individual Folders/Dyuthi Dinesh (dnd2129)/Task - Clean Historical Evaluation Data/Task - Clean Historical Evaluation Data/UNI Matching/ensemble_course_uni map.csv')
def clean_name_parts(name):
    name = str(name).lower().replace('*', '').replace('.', '').replace(',', '')
    name = re.sub(r'\bet al\b|jr|sr|iii|iv', '', name)
    name = re.sub(r'[^a-z\s]', '', name)
    name = re.sub(r'\s+', ' ', name).strip()
    return [p for p in name.split() if not re.fullmatch(r'[a-z]', p)]

def split_professors(df, col= 'professor_fullname'):
    df[col] = df[col].astype(str).str.split(r'\s*/\s*|\s*&\s*')
    return df.explode(col).reset_index(drop=True)

def split_name_columns(df, source_col='professor_fullname'):
    df[source_col] = df[source_col].astype(str).str.strip()
    df['name_parts'] = df[source_col].apply(lambda x: clean_name_parts())
    max_parts = df['name_parts'].apply(len).max()
    for i in range(max_parts):
        df[f'name_{i+1}'] = df['name_parts'].apply(lambda x: x[i] if len(x) > i else '')
    return df.drop(columns=['name_parts'])

def match_by_first_last_course(row):
    if pd.notna(row['professor_uni']) and row['professor_uni'].strip() != '':
        return row['professor_uni']


    for name in row['clean_professor_fullname']:
            # Try token as first_name and other_token as last_name
            match = name_ref_df[
                (name_ref_df['first_name'] == name) | 
                (name_ref_df['last_name'] == name)
            ]
            if len(match) == 1:
                return match.iloc[0]['uni']
            
            
            #try one name and courseID
            match = name_ref_df[
                ((name_ref_df['first_name'] == name) |
                (name_ref_df['last_name'] == name)) & 
                (course_to_uni_df['course'] == row['unique_id'])
            ]
            if len(match) == 1:
                return match.iloc[0]['uni']

    return ''


df_multiple_explode = split_professors(df_multiple)
df_multiple_explode['clean_professor_fullname'] = df_multiple_explode['professor_fullname'].apply(lambda x: clean_name_parts(x))


# df_multiple_explode['professor_uni'] = ''
df_multiple_explode['multi_professor_uni'] = df_multiple_explode.apply(match_by_first_last_course, axis=1)
missing = df_multiple_explode[df_multiple_explode['multi_professor_uni'].isna() | (df_multiple_explode['multi_professor_uni'].str.strip() == '')]

df_multiple_explode.to_csv("final multi_profs exploded.csv")

#missing.to_csv("final multiple_profs_missing.csv", index = True)
