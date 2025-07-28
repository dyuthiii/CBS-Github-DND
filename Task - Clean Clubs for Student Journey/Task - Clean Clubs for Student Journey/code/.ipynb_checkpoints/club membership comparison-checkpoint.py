# -*- coding: utf-8 -*-
"""
Created on Mon Jul  7 16:00:33 2025

@author: dnd2129
"""
import pandas as pd
import datetime as dt

athena_dta = pd.read_excel('data io/Export Student Activity - from Athena BU only.xlsx',
                         sheet_name='Sheet1', header=2)
campusgroups_dta = pd.read_excel("data io/CampusGroups Clubs.xlsx")

#how many blank start dates are there for Athena?

athena_dta['Start Date (Actual)'].replace("", pd.NA).isna().sum()
#1570

#filtering for 2019                 
athena_dta['Start Date (Actual)'] = pd.to_datetime(athena_dta['Start Date (Actual)'],
                                                   format = '%Y-%m-%d %H:%M:%S')

#14 JULY 2025-- LETS NOT DATE FILTER ATHENA because years are diff but exist.
# athena_filtd = athena_dta[athena_dta['Start Date (Actual)'].dt.year >= 2019]
athena_filtd= athena_dta

#campusgroups
campusgroups_dta['membershipStartDate'].replace("", pd.NA).isna().sum() #0 missing


campusgroups_dta['membershipStartDate'] = pd.to_datetime(campusgroups_dta['membershipStartDate'],
                                                   format = '%Y-%m-%d %H:%M:%S')

# campusgroups_filtd = campusgroups_dta[campusgroups_dta['membershipStartDate'].dt.year >= 2019]
campusgroups_filtd = campusgroups_dta

#There is only 1 row which is in 2015

'''
#Investigation 1: for 2019 onward, which club memberships exist in one file and not the other
'''
# Step 1: map club names
#sub-step- clean the club names column (remove everything before '-' in athena ,
#trim ws, lowercase etc.)


athena_filtd['club_name'] = (
    athena_filtd['Student Activity Description']
    .astype(str)
    .str.split('-', n=1)
    .str[-1]                     # take the part after the first '-'
    .str.strip()                 # remove leading/trailing whitespace
    .str.lower()                 # convert to lowercase
)


campusgroups_filtd['club_name'] = (
    campusgroups_filtd['groupName']
    .astype(str)
    .str.strip()                 # remove leading/trailing whitespace
    .str.lower()                 # convert to lowercase
)

#Checking all club names and the number of times they occur in each df
athena_filtd_clubs = athena_filtd['club_name'].value_counts()
campusgroups_filtd_clubs = campusgroups_filtd['club_name'].value_counts()
club_list = [athena_filtd_clubs, campusgroups_filtd_clubs]

# Convert value_counts to DataFrames
athena_clubs_df = athena_filtd['club_name'].value_counts().reset_index()
athena_clubs_df.columns = ['club_name', 'count']

campusgroups_clubs_df = campusgroups_filtd['club_name'].value_counts().reset_index()
campusgroups_clubs_df.columns = ['club_name', 'count']

# Write to Excel with two sheets
# with pd.ExcelWriter('data io/initial club_map.xlsx') as writer:
#     athena_clubs_df.to_excel(writer, sheet_name='athena clubs', index=False)
#     campusgroups_clubs_df.to_excel(writer, sheet_name='campusgroup clubs', index=False)





#Manually make 'combined' subsheet

std_map = pd.read_excel('data io/club_map.xlsx', 'combined')

athena_filtd = pd.merge(athena_filtd, std_map, on="club_name", how='left')
campusgroups_filtd = pd.merge(campusgroups_filtd, std_map, on="club_name", how='left')

athena_filtd_clubs_df = athena_filtd['common_mapped_name'].value_counts().reset_index()
athena_filtd_clubs_df.columns = ['common_mapped_name', 'count']

campusgroups_filtd_clubs_df = campusgroups_filtd['common_mapped_name'].value_counts().reset_index()
campusgroups_filtd_clubs_df.columns = ['common_mapped_name', 'count']


print("NaNs in campusgroups_filtd common_mapped_name:", campusgroups_filtd['common_mapped_name'].isna().sum())
print("NaNs in athena_filtd common_mapped_name:", athena_filtd['common_mapped_name'].isna().sum())

#merging on UNI and club_name
athena_filtd['UNI'] = athena_filtd['UNI'].astype(str)
campusgroups_filtd['UNI'] = campusgroups_filtd ['UNI'].astype(str)

campusgroups_filtd['common_mapped_name'] = (
    campusgroups_filtd['common_mapped_name']
    .astype(str)
    .str.strip()                 # remove leading/trailing whitespace
    .str.lower()                 # convert to lowercase
)

athena_filtd['common_mapped_name'] = (
    athena_filtd['common_mapped_name']
    .astype(str)
    .str.strip()                 # remove leading/trailing whitespace
    .str.lower()                 # convert to lowercase
)

campusgroups_filtd_df = campusgroups_filtd.drop_duplicates(subset=[col for col in campusgroups_filtd.columns if col != 'club_name'])
athena_filtd_df = athena_filtd.drop_duplicates(subset=[col for col in athena_filtd.columns if col != 'club_name'])


#MERGING
merged = athena_filtd_df.merge(campusgroups_filtd_df,
                            on= ['UNI', 'common_mapped_name'],
                            how = 'outer', indicator=True)
merged['UNI'] = merged['UNI'].astype(str)
only_in_athena = merged[merged['_merge'] == 'left_only']
only_in_campusgroups = merged[merged['_merge'] == 'right_only']
in_both = merged[merged['_merge'] == 'both']

# Write to Excel with three sheets
with pd.ExcelWriter('data io/club_membership_exclusive 22 july updated club.xlsx') as writer:
    only_in_athena.to_excel(writer, sheet_name='only_in_athena', index=False)
    only_in_campusgroups.to_excel(writer, sheet_name='only_in_campusgroups', index=False)
    in_both.to_excel(writer, sheet_name='in_both', index=False)
    
    
    
    '''
    22 july:
    only_in_athena = 130048
    only_in_campusgroups= 78549
    in_both = 5207
    '''
'''
without 2019 filter & updated 15 july club mapping
only_in_athena = 130079
only_in_campusgroups= 78579
in_both = 5176
'''

'''
Athnea BU only after 2019 n =1580
Campusgroups after 2019 n = 83728

only_in_athena = 190
only_in_campusgroups= 82336
in_both = 1394
'''

'''
without 2019 filter on athena data:
only in athena: 130091
only in campusgroups = 78599
in both = 5164

initial athena= 135205
initial campusgroups=83728

'''