import pandas as pd
import numpy as np

df1 = pd.read_csv("./data/pipeline_contract_details.csv").rename(columns = {"Pipeline" : "Pipeline Name"})
df2 = pd.read_csv("./data/shipper_details.csv")
for df in [df1, df2]:
    df.query('`Contract Number` != "NEXT00392P"', inplace = True)
    df['Contract Number'] = df['Contract Number'].astype(str)
    df['Rate Schedule'] = df['Rate Schedule'].astype(str)

    df.loc[df['Rate Schedule'].str.match(r"600\d{1}", na = False), "Contract End Date"] = df['Contract Start Date']
    df.loc[df['Rate Schedule'].str.match(r"600\d{1}", na = False), "Contract Start Date"] = df['Contract Number']
    df.loc[df['Rate Schedule'].str.match(r"600\d{1}", na = False), "Contract Number"] = df['Rate Schedule']
    df.loc[df['Rate Schedule'].str.match(r"600\d{1}", na = False), "Rate Schedule"] = "50-FT"
    df.loc[df['Contract Number'].str.fullmatch(r"\d{1}/\d{1}/\d{4}", na = False), "Contract End Date"] = df['Contract Start Date']
    df.loc[df['Contract Number'].str.fullmatch(r"\d{1}/\d{1}/\d{4}", na = False), "Contract Start Date"] = df['Contract Number']
    df.loc[df['Contract Number'].str.fullmatch(r"\d{1}/\d{1}/\d{4}", na = False), "Contract Number"] = df['Rate Schedule']
    df.loc[df['Rate Schedule'].str.contains('FT2-', na = False), "Rate Schedule"] = "FT2"
    df.loc[df['Contract Number'].str.fullmatch(r"\d{2}/\d{1,2}/\d{4}", na = False), "Contract End Date"] = df['Contract Start Date']
    df.loc[df['Contract Number'].str.fullmatch(r"\d{2}/\d{1,2}/\d{4}", na = False), "Contract Start Date"] = df['Contract Number']
    df.loc[df['Contract Number'].str.fullmatch(r"\d{2}/\d{1,2}/\d{4}", na = False), "Contract Number"] = df['Rate Schedule'].apply(lambda s : s.split(' ')[-1])
    df['Rate Schedule'] = df['Rate Schedule'].apply(lambda s : s.replace("  ", " "))
    df.loc[df['Rate Schedule'].str.match("Rate Schedule FTS"), "Rate Schedule"] = "FTS"
    df.loc[df['Rate Schedule'].str.match("Rate Schedule FT"), "Rate Schedule"] = "FT"
    df.loc[df['Rate Schedule'].str.match("Rate Schedule BH"), "Rate Schedule"] = "BH"
    df.loc[df['Rate Schedule'] == "FT-1 (North Bakken Expansio", "Rate Schedule"] = "FT-1 (North Bakken Expansion)"
    df.loc[(df['Rate Schedule'] == 'FT 500459') | (df['Rate Schedule'] == 'FT 500425'), "Rate Schedule"] = "FT"
    df.loc[df['Rate Schedule'].str.match("RATE SCHEDULE"), "Rate Schedule"] = df['Rate Schedule'].apply(lambda s : s.split(' ')[-1])
    df['Contract Start Date'] = pd.to_datetime(df['Contract Start Date'])
    df['Contract End Date'] = pd.to_datetime(df['Contract End Date'], errors = 'coerce')
    df['Contract End Date'] = df['Contract End Date'].fillna(np.datetime64("2099-12-31"))
    df['Key'] = df.iloc[:, range(11)].apply(lambda col : col.astype(str)).sum(axis = 1)

pipeline_header = df1.loc[df1.iloc[:, range(15, 21)].isnull().all(1)]
pipeline_body = df1.loc[df1.iloc[:, range(15, 21)].notnull().any(1)]
kept_columns = list(map(lambda s : s + "_x", df1.columns[:15])) + list(map(lambda s : s + "_y", df1.columns[15:21]))
merged1 = pipeline_header.merge(pipeline_body, on = 'Key')[kept_columns]
merged1.columns = df1.drop('Key', axis = 1).columns

shipper_header = df2.loc[df2.iloc[:, range(15, 21)].isnull().all(1)]
shipper_body = df2.loc[df2.iloc[:, range(15, 21)].notnull().any(1)]
kept_columns = list(map(lambda s : s + "_x", df2.columns[:15])) + list(map(lambda s : s + "_y", df2.columns[15:21]))
merged2 = shipper_header.merge(shipper_body, on = 'Key')[kept_columns]
merged2.columns = df2.drop('Key', axis = 1).columns

merged1.to_csv("./data/pipeline_details_clean.csv", index = False)
merged2.to_csv("./data/shipper_details_clean.csv", index = False)