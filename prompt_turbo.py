import csv
import openai
import pandas as pd
import numpy as np
import time

def generate_examples(example_file = 'MoA_one_shot.csv'):
    # TODO test if adding drug is better (need to pad examples then...!)
    examples = pd.read_csv(example_file)
    example_answers = {}
    example_prompts = {}
    
    for index, row in examples.iterrows():
        MoA = row['MoA']
        example_answers[MoA] = row['Answers From Example Articles']
        # Pass these in as arrays
        MoA_titles = row['Titles From Example Articles']
        MoA_abstracts = row['Abstracts From Example Articles']

        MoA_prompts = []
        for i in range(len(MoA_titles)):
            title = MoA_titles[i]
            abstract = MoA_abstracts[i]
            prompt = "Title: {}\n Abstract: {}".format(title, abstract)
            MoA_prompts.append(prompt)
        print(MoA_prompts)
        
        # Remove this once everything has examples
        if MoA == "Partial Agonist":
            break
        
        example_prompts[MoA] = MoA_prompts

    return example_prompts, example_answers

def generate_prompt(article, MoA, example_prompts, example_answers):
    def generate_example(index):
        prompt = "I will give you an article then ask a few questions about it. \n"
        prompt += example_prompts[MoA][index] + "\n"
        prompt += "Here are the questions about the article: \n"
        idx = 0
        for question in questions:
            idx += 1
            prompt += "Q{}: ".format(idx)  + question + "\n"
            # if we care about drug too need to start indexing by question type
            prompt += "A{0}: {1}".format(idx, example_answers[MoA][index]) +"\n"
        
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
    for i in range(len(example_prompts[MoA])):
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

def parse_all(file_name, example_prompts, example_answers):
      answer_df = pd.DataFrame()
      data_df = pd.read_csv(file_name)
      ids = []
      answers = []
      num_processed = 0

      for index, row in data_df.iterrows():
          num_processed += 1

          title = row['ARTICLE TITLE']
          abstract = row['ABSTRACT']
          prompt = "Title: {}\n Abstract: {}".format(title, abstract)
          MoA = row['MoA']

          prompt = generate_prompt(prompt, MoA, example_prompts, example_answers)
          print("Curr ID answer {}:".format(row['PMID']))

          ids.append(row['PMID'])
          ans = run_prompt(prompt)
          answers.append(ans)

          if num_processed >= 100:
              break
          # time.sleep()

      print(len(answers))
      print(len(ids))
      answer_df['Pub Med ID'] = ids
      answer_df['Answers'] = answers
      answer_df.to_csv('sampleresults_turbo.csv', index = False)
      print(answer_df)

if __name__ == "__main__":
    # TODO add argument parser for file names
    ########### MAKE SURE TO COMMENT THIS OUT WHEN COMMITTING ############
    openai.api_key = "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" # vedant key

    questions = []
    questions.append("What are the mechanism of action(s) (target of the chemical reaction) and the receptor subtype(s) that the drug(s) are being evaluated with?")
    # need to use acutal example csv to get examples
    # example_prompts, example_answers = generate_examples()
    example_prompts = {}
    example_answers = {}
    example_prompts['Partial Agonist'] =["""The Taq1A polymorphism in the dopamine D2 receptor (DRD2) gene could be related to the response to antipsychotics. We examined the effects of the Taq1A polymorphism on the plasma monoamine metabolites during the treatment of schizophrenia with aripiprazole, a DRD2 partial agonist.""", """This phase III study evaluated the efficacy and safety of cariprazine, a dopamine D3 and D2 receptor partial agonist with preferential binding to D3 receptors, in patients with acute exacerbation of schizophrenia. Patients were randomized to 6-week double-blind treatment with placebo, cariprazine 3 to 6 mg/d, or cariprazine 6 to 9 mg/d. """, """This study evaluated whether alterations in serotonin function in schizophrenic patients could be demonstrated by comparing the reactivity to a serotonin partial agonist, m-chlorophenylpiperazine (MCPP) in patients and healthy subjects. This study also assessed whether stimulation of serotonin receptors influenced the symptoms of schizophrenia."""]
    example_answers['Partial Agonist'] = ["The mechanism of action is: partial agonist. The receptor subtype(s) are: dopamine D2 receptor partial agonist.", "The mechanism of action is: partial agonist. The receptor subtype(s) are: dopamine D3 and D2 receptor partial agonist.", "The mechanism of action is: partial agonist. The receptor subtype(s) are: serotonin partial agonist."]
    print(example_prompts, example_answers)
    parse_all('schiz_abstracts.csv', example_prompts,
            example_answers)
    
