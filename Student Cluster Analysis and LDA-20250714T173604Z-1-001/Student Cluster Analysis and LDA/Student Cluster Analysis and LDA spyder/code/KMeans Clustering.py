# -*- coding: utf-8 -*-
"""
Created on Mon Jul 21 15:19:20 2025

@author: dnd2129
"""

#%pip install factor_analyzer

import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA



df= pd.read_csv("data io/IV DV binary one row per student.csv")
#print(list(df.columns))
course_Y = df.drop(['PID', 'UNI', 'Grad_Class_Of', 'billing_program_school', 
                 'Program', 'Program Type',  
                  'Future Job Function', 'Future Job Industry','Unnamed: 0',
                  'courses_taken_str']
                   ,axis=1)


# STEP 1: Encode job columns (if not already)
# Use one-hot encoding or label encoding
job_X_encoded = pd.get_dummies(df[['Future Job Function', 'Future Job Industry']], drop_first=True)


'''
elbow plot for optimal clusters
'''


# Assuming X is your input features (e.g., job function + industry, encoded)
inertia = []
K_range = range(1, 11)

for k in K_range:
    kmeans = KMeans(n_clusters=k, random_state=42)
    kmeans.fit(job_X_encoded)
    inertia.append(kmeans.inertia_)

# Plotting the Elbow
plt.figure(figsize=(8, 4))
plt.plot(K_range, inertia, marker='o')
plt.xlabel('Number of Clusters (k)')
plt.ylabel('Inertia (Within-cluster SSE)')
plt.title('Elbow Method for Optimal k')
plt.grid(True)
plt.show()

#LOOKs like we can go with k=2, 3 or 4. 


'''
Run K-Means with optimal clusters= 4
'''
# Run K-Means on job data
kmeans = KMeans(n_clusters=4, random_state=42)
df['job_cluster'] = kmeans.fit_predict(job_X_encoded)



 # example for cluster 0

cluster_course = df.drop(columns=course_Y.columns)
#cluster_course.to_csv("data io/one row per student, course list with cluster (predictors jf,ji).csv")

