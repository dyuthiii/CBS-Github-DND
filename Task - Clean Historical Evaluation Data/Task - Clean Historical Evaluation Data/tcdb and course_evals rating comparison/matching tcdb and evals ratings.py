# -*- coding: utf-8 -*-
"""
Created on Mon Jun 30 15:02:34 2025

@author: dnd2129
Identify courses that have significantly different BIEs that what is listed in the TCDB data.
"""

import pandas as pd


course_evals = pd.read_csv("final_course_evals_one_row_per_prof_per_course_per_term.csv")
tcdb = pd.read_excel("TCDB_CBS_Courses.xlsx")
tcdb['prof_fullname'] = tcdb['FirstName'].str.strip() +' '+ tcdb['LastName'].str.strip()



# Step 0: Strip whitespace from merging columns
course_evals['new_unique_course_id'] = course_evals['new_unique_course_id'].str.strip()
course_evals['fixed_name'] = course_evals['fixed_name'].str.strip()

tcdb['manual_unq_course_id'] = tcdb['manual_unq_course_id'].str.strip()
tcdb['prof_fullname'] = tcdb['prof_fullname'].str.strip()

# Step 1: Merge
merged_df = tcdb.merge(
    course_evals,
    right_on=['new_unique_course_id', 'correct_map' ],
    left_on=['manual_unq_course_id', 'UNI'],
    how='left',
    suffixes=('_tcdb', '_evals')
)

# Step 2: Round and Compare Ratings (up to 1 decimal place)
merged_df['Course_Rating_match'] = (
    round(merged_df['bie_course'], 1).fillna(-1) == round(merged_df['RatingCourse'], 1).fillna(-1)
)

merged_df['Prof_Rating_match'] = (
    round(merged_df['bie_professor'], 1).fillna(-1) == round(merged_df['RatingInstructor'], 1).fillna(-1)
)

#merged_df.to_csv("Ratings comparison tcdb v course_evals.csv")
