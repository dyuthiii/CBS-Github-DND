# -*- coding: utf-8 -*-
"""
Created on Thu Jun 19 13:35:33 2025

@author: dnd2129
"""
#pip install sentence_transformers
from sentence_transformers import SentenceTransformer, util
import torch
import pandas as pd
import re


# === Load & Clean Data ===

course_evals = pd.read_csv("course_evaluations_long_20001_to_20243.csv")
SIS = pd.read_excel("SIS Course Instructors.xlsx")
tcdb = pd.read_excel("TCDB_CBS_Courses.xlsx")

# Build full names for tcdb
tcdb['prof_fullname'] = tcdb['FirstName'].str.strip() + ' ' + tcdb['LastName'].str.strip()
course_evals['professor_fullname'] = course_evals['professor_fullname'].str.strip()

# Load model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Normalize names for consistency
def normalize_name(name):
    return str(name).strip().lower()

# Build reference name list and UNIs
ref_names = list({
    normalize_name(name): uni
    for name, uni in {
        **SIS.set_index('Instructor_Name')['Instructor_UNI'].to_dict(),
        **tcdb.set_index('prof_fullname')['UNI'].to_dict()
    }.items()
}.items())

ref_texts = [name for name, _ in ref_names]
ref_unis = [uni for _, uni in ref_names]
ref_embeddings = model.encode(ref_texts, convert_to_tensor=True)

# Matching function
def embedding_match(name, ref_texts, ref_embeddings, ref_unis, threshold=0.85):
    query_vec = model.encode(name, convert_to_tensor=True)
    scores = util.cos_sim(query_vec, ref_embeddings)[0]
    best_idx = torch.argmax(scores).item()
    if scores[best_idx] >= threshold:
        return ref_unis[best_idx]
    return None

# Apply to course_evals
def semantic_map(course_evals_df):
    course_evals_df['professor_uni'] = course_evals_df['professor_fullname'].apply(
        lambda x: embedding_match(x, ref_texts, ref_embeddings, ref_unis)
    )
    return course_evals_df

missing2 = course_evals[course_evals['professor_uni'].isna() | (course_evals['professor_uni'].str.strip() == '')]

