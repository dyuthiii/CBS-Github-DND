# -*- coding: utf-8 -*-
"""
Created on Mon Jun 30 15:02:34 2025

@author: dnd2129
Identify courses that have significantly different BIEs that what is listed in the TCDB data.
"""

import pandas as pd


course_evals = pd.read_csv("final_course_evals_one_row_per_prof_per_course_per_term.csv") #this is the one row per prof per course that I created in UNI matching
tcdb = pd.read_excel("TCDB_CBS_Courses.xlsx")
tcdb['prof_fullname'] = tcdb['FirstName'].str.strip() +' '+ tcdb['LastName'].str.strip()

'''
Strip whitespace from merging columns
'''
course_evals['new_unique_course_id'] = course_evals['new_unique_course_id'].str.strip()
course_evals['fixed_name'] = course_evals['fixed_name'].str.strip()

'''
cleaning fullname and manual course id I had created on the tcdb xl file (basically re-concatted all the individual elements to be simialr to course evals df
'''
tcdb['manual_unq_course_id'] = tcdb['manual_unq_course_id'].str.strip()
tcdb['prof_fullname'] = tcdb['prof_fullname'].str.strip()

'''
Merging tcdb and course_evals data on  unique course id and prof UNI
'''
merged_df = tcdb.merge(
    course_evals,
    right_on=['new_unique_course_id', 'correct_map' ],
    left_on=['manual_unq_course_id', 'UNI'],
    how='left',
    suffixes=('_tcdb', '_evals')
)

'''
#Roundthe evaluations scores bie course and bie professor and Compare Ratings (up to 1 decimal place) to see the number of ratings that match in tcdb and course_evals dfs
'''
merged_df['Course_Rating_match'] = (
    round(merged_df['bie_course'], 1).fillna(-1) == round(merged_df['RatingCourse'], 1).fillna(-1)
)

merged_df['Prof_Rating_match'] = (
    round(merged_df['bie_professor'], 1).fillna(-1) == round(merged_df['RatingInstructor'], 1).fillna(-1)
)

#merged_df.to_csv("Ratings comparison tcdb v course_evals.csv")
