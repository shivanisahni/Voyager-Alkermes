import pandas as pd

# Load the original CSV file
df = pd.read_csv('schiz.csv')

# Loop through each row and append the corresponding keyword to the abstract
# for index, row in df.iterrows():
#     abstract = row['ABSTRACTS']
#     keyword = row['KEYWORDS']
#     new_abstract = f"{abstract}\n Keywords: {keyword}"
#     df.at[index, 'ABSTRACTS'] = new_abstract

df['COMBINED'] = df['ABSTRACTS'] + "\n Keywords:" + df['KEYWORDS']
# Save the updated dataframe to a new CSV file
df.to_csv('schiz3.csv', index=False)
