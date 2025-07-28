# -*- coding: utf-8 -*-
"""
Created on Mon Jun 30 10:48:17 2025

@author: dnd2129

Make sure class sections in the eval data match those that are pulled from SIS.
Identify those that do not.
"""

import pandas as pd
import re

'''
function to clean course number
'''
def clean_course_num(course):
    # Make sure it's a string, strip whitespace, and convert to uppercase
    course = str(course).strip().upper()

    # Extract the first letter and a 4-digit number at the end
    match = re.search(r'([A-Z])[A-Z]*[\s-]?(\d{4})$', course)
    if match:
        return match.group(1) + match.group(2)
    return course  # Fallback if pattern doesn't match



'''
actual code
'''

course_evals_long = pd.read_csv("Z:/Individual Folders/Dyuthi Dinesh (dnd2129)/Task - Clean Historical Evaluation Data/Task - Clean Historical Evaluation Data/course_evaluations_long_20001_to_20243.csv")
SIS_instructor = pd.read_excel("Z:/Individual Folders/Dyuthi Dinesh (dnd2129)/Task - Clean Historical Evaluation Data/Task - Clean Historical Evaluation Data/SIS Course Instructors.xlsx")
#tcdb = pd.read_excel("TCDB_CBS_Courses.xlsx")

#cleaning columns we are using 
course_evals_long['professor_fullname'] = course_evals_long['professor_fullname'].str.strip()
course_evals_long['clean_course_number'] = course_evals_long['course_number'].apply(clean_course_num)

#Some course identifies in course_evals doesnt have term number and only have year-- so redefining unique course id
course_evals_long['new_unique_course_id'] = (
    course_evals_long['term_number'].astype(str) +
    course_evals_long['clean_course_number'].astype(str)+
    course_evals_long['section_number'].astype(str))


SIS_instructor['professor_fullname'] = SIS_instructor['Instructor_Name'].str.strip()
SIS_instructor['course_number'] = SIS_instructor['Course_Identifier'].str[-5:]
SIS_instructor['clean_course_number'] = SIS_instructor['course_number'].apply(clean_course_num)

SIS_instructor['new_unique_course_id'] = (
    SIS_instructor['Term_Identifier'].astype(str) +
    SIS_instructor['clean_course_number'].astype(str)+
    SIS_instructor['Section_Code'].astype(str))

SIS_instructor['new_unique_course_id'] =  SIS_instructor['new_unique_course_id'].fillna( SIS_instructor['Unique_id'])

#Filtering for new_unique_course_id not in SIS but in course_evals_long
merged = course_evals_long.merge(
    SIS_instructor,
    on='new_unique_course_id',     # or any other shared column
    how='left',
    indicator=True
)


not_in_SIS = merged[merged['_merge'] == 'left_only']

# course_evals_indiv_prof = pd.read_csv("Z:/Individual Folders/Dyuthi Dinesh (dnd2129)/Task - Clean Historical Evaluation Data/Task - Clean Historical Evaluation Data/final_course_evals_one_row_per_prof_per_course_per_term.csv")

# merged2 = course_evals_indiv_prof.merge(
#     not_in_SIS,
#     left_on=['new_unique_course_id', 'professor_fullname'],
#     right_on= ['new_unique_course_id', 'professor_fullname_x'],
#     how='left',
#     indicator='merge_status'  # use a unique column name
# )
# not_in_SIS = merged[merged['_merge'] == 'left_only']
#not_in_SIS.to_csv("missing SIS Courses from Course Evals.csv")
