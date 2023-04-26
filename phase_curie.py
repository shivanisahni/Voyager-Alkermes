import openai
import csv
import pandas as pd
import re


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
    prompt += "Q: Does the article mention something like subjects, patients, individuals, or healthy volunteers being inv oled in the trial? Please answer with YES or NO. \n"
    prompt += "A: \n"
    prompt += "Q: How many people were involved in the study? Please give a numerical answer if present, otherwise answer with N/A\n"
    prompt += "A: \n"
    prompt += "Q: Does the trial/study use the words pivotal or registrational or something similar? Please answer with YES or NO\n"
    prompt += "A: "
    return prompt


if __name__ == "__main__":
    openai.api_key = "" # vedant key

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
        ans = run_prompt(prompt)
        answers.append(ans)
        if num >= 100:
            break
    answer_df['PMID'] = ids
    answer_df['Answers'] = answers
    answer_df.to_csv('phase_turbo.csv', index=False)


    results = []
    for index, row in answer_df.iterrows():
        curr_answer = str(row['Answers'])
        query = re.findall("A:\s[\w]*", curr_answer)
        res = []
        for ele in query:
            ele = ele[3:].lower()
            res.append(ele)
        results.append(res)
    print(results)
    print()

    df['PHASE REVISED'] = ['' for i in range(len(df['PHASE SCRAPER']))]
    print(len(df['PHASE SCRAPER']))
    print(len(results))
    for i in range(0, 3):
        if df['PHASE SCRAPER'][i] == "Not Found":
            if len(results[i]) == 3:
                if results[i][0].lower() == "yes":
                    df['PHASE REVISED'][i] = 'Phase 1'
                elif results[i][1] >= '50':
                    df['PHASE REVISED'][i] = 'Phase 1'
                elif results[i][2] == "yes":
                    df['PHASE REVISED'][i] = 'Phase 3'

    df.to_csv('revised.csv', index = False)



    print(answer_df)

