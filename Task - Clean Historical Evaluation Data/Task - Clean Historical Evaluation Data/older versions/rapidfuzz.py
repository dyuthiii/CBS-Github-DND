# -*- coding: utf-8 -*-
"""
Created on Thu Jun 19 13:30:14 2025

@author: dnd2129
"""

from rapidfuzz import fuzz
import re
import pandas as pd

# --- Helpers ---
def normalize_name(name):
    name = str(name).lower().strip()
    name = re.sub(r'[^\w\s]', '', name)
    name = re.sub(r'\b[a-z]\b', '', name)
    name = re.sub(r'\s+', '', name)
    return name

# --- Hybrid Matching Logic ---
def fuzzy_match_fallback(norm_name, ref_dict, threshold=90):
    best_match = None
    best_score = 0
    for ref_norm, uni in ref_dict.items():
        score = fuzz.token_sort_ratio(norm_name, ref_norm)
        if score > best_score and score >= threshold:
            best_match = uni
            best_score = score
    return best_match

def hybrid_match(row, ref_dict):
    norm = normalize_name(row['professor_fullname'])
    if norm in ref_dict:
        return ref_dict[norm]
    return fuzzy_match_fallback(norm, ref_dict)

# --- Apply to course_evals ---
def map_with_fuzzy_matching(course_evals_df, prof_uni_mapping):
    course_evals_df['professor_uni'] = course_evals_df.apply(
        lambda row: hybrid_match(row, prof_uni_mapping), axis=1
    )
    return course_evals_df
# === Load & Clean Data ===

course_evals = pd.read_csv("course_evaluations_long_20001_to_20243.csv")
SIS = pd.read_excel("SIS Course Instructors.xlsx")
tcdb = pd.read_excel("TCDB_CBS_Courses.xlsx")

# Build full names for tcdb
tcdb['prof_fullname'] = tcdb['FirstName'].str.strip() + ' ' + tcdb['LastName'].str.strip()
course_evals['professor_fullname'] = course_evals['professor_fullname'].str.strip()

# # Normalize course identifiers
# course_evals['clean_course_number'] = course_evals['course_number'].apply(clean_course_num)
# tcdb['clean_CourseNum'] = tcdb['CourseNum'].apply(clean_course_num)
# SIS['clean_Course_Identifier'] = SIS['Course_Identifier'].apply(clean_course_num)

# course_evals['new_unique_course_id'] = course_evals['term_number'].astype(str) + course_evals['clean_course_number'] + course_evals['section_number']
# tcdb['new_unique_course_id'] = tcdb['SemesterNum'].astype(str) + tcdb['clean_CourseNum'] + tcdb['SectionNum']
# SIS['new_unique_course_id'] = SIS['Term_Identifier'].astype(str) + SIS['Course_Identifier'].str[-5:] + SIS['Section_Code'].astype(str)

# Assume prof_uni_mapping is your dict: {normalized name → uni}
prof_uni_mapping = {
    normalize_name(name): uni
    for name, uni in {
        **SIS.set_index('Instructor_Name')['Instructor_UNI'].to_dict(),
        **tcdb.set_index('prof_fullname')['UNI'].to_dict()
    }.items()
}

# Run fuzzy matching on full course evals
course_evals = map_with_fuzzy_matching(course_evals, prof_uni_mapping)
missing2 = course_evals[course_evals['professor_uni'].isna() | (course_evals['professor_uni'].str.strip() == '')]

# === Load & Clean Data ===

course_evals = pd.read_csv("course_evaluations_long_20001_to_20243.csv")
SIS = pd.read_excel("SIS Course Instructors.xlsx")
tcdb = pd.read_excel("TCDB_CBS_Courses.xlsx")

# Build full names for tcdb
tcdb['prof_fullname'] = tcdb['FirstName'].str.strip() + ' ' + tcdb['LastName'].str.strip()
course_evals['professor_fullname'] = course_evals['professor_fullname'].str.strip()
