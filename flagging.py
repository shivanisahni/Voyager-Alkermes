import pandas as pd

df = pd.read_csv('sampleresults_turbo.csv')

df['FLAG'] = [0] * len(df['Answers'])

for i in range(len(df['Answers'])):
    str1 = df['Answers'][i]
    if any(j.isdigit() for j in str1):
        df.at[i, 'FLAG'] = 1

df.to_csv('flaggedsampleresults_turbo.csv', index=False)


        