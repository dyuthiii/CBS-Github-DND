# -*- coding: utf-8 -*-
"""
Created on Mon Jul 14 13:38:05 2025

@author: dnd2129
"""
import pandas as pd

data_list= ["Z:\Individual Folders\Dyuthi Dinesh (dnd2129)\Student Cluster Analysis and LDA-20250714T173604Z-1-001\Student Cluster Analysis and LDA\Course Data 2016.csv",
"Z:\Individual Folders\Dyuthi Dinesh (dnd2129)\Student Cluster Analysis and LDA-20250714T173604Z-1-001\Student Cluster Analysis and LDA\Course Data 2017.csv",
"Z:\Individual Folders\Dyuthi Dinesh (dnd2129)\Student Cluster Analysis and LDA-20250714T173604Z-1-001\Student Cluster Analysis and LDA\Course Data 2018.csv",
"Z:\Individual Folders\Dyuthi Dinesh (dnd2129)\Student Cluster Analysis and LDA-20250714T173604Z-1-001\Student Cluster Analysis and LDA\Course Data 2019.csv",
"Z:\Individual Folders\Dyuthi Dinesh (dnd2129)\Student Cluster Analysis and LDA-20250714T173604Z-1-001\Student Cluster Analysis and LDA\Course Data 2020.csv",
"Z:\Individual Folders\Dyuthi Dinesh (dnd2129)\Student Cluster Analysis and LDA-20250714T173604Z-1-001\Student Cluster Analysis and LDA\Course Data 2021.csv",
"Z:\Individual Folders\Dyuthi Dinesh (dnd2129)\Student Cluster Analysis and LDA-20250714T173604Z-1-001\Student Cluster Analysis and LDA\Course Data 2022.csv",
"Z:\Individual Folders\Dyuthi Dinesh (dnd2129)\Student Cluster Analysis and LDA-20250714T173604Z-1-001\Student Cluster Analysis and LDA\Course Data 2023.csv",
"Z:\Individual Folders\Dyuthi Dinesh (dnd2129)\Student Cluster Analysis and LDA-20250714T173604Z-1-001\Student Cluster Analysis and LDA\Course Data 2024.csv",
"Z:\Individual Folders\Dyuthi Dinesh (dnd2129)\Student Cluster Analysis and LDA-20250714T173604Z-1-001\Student Cluster Analysis and LDA\Course Data 2025.csv"]

final_df= pd.DataFrame()

for file in data_list:
    df = pd.read_csv(file)
    final_df = pd.concat([final_df, df], ignore_index=True) 


final_df.to_csv("Course Data Merged.csv")
