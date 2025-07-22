# -*- coding: utf-8 -*-
"""
Created on Fri Jun 27 12:02:11 2025

@author: dnd2129

Cleaning final_evals (with UNIs) for one unique course per instructor
"""

import pandas as pd


course_evals = pd.read_excel("Z:/Individual Folders/Dyuthi Dinesh (dnd2129)/Task - Clean Historical Evaluation Data/Task - Clean Historical Evaluation Data/final_course_evals_with UNI.xlsx",
                            "final_map_with_multiple_tag") 
#THis is the NEW (1 July 2025) excel I created after adding UNIs to every prof. 


'''


 NOTICED AS KIERSTEN POINTED OUR THAT SOME unique_id in COURSE_EVALS RAW DATA 
 DON’t HAVE 13 digits!! (they are missing the term_number!!

   SO USE: new_unique_course_id WHICH I CREATED WHILE CLEANING THE PREV DATASET FOR UNI MATCHING.
'''
#checking if course id has 13 chars as it should
short_rows = course_evals[course_evals['new_unique_course_id'].astype(str).str.len() < 13]
#only 3-- ignore.
'''
Starting finding unique course per instructor per term
'''

course_evals_indiv = pd.read_excel("Z:/Individual Folders/Dyuthi Dinesh (dnd2129)/Task - Clean Historical Evaluation Data/Task - Clean Historical Evaluation Data/final_course_evals_with UNI.xlsx",
                            "Final_map_exploded")
SIS = pd.read_excel("SIS Course Instructors.xlsx")


# count number of rows with same 'unique_course_id' 
unq_course_counts = course_evals_indiv['new_unique_course_id'].value_counts().reset_index()
unq_course_counts.columns = ['new_unique_course_id', 'count']

# filtering for courses with >=2 values
multi_unq_courses = unq_course_counts[unq_course_counts['count'] >= 2]


#getting full data of these courses from course_evals_indv
multi_courses_df = course_evals_indiv[course_evals_indiv['new_unique_course_id'].isin(multi_unq_courses['new_unique_course_id'])]

#Now, we need to make sure the PROF Final_unis are diff-- and only retain rows where the new_unique_course_id and 'correct remap' are the same
# Step 1: Count occurrences of each (new_unique_course_id, correct remap) pair
pair_counts = multi_courses_df.groupby(['new_unique_course_id', 'correct_map']).size().reset_index(name='count')

# Step 2: Filter for combinations that occur more than once
duplicate_pairs = pair_counts[pair_counts['count'] > 1]

# Step 3: Filter the original dataframe to keep only those (new_unique_course_id, correct remap) pairs
duplicate_pairs_course_evals = multi_courses_df.merge(duplicate_pairs[['new_unique_course_id', 'correct_map']], 
                                                      on=['new_unique_course_id', 'correct_map'], how='inner')

#duplicate_pairs_course_evals.to_csv("FINAL_duplicate_pairs_course_evals.csv")

'''
manually looked up courses on SIS and created new sheet in same xl called 'retained rows'
'''
#first, lets remove everything in the duplicated_pairs_course_evals df from course_evals_indiv
deduplicated_course_evals = course_evals_indiv.merge(
    duplicate_pairs_course_evals,
    how='left',
    indicator=True
)

# Keep only rows that were not in duplicated_pairs_course_evals
deduplicated_course_evals = deduplicated_course_evals[deduplicated_course_evals['_merge'] == 'left_only']
# Drop the merge indicator column
deduplicated_course_evals = deduplicated_course_evals.drop(columns=['_merge'])


#Now add the 'retained rows' to the deduplicated_course_evals set 
#to get one row per course per term per prof.

retained_rows = pd.read_excel("FINAL_duplicate_pairs_course_evals.xlsx",
                            "retained rows")

merged_one_row_per_prof_per_course = pd.concat([deduplicated_course_evals, retained_rows], ignore_index=True)
#merged_one_row_per_prof_per_course.to_csv("final_course_evals_one_row_per_prof_per_course_per_term.csv")

