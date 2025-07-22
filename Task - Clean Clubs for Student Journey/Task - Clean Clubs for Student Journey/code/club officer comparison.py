# -*- coding: utf-8 -*-
"""
Created on Thu Jul 10 17:21:47 2025

@author: dnd2129
Investigation 2: for 2019 onward, 
which officer positions exist in one file but not the other?
"""

import pandas as pd
import datetime as dt

athena_dta = pd.read_excel('C:/Users/dnd2129/Documents/CBS-Github-DND/Task - Clean Clubs for Student Journey/Task - Clean Clubs for Student Journey/data io/Export Student Activity - from Athena BU only.xlsx',
                         sheet_name='Sheet1', header=2)
campusgroups_dta = pd.read_excel("C:/Users/dnd2129/Documents/CBS-Github-DND/Task - Clean Clubs for Student Journey/Task - Clean Clubs for Student Journey/data io/CampusGroups Clubs.xlsx")



athena_dta['Start Date (Actual)'] = pd.to_datetime(athena_dta['Start Date (Actual)'],
                                                   format = '%Y-%m-%d %H:%M:%S')

#Not filtering athena for 2019
# athena_filtd = athena_dta[athena_dta['Start Date (Actual)'].dt.year >= 2019]
athena_filtd = athena_dta

#campusgroups
campusgroups_dta['membershipStartDate'].replace("", pd.NA).isna().sum() #0 missing


campusgroups_dta['membershipStartDate'] = pd.to_datetime(campusgroups_dta['membershipStartDate'],
                                                   format = '%Y-%m-%d %H:%M:%S')

# campusgroups_filtd = campusgroups_dta[campusgroups_dta['membershipStartDate'].dt.year >= 2019]
campusgroups_filtd = campusgroups_dta

# Cleaningand creatingmapped club name col
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

std_map = pd.read_excel('C:/Users/dnd2129/Documents/CBS-Github-DND/Task - Clean Clubs for Student Journey/Task - Clean Clubs for Student Journey/data io/club_map.xlsx', 'combined')

athena_filtd = pd.merge(athena_filtd, std_map, on="club_name", how='left')
campusgroups_filtd = pd.merge(campusgroups_filtd, std_map, on="club_name", how='left')


#Just seeing all positions that exist
athena_positions = athena_filtd['Student Activity Participation'].value_counts().reset_index()
athena_positions.columns = ['Position_name', 'count']

campusgroups_positions = campusgroups_filtd['officerPosition'].value_counts().reset_index()
campusgroups_positions.columns = ['Position_name', 'count']



# === Step 1: Flag officer roles ===

# Athena officer_flag: exclude 'Member', 'Participated', and blanks
athena_filtd['officer_flag'] = (
    (athena_filtd['Student Activity Participation'].notna()) &
    (~athena_filtd['Student Activity Participation'].isin(['Member', 'Participated']))
).astype(int)  # use int (0/1) instead of str

# CampusGroups officer_flag: fix and re-calculate if needed
campusgroups_filtd['officer_flag'] = (
    (campusgroups_filtd['officer'] == 1)
).astype(int)  # again, use int not str

# === Step 2: CampusGroups aggregation ===

def aggregate_position(pos, custom, role):
    combined = pd.concat([pos, custom, role]).dropna().astype(str)
    combined = combined[combined.str.strip() != '']  # remove blanks
    if combined.empty:
        return 'Unknown'
    return ', '.join(sorted(set(val.strip() for val in combined)))

campusgroup_grouped = campusgroups_filtd.groupby(['UNI', 'common_mapped_name']).agg({
    'officer_flag': 'max',
    'officerPosition': lambda x: list(x),
    'officerCustomPosition': lambda x: list(x),
    'officerRole': lambda x: list(x)
}).reset_index()

# Apply row-wise aggregation for officer positions
campusgroup_grouped['aggregated_officer_position'] = campusgroup_grouped.apply(
    lambda row: aggregate_position(
        pd.Series(row['officerPosition']),
        pd.Series(row['officerCustomPosition']),
        pd.Series(row['officerRole'])
    ) if row['officer_flag'] == 1 else '',
    axis=1
)

# Drop raw position columns if you don't need them
campusgroup_grouped = campusgroup_grouped.drop(columns=[
    'officerPosition', 'officerCustomPosition', 'officerRole'
])

# === Step 3: Athena aggregation ===

athena_grouped = athena_filtd.groupby(['UNI', 'common_mapped_name']).agg({
    'officer_flag': 'max',
    'Student Activity Participation': lambda x: ', '.join(
        sorted(set(
            str(val).strip() for val in x
            if pd.notna(val) and str(val).strip() not in ['Member', 'Participated']
        ))
    )
}).reset_index()

# Rename for consistency
athena_grouped = athena_grouped.rename(columns={
    'Student Activity Participation': 'aggregated_officer_position'
})

# === Step 4 (Optional): Ensure both outputs have the same columns ===

standard_cols = ['UNI', 'common_mapped_name', 'officer_flag', 'aggregated_officer_position']
campusgroup_grouped = campusgroup_grouped[standard_cols]
athena_grouped = athena_grouped[standard_cols]



merged = athena_grouped.merge(campusgroup_grouped,
                            on= ['UNI', 'common_mapped_name'],
                            how = 'outer', indicator=True)
merged['UNI'] = merged['UNI'].astype(str)
only_in_athena = merged[merged['_merge'] == 'left_only']
only_in_campusgroups = merged[merged['_merge'] == 'right_only']
in_both = merged[merged['_merge'] == 'both']

with pd.ExcelWriter('C:/Users/dnd2129/Documents/CBS-Github-DND/Task - Clean Clubs for Student Journey/Task - Clean Clubs for Student Journey/data io/club_officer_exclusive updated 22 july.xlsx') as writer:
    only_in_athena.to_excel(writer, sheet_name='only_in_athena', index=False)
    only_in_campusgroups.to_excel(writer, sheet_name='only_in_campusgroups', index=False)
    in_both.to_excel(writer, sheet_name='in_both', index=False)


'''
22 July
only in athena(only BU)= 76534
only in campusgroups = 77773
in_both= 5130


'''
'''
july 15: No 2019 filter, updated club map, updated officer flag for campusgroup.
only in athena(only BU)= 76565
only in campusgroups = 77803
in_both= 5100
'''

'''
No 2019 filter
only in athena(only BU)= 76396
only in campusgroups = 77824
in_both=5079

'''
'''
with 2019 filter
only_athena (only BU)= 191
only_campusgroups= 81453
in_both = 1378
'''