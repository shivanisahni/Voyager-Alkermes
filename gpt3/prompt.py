import csv
import openai
import pandas as pd
import numpy as np

questions = []

# TODO see if trying to complete instead of ask questions is better
# Wording of the questions is important
questions.append("From the above article, what is the disease, indication, or medical condition being tested?")
questions.append("What is the drug that is being evaluated for on its efficacy or safety in the article?") # might hvae to edit toi get short or long name
questions.append("What is the mechanism of action (target of the chemical reaction) that the drug is being evaluated with?")
questions.append("Was the clinical trial in the article evaluated in humans?")
questions.append("The phase (either 1, 2, or 3) that the clinical trial in the article was in is?")
questions.append("Did the drug from the article result in improvements in patients and was it successful in its job?")
questions.append("When was this clinical trial done (START and END date needed)?")

openai.api_key = "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" 

answers = []
df = pd.DataFrame()

def generate_prompt(article):
    # generates prompt to feed into openai
    prompt = "I will give you an article then ask a few questions about it. \n"
    prompt += article + "\n"
    prompt += "Here are the questions about the article: \n"
    index = 0
    for question in questions:
        index += 1
        prompt += "Q{}: ".format(index)  + question + "\n"
        prompt += "A{}:".format(index) +"\n"
    
    return prompt

# TODO implement if want to parse by ourselves
def get_article(pubmed_id):
    link = "https://pubmed.ncbi.nlm.nih.gov/{}/".format(pubmed_id)
# print(article)

def run_prompt(prompt):
    response = openai.Completion.create(
            model = "text-davinci-003", 
            prompt = prompt,
            temperature = 0,
            max_tokens = 200,
            top_p = 1,
            frequency_penalty = 0,
            presence_penalty = 0
            )
    # print(response)
    text = response['choices'][0]['text'].strip()
    print(text)
    return text

# need to download file_name into local directory to work
def parse_all(file_name = 'scraped3-sample.csv'):
    with open(file_name, 'r') as csv_file:
        reader = csv.reader(csv_file)

        ids = []

        for row in reader:
            curr_article = row[1]
            prompt = generate_prompt(curr_article)
            print("Curr ID answer {}:".format(row[0]))
            ids.append(row[0])
            ans = run_prompt(prompt)
            answers.append(ans)
        
        # print(len(answers))
        # print(len(ids))
        df['Pub Med ID'] = ids
        df['Answers'] = answers
        df.to_csv('sampleresults.csv', index = False)
        print(df)

parse_all()

       
