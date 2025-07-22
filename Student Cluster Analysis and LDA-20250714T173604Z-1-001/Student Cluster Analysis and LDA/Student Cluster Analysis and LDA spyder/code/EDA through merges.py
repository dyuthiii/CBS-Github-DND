# -*- coding: utf-8 -*-
"""
Created on Thu Jul 17 14:56:29 2025

@author: dnd2129
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from openpyxl import Workbook
import re
import datetime as datetime
from utils import *


df = pd.read_csv('Course Data Merged.csv')

#popular professors-- need to merge with 'final_course_evals_one_row_per_prof_per_course_per_term'

prof_course = pd.read_csv("Z:/Individual Folders/Dyuthi Dinesh (dnd2129)/Task - Clean Historical Evaluation Data/Task - Clean Historical Evaluation Data/deduplicated evals one row per prof per course per term/final_course_evals_one_row_per_prof_per_course_per_term.csv")

prof_course_filtd = prof_course[["new_unique_course_id", "fixed_name", "correct_map", "course_title" , "bie_course", "bie_professor"]]
#df course ID is diff-- need to change.
first_5_chars = df['Unique_Course_ID'].str[0:5]
last_8_chars = df['Unique_Course_ID'].str[-8:]
df['new_unique_course_id'] = first_5_chars + last_8_chars


#Merging dfs
coursedf_profdf = df.merge(prof_course_filtd, how="left",
                           left_on = "new_unique_course_id",
                           right_on = "new_unique_course_id", 
                           suffixes=("_course", "_prof"))

#coursedf_profdf.to_csv("Course_Profs merged.csv")

#popular professors
prof_table = coursedf_profdf['fixed_name'].value_counts()


#pop profs by term identifier
counts = coursedf_profdf.groupby(["Term_Identifier", "fixed_name"]).size().reset_index(name="count")

# Sort within each Term_Identifier by count descending
prof_term = counts.sort_values(by=["Term_Identifier", "count"], ascending=[True, False])

'''
Each Prof popularity over time
'''
# Count how many times each prof appears in each term
counts = coursedf_profdf.groupby(["fixed_name", "Term_Identifier"]).size().reset_index(name="count")

# Pivot to have terms as columns, profs as rows
pivot = counts.pivot(index="fixed_name", columns="Term_Identifier", values="count")

# Fill NaNs with 0 convert to int
pivot = pivot.fillna(0).astype(int)

# sort professors by total counts across all terms
pivot["total"] = pivot.sum(axis=1)
pivot = pivot.sort_values("total", ascending=False)


'''
#Writing
'''
prof_pop_vars = {"Popular profs": prof_table, 
                 "Popular profs by term":prof_term,
                 "Prof popularity over time": pivot}
#write_vars_to_excel("Prof Popularity.xlsx", prof_pop_vars)



