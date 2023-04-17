import csv
import openai
import pandas as pd
import numpy as np
import time

questions = []
example_answers = {}

# Wording of the questions is important
# questions.append("From the above article, what is the disease, indication, or medical condition being tested?")
# questions.append("What is the drug that is being evaluated for on its efficacy or safety in the article?") # might hvae to edit toi get short or long name
questions.append("What is the mechanism of action (target of the chemical reaction) and the receptor subtype that the drug is being evaluated with?")
# questions.append("Was the clinical trial in the article evaluated in humans?")
# questions.append("The phase (either 1, 2, or 3) that the clinical trial in the article was in is?")
# questions.append("Did the drug from the article result in improvements in patients and was it successful in its job?")
# questions.append("When was this clinical trial done (START and END date needed)?")

# TODO test if adding drug is better
example_answers[questions[0]] = ["The mechanism of action is: antagonist. The receptor subtype is: D1 receptor antagonist.",
        "The mechanism of action is: agonist/antagonist. The receptor subtype(s) are: selective estrogen receptor modulator agonist/antagonist",
        "The mechanism of action is: antagonist. The receptor subtype(s) are: H-2 antagonist.",
        "The mechanism of action is: agonist. The receptor subtype(s) are: dopamine D3-preferring D3/D2 receptor partial agonist and serotonin 5-HT1A receptor partial agonist."]


########### MAKE SURE TO COMMENT THIS OUT WHEN COMMITTING ############
openai.api_key = "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" # vedant key

answers = []
df = pd.DataFrame()

def generate_prompt(article):
    def generate_example(index):
        prompt = "I will give you an article then ask a few questions about it. \n"
        prompt += examples[index] + "\n"
        prompt += "Here are the questions about the article: \n"
        idx = 0
        for question in questions:
            idx += 1
            prompt += "Q{}: ".format(idx)  + question + "\n"
            prompt += "A{0}: {1}".format(idx, example_answers[question][index]) +"\n"
        
        return prompt

    def generate_actual():
        prompt = "I will give you an article then ask a few questions about it. \n"
        prompt += article + "\n"
        prompt += "Here are the questions about the article: \n"
        index = 0
        for question in questions:
            index += 1
            prompt += "Q{}: ".format(index)  + question + "\n"
            prompt += "A{}:".format(index) +"\n"
        
        return prompt
    total_prompt = ""
    for i in range(4):
        total_prompt += generate_example(i) + "\n\n"
    total_prompt += generate_actual()
    return total_prompt

# TODO implement if want to parse by ourselves
def get_article(pubmed_id):
    link = "https://pubmed.ncbi.nlm.nih.gov/{}/".format(pubmed_id)

def run_prompt(prompt):
    response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
            {"role": "system", "content": "You are a very helpful medical researcher."},
            {"role": "user", "content": prompt}]
    )
    text = response['choices'][0]['message']['content']
    print(text)
    return text

# TODO add titles on examples
examples = []
examples.append("""Studies in nonhuman primates documented that appropriate stimulation of dopamine (DA) D1 receptors in the dorsolateral prefrontal cortex (DLPFC) is critical for working memory processing. The defective ability of patients with schizophrenia at working memory tasks is a core feature of this illness. It has been postulated that this impairment relates to a deficiency in mesocortical DA function. In this study, D1 receptor availability was measured with positron emission tomography and the selective D1 receptor antagonist [11C]NNC 112 in 16 patients with schizophrenia (seven drug-naive and nine drug-free patients) and 16 matched healthy controls.""")
examples.append("""A substantial proportion of women with schizophrenia experience debilitating treatment-refractory symptoms. The efficacy of estrogen in modulating brain function in schizophrenia has to be balanced against excess exposure of peripheral tissue. Raloxifene hydrochloride is a selective estrogen receptor modulator (mixed estrogen agonist/antagonist) with potential psychoprotective effects and fewer estrogenic adverse effects.
To determine whether adjunctive raloxifene therapy reduces illness severity in women with refractory schizophrenia.""")
examples.append("""Smooth pursuit eye movements (SPEM) are often abnormal in schizophrenic patients and have been proposed as a trait marker of the disorder. We explored the use of SPEM as an outcome measure in an open-label clinical trial of famotidine, an H-2 antagonist, in patients with schizophrenia; famotidine has been proposed as an adjunctive medication, particularly for negative symptoms.""")
examples.append("""Negative symptoms in schizophrenia are heterogeneous and multidimensional; effective treatments are lacking. Cariprazine, a dopamine D3-preferring D3/D2 receptor partial agonist and serotonin 5-HT1A receptor partial agonist, was significantly more effective than risperidone in treating negative symptoms in a prospectively designed trial in patients with schizophrenia and persistent, predominant negative symptoms.""")

# TODO see if abstracts + title in csv are fully correct
def parse_all(file_name = 'schiz_abstracts.csv'):
      with open(file_name, 'r') as csv_file:
        reader = csv.reader(csv_file)

        ids = []
        idx = 0
        for row in reader:
            idx += 1
            # See if merging of title and article is correct
            curr_article = row[7]
            curr_title = row[2]
            prompt = generate_prompt("Title: {}\n Abstract: {}".format(curr_title, curr_article))
            print("Curr ID answer {}:".format(row[5]))
            ids.append(row[5])
            ans = run_prompt(prompt)
            answers.append(ans)
            if idx >= 100:
                break
            time.sleep(1.1)
        
        print(len(answers))
        print(len(ids))
        df['Pub Med ID'] = ids
        df['Answers'] = answers
        df.to_csv('sampleresults_turbo.csv', index = False)
        print(df)

parse_all()
