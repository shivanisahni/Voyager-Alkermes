import csv
import openai
import pandas as pd
import numpy as np

questions = []
example_answers = {}

# TODO see if trying to complete instead of ask questions is better
# Wording of the questions is important
# questions.append("From the above article, what is the disease, indication, or medical condition being tested?")
# questions.append("What is the drug that is being evaluated for on its efficacy or safety in the article?") # might hvae to edit toi get short or long name
questions.append("What is the mechanism of action (target of the chemical reaction) that the drug is being evaluated with?")
# questions.append("Was the clinical trial in the article evaluated in humans?")
# questions.append("The phase (either 1, 2, or 3) that the clinical trial in the article was in is?")
# questions.append("Did the drug from the article result in improvements in patients and was it successful in its job?")
# questions.append("When was this clinical trial done (START and END date needed)?")
#example_answers[questions[0]] = "The drug being evaluated for efficiency here is AXS-05, and the target mentioned in the article is oral N-methyl-D-aspartate (NMDA) receptor antagonist and σ1 receptor agonist, meaning the answer is 'oral N-methyl-D-aspartate (NMDA) receptor antagonist and σ1 receptor agonist'"
example_answers[questions[0]] = ["The disease being treated is Schizophrenia and we know that the mechanism of action is an antagonist, so the answer is D1 receptor antagonist.",
                                "The disease being treated is Schizophrenia and we know that the mechanism of action is an agonist/antagonist, so the answer is selective estrogen receptor modulator agonist/antagonist",
                                "The disease being treated is Schizophrenia and we know that the mechanism of action is an antagonist, so the answer is H-2 antagonist."]


openai.api_key = "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" #lilian key

answers = []
df = pd.DataFrame()

def generate_prompt(article):
    # generates prompt to feed into openai
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
    total_prompt = generate_example(0) + "\n\n" + generate_example(1) + "\n\n" + generate_example(2) + "\n\n" + generate_actual()
    return total_prompt

# TODO implement if want to parse by ourselves
def get_article(pubmed_id):
    link = "https://pubmed.ncbi.nlm.nih.gov/{}/".format(pubmed_id)
# print(article)

def run_prompt(prompt):
    response = openai.Completion.create(
            model = "text-curie-001", 
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

# example_article = """Abstract
# Objective: Altered glutamatergic neurotransmission has been implicated in the pathogenesis of depression. This trial evaluated the efficacy and safety of AXS-05 (dextromethorphan-bupropion), an oral N-methyl-D-aspartate (NMDA) receptor antagonist and σ1 receptor agonist, in the treatment of major depressive disorder (MDD).

# Methods: This double-blind, phase 3 trial, was conducted between June 2019 and December 2019. Patients with a DSM-5 diagnosis of MDD were randomized in a 1:1 ratio to receive dextromethorphan-bupropion (45 mg-105 mg tablet) or placebo, orally (once daily for days 1-3, twice daily thereafter) for 6 weeks. The primary endpoint was the change from baseline to week 6 in the Montgomery-Asberg Depression Rating Scale (MADRS) total score. Other efficacy endpoints and variables included MADRS changes from baseline at week 1 and 2, clinical remission (MADRS score ≤ 10), clinical response (≥ 50% reduction in MADRS score from baseline), clinician- and patient-rated global assessments, Quick Inventory of Depressive Symptomatology-Self-Rated, Sheehan Disability Scale, and quality of life measures.

# Results: A total of 327 patients were randomized: 163 patients to dextromethorphan-bupropion and 164 patients to placebo. Mean baseline MADRS total scores were 33.6 and 33.2 in the dextromethorphan-bupropion and placebo groups, respectively. The least-squares mean change from baseline to week 6 in MADRS total score was -15.9 points in the dextromethorphan-bupropion group and -12.0 points in the placebo group (least-squares mean difference, -3.87; 95% confidence interval [CI], -1.39 to -6.36; P = .002). Dextromethorphan-bupropion was superior to placebo for MADRS improvement at all time points including week 1 (P = .007) and week 2 (P < .001). Remission was achieved by 39.5% of patients with dextromethorphan-bupropion versus 17.3% with placebo (treatment difference, 22.2; 95% CI, 11.7 to 32.7; P < .001), and clinical response by 54.0% versus 34.0%, respectively (treatment difference, 20.0%; 95% CI, 8.4%, 31.6%; P < .001), at week 6. Results for most secondary endpoints were significantly better with dextromethorphan-bupropion than with placebo at almost all time points (eg, CGI-S least-squares mean difference at week 6, -0.48; 95% CI, -0.48 to -0.79; P = .002). The most common adverse events in the dextromethorphan-bupropion group were dizziness, nausea, headache, somnolence, and dry mouth. Dextromethorphan-bupropion was not associated with psychotomimetic effects, weight gain, or increased sexual dysfunction.

# Conclusions: In this phase 3 trial in patients with MDD, treatment with dextromethorphan-bupropion (AXS-05) resulted in significant improvements in depressive symptoms compared to placebo starting 1 week after treatment initiation and was generally well tolerated.""" 
examples = []
examples.append("""Studies in nonhuman primates documented that appropriate stimulation of dopamine (DA) D1 receptors in the dorsolateral prefrontal cortex (DLPFC) is critical for working memory processing. The defective ability of patients with schizophrenia at working memory tasks is a core feature of this illness. It has been postulated that this impairment relates to a deficiency in mesocortical DA function. In this study, D1 receptor availability was measured with positron emission tomography and the selective D1 receptor antagonist [11C]NNC 112 in 16 patients with schizophrenia (seven drug-naive and nine drug-free patients) and 16 matched healthy controls. [11C]NNC 112 binding potential (BP) was significantly elevated in the DLPFC of patients with schizophrenia (1.63 +/- 0.39 ml/gm) compared with control subjects (1.27 +/- 0.44 ml/gm; p = 0.02). In patients with schizophrenia, increased DLPFC [11C]NNC 112 BP was a strong predictor of poor performance at the n-back task, a test of working memory. These findings confirm that alteration of DLPFC D1 receptor transmission is involved in working memory deficits presented by patients with schizophrenia. Increased D1 receptor availability observed in patients with schizophrenia might represent a compensatory (but ineffective) upregulation secondary to sustained deficiency in mesocortical DA function.""")
examples.append("""A substantial proportion of women with schizophrenia experience debilitating treatment-refractory symptoms. The efficacy of estrogen in modulating brain function in schizophrenia has to be balanced against excess exposure of peripheral tissue. Raloxifene hydrochloride is a selective estrogen receptor modulator (mixed estrogen agonist/antagonist) with potential psychoprotective effects and fewer estrogenic adverse effects.
To determine whether adjunctive raloxifene therapy reduces illness severity in women with refractory schizophrenia.""")
examples.append("""Smooth pursuit eye movements (SPEM) are often abnormal in schizophrenic patients and have been proposed as a trait marker of the disorder. We explored the use of SPEM as an outcome measure in an open-label clinical trial of famotidine, an H-2 antagonist, in patients with schizophrenia; famotidine has been proposed as an adjunctive medication, particularly for negative symptoms.""")
def parse_all(file_name = 'schiz_abstracts.csv'):
    with open(file_name, 'r') as csv_file:
        reader = csv.reader(csv_file)

        ids = []
        idx = 0
        for row in reader:
            idx += 1
            curr_article = row[7]
            prompt = generate_prompt(curr_article)
            print("Curr ID answer {}:".format(row[5]))
            ids.append(row[5])
            ans = run_prompt(prompt)
            answers.append(ans)
            if idx >= 100:
                break
        
        print(len(answers))
        print(len(ids))
        df['Pub Med ID'] = ids
        df['Answers'] = answers
        df.to_csv('sampleresults_curie.csv', index = False)
        print(df)

parse_all()

