# -*- coding: utf-8 -*-
"""
Created on Mon Jul 21 11:19:23 2025

@author: dnd2129
see colab
"""

import pandas as pd
import numpy as np

df = pd.read_csv('one row per student.csv')
#print(list(df.columns))

print(df['Program Type'].value_counts()) #all full time MBA
print(df['Program'].value_counts()) #all MBA

#cross tabbing Future Job Function and Future Job Industry
df_jf = pd.crosstab(df["UNI"], df["Future Job Function"])
df_ji = pd.crosstab(df["UNI"], df["Future Job Industry"])

jobs_merged = df_jf.merge(df_ji, how = "left", on="UNI")


df_binary = df.merge(jobs_merged, how="left", on="UNI")
df_binary.to_csv("IV DV binary one row per student.csv")

'''
Adding a col with all course names 
for each student for later use (refering after K-Means etc)
'''
# Assume course_cols is the list of all course columns (binary indicators)
course_cols = list(df.drop(['PID', 'UNI', 'Grad_Class_Of', 'billing_program_school', 
                 'Program', 'Program Type',  
                  'Future Job Function', 'Future Job Industry','Unnamed: 0'], 
                       axis=1))

# Create a new column 'courses_taken' with a string list of courses taken
df['courses_taken'] = df[course_cols].apply(
    lambda row: [course for course in course_cols if row[course] == 1], axis=1
)

# Optionally, convert the list to a comma-separated string instead of list
df['courses_taken_str'] = df['courses_taken'].apply(lambda x: ', '.join(x))
df.to_csv("IV DV binary one row per student.csv")
