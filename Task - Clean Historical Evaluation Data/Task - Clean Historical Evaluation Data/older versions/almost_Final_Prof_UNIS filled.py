# -*- coding: utf-8 -*-
"""
Created on Tue Jun 17 20:55:45 2025

@author: dnd2129
"""

# -*- coding: utf-8 -*-
"""
Created on Tue Jun 17 2025
@author: dnd2129
Fill UNIs into evals data (from SIS and TCDB if required)
"""

import pandas as pd
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
    # Remove any part that is a single letter, possibly followed by punctuation
    parts = [p for p in parts if not re.match(r'^[a-z](\W*)$', p)]
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
    name = str(name).lower().replace('*', '').replace('.', '').replace(',', '')
    name = re.sub(r'\bet al\b|jr|sr|iii|iv', '', name)
    name = re.sub(r'[^a-z\s]', '', name)
    name = re.sub(r'\s+', ' ', name).strip()
    parts = name.split()
    return [p for p in parts if not re.fullmatch(r'[a-z]', p)]

def split_professors(df, col='professor_fullname'):
    df[col] = df[col].astype(str).str.split(r'\s*/\s*|\s*&\s*')
    return df.explode(col).reset_index(drop=True)

# def split_name_columns(df, source_col='professor_fullname'):
#     df[source_col] = df[source_col].astype(str).str.strip()
#     df['name_parts'] = df[source_col].apply(lambda x: clean_name_parts(remove_initials(x)))
#     df['name_1'] = df['name_parts'].apply(lambda x: x[0] if len(x) > 0 else '')
#     df['name_2'] = df['name_parts'].apply(lambda x: x[1] if len(x) > 1 else '')
#     df['name_3'] = df['name_parts'].apply(lambda x: x[2] if len(x) > 2 else '')
#     return df.drop(columns=['name_parts'])

def split_name_columns(df, source_col='professor_fullname'):
    df[source_col] = df[source_col].astype(str).str.strip()
    df['name_parts'] = df[source_col].apply(lambda x: clean_name_parts(remove_initials(x)))

    # Determine the max number of parts across all rows
    max_parts = df['name_parts'].apply(len).max()

    # Create name_1, name_2, ..., name_N columns
    for i in range(max_parts):
        df[f'name_{i+1}'] = df['name_parts'].apply(lambda x: x[i] if len(x) > i else '')

    return df.drop(columns=['name_parts'])


def build_mapping(df, name_col, uni_col, course_col):
    return {
        (normalize_name(row[name_col]), str(row[course_col]).strip().lower()): str(row[uni_col]).strip().lower()
        for _, row in df.iterrows()
    }

# ========== Matching Logic ==========

def sequential_fill(row):
    if pd.notna(row['professor_uni']) and row['professor_uni'].strip() != '':
        return row['professor_uni']

    name = normalize_name(row['professor_fullname'])
    flipped = normalize_name(flip_name(row['professor_fullname']))
    for variant in {name, flipped}:
        if variant in prof_uni_mapping:
            return prof_uni_mapping[variant]

    course = str(row['new_unique_course_id']).strip().lower()
    variants = generate_name_variants(row['professor_fullname'])
    matches = [prof_uni_course_mapping[(v, course)] for v in variants if (v, course) in prof_uni_course_mapping]
    if len(matches) == 1:
        return matches[0]

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

    tokens = clean_name_parts(row['professor_fullname'])
    mask = name_ref_df.apply(lambda r: any(tok in r['first_name'] or tok in r['last_name'] for tok in tokens), axis=1)
    matches = name_ref_df[mask]
    if len(matches) == 1:
        return matches.iloc[0]['uni']

    return row['professor_uni']


def check_names_in_map(row):
    if pd.notna(row['professor_uni']) and row['professor_uni'].strip() != '':
        return row['professor_uni']

    # Step 1: Collect all non-empty name fields dynamically (any column starting with "name_")
    name_fields = [str(row[col]) for col in row.index if col.startswith('name_') and pd.notna(row[col])]

    parts = []
    for name in name_fields:
        cleaned = name.replace('*', '').strip().lower()
        split_parts = cleaned.split()
        # Remove initials: single letter optionally followed by punctuation
        split_parts = [p for p in split_parts if not re.match(r'^[a-z](\W*)$', p)]
        parts.extend(split_parts)

    if not parts:
        return row['professor_uni']

    course = str(row['new_unique_course_id']).strip().lower()

    # Step 2: Try all 3-part permutations first
    perm_length = min(len(parts), 3)
    all_perms = permutations(parts, perm_length)

    for triplet in all_perms:
        # Pad with None to always have f, m, l structure
        f, m, l = (triplet + (None,) * (3 - len(triplet)))[:3]
        name_parts = [p for p in [f, m, l] if p]

        matches = name_ref_df[
            (
                ((name_ref_df['first_name'] == f) & (name_ref_df['last_name'] == l)) |
                ((name_ref_df['first_name'] == l) & (name_ref_df['last_name'] == f)) |
                ((name_ref_df['first_name'] == f) & (name_ref_df['last_name'] == m)) |
                ((name_ref_df['first_name'] == m) & (name_ref_df['last_name'] == f)) |
                ((name_ref_df['first_name'] == m) & (name_ref_df['last_name'] == l)) |
                ((name_ref_df['first_name'] == l) & (name_ref_df['last_name'] == m))
            ) |
            (name_ref_df['first_name'].isin(name_parts)) |
            (name_ref_df['last_name'].isin(name_parts))
        ]

        if len(matches) == 1:
            return matches.iloc[0]['uni']
        elif len(matches) > 1:
            # Try normalized first+last
            sub = matches.copy()
            sub['matched'] = sub.apply(lambda x: (normalize_name(x['first_name'] + ' ' + x['last_name']), course), axis=1)
            sub = sub[sub['matched'].isin(prof_uni_course_mapping)]
            if len(sub) == 1:
                return sub.iloc[0]['uni']

            # Try reversed
            sub = matches.copy()
            sub['matched'] = sub.apply(lambda x: (normalize_name(x['last_name'] + ' ' + x['first_name']), course), axis=1)
            sub = sub[sub['matched'].isin(prof_uni_course_mapping)]
            if len(sub) == 1:
                return sub.iloc[0]['uni']

    return row['professor_uni']


# def check_names_in_map(row):
#     if pd.notna(row['professor_uni']) and row['professor_uni'].strip() != '':
#         return row['professor_uni']

#     names = [row['name_1'], row['name_2'], row['name_3']]
#     names = [re.sub(r'[^\w\s]', '', n.strip().lower()) for n in names if n and str(n).strip() != '']
#     course = str(row['new_unique_course_id']).strip().lower()

# #checking if first or last name in course_evals is in mapping,or reverse; 
# #alternatively, just cheking if the last_name in mapping matches either the first or last name in course_evals
#     pairs = [(a, b, c) for a in names for b in names for c in names]
#     for f, m, l in pairs:
#         matches =  name_ref_df[
#         (
#             ((name_ref_df['first_name'] == f) & (name_ref_df['last_name'] == l)) |
#             ((name_ref_df['first_name'] == l) & (name_ref_df['last_name'] == f)) |
#             ((name_ref_df['first_name'] == f) & (name_ref_df['last_name'] == m)) |
#             ((name_ref_df['first_name'] == m) & (name_ref_df['last_name'] == f)) |
#             ((name_ref_df['first_name'] == m) & (name_ref_df['last_name'] == l)) |
#             ((name_ref_df['first_name'] == l) & (name_ref_df['last_name'] == m))
#         ) |
#         (name_ref_df['first_name'].isin([f, m, l])) | #Maybe remove this-- might be too general
#         (name_ref_df['last_name'].isin([f, m, l]))
#     ]

#         if len(matches) == 1:
#             return matches.iloc[0]['uni']
#         elif len(matches) > 1:
#             # First try normal order
#             sub = matches.copy()
#             sub['matched'] = sub.apply(lambda x: (normalize_name(x['first_name'] + ' ' + x['last_name']), course), axis=1)
#             sub = sub[sub['matched'].isin(prof_uni_course_mapping)]
#             if len(sub) == 1:
#                 return sub.iloc[0]['uni']

#             # Then try reversed order
#             sub = matches.copy()
#             sub['matched'] = sub.apply(lambda x: (normalize_name(x['last_name'] + ' ' + x['first_name']), course), axis=1)
#             sub = sub[sub['matched'].isin(prof_uni_course_mapping)]
#             if len(sub) == 1:
#                 return sub.iloc[0]['uni']

#     return row['professor_uni']

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



prof_uni_course_mapping = {**build_mapping(SIS, 'Instructor_Name', 'Instructor_UNI', 'new_unique_course_id'),
                           **build_mapping(tcdb, 'prof_fullname', 'UNI', 'new_unique_course_id')}

prof_uni_mapping = {
    normalize_name(remove_initials(k)): v for k, v in {
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




# ========== Apply Matching Steps ==========

course_evals['professor_fullname'] = course_evals['professor_fullname'].apply(remove_initials)
course_evals = split_name_columns(course_evals)
course_evals['professor_uni'] = course_evals.apply(sequential_fill, axis=1)

course_to_uni = course_evals[course_evals['professor_uni'].notna() & (course_evals['professor_uni'] != '')] \
    .groupby('new_unique_course_id')['professor_uni'] \
    .agg(lambda x: x.value_counts().idxmax()).to_dict()

course_evals['professor_uni'] = course_evals.apply(lambda r: course_to_uni.get(r['new_unique_course_id'], r['professor_uni']), axis=1)
course_evals['professor_uni'] = course_evals.apply(check_names_in_map, axis=1)
missing = course_evals[course_evals['professor_uni'].isna() | (course_evals['professor_uni'].str.strip() == '')]

#splitting courses with multiple profs
# course_evals = split_professors(course_evals)


# course_evals['professor_uni'] = course_evals.apply(lambda r: course_to_uni.get(r['new_unique_course_id'], r['professor_uni']), axis=1)
# course_evals['professor_uni'] = course_evals.apply(check_names_in_map, axis=1)
# missing = course_evals[course_evals['professor_uni'].isna() | (course_evals['professor_uni'].str.strip() == '')]
# ========== Output ==========

course_evals.to_csv("course_evals_with_unis.csv", index=False)
missing.to_csv("missing_unis_evals.csv", index=False)
name_ref_df.to_csv("name_Ref_df.csv")
