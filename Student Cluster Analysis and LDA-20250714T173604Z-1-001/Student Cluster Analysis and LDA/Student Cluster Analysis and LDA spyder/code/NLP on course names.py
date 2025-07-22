# -*- coding: utf-8 -*-
"""
Created on Mon Jul 21 16:43:06 2025

@author: dnd2129
"""

import pandas as pd
from sklearn.decomposition import LatentDirichletAllocation
import matplotlib.pyplot as plt
import numpy as np

df= pd.read_excel("C:/Users/dnd2129/Documents/CBS-Github-DND/Student Cluster Analysis and LDA-20250714T173604Z-1-001/Student Cluster Analysis and LDA/raw data/Project - Student Course Clustering/Student Course Elective Enrollments Graduates 2016-2025.xlsx")


#creating combined course name column-- prefer coursedog over sis
df['combined_name'] = np.where(
    df['CourseDog/SM Class Name']!= 'nan',
    df['CourseDog/SM Class Name'],
    df['SIS Class Name']
)

