# -*- coding: utf-8 -*-
"""
Created on Thu Jul 17 15:43:55 2025

@author: dnd2129
Ran on colab and copied code here.
"""

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

df = pd.read_csv('Course Data Merged.csv')

#unique courses
len(set(df['Class_Name (SIS)'])) #628 unique courses.


#corr matrix too large so im only gonna take top 20 courses
top_20_courses = df['Class_Name (SIS)'].value_counts().nlargest(20).index
df = df[df['Class_Name (SIS)'].isin(top_20_courses)]
np.shape(df)

# Get  random sample of students
unique_students = df['UNI'].unique()
np.random.seed(42) #im setting this seed here so we get same sample here on out.
sampled_students = np.random.choice(unique_students, size=250, replace=False)
sampled_df = df[df['UNI'].isin(sampled_students)]

sampled_df.head()
np.shape(sampled_df)

# Step 1: Create a binary matrix — rows = students, columns = courses
binary_matrix = sampled_df.pivot_table(
    index='UNI',
    columns='Class_Name (SIS)',
    aggfunc=lambda x: 1,  # mark 1 if the student took the course
    fill_value=0
)
binary_matrix.head()

# Step 2: Compute the correlation (or co-occurrence) matrix
course_corr = binary_matrix.corr()
course_corr.head()

#course_corr.to_csv('random sample (all courses) course_corr.csv')


# Step 3: Plot heatmap
plt.figure(figsize=(12, 10))
sns.heatmap(course_corr, cmap='coolwarm', center=0, annot=False)
plt.title("Elective Course Co-Taking Correlation Heatmap")
plt.xticks(rotation=90)
plt.yticks(rotation=0)
plt.tight_layout()
plt.show()