import pandas as pd
import numpy as np

dfs = [pd.read_csv(f"./data/contract_data_raw/contract_details_{i}.csv") \
       .drop('Quarter', axis = 1) \
       .replace('\xa0', np.nan) for i in range(1, 27)]
df = pd.concat(dfs)
df['joiner'] = df.drop('Calendar Quarter', axis = 1).aggregate(lambda x : x.astype(str)).aggregate(sum, axis = 1)
df = df.groupby('joiner').first().reset_index().drop('joiner', axis = 1)
df.to_csv('./data/contract_details.csv', index = False)