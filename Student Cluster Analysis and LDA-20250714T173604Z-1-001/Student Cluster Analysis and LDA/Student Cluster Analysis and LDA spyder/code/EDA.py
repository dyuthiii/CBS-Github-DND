# -*- coding: utf-8 -*-
"""
Created on Mon Jul 14 13:51:31 2025

@author: dnd2129
Kiersten:
The datasets are one record per person per course enrolled. 
Only non-Core courses are included. 
Only full-time MBA students are included. 
All dual-degree students were excluded. 
I included the classes of 2016 through 2025. 
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from openpyxl import Workbook
import re
from utils import *


df = pd.read_csv('Course Data Merged.csv')

#descriptives and initial checks
df_head = df.head()          # First 5 rows
df.info()          

#categorical col value counts and dictionary of each var
col_counts = cat_counts(df)

[num_describe, 
 cat_describe, 
 null, 
 correlation_matrix] = fn_descriptives(df)

#Grouped by vars
# Group by gender, race, and elective, then count
grouped_gender = df.groupby(['Combined Gender', 
                             'Class_Name (SIS)', 
                             'Course_Identifier']).size().reset_index(name='count')
top_gender_electives = grouped_gender.sort_values('count', ascending=False).drop_duplicates(subset=['Combined Gender', 'Class_Name (SIS)', 'Course_Identifier'])


#Combined Federal Race
grouped_race = df.groupby(['Combined Federal Race', 
                             'Class_Name (SIS)', 
                             'Course_Identifier']).size().reset_index(name='count')
top_race_electives = grouped_race.sort_values('count', ascending=False).drop_duplicates(subset=['Combined Federal Race', 'Class_Name (SIS)', 'Course_Identifier'])


#SIS Citizenship
grouped_citizen = df.groupby(['SIS Citizenship', 
                             'Class_Name (SIS)', 
                             'Course_Identifier']).size().reset_index(name='count')
top_citizen_electives = grouped_citizen.sort_values('count', ascending=False).drop_duplicates(subset=['SIS Citizenship', 'Class_Name (SIS)', 'Course_Identifier'])

#Future Job Industry
grouped_job = df.groupby(['Future Job Industry', 
                             'Class_Name (SIS)', 
                             'Course_Identifier']).size().reset_index(name='count')
top_job_electives = grouped_job.sort_values('count', ascending=False).drop_duplicates(subset=['Future Job Industry', 'Class_Name (SIS)', 'Course_Identifier'])

#Future Job Function
grouped_function = df.groupby(['Future Job Function', 
                             'Class_Name (SIS)', 
                             'Course_Identifier']).size().reset_index(name='count')
top_function_electives = grouped_function.sort_values('count', ascending=False).drop_duplicates(subset=['Future Job Function', 'Class_Name (SIS)', 'Course_Identifier'])



#writing
vars = {
    "num_describe": num_describe,
    "cat_describe": cat_describe,
    "null": null,
    "cor" : correlation_matrix,
    "col_counts": col_counts,
    "top_gender_electives": top_gender_electives,
    "top_race_electives": top_race_electives,
    "top_citizen_electives": top_citizen_electives,
    "top_Future Job Industry electives": top_job_electives,
    "top_function_electives":top_function_electives
}

#write_vars_to_excel("Course Data descriptives.xlsx", vars)






