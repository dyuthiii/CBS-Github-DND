# -*- coding: utf-8 -*-
"""
Created on Mon Jul 14 11:16:48 2025

@author: dnd2129
Clubs Final dataset compilation
"""

'''
We need to create a final club dataset from the campusgroups and athena data. It should be one record per person per club with the following fields:
UniClub Name (cleaned to align with each other)Leadership Flag (flag for if they ever held a officer position for that club)Leadership Positions (comma separated list of all of the office positions they held for that club)
The final dataset should have all of the data from each dataset,
removing duplicates that are in both campusgroups and athena.
If the club is in both datasets, but only marked as a leadership position in one, we should consider them an officer. 

Only BU clubs from Athena should be included.



Answer:
the merged df from club officer comparison has this.

'''
merged['final_aggregated_officer_position'] = merged.apply(
    lambda row: ', '.join(sorted(set(
        [pos.strip() for pos in (
            str(row['aggregated_officer_position_x']) + ',' + str(row['aggregated_officer_position_y'])
        ).split(',') if pos.strip() != '']
    ))),
    axis=1
)

merged.to_csv("C:/Users/dnd2129/Documents/CBS-Github-DND/Task - Clean Clubs for Student Journey/Task - Clean Clubs for Student Journey/data io/final club dataset merged 22 july.csv")
'''
22 july
159437 values
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
159299 values
76396 from only in athena,
77824 from only in campusgroups,
5079 from in_both

This shouldn't have duplicates.
'''