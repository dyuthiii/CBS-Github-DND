# -*- coding: utf-8 -*-
"""
Created on Mon Jul 14 13:51:31 2025

@author: dnd2129
Kiersten:
The datasets are one record per person per course enrolled. 
Only non-Core courses are included. 
Only full-time MBA students are included. 
All dual-degree students were excluded. 
I included the classes of 2016 through 2025. 
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from openpyxl import Workbook
import re
from utils import *


df = pd.read_excel("C:/Users/dnd2129/Documents/CBS-Github-DND/Student Cluster Analysis and LDA-20250714T173604Z-1-001/Student Cluster Analysis and LDA/raw data/Project - Student Course Clustering/Student Course Elective Enrollments Graduates 2016-2025.xlsx")

#descriptives and initial checks
df_head = df.head()          # First 5 rows
df.info()          

#categorical col value counts and dictionary of each var
col_counts = cat_counts(df)

[num_describe, 
 cat_describe, 
 null, 
 correlation_matrix] = fn_descriptives(df)

#Grouped by vars
# Group by gender, race, and elective, then count
grouped_gender = df.groupby(['Combined Gender', 
                             'combined_name', 
                             'Course_Identifier']).size().reset_index(name='count')
top_gender_electives = grouped_gender.sort_values('count', ascending=False).drop_duplicates(subset=['Combined Gender', 'combined_name', 'Course_Identifier'])


#Combined Federal Race
grouped_race = df.groupby(['Combined Federal Race', 
                             'combined_name', 
                             'Course_Identifier']).size().reset_index(name='count')
top_race_electives = grouped_race.sort_values('count', ascending=False).drop_duplicates(subset=['Combined Federal Race', 'combined_name', 'Course_Identifier'])


#SIS Citizenship
grouped_citizen = df.groupby(['SIS Citizenship', 
                             'combined_name', 
                             'Course_Identifier']).size().reset_index(name='count')
top_citizen_electives = grouped_citizen.sort_values('count', ascending=False).drop_duplicates(subset=['SIS Citizenship', 'combined_name', 'Course_Identifier'])

#Future Job Industry
grouped_job = df.groupby(['Future Job Industry', 
                             'combined_name', 
                             'Course_Identifier']).size().reset_index(name='count')
top_job_electives = grouped_job.sort_values('count', ascending=False).drop_duplicates(subset=['Future Job Industry', 'combined_name', 'Course_Identifier'])

#Future Job Function
grouped_function = df.groupby(['Future Job Function', 
                             'combined_name', 
                             'Course_Identifier']).size().reset_index(name='count')
top_function_electives = grouped_function.sort_values('count', ascending=False).drop_duplicates(subset=['Future Job Function', 'combined_name', 'Course_Identifier'])



#writing
vars = {
    "num_describe": num_describe,
    "cat_describe": cat_describe,
    "null": null,
    "cor" : correlation_matrix,
    "col_counts": col_counts,
    "top_gender_electives": top_gender_electives,
    "top_race_electives": top_race_electives,
    "top_citizen_electives": top_citizen_electives,
    "top_Future Job Industry electives": top_job_electives,
    "top_function_electives":top_function_electives
}

write_vars_to_excel("C:/Users/dnd2129/Documents/CBS-Github-DND/Student Cluster Analysis and LDA-20250714T173604Z-1-001/Student Cluster Analysis and LDA/Student Cluster Analysis and LDA spyder/data io/Course Data descriptives.xlsx", vars)


# -*- coding: utf-8 -*-
"""
Created on Thu Jul 17 14:56:29 2025

@author: dnd2129
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from openpyxl import Workbook
import re
import datetime as datetime
from utils import *


df = pd.read_excel("C:/Users/dnd2129/Documents/CBS-Github-DND/Student Cluster Analysis and LDA-20250714T173604Z-1-001/Student Cluster Analysis and LDA/raw data/Project - Student Course Clustering/Student Course Elective Enrollments Graduates 2016-2025.xlsx")
df['year'] = df["Unique_Course_ID"].str[0:4]
#popular professors-- need to merge with 'final_course_evals_one_row_per_prof_per_course_per_term'

prof_course = pd.read_csv("C:/Users/dnd2129/Documents/CBS-Github-DND/Student Cluster Analysis and LDA-20250714T173604Z-1-001/Student Cluster Analysis and LDA/Student Cluster Analysis and LDA spyder/data io/final_course_evals_one_row_per_prof_per_course_per_term.csv")

prof_course_filtd = prof_course[["new_unique_course_id", "fixed_name", "correct_map", "course_title" , "bie_course", "bie_professor"]]
#df course ID is diff-- need to change.
first_5_chars = df['Unique_Course_ID'].str[0:5]
last_8_chars = df['Unique_Course_ID'].str[-8:]
df['new_unique_course_id'] = first_5_chars + last_8_chars


#Merging dfs
coursedf_profdf = df.merge(prof_course_filtd, how="left",
                           left_on = "new_unique_course_id",
                           right_on = "new_unique_course_id", 
                           suffixes=("_course", "_prof"))

coursedf_profdf.to_csv("Course_Profs merged.csv")


#popular professors
prof_table = coursedf_profdf['fixed_name'].value_counts()


#pop profs by term identifier
coursedf_profdf["Term_Identifier"] = coursedf_profdf["Unique_Course_ID"].str[4]
counts = coursedf_profdf.groupby(["year","Term_Identifier", "fixed_name"]).size().reset_index(name="count")

# Sort within each Term_Identifier by count descending
prof_term = counts.sort_values(by=["year","Term_Identifier", "count"], ascending=[False, True, False])

'''
Each Prof popularity over time
'''
# Count how many times each prof appears in each term
counts = coursedf_profdf.groupby(["fixed_name", "Term_Identifier", "year"]).size().reset_index(name="count")

# Pivot to have terms as columns, profs as rows
pivot = counts.pivot(index=["year", "fixed_name"], columns= ["Term_Identifier"], values="count")

# Fill NaNs with 0 convert to int
pivot = pivot.fillna(0).astype(int)

# sort professors by total counts across all terms
pivot["total"] = pivot.sum(axis=1)
pivot = pivot.sort_values("total", ascending=False)


'''
#Writing
'''
prof_pop_vars = {"Popular profs": prof_table, 
                 "Popular profs by term":prof_term,
                 "Prof popularity over time": pivot}
write_vars_to_excel("C:/Users/dnd2129/Documents/CBS-Github-DND/Student Cluster Analysis and LDA-20250714T173604Z-1-001/Student Cluster Analysis and LDA/Student Cluster Analysis and LDA spyder/data io/Prof Popularity.xlsx", prof_pop_vars)







