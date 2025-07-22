# -*- coding: utf-8 -*-
"""
Created on Mon Jul 21 16:43:06 2025

@author: dnd2129
"""

import pandas as pd
from sklearn.decomposition import LatentDirichletAllocation
import matplotlib.pyplot as plt


df= pd.read_csv("IV DV binary one row per student.csv")
#print(list(df.columns))
course_Y = df.drop(['PID', 'UNI', 'Grad_Class_Of', 'billing_program_school', 
                 'Program', 'Program Type',  
                  'Future Job Function', 'Future Job Industry','Unnamed: 0',
                  'courses_taken_str', 'Unnamed: 0.1', 'courses_taken']
                   ,axis=1)
job_X_encoded = df[['Future Job Function', 'Future Job Industry']]

lda = LatentDirichletAllocation(n_components=4, random_state=42)  # 4 latent classes
lda_result = lda.fit_transform(course_Y)

# 3. Assign each student to the most likely latent class
df['latent_class'] = lda_result.argmax(axis=1)

# 4. Optional: inspect class composition
topic_word_dist = pd.DataFrame(lda.components_, columns=course_Y.columns)
topic_word_dist_normalized = topic_word_dist.div(topic_word_dist.sum(axis=1), axis=0)

# View top courses in each class
top_courses_by_class = topic_word_dist_normalized.apply(lambda x: x.nlargest(10).index.tolist(), axis=1)

