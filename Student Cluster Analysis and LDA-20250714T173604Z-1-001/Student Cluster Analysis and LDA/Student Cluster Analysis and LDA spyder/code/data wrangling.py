# -*- coding: utf-8 -*-
"""
Created on Mon Jul 21 11:19:23 2025

@author: dnd2129
see colab
"""

import pandas as pd
import numpy as np

df = pd.read_excel("C:/Users/dnd2129/Documents/CBS-Github-DND/Student Cluster Analysis and LDA-20250714T173604Z-1-001/Student Cluster Analysis and LDA/raw data/Project - Student Course Clustering/Student Course Elective Enrollments Graduates 2016-2025.xlsx")

#unique courses
len(set(df['combined_name'])) #577 unique courses based on course name
len(set(df['Course_Identifier'])) # 561 Course_Identifier
len(set(df['uni'])) #7625 students

binary_matrix = pd.crosstab(df["uni"], df["Course_Identifier"]).reset_index()

#merging
#merging df and coursE_binary matrix
selected_cols = ['Person ID', 'uni', 'Grad_Year', 'billing_program_school', 
                 'Program', 'Program Type',  
                  'Future Job Function', 'Future Job Industry'] #merging on the intersection of these cols.
'''
removed following cols
'Slate Citizenship 1', 'Slate Citizenship 2', 
'SIS Citizenship',
 'Domestic / International', 'Combined Federal Race', 
 'Combined Hispanic Flag', 'Combined Black Flag', 
 'Combined Gender', 'Combined Native Flag', 
 'Combined NHOPI Flag', 'Combined White Flag',
'''
#getting a filtered df with only job function, 
#job industry andcourses as binary matrix for further analysis
#one row per student per course
filtd_df = df[df.columns.intersection(selected_cols)].drop_duplicates()

wide_df = binary_matrix.merge(filtd_df, how = 'left',on= 'uni')


selected_cols2 = ['uni', 'Grad_Year']

wide_df = wide_df[wide_df.columns.intersection(selected_cols2)].drop_duplicates() 
wide_df = wide_df.merge(binary_matrix, how = 'left',on= 'uni')

wide_df.to_csv("C:/Users/dnd2129/Documents/CBS-Github-DND/Student Cluster Analysis and LDA-20250714T173604Z-1-001/Student Cluster Analysis and LDA/Student Cluster Analysis and LDA spyder/data io/one row per student.csv")
table = wide_df['uni'].value_counts() #one row per uni!


#print(list(df.columns))



#cross tabbing Future Job Function and Future Job Industry
df_jf = pd.crosstab(filtd_df["uni"], filtd_df["Future Job Function"])
df_ji = pd.crosstab(filtd_df["uni"], filtd_df["Future Job Industry"])

jobs_merged = df_jf.merge(df_ji, how = "left", on="uni")


df_job_matrix = wide_df.merge(jobs_merged, how="left", on="uni")
df_job_matrix.to_csv("C:/Users/dnd2129/Documents/CBS-Github-DND/Student Cluster Analysis and LDA-20250714T173604Z-1-001/Student Cluster Analysis and LDA/Student Cluster Analysis and LDA spyder/data io/IV DV jobs matrix one row per student.csv")

'''
Adding a col with all course names 
for each student for later use (refering after K-Means etc)
'''
# Assume course_cols is the list of all course columns (binary indicators)
course_cols = list(binary_matrix.drop(['uni'], 
                       axis=1)) #dropping all column names which arent courses

# Create a new column 'courses_taken' with a string list of courses taken
wide_df['courses_taken'] = binary_matrix[course_cols].apply(
    lambda row: [course for course in course_cols if row[course] == 1], axis=1
) #to the original df, adding all course names from the binary matrix as a list if student has taken the course



# Optionally, convert the list to a comma-separated string instead of list


wide_df['courses_taken_str'] = wide_df['courses_taken'].apply(lambda x: ', '.join(x))

wide_df.to_csv("C:/Users/dnd2129/Documents/CBS-Github-DND/Student Cluster Analysis and LDA-20250714T173604Z-1-001/Student Cluster Analysis and LDA/Student Cluster Analysis and LDA spyder/data io/IV DV binary one row per student.csv")
