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
MoA_to_run = ['Agonist', 'Partial Agonist', 'Antagonist', 'Inverse Agonist']

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
        
        #if num_processed >= 100:
            #break time.sleep(1.1)

      print(len(answers))
      print(len(ids))
      answer_df['Pub Med ID'] = ids
      answer_df['Answers'] = answers
      answer_df['MoA'] = moas
      answer_df.to_csv('schiz_turbo.csv', index = False)
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
    
    example_prompts['Agonist'] = ["""Studies in nonhuman primates documented that appropriate stimulation of dopamine (DA) D1 receptors in the dorsolateral prefrontal cortex (DLPFC) is critical for working memory processing. The defective ability of patients with schizophrenia at working memory tasks is a core feature of this illness. It has been postulated that this impairment relates to a deficiency in mesocortical DA function. In this study, D1 receptor availability was measured with positron emission tomography and the selective D1 receptor antagonist [11C]NNC 112 in 16 patients with schizophrenia (seven drug-naive and nine drug-free patients) and 16 matched healthy controls.""", """A substantial proportion of women with schizophrenia experience debilitating treatment-refractory symptoms. The efficacy of estrogen in modulating brain function in schizophrenia has to be balanced against excess exposure of peripheral tissue. Raloxifene hydrochloride is a selective estrogen receptor modulator (mixed estrogen agonist/antagonist) with potential psychoprotective effects and fewer estrogenic adverse effects. To determine whether adjunctive raloxifene therapy reduces illness severity in women with refractory schizophrenia.""", """Smooth pursuit eye movements (SPEM) are often abnormal in schizophrenic patients and have been proposed as a trait marker of the disorder. We explored the use of SPEM as an outcome measure in an open-label clinical trial of famotidine, an H-2 antagonist, in patients with schizophrenia; famotidine has been proposed as an adjunctive medication, particularly for negative symptoms.""", """Negative symptoms in schizophrenia are heterogeneous and multidimensional; effective treatments are lacking. Cariprazine, a dopamine D3-preferring D3/D2 receptor partial agonist and serotonin 5-HT1A receptor partial agonist, was significantly more effective than risperidone in treating negative symptoms in a prospectively designed trial in patients with schizophrenia and persistent, predominant negative symptoms."""]
    example_prompts['Partial Agonist'] = ["""The Taq1A polymorphism in the dopamine D2 receptor (DRD2) gene could be related to the response to antipsychotics. We examined the effects of the Taq1A polymorphism on the plasma monoamine metabolites during the treatment of schizophrenia with aripiprazole, a DRD2 partial agonist.""", """This phase III study evaluated the efficacy and safety of cariprazine, a dopamine D3 and D2 receptor partial agonist with preferential binding to D3 receptors, in patients with acute exacerbation of schizophrenia. Patients were randomized to 6-week double-blind treatment with placebo, cariprazine 3 to 6 mg/d, or cariprazine 6 to 9 mg/d. """, """This study evaluated whether alterations in serotonin function in schizophrenic patients could be demonstrated by comparing the reactivity to a serotonin partial agonist, m-chlorophenylpiperazine (MCPP) in patients and healthy subjects. This study also assessed whether stimulation of serotonin receptors influenced the symptoms of schizophrenia."""]
    example_prompts['Antagonist'] = ["""Several lines of evidence from post-mortem, brain imaging, and genetic studies in schizophrenia patients suggest that Gamma-amino butyric acid (GABA) deficits may contribute to the pathophysiology of schizophrenia. Pharmacological induction of a transient GABA-deficit state has been shown to enhance vulnerability of healthy subjects to the psychotomimetic effects of various drugs. Exacerbating or creating a GABA deficit was hypothesized to induce or unmask psychosis in schizophrenia patients, but not in healthy controls. To test this hypothesis, a transient GABA deficit was pharmacologically induced in schizophrenia patients and healthy controls using iomazenil, an antagonist and partial inverse agonist of the benzodiazepine receptor. In a double-blind, randomized, placebo-controlled study, clinically stable chronic schizophrenia patients (n=13) received iomazenil (3.7 μg administered intravenously over 10 min).""", """Some schizophrenia patients are more sensitive to amphetamine (AMPH)-induced exacerbations in psychosis-an effect that correlates with higher striatal dopamine release. This enhanced vulnerability may be related to gamma-aminobutyric acid (GABA) deficits observed in schizophrenia. We hypothesized that a pharmacologically induced GABA deficit would create vulnerability to the psychotomimetic effects to the 'subthreshold' dose of AMPH in healthy subjects, which by itself would not induce clinically significant increase in positive symptoms. To test this hypothesis, a GABA deficit was induced by intravenous infusion of iomazenil (IOM; 3.7 μg/kg), an antagonist and partial inverse agonist of benzodiazepine receptor.""", """Nicotinic acetylcholine receptors (nAChRs) have been implicated in the pathophysiology of cognitive deficits in the domains of attention and memory in schizophrenia. While nicotinic agonists and antagonists have been proposed as smoking cessation aids, few comparisons have been made of these agents on cognitive performance in individuals with schizophrenia. This study investigated the acute effects of a nAChR antagonist, mecamylamine, and partial agonist, varenicline, on cognitive function in non-smokers with and without schizophrenia."""]

    example_prompts['Inverse Agonist'] = ["""Several lines of evidence from post-mortem, brain imaging, and genetic studies in schizophrenia patients suggest that Gamma-amino butyric acid (GABA) deficits may contribute to the pathophysiology of schizophrenia. Pharmacological induction of a transient GABA-deficit state has been shown to enhance vulnerability of healthy subjects to the psychotomimetic effects of various drugs. Exacerbating or creating a GABA deficit was hypothesized to induce or unmask psychosis in schizophrenia patients, but not in healthy controls. To test this hypothesis, a transient GABA deficit was pharmacologically induced in schizophrenia patients and healthy controls using iomazenil, an antagonist and partial inverse agonist of the benzodiazepine receptor. In a double-blind, randomized, placebo-controlled study, clinically stable chronic schizophrenia patients (n=13) received iomazenil (3.7 μg administered intravenously over 10 min).""", """Some schizophrenia patients are more sensitive to amphetamine (AMPH)-induced exacerbations in psychosis-an effect that correlates with higher striatal dopamine release. This enhanced vulnerability may be related to gamma-aminobutyric acid (GABA) deficits observed in schizophrenia. We hypothesized that a pharmacologically induced GABA deficit would create vulnerability to the psychotomimetic effects to the 'subthreshold' dose of AMPH in healthy subjects, which by itself would not induce clinically significant increase in positive symptoms. To test this hypothesis, a GABA deficit was induced by intravenous infusion of iomazenil (IOM; 3.7 μg/kg), an antagonist and partial inverse agonist of benzodiazepine receptor."""]
    example_answers['Agonist'] = ["The receptor(s) are: dopamine. The subtype(s) are: D1. The binding mode(s) are: antagonist. Therefore the mechanism of action is: D1 dopamine antagonist.", "The receptor(s) are: selective estrogen. The subtype(s) are: N/A. The binding mode(s) are: modulator agonist/antagonist. Thefore the mechanism of action is: selective estrogen receptor modulator agonist/antagonist", "The receptor(s) are: N/A. The subtype(s) are: H-2. The binding mode(s) are: antagonist. Therefore the mechanism of action is H-2 antagonist.", "The receptor(s) are: dopamine and serotonin. The subtype(s) are: D3/D2 and 5-HT1A. The binding mode(s) are: partial agonist. Therefore the mechanism of action is: dopamine D3-preferring D3/D2 receptor partial agonist and serotonin 5-HT1A receptor partial agonist."]
    example_answers['Partial Agonist'] = ["The receptor(s) are: dopamine. The subtype(s) are: D2. The binding mode(s) are: partial agonist. Therefore the mechanism of action is: dopamine D2 receptor partial agonist.", "The receptor(s) are: dopamine. The subtype(s) are: D3 and D2. The binding mode is: partial agonist. Therefore the mechanism of action is: dopamine D3 and D2 receptor partial agonist.", "The receptor(s) are: serotonin. The subtype(s) are: N/A. The binding mode is: partial agonist. Therefore the mechanism of action is: serotonin partial agonist."]
    example_answers['Antagonist'] = ["The receptor(s) are: benzodiazepine. The subtype(s) are: N/A. The binding mode is: partial inverse agonist. Therefore the mechanism of action is: benzodiazepine receptor antagonist and partial inverse agonist.", "The receptor(s) are: benzodiazepine. The subtype(s) are: N/A. The binding mode is: partial inverse agonist. Therefore the mechanism of action is: benzodiazepine receptor antagonist and partial inverse agonist.", "The receptor(s) are: nicotinic acetylcholine. The subtype(s) are: N/A. The binding mode(s) are: antagonist and partial agonist. Therefore the mechanism of action is: nicotinic acetylcholine receptor antagonist (mecamylamine) and a partial agonist (varenicline)."]

    example_answers['Inverse Agonist'] = ["The receptor(s) are: benzodiazepine. The subtype(s) are: N/A. The binding mode(s) are: antagonist and partial inverse agonist. Therefore the mechanism of action is: benzodiazepine receptor antagonist and partial inverse agonist.", "The receptor(s) are: benzodiazepine. The subtype(s) are: N/A. The binding mode(s) are: antagonist and partial inverse agonist. Therefore the mechanism of action is: benzodiazepine receptor antagonist and partial inverse agonist."]

    print(example_prompts, example_answers)
    parse_all('schiz.csv', example_prompts,
            example_answers)
