# -*- coding: utf-8 -*-
"""
Created on Thu Jun 19 13:35:33 2025
@author: dnd2129
"""

import pandas as pd
import re
import torch
from rapidfuzz import fuzz
from sentence_transformers import SentenceTransformer, util

'''
Loading data
'''
course_evals = pd.read_csv("course_evaluations_long_20001_to_20243.csv")
SIS = pd.read_excel("SIS Course Instructors.xlsx")
tcdb = pd.read_excel("TCDB_CBS_Courses.xlsx")

'''
Build full names for tcdb-- cleaning names by removing whitespace and concating first and last name in tcdbas other datasets have fullname.
'''
tcdb['prof_fullname'] = tcdb['FirstName'].astype(str).str.strip() + ' ' + tcdb['LastName'].astype(str).str.strip()
course_evals['professor_fullname'] = course_evals['professor_fullname'].astype(str).str.strip()

'''
Helper functions to normalize prof names across datasets
'''
def normalize_name(name):
    """Normalize by removing punctuation, initials, whitespace, lowercase"""
    name = str(name).lower().strip()
    name = re.sub(r'[^\w\s]', '', name)
    name = re.sub(r'\b[a-z]\b', '', name)  # remove single-letter initials
    name = re.sub(r'\s+', '', name)
    return name
    
'''
Building a map with prof names and UNIs from SIS and tcdb
'''
def build_reference_bank(SIS, tcdb):
    # Combine and drop rows with missing names or UNIs
    combined = {
        **SIS.set_index('Instructor_Name')['Instructor_UNI'].dropna().to_dict(),
        **tcdb.set_index('prof_fullname')['UNI'].dropna().to_dict()
    }

    # Dictionary to Normalize names (removing ws and lowering case
    ref_dict = {
        normalize_name(k): v.strip().lower()
        for k, v in combined.items()
        if isinstance(k, str) and isinstance(v, str)
    }

    ref_names = list(ref_dict.keys())
    ref_unis = list(ref_dict.values())

    #Generate embeddings & sentence transformer for matching prof and UNI
    model = SentenceTransformer("all-MiniLM-L6-v2")
    ref_embeddings = model.encode(ref_names, convert_to_tensor=True)

    return ref_dict, ref_names, ref_unis, ref_embeddings, model

'''
Functions for name- UNI matching (models using embedding matches)
'''
def exact_match(norm_name, ref_dict):
    return ref_dict.get(norm_name)

def fuzzy_match(norm_name, ref_dict, threshold=90):
    best_score = 0
    best_uni = None
    for ref_norm, uni in ref_dict.items():
        score = fuzz.token_sort_ratio(norm_name, ref_norm)
        if score > best_score and score >= threshold:
            best_score = score
            best_uni = uni
    return best_uni

def embedding_match(name, ref_names, ref_embeddings, ref_unis, model, threshold=0.85):
    query_vec = model.encode(name, convert_to_tensor=True)
    scores = util.cos_sim(query_vec, ref_embeddings)[0]
    best_idx = torch.argmax(scores).item()
    if scores[best_idx] >= threshold:
        return ref_unis[best_idx]
    return None

'''
Runnign Ensemble model for matchign name-prof in course_evals dataset
'''

def map_unis_ensemble(course_evals_df, ref_dict, ref_names, ref_unis, ref_embeddings, model):
    def match_all(row):
        raw_name = row['professor_fullname']
        norm_name = normalize_name(raw_name)

        # Tier 1: Exact matches
        uni = exact_match(norm_name, ref_dict)
        if uni:
            return uni

        # Tier 2: Fuzzy matches
        uni = fuzzy_match(norm_name, ref_dict)
        if uni:
            return uni

        # Tier 3: Embedding matches
        uni = embedding_match(raw_name, ref_names, ref_embeddings, ref_unis, model)
        return uni

    course_evals_df['professor_uni'] = course_evals_df.apply(match_all, axis=1)
    return course_evals_df

'''
Running 
'''

ref_dict, ref_names, ref_unis, ref_embeddings, model = build_reference_bank(SIS, tcdb)
course_evals = map_unis_ensemble(course_evals, ref_dict, ref_names, ref_unis, ref_embeddings, model)

'''
Check for missing UNIs after all the matches
'''

missing = course_evals[course_evals['professor_uni'].isna() | (course_evals['professor_uni'].str.strip() == '')]
print("❗ Unmatched rows:", len(missing))

# Optional: Save results
course_evals.to_csv("course_evals_with_unis.csv", index=False)
missing.to_csv("unmatched_professors.csv", index=False)


'''
PART 2: MANUALLY MAPPING UNIS to PROF without mdoels
'''
###########______________Not SPLITTING NAMES YET

#++++++++++++++++++++++++Manual+++++++++++++++++++++++
import pandas as pd
import re
from itertools import permutations

'''
Helper functions for cleaning 
'''

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

'''
Main mapping functions
'''

def map_unis_by_loose_name_match(course_evals_df, name_ref_df):
    course_evals_df['normalized_professor_fullname'] = course_evals_df['professor_fullname'].apply(normalize_name) #normalizing fullname
    
    name_ref_df['full_name'] = name_ref_df['first_name'].astype(str) + name_ref_df['last_name'].astype(str) #splitting to first and last name
    name_ref_df['normalized_ref_name'] = name_ref_df['full_name'].apply(normalize_name) #normalizing names in the reference map 
    
    ref_name_to_uni = dict(zip(name_ref_df['normalized_ref_name'], name_ref_df['uni'])) #returning normalized name and UNI matches

    def match_uni(row):
        norm = row['normalized_professor_fullname']
        # Try direct match
        if norm in ref_name_to_uni:
            return ref_name_to_uni[norm] #fullname match
        # Try fuzzy containment
        for ref_norm, uni in ref_name_to_uni.items():
            if ref_norm in norm or norm in ref_norm: #if parts of name matches
                return uni
        return row.get('professor_uni', '')

    course_evals_df['professor_uni'] = course_evals_df.apply(match_uni, axis=1)
    course_evals_df.drop(columns=['normalized_professor_fullname'], inplace=True)
    return course_evals_df

'''
Load and clean data
'''

# course_evals = pd.read_csv("course_evaluations_long_20001_to_20243.csv")
# SIS = pd.read_excel("SIS Course Instructors.xlsx")
# tcdb = pd.read_excel("TCDB_CBS_Courses.xlsx")

'''
# Build full names for tcdb
'''
tcdb['prof_fullname'] = tcdb['FirstName'].str.strip() + ' ' + tcdb['LastName'].str.strip()
course_evals['professor_fullname'] = course_evals['professor_fullname'].str.strip()

'''
# Normalize course identifiers for all dfs
'''
course_evals['clean_course_number'] = course_evals['course_number'].apply(clean_course_num)
tcdb['clean_CourseNum'] = tcdb['CourseNum'].apply(clean_course_num)
SIS['clean_Course_Identifier'] = SIS['Course_Identifier'].apply(clean_course_num)

course_evals['new_unique_course_id'] = course_evals['term_number'].astype(str) + course_evals['clean_course_number'] + course_evals['section_number']
tcdb['new_unique_course_id'] = tcdb['SemesterNum'].astype(str) + tcdb['clean_CourseNum'] + tcdb['SectionNum']
SIS['new_unique_course_id'] = SIS['Term_Identifier'].astype(str) + SIS['Course_Identifier'].str[-5:] + SIS['Section_Code'].astype(str)

'''
Building mappings for course-professor-UNI
'''
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
name_ref_df = name_ref_df.drop_duplicates(subset=['first_name', 'last_name'], keep='first')
# === Run Mapping ===

course_evals = map_unis_by_loose_name_match(course_evals, name_ref_df)

# === Check for missing matches ===
missing2 = course_evals[course_evals['professor_uni'].isna() | (course_evals['professor_uni'].str.strip() == '')]



'''
MANUAL PART 2: SPLITTING FULL NAME 
'''
##########Splitting into just 2 names ###############

# Fixed and cleaned version of your matching code

import pandas as pd
import re
from itertools import permutations

'''
helper functions
'''

def normalize_name(name):
    name = str(name).replace('*', '').strip().lower()
    name = re.sub(r'[\W_]', '', name)  # remove punctuation
    return name

def remove_initials(name):
    parts = str(name).strip().split()
    return ' '.join([p for p in parts if not re.fullmatch(r'[a-zA-Z]\.?', p)])

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
    return [p for p in name.split() if not re.fullmatch(r'[a-z]', p)]

def split_name_columns(df, source_col='professor_fullname'):
    df[source_col] = df[source_col].astype(str).str.strip()
    df['name_parts'] = df[source_col].apply(lambda x: clean_name_parts(remove_initials(x)))
    max_parts = df['name_parts'].apply(len).max()
    for i in range(max_parts):
        df[f'name_{i+1}'] = df['name_parts'].apply(lambda x: x[i] if len(x) > i else '')
    return df.drop(columns=['name_parts'])

'''
functions for name matching
'''

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

    # Step 1: Clean and extract valid name tokens
    raw_tokens = [row.get(col, '') for col in row.index if col.startswith('name_')]
    tokens = [re.sub(r'[^\w\s]', '', n.strip().lower()) for n in raw_tokens if n and str(n).strip() != '']
    course = str(row['new_unique_course_id']).strip().lower()

    # Step 2: Generate all 2-part pairs
    from itertools import permutations
    pairs = list(permutations(tokens, 2)) #permutations of names

    for f, l in pairs:
        # Try normal (f l) and reversed (l f) combinations
        for first, last in [(f, l), (l, f)]:
            norm_name = normalize_name(f"{first} {last}")
            key = (norm_name, course)
            if key in prof_uni_course_mapping:
                return prof_uni_course_mapping[key]

        # Try name_ref_df direct lookup checking permutations of name parts to see if any of them match-- looking for two parts to match atleast to avoid incorrect matching
        matches = name_ref_df[
            ((name_ref_df['first_name'] == f) & (name_ref_df['last_name'] == l)) |
            ((name_ref_df['first_name'] == l) & (name_ref_df['last_name'] == f)) |
            (name_ref_df['first_name'].isin([f, l])) |
            (name_ref_df['last_name'].isin([f, l]))
        ]

        if len(matches) == 1: #if exactly one match is found, return UNI
            return matches.iloc[0]['uni']
        elif len(matches) > 1: #If more than one match is found-- need to narrow down. 
            # Try to narrow down with course-aware normalized keys
            matches['matched_key'] = matches.apply(
                lambda x: (normalize_name(f"{x['first_name']} {x['last_name']}"), course), axis=1
            )
            matches = matches[matches['matched_key'].isin(prof_uni_course_mapping)]
            if len(matches) == 1:
                return prof_uni_course_mapping[matches.iloc[0]['matched_key']]

    return row.get('professor_uni', '')



'''
applying matching steps
'''

course_evals['professor_fullname'] = course_evals['professor_fullname'].apply(remove_initials)
course_evals = split_name_columns(course_evals)
course_evals['professor_uni'] = course_evals.apply(sequential_fill, axis=1)

course_to_uni = course_evals[course_evals['professor_uni'].notna() & (course_evals['professor_uni'] != '')] \
    .groupby('new_unique_course_id')['professor_uni'] \
    .agg(lambda x: x.value_counts().idxmax()).to_dict()

course_evals['professor_uni'] = course_evals.apply(lambda r: course_to_uni.get(r['new_unique_course_id'], r['professor_uni']), axis=1)
course_evals['professor_uni'] = course_evals.apply(check_names_in_map, axis=1)
missing3 = course_evals[course_evals['professor_uni'].isna() | (course_evals['professor_uni'].str.strip() == '')]


'''
STEP 4: MANUAL 3: CHECKING EACH NAME COLUMN FROM COURSE EVALS IN MAP Last name
'''

'''
#just matching for the last name in the map if either name part matches last name from map
'''
def match_by_last_name(row):
    if pd.notna(row['professor_uni']) and row['professor_uni'].strip() != '':
        return row['professor_uni']
    name_parts = [row[col] for col in row.index if col.startswith('name_') and pd.notna(row[col])]
    for token in name_parts:
        matches = name_ref_df[name_ref_df['last_name'] == token.lower()] 
        if len(matches) == 1: #if match is exactly 1-- returning the UNI.
            return matches.iloc[0]['uni']
    
    return ''

'''
# Apply match function
'''
course_evals['professor_uni'] = course_evals.apply(match_by_last_name, axis=1)
missing4 = course_evals[course_evals['professor_uni'].isna() | (course_evals['professor_uni'].str.strip() == '')]

'''
trying to match any name part with first name
'''
def match_by_first_name(row):
    if pd.notna(row['professor_uni']) and row['professor_uni'].strip() != '':
        return row['professor_uni']

    name_parts = [row[col] for col in row.index if col.startswith('name_') and pd.notna(row[col])]
    for token in name_parts:
        matches = name_ref_df[name_ref_df['first_name'] == token.lower()]
        if len(matches) == 1:
            return matches.iloc[0]['uni']
    
    return ''


'''
apply match function
'''
course_evals['professor_uni'] = course_evals.apply(match_by_first_name, axis=1)
missing5 = course_evals[course_evals['professor_uni'].isna() | (course_evals['professor_uni'].str.strip() == '')] #finding missing UNIs


'''
more match functions for different permutations again by tokenizing name
'''
def match_by_first_last_name(row):
    if pd.notna(row['professor_uni']) and row['professor_uni'].strip() != '':
        return row['professor_uni']

    name_parts = [row[col] for col in row.index if col.startswith('name_') and pd.notna(row[col])]
    name_parts = [n.lower() for n in name_parts]

    for i, token in enumerate(name_parts):
        for j, other_token in enumerate(name_parts):
            if i == j:
                continue
            # Try token as first_name and other_token as last_name
            match = name_ref_df[
                (name_ref_df['first_name'] == token) & 
                (name_ref_df['last_name'] == other_token)
            ]
            if len(match) == 1:
                return match.iloc[0]['uni']
            
            # Try flipped: token as last_name and other_token as first_name
            match = name_ref_df[
                (name_ref_df['first_name'] == other_token) & 
                (name_ref_df['last_name'] == token)
            ]
            if len(match) == 1:
                return match.iloc[0]['uni']

    return ''

'''
# Apply this function
'''
course_evals['professor_uni'] = course_evals.apply(match_by_first_last_name, axis=1)
missing6 = course_evals[course_evals['professor_uni'].isna() | (course_evals['professor_uni'].str.strip() == '')]


'''
writing all to csvs
'''

course_evals.to_csv("ensemble_course_evals_with_unis.csv", index=False)
missing.to_csv("ensemble_missing_unis_evals.csv", index=False)
name_ref_df.to_csv("ensemble_name_Ref_df.csv")



course_to_uni_df = pd.DataFrame(course_to_uni, index = [1])
course_to_uni_df = course_to_uni_df.T
course_to_uni_df.to_csv("ensemble_course_uni map.csv", index = True)
