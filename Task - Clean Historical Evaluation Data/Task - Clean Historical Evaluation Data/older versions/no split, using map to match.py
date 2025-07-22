# -*- coding: utf-8 -*-
"""
Created on Thu Jun 19 12:33:50 2025
@author: dnd2129
"""

import pandas as pd
import re
from itertools import permutations

# === Helpers ===

def normalize_name(name):
    """Normalize by removing initials, punctuation, spaces, and lowercasing."""
    name = str(name).lower().strip()
    name = re.sub(r'[^\w\s]', '', name)             # remove punctuation
    name = re.sub(r'\b[a-z]\b', '', name)           # remove single-letter initials
    name = re.sub(r'\s+', '', name)                 # remove all whitespace
    return name

def clean_course_num(course):
    course = str(course).strip().upper()
    match = re.search(r'([A-Z])[A-Z]*[\s-]?(\d{4})$', course)
    return match.group(1) + match.group(2) if match else course

def clean_name_parts(name):
    name = str(name).lower().replace('*', '').replace('.', '').replace(',', '')
    name = re.sub(r'\bet al\b|jr|sr|iii|iv', '', name)
    name = re.sub(r'[^a-z\s]', '', name)
    name = re.sub(r'\s+', ' ', name).strip()
    parts = name.split()
    return [p for p in parts if not re.fullmatch(r'[a-z]', p)]

def build_mapping(df, name_col, uni_col, course_col):
    return {
        (normalize_name(row[name_col]), str(row[course_col]).strip().lower()): str(row[uni_col]).strip().lower()
        for _, row in df.iterrows()
    }

# === Main Mapping Logic ===

def map_unis_by_loose_name_match(course_evals_df, name_ref_df):
    course_evals_df['normalized_professor_fullname'] = course_evals_df['professor_fullname'].apply(normalize_name)
    
    name_ref_df['full_name'] = name_ref_df['first_name'].astype(str) + name_ref_df['last_name'].astype(str)
    name_ref_df['normalized_ref_name'] = name_ref_df['full_name'].apply(normalize_name)
    
    ref_name_to_uni = dict(zip(name_ref_df['normalized_ref_name'], name_ref_df['uni']))

    def match_uni(row):
        norm = row['normalized_professor_fullname']
        # Try direct match
        if norm in ref_name_to_uni:
            return ref_name_to_uni[norm]
        # Try fuzzy containment
        for ref_norm, uni in ref_name_to_uni.items():
            if ref_norm in norm or norm in ref_norm:
                return uni
        return row.get('professor_uni', '')

    course_evals_df['professor_uni'] = course_evals_df.apply(match_uni, axis=1)
    course_evals_df.drop(columns=['normalized_professor_fullname'], inplace=True)
    return course_evals_df

# === Load & Clean Data ===

course_evals = pd.read_csv("course_evaluations_long_20001_to_20243.csv")
SIS = pd.read_excel("SIS Course Instructors.xlsx")
tcdb = pd.read_excel("TCDB_CBS_Courses.xlsx")

# Build full names for tcdb
tcdb['prof_fullname'] = tcdb['FirstName'].str.strip() + ' ' + tcdb['LastName'].str.strip()
course_evals['professor_fullname'] = course_evals['professor_fullname'].str.strip()

# Normalize course identifiers
course_evals['clean_course_number'] = course_evals['course_number'].apply(clean_course_num)
tcdb['clean_CourseNum'] = tcdb['CourseNum'].apply(clean_course_num)
SIS['clean_Course_Identifier'] = SIS['Course_Identifier'].apply(clean_course_num)

course_evals['new_unique_course_id'] = course_evals['term_number'].astype(str) + course_evals['clean_course_number'] + course_evals['section_number']
tcdb['new_unique_course_id'] = tcdb['SemesterNum'].astype(str) + tcdb['clean_CourseNum'] + tcdb['SectionNum']
SIS['new_unique_course_id'] = SIS['Term_Identifier'].astype(str) + SIS['Course_Identifier'].str[-5:] + SIS['Section_Code'].astype(str)

# === Build Mappings ===

# 1. Course-specific prof–UNI mapping
prof_uni_course_mapping = {**build_mapping(SIS, 'Instructor_Name', 'Instructor_UNI', 'new_unique_course_id'),
                           **build_mapping(tcdb, 'prof_fullname', 'UNI', 'new_unique_course_id')}

# 2. General prof→UNI mapping (name only, not course-specific)
prof_uni_mapping = {
    normalize_name(name): uni
    for name, uni in {
        **SIS.set_index('Instructor_Name')['Instructor_UNI'].to_dict(),
        **tcdb.set_index('prof_fullname')['UNI'].to_dict()
    }.items()
}

# 3. Reference table of first/last names for matching
# Rebuild from raw names so we can extract first/last tokens before normalizing
raw_name_uni_pairs = list(SIS[['Instructor_Name', 'Instructor_UNI']].dropna().values) + \
                     list(tcdb[['prof_fullname', 'UNI']].dropna().values)

ref_data = []
for raw_name, uni in raw_name_uni_pairs:
    parts = clean_name_parts(raw_name)
    if len(parts) >= 2:
        ref_data.append({
            'first_name': parts[0],     # assume first token is first name
            'last_name': parts[-1],     # assume last token is last name
            'uni': uni.strip().lower()
        })

name_ref_df = pd.DataFrame(ref_data)

# === Run Mapping ===

course_evals = map_unis_by_loose_name_match(course_evals, name_ref_df)

# === Check for missing matches ===
missing2 = course_evals[course_evals['professor_uni'].isna() | (course_evals['professor_uni'].str.strip() == '')]
