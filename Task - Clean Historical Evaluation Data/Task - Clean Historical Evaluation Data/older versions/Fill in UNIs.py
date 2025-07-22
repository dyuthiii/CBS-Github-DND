# -*- coding: utf-8 -*-
"""
Created on Tue Jun 17 15:10:14 2025

@author: dnd2129
Fill UNIs into evals data (from SIS and tcdb if required)
"""
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 17 17:08:16 2025

@author: dnd2129
"""

import pandas as pd
import numpy as np
import re
from itertools import permutations

# ========== Utility Functions ==========

def clean_course_num(course):
    course = str(course).strip().upper()
    match = re.search(r'([A-Z])[A-Z]*[\s-]?(\d{4})$', course)
    return match.group(1) + match.group(2) if match else course

def normalize_name(name):
    name = str(name).replace('*', '').strip().lower()
    parts = name.split()
    if len(parts) == 3 and re.match(r'^[a-z]\.?$', parts[1]):
        parts.pop(1)
    return ' '.join(parts)

def flip_name(name):
    parts = name.strip().split()
    return ' '.join(parts[::-1]) if len(parts) >= 2 else name

def generate_name_variants(name):
    name = normalize_name(name)
    parts = name.split()
    return {name} if len(parts) < 2 else {' '.join(p) for p in permutations(parts)}

def split_professors(df, col='professor_fullname'):
    df[col] = df[col].astype(str).str.split(r'\s*/\s*|\s*&\s*')
    return df.explode(col).reset_index(drop=True)

# ========== Data Load & Preprocess ==========

course_evals = pd.read_csv("course_evaluations_long_20001_to_20243.csv")
SIS = pd.read_excel("SIS Course Instructors.xlsx")
tcdb = pd.read_excel("TCDB_CBS_Courses.xlsx")

tcdb['prof_fullname'] = tcdb['FirstName'].str.strip() + ' ' + tcdb['LastName'].str.strip()
course_evals['professor_fullname'] = course_evals['professor_fullname'].str.strip()

# Clean course numbers
course_evals['clean_course_number'] = course_evals['course_number'].apply(clean_course_num)
tcdb['clean_CourseNum'] = tcdb['CourseNum'].apply(clean_course_num)
SIS['clean_Course_Identifier'] = SIS['Course_Identifier'].apply(clean_course_num)

# Unique course IDs
course_evals['new_unique_course_id'] = course_evals['term_number'].astype(str) + course_evals['clean_course_number'] + course_evals['section_number']
tcdb['new_unique_course_id'] = tcdb['SemesterNum'].astype(str) + tcdb['clean_CourseNum'] + tcdb['SectionNum']
SIS['new_unique_course_id'] = SIS['Term_Identifier'].astype(str) + SIS['Course_Identifier'].str[-5:] + SIS['Section_Code'].astype(str)

# ========== Build Initial Mapping ==========

# Normalize names and map
def build_mapping(df, name_col, uni_col, course_col):
    return {
        (normalize_name(row[name_col]), str(row[course_col]).strip().lower()): str(row[uni_col]).strip().lower()
        for _, row in df.iterrows()
    }

prof_uni_course_mapping = {**build_mapping(SIS, 'Instructor_Name', 'Instructor_UNI', 'new_unique_course_id'),
                           **build_mapping(tcdb, 'prof_fullname', 'UNI', 'new_unique_course_id')}

# Build simple name-only mapping
prof_uni_mapping = {
    normalize_name(k): v for k, v in {
        **SIS.set_index('Instructor_Name')['Instructor_UNI'].to_dict(),
        **tcdb.set_index('prof_fullname')['UNI'].to_dict()
    }.items()
}

# ========== Fill UNIs ==========

def fill_uni(row, mapping):
    if pd.notna(row['professor_uni']) and row['professor_uni'] != '':
        return row['professor_uni']
    variants = [row['professor_fullname'], flip_name(row['professor_fullname'])]
    variants = [normalize_name(v) for v in variants]
    for var in variants:
        if var in mapping:
            return mapping[var]
    return row['professor_uni']

course_evals['professor_uni'] = course_evals.apply(lambda r: fill_uni(r, prof_uni_mapping), axis=1)
print(f"UNIs missing after initial fill: {course_evals['professor_uni'].isna().sum()}")

# Split multi-prof rows
course_evals = split_professors(course_evals)

# Repeat fill on split
course_evals['professor_uni'] = course_evals.apply(lambda r: fill_uni(r, prof_uni_mapping), axis=1)
print(f"UNIs missing after split fill: {course_evals['professor_uni'].isna().sum()}")

# ========== Match by partial name + course ==========

def partial_match_fill(row, mapping):
    if pd.notna(row['professor_uni']) and row['professor_uni'] != '':
        return row['professor_uni']
    pname = normalize_name(row['professor_fullname'])
    course = str(row['new_unique_course_id']).strip().lower()
    matches = [uni for (name, c), uni in mapping.items() if c == course and pname in name]
    return matches[0] if len(matches) == 1 else row['professor_uni']

course_evals['professor_uni'] = course_evals.apply(lambda r: partial_match_fill(r, prof_uni_course_mapping), axis=1)
print(f"UNIs missing after partial match: {course_evals['professor_uni'].isna().sum()}")

# ========== Course-based fallback ==========

# Most common UNI per course
course_to_uni = course_evals[course_evals['professor_uni'].notna() & (course_evals['professor_uni'] != '')]\
    .groupby('new_unique_course_id')['professor_uni']\
    .agg(lambda x: x.value_counts().idxmax()).to_dict()

course_evals['professor_uni'] = course_evals.apply(
    lambda r: course_to_uni.get(r['new_unique_course_id'], r['professor_uni']),
    axis=1
)
print(f"UNIs missing after course fallback: {course_evals['professor_uni'].isna().sum()}")

# ========== Flexible name permutation match ==========

def flexible_name_fill(row, mapping):
    if pd.notna(row['professor_uni']) and row['professor_uni'].strip() != '':
        return row['professor_uni']
    course = str(row['new_unique_course_id']).strip().lower()
    variants = generate_name_variants(row['professor_fullname'])
    matches = [mapping[(v, course)] for v in variants if (v, course) in mapping]
    return matches[0] if len(matches) == 1 else row['professor_uni']

course_evals['professor_uni'] = course_evals.apply(lambda r: flexible_name_fill(r, prof_uni_course_mapping), axis=1)
print(f"UNIs missing after flexible name match: {course_evals['professor_uni'].isna().sum()}")



# ========== Final Surname + First Name Matching (dropping initials) ==========

def strip_middle_initial(name):
    parts = normalize_name(name).split()
    # Remove middle initial like "Z." or "W"
    parts = [p for p in parts if not re.fullmatch(r'[a-z]\.?', p)]
    return parts

# Build mapping from surname to (first name → UNI)
surname_to_firstname_uni = {}
for fullname, uni in prof_uni_mapping.items():
    parts = strip_middle_initial(fullname)
    if len(parts) >= 2:
        surname, first_name = parts[0], parts[-1]
        if surname not in surname_to_firstname_uni:
            surname_to_firstname_uni[surname] = []
        surname_to_firstname_uni[surname].append((first_name, uni))

def surname_firstname_fill(row):
    if pd.notna(row['professor_uni']) and row['professor_uni'].strip() != '':
        return row['professor_uni']
    
    parts = strip_middle_initial(row['professor_fullname'])
    if len(parts) < 2:
        return row['professor_uni']
    
    surname = parts[0]
    first_name = parts[-1]

    candidates = surname_to_firstname_uni.get(surname, [])
    if len(candidates) == 1:
        return candidates[0][1]  # Only one person with that surname
    for fname, uni in candidates:
        if fname == first_name:
            return uni

    return row['professor_uni']

course_evals['professor_uni'] = course_evals.apply(surname_firstname_fill, axis=1)
print(f"UNIs missing after surname+firstname fallback (no initials): {course_evals['professor_uni'].isna().sum()}")

# ========== Build First & Last Name Mapping ==========

# Extract normalized first and last names from full names in the mapping
name_parts_list = []
for fullname, uni in prof_uni_mapping.items():
    parts = normalize_name(fullname).split()
    if len(parts) >= 2:
        first_name = parts[-1]
        last_name = parts[0]
        name_parts_list.append({'first_name': first_name, 'last_name': last_name, 'uni': uni})

name_parts_df = pd.DataFrame(name_parts_list)

def partial_contains_fill(row, name_parts_df):
    if pd.notna(row['professor_uni']) and row['professor_uni'].strip() != '':
        return row['professor_uni']
    
    name = normalize_name(row['professor_fullname'])
    tokens = name.split()
    if not tokens:
        return row['professor_uni']
    
    matches = name_parts_df[
        name_parts_df['first_name'].apply(lambda x: any(t in x for t in tokens)) |
        name_parts_df['last_name'].apply(lambda x: any(t in x for t in tokens))
    ]
    
    if len(matches) == 1:
        return matches.iloc[0]['uni']
    
    return row['professor_uni']
course_evals['professor_uni'] = course_evals.apply(lambda r: partial_contains_fill(r, name_parts_df), axis=1)
print(f"UNIs missing after partial text match: {course_evals['professor_uni'].isna().sum()}")
########################
import pandas as pd
import re

# --- 1. Normalize function ---
def clean_name_parts(name):
    name = str(name).lower().replace('*', '').replace('.', '')
    name = re.sub(r'\bet al\b|jr|sr|iii|iv', '', name)  # remove suffixes
    name = re.sub(r'[^a-z,\s]', '', name)  # remove punctuation except comma
    name = re.sub(r'\s+', ' ', name).strip()
    parts = name.replace(',', ' ').split()
    parts = [p for p in parts if not re.fullmatch(r'[a-z]', p)]  # remove initials
    return parts

# --- 2. Build reference table ---
ref_data = []
for fullname, uni in prof_uni_mapping.items():
    parts = clean_name_parts(fullname)
    if len(parts) >= 2:
        ref_data.append({'first_name': parts[-1], 'last_name': parts[0], 'uni': uni})
name_ref_df = pd.DataFrame(ref_data)

# --- 3. Matching function using partial containment ---
def best_partial_match(prof_name, ref_df):
    tokens = clean_name_parts(prof_name)
    if not tokens:
        return None
    
    # Match any token that appears in either first or last name
    mask = ref_df.apply(lambda row: any(tok in row['first_name'] or tok in row['last_name'] for tok in tokens), axis=1)
    matches = ref_df[mask]
    
    if len(matches) == 1:
        return matches.iloc[0]['uni']
    return None  # ambiguous or no match

course_evals['professor_uni'] = course_evals.apply(
    lambda r: r['professor_uni'] if pd.notna(r['professor_uni']) and r['professor_uni'].strip() != ''
    else best_partial_match(r['professor_fullname'], name_ref_df),
    axis=1
)

print(f"UNIs missing after deep fuzzy text mapping: {course_evals['professor_uni'].isna().sum()}")

# --- Final fallback: First token in professor_fullname matches last name in map ---
def last_name_only_fill(row, ref_df):
    if pd.notna(row['professor_uni']) and row['professor_uni'].strip() != '':
        return row['professor_uni']
    
    name = str(row['professor_fullname']).strip().lower()
    last_name = re.split(r'[\s,]+', name)[0]  # First token, assuming it's the last name
    
    matches = ref_df[ref_df['last_name'] == last_name]
    matches2 = ref_df[ref_df['first_name'] == last_name]
    if len(matches) == 1:
        return matches.iloc[0]['uni']
    
    return row['professor_uni']

course_evals['professor_uni'] = course_evals.apply(
    lambda r: last_name_only_fill(r, name_ref_df),
    axis=1
)

print(f"UNIs missing after final last-name fallback: {course_evals['professor_uni'].isna().sum()}")
###ALL PERMUTATIONS
def last_name_only_fill(row, ref_df):
    if pd.notna(row['professor_uni']) and row['professor_uni'].strip() != '':
        return row['professor_uni']

    # Normalize and split
    name = str(row['professor_fullname']).strip().lower()
    parts = re.split(r'[\s,]+', name)
    if not parts:
        return row['professor_uni']
    
    first_token = parts[0]
    last_token = parts[-1] if len(parts) > 1 else parts[0]

    # All 4 permutations
    candidates = pd.concat([
        ref_df[(ref_df['first_name'] == first_token) & (ref_df['last_name'] == last_token)],
        ref_df[(ref_df['first_name'] == last_token) & (ref_df['last_name'] == first_token)],
        ref_df[(ref_df['last_name'] == first_token)],
        ref_df[(ref_df['first_name'] == first_token)]
    ]).drop_duplicates()

    if len(candidates) == 1:
        return candidates.iloc[0]['uni']

    return row['professor_uni']

course_evals['professor_uni'] = course_evals.apply(
    lambda r: last_name_only_fill(r, name_ref_df),
    axis=1
)

print(f"UNIs missing after all 4-way name fallback: {course_evals['professor_uni'].isna().sum()}")

# ========== Output Remaining Missing UNIs ==========

missing = course_evals[course_evals['professor_uni'].isna() | (course_evals['professor_uni'].str.strip() == '')]
missing.to_csv("missing_unis_evals.csv", index=False)

# ========== Export Final Mapping ==========

prof_course_uni_df = pd.DataFrame([
    {'professor_fullname': k[0], 'new_unique_course_id': k[1], 'professor_uni': v}
    for k, v in prof_uni_course_mapping.items()
])
prof_course_uni_df.to_csv("prof_course_uni_map.csv", index=False)
