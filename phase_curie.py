import openai
import csv
import pandas as pd
import re
import numpy as np
from bs4 import BeautifulSoup
import requests


def run_prompt(prompt):
    print("running")
    try:
        response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                {"role": "system", "content": "You are a very helpful medical researcher."},
                {"role": "user", "content": prompt}]
        )
        text = response['choices'][0]['message']['content']
        print(text)
    except:
        print("Error")
        text = "None"
    return text

def generate_prompt(article):
    prompt = "I am going to give you an article and then ask you a simple question about it."
    prompt += "\n" + article

    prompt += "Q: Does the article explicitly mention the clinical trial phase of the study, like Phase 1, Phase 2 or Phase 3?\n"
    prompt += "A: \n"

    prompt += "Q: What is the clinical trial phase mentioned in the study? If no phase is stated please say Unknown.\n"
    prompt += "A: \n"

    prompt += "Q: Are humans mentioned in this study? Please answer with YES or NO."
    prompt += "A: \n"

    prompt += "Q: How many people were involved in the study? Please give only the number if present, otherwise answer with N/A\n"
    prompt += "A: \n"

    prompt += "Q: Does the article mention something like healthy subjects, healthy patients, or healthy volunteers being involved in the trial? Please answer with YES or NO. \n"
    prompt += "A: \n"

    prompt += "Q: Does the trial/study use the words pivotal or registrational or something similar? Please answer with YES or NO\n"
    prompt += "A: "

    return prompt

def nct_scrape(file_name):
    #file_name = 'schiz.csv'
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
        num = 0
        for row in reader:
            num += 1
            if num >= 10:
                break
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

if __name__ == "__main__":
    openai.api_key = "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" # vedant key

    df = pd.read_csv('schiz_combined100.csv')
    answer_df = pd.DataFrame()
    num = 0
    answers = []
    ids = []
    for index, row in df.iterrows():
        num += 1
        ids.append(row['PMID'])
        abstract = row['COMBINED']
        prompt = generate_prompt(abstract)
        print(prompt)
        ans = run_prompt(prompt)
        answers.append(ans)
        if num >= 10:
            break
    answer_df['PMID'] = ids
    answer_df['Answers'] = answers
    answer_df.to_csv('phase_turbo.csv', index=False)


    results = []
    for index, row in answer_df.iterrows():
        curr_answer = str(row['Answers'])
        query = re.findall("A:\s[\w]*\s*[\d]*", curr_answer)
        res = []
        for ele in query:
            ele = ele[3:].lower()
            res.append(ele)
        results.append(res)
    print(results)
    print()
    
    phases = []
    nctresults = nct_scrape('schiz_combined100.csv')
    nctdf = pd.read_csv('schiz_phase_link.csv')
    idx = nctdf["Pub Med ID"]
    nctdf.index = idx
    
    for i in range(len(results)):
        # res[0] = phase mentioned?
        # res[2] = humans mentioned?
        # res[3] = # of humans
        # res[4] = healthy or not
        # res[5] = pivotal or registrational
        res = results[i]
        pmid = ids[i]
        col_write = "PHASE REVISED"
        if len(res) == 6:
            if "yes" in res[0]:
                phases.append(res[1])
            elif "no" in res[0]:
                if nctdf.loc[pmid, "Phase"] == "Not Found":
                    if "no" in res[2]:
                        phases.append("Preclinical")
                    elif "yes" in results[i][4]:
                        phases.append("Phase 1")
                    elif results[i][3].isnumeric() and int(results[i][3]) < 50:
                        phases.append("Phase 1")
                    elif "yes" in results[i][5]:
                        phases.append("Phase 3")
                    else:
                        phases.append("Unknown")
        else:
            phases.append("Unknown")
    
    print(phases)
    df['PHASE REVISED'] = phases
    df.to_csv('revised.csv', index = False)



    print(answer_df)
