# -*- coding: utf-8 -*-
"""
read a csv derived from an evtx file and perform basic summary

"""

import argparse
import pandas as pd

parser = argparse.ArgumentParser(description="Exploration of Windows Event Log generated by the Powershell command: get-winevent -Path log.evtx | export-csv log.csv")
parser.add_argument("filename", type=str, help="name of csv file")
parser.add_argument("-d","--date", help="Date range in YYYYMM-YYYYMM (inclusive) format. If the start (or end) is omitted, the summary will be from the earliest (or latest) entries. If this argument is not specified, the default behaviours is to take the entire log file")

args = parser.parse_args()
filename = args.filename

df = pd.read_csv(filename, sep=";", index_col=False, skiprows=1)
print("\n---- [Full Data Set] Exploration of Raw Data Set ----")
print(df.info())
# print(df.head())

print("\n---- [Full Data Set] Dimensions ----")
print(df.shape)

print("\n---- [Full Data Set] Column Names ----")
print(df.columns)

# This is tailored for Application logs!!
# Pick only the useful columns
# May still need to re-cast certain columns, esp the date (TimeCreated)
df1 = df[['Message', 'Id', 'Version', 'Qualifiers', 'Level', 'Task', 'Opcode','Keywords', 'RecordId', 'ProviderName', 'ProviderId', 'ProcessId', 'ThreadId', 'MachineName', 'UserId', 'TimeCreated','LevelDisplayName', 'OpcodeDisplayName', 'TaskDisplayName']].copy()

# print an entry
# print(df1['Message'][4664])

#Recasting
# pandas is quite smart to be able to figure out the format on its own
df1['TimeCreated'] = pd.to_datetime(df1.TimeCreated)

if args.date:
    # print(args.date)
    [start, end] = args.date.split("-")
    # date end point defaults to exclusive in filter regardless of inequality type, so need to bump up a month
    if end[4:6] == "12":
        end = str(int(end[0:4])+1) + "01"
    else:
        end = end[0:4] + str(int(end[4:6]) + 1).zfill(2)

    if start and (not end):
        df2 = df1[df1["TimeCreated"] >= (start[0:4] + "-" + start[4:6])]
    elif end and (not start):
        df2 = df1[df1["TimeCreated"] <= end[0:4] + "-"+ end[4:6]]
    elif end and start:
        df2 = df1[(df1["TimeCreated"] >= start[0:4] + "-"+ start[4:6]) & (df1["TimeCreated"] <= end[0:4] + "-" + end[4:6])]
    else:
        df2 = df1
else:
    df2 = df1
    
#print(df2.info())
#print(df2["TimeCreated"][:10])
# print(df2["TimeCreated"][1600:])

# Print useful summary information
# What are all the providers?
print("\n---- [Filtered Data Set] Unique providers (applications) and their event counts ----")
print(df2["ProviderName"].value_counts())

print("\n---- [Filtered Data Set] Event types (info, error, warning, etc) and their event counts ----")
print(df2["LevelDisplayName"].value_counts())

print("\n---- [Filtered Data Set] Providers (applications) and their number of non-null unique messages ----")
# print(df2["ProviderName"].value_counts())
print(df2.groupby('ProviderName')[['Message']].nunique())