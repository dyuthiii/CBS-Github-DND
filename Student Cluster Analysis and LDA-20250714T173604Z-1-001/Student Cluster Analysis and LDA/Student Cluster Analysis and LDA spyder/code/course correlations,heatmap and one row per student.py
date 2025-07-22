# -*- coding: utf-8 -*-
"""
Created on Mon Jul 21 14:24:27 2025

@author: dnd2129
"""

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

df = pd.read_csv('Course Data Merged.csv')

#unique courses
len(set(df['Class_Name (SIS)'])) #628 unique courses based on course name
len(set(df['Course_Identifier'])) # 586 Course_Identifier
len(set(df['UNI'])) #7638 students

binary_matrix = pd.crosstab(df["UNI"], df["Course_Identifier"])
cor_matrix = binary_matrix.corr()

plt.figure(figsize=(8,6))
sns.heatmap(cor_matrix, annot=True, cmap="coolwarm", fmt=".2f", linewidths=0.5)
plt.title("Correlation Heatmap")
plt.show()

#cor_matrix.to_csv("All course correlations.csv")


#merging
#merging df and coursE_binary matrix
selected_cols = ['PID', 'UNI', 'Grad_Class_Of', 'billing_program_school', 
                 'Program', 'Program Type',  
                  'Future Job Function', 'Future Job Industry']
'''
removed following cols
'Slate Citizenship 1', 'Slate Citizenship 2', 
'SIS Citizenship',
 'Domestic / International', 'Combined Federal Race', 
 'Combined Hispanic Flag', 'Combined Black Flag', 
 'Combined Gender', 'Combined Native Flag', 
 'Combined NHOPI Flag', 'Combined White Flag',
'''
filtd_df = df[df.columns.intersection(selected_cols)].drop_duplicates()

wide_df = binary_matrix.merge(filtd_df, how = 'left',on= 'UNI')

#wide_df.to_csv("one row per student.csv")

