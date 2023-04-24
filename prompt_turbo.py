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

# CHANGE THIS WHEN RUNNING
MoA_to_run = ['Activator', 'Stimulator', 'Inhibitor']

def parse_all(file_name, example_prompts, example_answers):
      answer_df = pd.DataFrame()
      data_df = pd.read_csv(file_name)
      ids = []
      answers = []
      moas = []
      num_processed = 0

      for index, row in data_df.iterrows():
        num_processed += 1

        title = row['ARTICLE TITLE']
        abstract = row['COMBINED']
        prompt = "Title: {}\n Abstract: {}".format(title, abstract)
        MoA = row['MoA']

        # Only run the ones in the MoA_to_run (varies on person)
        if MoA not in MoA_to_run:
            ans = "None"
        else:
            prompt = generate_prompt(prompt, MoA, example_prompts, example_answers)
            print("Curr ID answer {}:".format(row['PMID']))
            ids.append(row['PMID'])
            try:
                ans = run_prompt(prompt)
            except:
                print("An exception occured {}".format(row['PMID']))
                ans = "None"
            answers.append(ans)
            moas.append(MoA)
            time.sleep(0.8)
        
        #if num_processed >= 100:
            #break time.sleep(1.1)

      print(len(answers))
      print(len(ids))
      answer_df['Pub Med ID'] = ids
      answer_df['Answers'] = answers
      answer_df['MoA'] = moas
      answer_df.to_csv('schiz_turbo_john.csv', index = False)
      print(answer_df)

if __name__ == "__main__":
    # TODO add argument parser for file names
    ########### MAKE SURE TO COMMENT THIS OUT WHEN COMMITTING ############
    openai.api_key = "" # vedant key

    questions = []
    questions.append("What are the mechanism of action(s) (target of the chemical reaction) and the receptor subtype(s) that the drug(s) are being evaluated with?")
    # need to use acutal example csv to get examples
    # example_prompts, example_answers = generate_examples()
    example_prompts = {}
    example_answers = {}
    
    example_prompts['Activator'] = ["""Forty patients with schizophrenia were randomly divided into two groups. The intervention group, in addition to pharmacological treatment, underwent a multi-session exercise program for 8 weeks. At the beginning and end of the study, patients were assessed for cognitive status and negative symptoms using the Mini-Mental State Examination (MMSE) and Positive and Negative Syndrome Scale (PANSS), respectively.""", """ This study assessed the psychopathological effects of participation in a 10-session horticultural therapy program in patients with schizophrenia.""", """The objective of this study was to investigate the efficacy and safety of L-lysine as an adjunctive to risperidone in the treatment of patients with chronic schizophrenia during an 8-week trial. Seventy-two chronic schizophrenia inpatients with a Positive and Negative Syndrome Scale (PANSS) total score of ≥ 60 participated in a randomized, double-blind, placebo-controlled trial in the active phase of their disease and underwent 8 weeks of treatment with either L-lysine (6 g/day) or placebo as an adjunctive to risperidone."""]
    example_answers['Activator'] = ["The receptor(s) are: N/A. The subtype(s) are: N/A. The binding mode is: activator. Therefore the mechanism of action is: a multi-session exercise program.", "The receptor(s) are: N/A. The subtype(s) are: N/A.The binding mode is: activator. Therefore the mechanism of action is: a horticultural therapy program.", "The receptor(s) are: L-lysine. The subtypes(s) are: N/A. Therefore the mechanism of action is: L-lysine activator."]
    
    example_prompts['Inhibitor'] = ["""Tricyclic, selective serotonin reuptake inhibitors and monoamine oxidase antidepressants appear to be able to modify negative symptoms in schizophrenia, although, once again, carefully designed trials are needed."""]
    example_answers['Inhibitor'] = ["The receptor(s) are: serotonin. The subtype(s) are: N/A. The binding mode is: reuptake inhibitors. Therefore the mechanism of action is: selective serotonin reuptake inhibitors"]

    example_prompts['Stimulant'] = ["""In the four-site Treatment of Severe Childhood Aggression (TOSCA) study, addition of risperidone to stimulant and parent training moderately improved parent-rated disruptive behavior disorder (DBD) symptoms. This secondary study explores outcomes other than DBD and attention-deficit/hyperactivity disorder (ADHD) as measured by the Child and Adolescent Symptom Inventory-4R (CASI-4R). A total of 168 children ages 6-12 with severe aggression (physical harm), DBD, and ADHD were randomized to parent training plus stimulant plus placebo (basic treatment) or parent training plus stimulant plus risperidone (augmented treatment) for 9 weeks. All received only parent training plus stimulant for the first 3 weeks, then those with room for improvement received a second drug (placebo or risperidone) for 6 weeks.""", """Methylphenidate is a first-line treatment for ADHD; its contribution to sleep problems in adult ADHD is currently unclear. This study investigates (a) subjective sleep disturbances in a group of initially stimulant medication-naïve adults with ADHD and (b) reported changes in sleep problems after 6 weeks of methylphenidate treatment. A prospective, non-randomized, non-blinded, 6-week follow-up study utilising a self-report measure. We found (1) a large difference in reported sleep quality between methylphenidate medication-naïve patients and controls at baseline, (2) a marked improvement in patients after methylphenidate medication, and (3) largest improvement for patients with the poorest reported sleep at baseline. The study indicates that treatment with methylphenidate increases subjective sleep quality for at least some adults with ADHD."""]
    example_answers['Stimulant'] = ["The receptor(s) are: N/A. The subtype(s) are: N/A. The binding mode is: stimulant. Thereofore the mechanism of action is: stimulant.", "The receptor(s) are: N/A. The subtype(s) are: N/A. The binding mode is: stimulant. Thereofore the mechanism of action is: stimulant."]
    

    print(example_prompts, example_answers)
    parse_all('schiz.csv', example_prompts,
            example_answers)
