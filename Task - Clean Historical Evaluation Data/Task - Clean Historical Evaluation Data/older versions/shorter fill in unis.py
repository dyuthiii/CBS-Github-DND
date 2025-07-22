# -*- coding: utf-8 -*-
"""
Created on Tue Jun 17 2025
@author: dnd2129
Fill UNIs into evals data (from SIS and TCDB if required)
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

def remove_initials(name):
    parts = str(name).strip().split()
    return ' '.join([p for p in parts if not re.fullmatch(r'[A-Z]\.?', p, flags=re.IGNORECASE)])

def flip_name(name):
    parts = name.strip().split()
    return ' '.join(parts[::-1]) if len(parts) >= 2 else name

def generate_name_variants(name):
    name = normalize_name(name)
    parts = name.split()
    return {name} if len(parts) < 2 else {' '.join(p) for p in permutations(parts)}

def clean_name_parts(name):
    name = str(name).lower().replace('*', '').replace('.', '')
    name = re.sub(r'\bet al\b|jr|sr|iii|iv', '', name)
    name = re.sub(r'[^a-z,\s]', '', name)
    name = re.sub(r'\s+', ' ', name).strip()
    parts = name.replace(',', ' ').split()
    return [p for p in parts if not re.fullmatch(r'[a-z]', p)]

def split_professors(df, col='professor_fullname'):
    df[col] = df[col].astype(str).str.split(r'\s*/\s*|\s*&\s*')
    return df.explode(col).reset_index(drop=True)

def split_name_columns(df, source_col='professor_fullname'):
    df[source_col] = df[source_col].astype(str).str.strip()
    df['name_parts'] = df[source_col].apply(lambda x: remove_initials(x).split())
    df['name_1'] = df['name_parts'].apply(lambda x: x[0] if len(x) > 0 else '')
    df['name_2'] = df['name_parts'].apply(lambda x: x[1] if len(x) > 1 else '')
    df['name_3'] = df['name_parts'].apply(lambda x: x[2] if len(x) > 2 else '')
    return df.drop(columns=['name_parts'])

# ========== Load & Process Data ==========

course_evals = pd.read_csv("course_evaluations_long_20001_to_20243.csv")
SIS = pd.read_excel("SIS Course Instructors.xlsx")
tcdb = pd.read_excel("TCDB_CBS_Courses.xlsx")

tcdb['prof_fullname'] = tcdb['FirstName'].str.strip() + ' ' + tcdb['LastName'].str.strip()
course_evals['professor_fullname'] = course_evals['professor_fullname'].str.strip()

course_evals['clean_course_number'] = course_evals['course_number'].apply(clean_course_num)
tcdb['clean_CourseNum'] = tcdb['CourseNum'].apply(clean_course_num)
SIS['clean_Course_Identifier'] = SIS['Course_Identifier'].apply(clean_course_num)

course_evals['new_unique_course_id'] = course_evals['term_number'].astype(str) + course_evals['clean_course_number'] + course_evals['section_number']
tcdb['new_unique_course_id'] = tcdb['SemesterNum'].astype(str) + tcdb['clean_CourseNum'] + tcdb['SectionNum']
SIS['new_unique_course_id'] = SIS['Term_Identifier'].astype(str) + SIS['Course_Identifier'].str[-5:] + SIS['Section_Code'].astype(str)

# ========== Build Mappings ==========

def build_mapping(df, name_col, uni_col, course_col):
    return {
        (normalize_name(row[name_col]), str(row[course_col]).strip().lower()): str(row[uni_col]).strip().lower()
        for _, row in df.iterrows()
    }

prof_uni_course_mapping = {**build_mapping(SIS, 'Instructor_Name', 'Instructor_UNI', 'new_unique_course_id'),
                           **build_mapping(tcdb, 'prof_fullname', 'UNI', 'new_unique_course_id')}

prof_uni_mapping = {
    normalize_name(k): v for k, v in {
        **SIS.set_index('Instructor_Name')['Instructor_UNI'].to_dict(),
        **tcdb.set_index('prof_fullname')['UNI'].to_dict()
    }.items()
}

# ========== Build First/Last Name Reference Table ==========

ref_data = []
for fullname, uni in prof_uni_mapping.items():
    parts = clean_name_parts(fullname)
    if len(parts) >= 2:
        ref_data.append({'first_name': parts[-1], 'last_name': parts[0], 'uni': uni})
name_ref_df = pd.DataFrame(ref_data)

# ========== Sequential Matching ==========

def sequential_fill(row):
    if pd.notna(row['professor_uni']) and row['professor_uni'].strip() != '':
        return row['professor_uni']

    # Exact / flipped
    name = normalize_name(row['professor_fullname'])
    flipped = normalize_name(flip_name(row['professor_fullname']))
    for variant in {name, flipped}:
        if variant in prof_uni_mapping:
            return prof_uni_mapping[variant]

    # Permutation + course
    course = str(row['new_unique_course_id']).strip().lower()
    variants = generate_name_variants(row['professor_fullname'])
    matches = [prof_uni_course_mapping[(v, course)] for v in variants if (v, course) in prof_uni_course_mapping]
    if len(matches) == 1:
        return matches[0]

    # First+last direct match
    parts = clean_name_parts(row['professor_fullname'])
    if len(parts) >= 2:
        fname, lname = parts[-1], parts[0]
        candidates = pd.concat([
            name_ref_df[(name_ref_df['first_name'] == fname) & (name_ref_df['last_name'] == lname)],
            name_ref_df[(name_ref_df['first_name'] == lname) & (name_ref_df['last_name'] == fname)],
            name_ref_df[(name_ref_df['first_name'] == fname)],
            name_ref_df[(name_ref_df['last_name'] == lname)]
        ]).drop_duplicates()
        if len(candidates) == 1:
            return candidates.iloc[0]['uni']

    # Token match
    tokens = clean_name_parts(row['professor_fullname'])
    mask = name_ref_df.apply(lambda r: any(tok in r['first_name'] or tok in r['last_name'] for tok in tokens), axis=1)
    matches = name_ref_df[mask]
    if len(matches) == 1:
        return matches.iloc[0]['uni']

    return row['professor_uni']

def check_names_in_map(row):
    if pd.notna(row['professor_uni']) and row['professor_uni'].strip() != '':
        return row['professor_uni']
    names_to_check = {row['name_1'].lower().strip(), row['name_2'].lower().strip(), row['name_3'].lower().strip()} - {''}
    matches = name_ref_df[
        name_ref_df['first_name'].isin(names_to_check) |
        name_ref_df['last_name'].isin(names_to_check)
    ]
    if len(matches) == 1:
        return matches.iloc[0]['uni']
    return row['professor_uni']

# ========== Apply Matching Steps ==========

# Step 1: Remove initials
course_evals['professor_fullname'] = course_evals['professor_fullname'].apply(remove_initials)

# Step 2: Split multi-professor rows
course_evals = split_professors(course_evals)

# Step 3: Main matching function
course_evals['professor_uni'] = course_evals.apply(sequential_fill, axis=1)

# Step 4: Fallback to most frequent UNI for the course
course_to_uni = course_evals[course_evals['professor_uni'].notna() & (course_evals['professor_uni'] != '')] \
    .groupby('new_unique_course_id')['professor_uni'] \
    .agg(lambda x: x.value_counts().idxmax()).to_dict()

course_evals['professor_uni'] = course_evals.apply(lambda r: course_to_uni.get(r['new_unique_course_id'], r['professor_uni']), axis=1)

# Step 5: Add name tokens and check fallback matches
course_evals = split_name_columns(course_evals)
course_evals['professor_uni'] = course_evals.apply(check_names_in_map, axis=1)

# ========== Output ==========

course_evals.to_csv("course_evals_with_unis.csv", index=False)

missing = course_evals[course_evals['professor_uni'].isna() | (course_evals['professor_uni'].str.strip() == '')]
# missing.to_csv("missing_unis_evals.csv", index=False)
