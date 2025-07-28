# -*- coding: utf-8 -*-
"""
Created on Mon Jul 21 14:24:27 2025

@author: dnd2129
"""

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

df = pd.read_csv("C:/Users/dnd2129/Documents/CBS-Github-DND/Student Cluster Analysis and LDA-20250714T173604Z-1-001/Student Cluster Analysis and LDA/Student Cluster Analysis and LDA spyder/data io/one row per student.csv")


binary_matrix = df.iloc[:, 3:]


cor_matrix = binary_matrix.corr()

# plt.figure(figsize=(8,6))
# sns.heatmap(cor_matrix, annot=True, cmap="coolwarm", fmt=".2f", linewidths=0.5)
# plt.title("Correlation Heatmap")
# plt.show()

cor_matrix.to_csv("C:/Users/dnd2129/Documents/CBS-Github-DND/Student Cluster Analysis and LDA-20250714T173604Z-1-001/Student Cluster Analysis and LDA/Student Cluster Analysis and LDA spyder/data io/All course correlations.csv")



