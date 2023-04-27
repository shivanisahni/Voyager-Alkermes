import requests
import csv
import re
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup


file_name = 'schiz.csv'
num_articles = 0
nct = []
phase = []
ids = []
df = pd.DataFrame()

"""
url = "https://pubmed.ncbi.nlm.nih.gov/22697189/"
req = requests.get(url)
soup = BeautifulSoup(req.content, "html.parser")
link = soup.find("a", attrs={'title': 'See in ClinicalTrials.gov'})
raw_text = link.text
cleaned_text = raw_text.strip()
print("https://clinicaltrials.gov/ct2/show/" + cleaned_text)
"""

with open(file_name, 'r') as csv_file:
    reader = csv.reader(csv_file)
    next(reader)
    for row in reader:
        paper_url = row[3]
        pmid = row[5]
        req = requests.get(paper_url)
        soup = BeautifulSoup(req.content, "html.parser")
        try:
            link = soup.find("a", attrs={'title': 'See in ClinicalTrials.gov'})
            raw_text = link.text
            trial_id = raw_text.strip()
            URL = "https://clinicaltrials.gov/ct2/show/" + trial_id
            try: 
                page = requests.get(URL)
                soup = BeautifulSoup(page.content, "html.parser")
                table_contents = soup.find_all("span", attrs={'style': 'display:block;margin-bottom:1ex;'})
                ans = table_contents[-1].text
            except:
                ans = "Not Found"
        except:
            trial_id = "None"
            ans = "Not Found"
        if ans.find("Phase") == -1:
            ans = "Not Found"    
        nct.append(trial_id)
        phase.append(ans)
        ids.append(pmid)
        num_articles += 1
        print(num_articles, trial_id, ans)

    df['Pub Med ID'] = pd.Series(ids)
    df['Clinical Trial ID'] = pd.Series(nct)
    df['Phase'] = pd.Series(phase)
    df.to_csv('schiz_phase_link.csv', index = False)
    print(df)

