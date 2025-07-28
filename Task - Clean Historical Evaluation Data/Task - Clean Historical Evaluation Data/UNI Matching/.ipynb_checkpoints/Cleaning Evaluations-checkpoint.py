# -*- coding: utf-8 -*-
"""
17 June 2025 12:35pm


Evaluatons: One record per course per prof per term
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

import re

'''
functions
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
code
'''

course_evals_long = pd.read_csv("course_evaluations_long_20001_to_20243.csv")
SIS_instructor = pd.read_excel("SIS Course Instructors.xlsx")
tcdb = pd.read_excel("TCDB_CBS_Courses.xlsx")

#cleaning columns we are using 
course_evals_long['professor_fullname'] = course_evals_long['professor_fullname'].str.strip()
course_evals_long['clean_course_number'] = course_evals_long['course_number'].apply(clean_course_num)

#Some course ids in course_evals doesnt have term number and only have year-- so redefining unique course id
course_evals_long['new_unique_course_id'] = (
    course_evals_long['term_number'].astype(str) +
    course_evals_long['clean_course_number'].astype(str)+
    course_evals_long['section_number'].astype(str))


# SIS_instructor['new_unique_course_id'] = (
#     SIS_instructor['Term_Identifier'].astype(str) +
#     SIS_instructor['Course_Identifier'].str[-5:] +
#     SIS_instructor['Section_Code'].astype(str)
# )



'''
1) Finding duplicates in course_evals_long based on the newly created course id and professor fullname
'''
duplicates_evals= course_evals_long[course_evals_long.duplicated(
    subset=['new_unique_course_id','professor_fullname'], keep=False)]

'''
tcdb processing
'''
#finding these courses in tcdb 
#but first creating new unique courseid for tcdb as well so that the new unique course id is standardized
tcdb['clean_CourseNum'] = tcdb['CourseNum'].apply(clean_course_num)
tcdb['new_unique_course_id'] = (
    tcdb['SemesterNum'].astype(str)+
    tcdb['clean_CourseNum'].astype(str)+
    tcdb['SectionNum'])


#Cleaning prof full name in tcdb
tcdb['prof_fullname'] = tcdb['FirstName'].str.strip() +' '+ tcdb['LastName'].str.strip()
#removing duplicates from tcdb-- as there are multiple for same
duplicates_tcdb= tcdb[tcdb.duplicated(subset=['new_unique_course_id', 
                                              'prof_fullname'], 
                                      keep=False)]
#duplicates are occuring when there are co-instructors-- so theres 2 courses with same unique ID because the instructors are diff
#Which eval do we want to fill from theat course to the evals df?? Which prof's eval?
#ORRRR are there multiple evals in course_evals BECAUSE of multiple profs?--
# evals needs one course per term PER INSTRUCTOR. 
#so match with both uniq course id and prof name-- No duplicates in tcdb now
duplicates_evals['new_unique_course_id'] = duplicates_evals['new_unique_course_id'].str.strip()
tcdb['new_unique_course_id'] = tcdb['new_unique_course_id'].str.strip()

'''
cleaning the duplicates subset fron course_evals
'''
duplicates_evals['professor_fullname'] = duplicates_evals['professor_fullname'].str.strip()
tcdb['prof_fullname'] = tcdb['prof_fullname'].str.strip()

'''
mergig duplicates subset and tcdb
'''
duplicates_evals_merged = pd.merge(duplicates_evals, tcdb, how ='left', 
                             left_on=['new_unique_course_id', 'professor_fullname'],
                             right_on= ['new_unique_course_id', 'prof_fullname'])
#only 	new_unique_course_id 20241E4108001 is present in tcdb, 
#not 	new_unique_course_id 20211E4108001-- so no matching in merge. 
'''
writing to csv
'''
duplicates_evals_merged.to_csv("evals duplicates merged with tcdb.csv")

'''
imputing duplicates with desired values for bie-course and bie_professor
'''
deduplicates_imputed = duplicates_evals_merged

# Keep rows where difference is less than 0.1
deduplicates_imputed = deduplicates_imputed[
    (abs(deduplicates_imputed['RatingCourse'] - deduplicates_imputed['bie_course']) < 0.1) &
    (abs(deduplicates_imputed['RatingInstructor'] - deduplicates_imputed['bie_professor']) < 0.1)
    ]
deduplicates_imputed = deduplicates_imputed.dropna(subset=['RatingCourse', 'bie_course', 'RatingInstructor', 'bie_professor'])


#if the difference between RatingCourse, RatingInstructor and bie_course, bie_professor <0.1, fill with RatingCourse and RatingInstructor respectively
# Fill bie_course where the absolute difference < 0.1
mask_course = (deduplicates_imputed['bie_course'].notna()) & (abs(deduplicates_imputed['bie_course'] - deduplicates_imputed['RatingCourse']) < 0.1)
deduplicates_imputed.loc[mask_course, 'bie_course'] = deduplicates_imputed.loc[mask_course, 'RatingCourse']

# Fill bie_professor where the absolute difference < 0.1
mask_prof = (deduplicates_imputed['bie_professor'].notna()) & (abs(deduplicates_imputed['bie_professor'] - deduplicates_imputed['RatingInstructor']) < 0.1)
deduplicates_imputed.loc[mask_prof, 'bie_professor'] = deduplicates_imputed.loc[mask_prof, 'RatingInstructor']

'''
removing duplicates from the main course evals df
'''
#drop evals duplicates from main df
evals_no_dupes = course_evals_long.drop_duplicates(subset=['new_unique_course_id', 'professor_fullname'], keep=False)

'''
putting the desired course evals rows (with imputed ratings) into the main course evals df to get full course evals data with correct ratings.
'''
#append deduplicated df with imputed rows from RatingCourse RatingInstructor
imputed_evals = pd.concat([evals_no_dupes, deduplicates_imputed], ignore_index=True)
non_inputed_unfixable_dupes_evals = duplicates_evals_merged[~duplicates_evals_merged.apply(tuple, axis=1).isin(deduplicates_imputed.apply(tuple, axis=1))]

'''
writing subset of not-imputed values for manual review
'''
non_inputed_unfixable_dupes_evals.to_csv("non_imputed_dupes_evals.csv")
