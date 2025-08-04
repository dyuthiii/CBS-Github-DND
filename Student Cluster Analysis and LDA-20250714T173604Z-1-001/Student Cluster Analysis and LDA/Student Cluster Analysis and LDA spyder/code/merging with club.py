# -*- coding: utf-8 -*-
"""
Created on Tue Jul 29 10:23:33 2025

@author: dnd2129

create a dataset add clubs (as binary data) to the course-job-course_list binary matrix
"""
import pandas as pd
cj = pd.read_csv("C:/Users/dnd2129/Documents/CBS-Github-DND/Student Cluster Analysis and LDA-20250714T173604Z-1-001/Student Cluster Analysis and LDA/Student Cluster Analysis and LDA spyder/data io/course-job-course_list binary matrix.csv") 
clubs = pd.read_csv("C:/Users/dnd2129/Documents/CBS-Github-DND/Student Cluster Analysis and LDA-20250714T173604Z-1-001/Student Cluster Analysis and LDA/Student Cluster Analysis and LDA spyder/data io/final club dataset merged 22 july.csv")

clubs['club_officer_flag'] = clubs['merged_final_flag'].apply(lambda x: 1 if x == True else 0)
club_uni_offlag = clubs[["UNI", "club_officer_flag"]]

clubs_bm = pd.crosstab(clubs['UNI'], clubs['common_mapped_name']).reset_index()
clubs_bm_offflag = clubs_bm.merge(club_uni_offlag, how = 'left',
                                  on = 'UNI')


#merging the clubs bm to cj
merged = cj.merge(clubs_bm_offflag, how= "left", left_on = "uni", right_on="UNI")



#now I need to get 1 row per student-- and the only reason it is multiple is the club officer flag
#grouping by uni and summing number of officer positions
one_row_per_student = merged.groupby('UNI')['club_officer_flag'].sum().reset_index()
one_row_per_student = one_row_per_student.rename(columns={'club_officer_flag': 'num_officer_positions'})

cj_clubsbm_onerow_merge = cj.merge(one_row_per_student, how= "left", left_on = "uni", right_on="UNI")
cj_clubsbm_onerow_merge.to_csv("C:/Users/dnd2129/Documents/CBS-Github-DND/Student Cluster Analysis and LDA-20250714T173604Z-1-001/Student Cluster Analysis and LDA/Student Cluster Analysis and LDA spyder/data io/course, job, clubsoffcount binary matrix.csv")
