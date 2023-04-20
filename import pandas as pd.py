import pandas as pd

# Load the CSV file into a pandas dataframe
df = pd.read_csv('schiz.csv')

# Concatenate the two columns and store the result in a new column
df['ABSTRACT'] += "\n KEYWORDS: " + ' '.join(df['KEYWORDS'][1: -1])
df.drop('KEYWORDS', axis = 1)

# Save the updated dataframe as a new CSV file
df.to_csv('schiz_2.csv', index=False)