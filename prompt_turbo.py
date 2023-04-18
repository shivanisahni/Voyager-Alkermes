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
        abstract = row['ABSTRACT']
        prompt = "Title: {}\n Abstract: {}".format(title, abstract)
        MoA = row['MoA']

        prompt = generate_prompt(prompt, MoA, example_prompts, example_answers)
        print("Curr ID answer {}:".format(row['PMID']))

        ids.append(row['PMID'])
        ans = run_prompt(prompt)
        if (ans == 'None'):
            ans = "The mechanism of action is: " + row['MoA'] + ". The receptor subtype(s) could not be found."
        answers.append(ans)
        moas.append(MoA)
        
        #if num_processed >= 100:
            #break
        time.sleep(1.1)

      print(len(answers))
      print(len(ids))
      answer_df['Pub Med ID'] = ids
      answer_df['Answers'] = answers
      answer_df['MoA'] = moas
      answer_df.to_csv('turbo_alz.csv', index = False)
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
    
    example_prompts['Agonist'] = ["""Studies in nonhuman primates documented that appropriate stimulation of dopamine (DA) D1 receptors in the dorsolateral prefrontal cortex (DLPFC) is critical for working memory processing. The defective ability of patients with schizophrenia at working memory tasks is a core feature of this illness. It has been postulated that this impairment relates to a deficiency in mesocortical DA function. In this study, D1 receptor availability was measured with positron emission tomography and the selective D1 receptor antagonist [11C]NNC 112 in 16 patients with schizophrenia (seven drug-naive and nine drug-free patients) and 16 matched healthy controls.""", """A substantial proportion of women with schizophrenia experience debilitating treatment-refractory symptoms. The efficacy of estrogen in modulating brain function in schizophrenia has to be balanced against excess exposure of peripheral tissue. Raloxifene hydrochloride is a selective estrogen receptor modulator (mixed estrogen agonist/antagonist) with potential psychoprotective effects and fewer estrogenic adverse effects. To determine whether adjunctive raloxifene therapy reduces illness severity in women with refractory schizophrenia.""", """Smooth pursuit eye movements (SPEM) are often abnormal in schizophrenic patients and have been proposed as a trait marker of the disorder. We explored the use of SPEM as an outcome measure in an open-label clinical trial of famotidine, an H-2 antagonist, in patients with schizophrenia; famotidine has been proposed as an adjunctive medication, particularly for negative symptoms.""", """Negative symptoms in schizophrenia are heterogeneous and multidimensional; effective treatments are lacking. Cariprazine, a dopamine D3-preferring D3/D2 receptor partial agonist and serotonin 5-HT1A receptor partial agonist, was significantly more effective than risperidone in treating negative symptoms in a prospectively designed trial in patients with schizophrenia and persistent, predominant negative symptoms."""]
    example_answers['Agonist'] = ["The mechanism of action is: antagonist. The receptor subtype(s) are: D1 receptor antagonist.", "The mechanism of action is: agonist/antagonist. The receptor subtype(s) are: selective estrogen receptor modulator agonist/antagonist", "The mechanism of action is: antagonist. The receptor subtype(s) are: H-2 antagonist.", "The mechanism of action is: agonist. The receptor subtype(s) are: dopamine D3-preferring D3/D2 receptor partial agonist and serotonin 5-HT1A receptor partial agonist."]
    
    example_prompts['Antagonist'] = ["""Several lines of evidence from post-mortem, brain imaging, and genetic studies in schizophrenia patients suggest that Gamma-amino butyric acid (GABA) deficits may contribute to the pathophysiology of schizophrenia. Pharmacological induction of a transient GABA-deficit state has been shown to enhance vulnerability of healthy subjects to the psychotomimetic effects of various drugs. Exacerbating or creating a GABA deficit was hypothesized to induce or unmask psychosis in schizophrenia patients, but not in healthy controls. To test this hypothesis, a transient GABA deficit was pharmacologically induced in schizophrenia patients and healthy controls using iomazenil, an antagonist and partial inverse agonist of the benzodiazepine receptor. In a double-blind, randomized, placebo-controlled study, clinically stable chronic schizophrenia patients (n=13) received iomazenil (3.7 μg administered intravenously over 10 min).""", """Some schizophrenia patients are more sensitive to amphetamine (AMPH)-induced exacerbations in psychosis-an effect that correlates with higher striatal dopamine release. This enhanced vulnerability may be related to gamma-aminobutyric acid (GABA) deficits observed in schizophrenia. We hypothesized that a pharmacologically induced GABA deficit would create vulnerability to the psychotomimetic effects to the 'subthreshold' dose of AMPH in healthy subjects, which by itself would not induce clinically significant increase in positive symptoms. To test this hypothesis, a GABA deficit was induced by intravenous infusion of iomazenil (IOM; 3.7 μg/kg), an antagonist and partial inverse agonist of benzodiazepine receptor.""", """Nicotinic acetylcholine receptors (nAChRs) have been implicated in the pathophysiology of cognitive deficits in the domains of attention and memory in schizophrenia. While nicotinic agonists and antagonists have been proposed as smoking cessation aids, few comparisons have been made of these agents on cognitive performance in individuals with schizophrenia. This study investigated the acute effects of a nAChR antagonist, mecamylamine, and partial agonist, varenicline, on cognitive function in non-smokers with and without schizophrenia."""]
    example_answers['Antagonist'] = ["The mechanism of action is: antagonist and partial inverse agonist. The receptor subtype(s) area: benzodiazepine receptor antagonist and partial inverse agonist.", "The mechanism of action is: antagonist and partial inverse agonist. The receptor subtype(s) are: benzodiazepine receptor antagonist and partial inverse agonist.", "The mechanism of action is: antagonist and partial agonist. The receptor subtype(s) are: nicotinic acetylcholine receptor antagonist (mecamylamine) and a partial agonist (varenicline)."]
    
    example_prompts['Inverse Agonist'] = ["""Several lines of evidence from post-mortem, brain imaging, and genetic studies in schizophrenia patients suggest that Gamma-amino butyric acid (GABA) deficits may contribute to the pathophysiology of schizophrenia. Pharmacological induction of a transient GABA-deficit state has been shown to enhance vulnerability of healthy subjects to the psychotomimetic effects of various drugs. Exacerbating or creating a GABA deficit was hypothesized to induce or unmask psychosis in schizophrenia patients, but not in healthy controls. To test this hypothesis, a transient GABA deficit was pharmacologically induced in schizophrenia patients and healthy controls using iomazenil, an antagonist and partial inverse agonist of the benzodiazepine receptor. In a double-blind, randomized, placebo-controlled study, clinically stable chronic schizophrenia patients (n=13) received iomazenil (3.7 μg administered intravenously over 10 min).""", """Some schizophrenia patients are more sensitive to amphetamine (AMPH)-induced exacerbations in psychosis-an effect that correlates with higher striatal dopamine release. This enhanced vulnerability may be related to gamma-aminobutyric acid (GABA) deficits observed in schizophrenia. We hypothesized that a pharmacologically induced GABA deficit would create vulnerability to the psychotomimetic effects to the 'subthreshold' dose of AMPH in healthy subjects, which by itself would not induce clinically significant increase in positive symptoms. To test this hypothesis, a GABA deficit was induced by intravenous infusion of iomazenil (IOM; 3.7 μg/kg), an antagonist and partial inverse agonist of benzodiazepine receptor."""]
    example_answers['Inverse Agonist'] = ["The mechanism of action is: antagonist and partial inverse agonist. The receptor subtype(s) area: benzodiazepine receptor antagonist and partial inverse agonist.", "The mechanism of action is: antagonist and partial inverse agonist. The receptor subtype(s) are: benzodiazepine receptor antagonist and partial inverse agonist."]
    
    example_prompts['Inhibitor'] = ["""Tricyclic, selective serotonin reuptake inhibitors and monoamine oxidase antidepressants appear to be able to modify negative symptoms in schizophrenia, although, once again, carefully designed trials are needed.""", """The results do not support adjunctive off-label cholinesterase inhibitor treatment in patients with depression and cognitive impairment.""", """Now that the mean donepezil concentrations in the plasma, when the patients took 5 mg/day, remained 28.9 ng/mL, approximately half of the plasma IC50, higher dose of donepezil might provide further benefits for patients with AD. This technique can be also applied to measure the in vivo plasma IC50 of other cholinesterase inhibitors such as rivastigmine and galantamine."""]
    example_answers['Inhibitor'] = ["The mechanism of action is: inhibitor. The receptor subtype(s) are: selective serotonin reuptake inhibitor.", "The mechanism of action is: inhibitor. The receptor subtype(s) are: cholinesterase inhibitor.", "The mechanism of action is: inhibitor. The receptor subtype(s) are: cholinesterase inhibitor."]
    
    example_prompts['Activator'] = ["""Forty patients with schizophrenia were randomly divided into two groups. The intervention group, in addition to pharmacological treatment, underwent a multi-session exercise program for 8 weeks. At the beginning and end of the study, patients were assessed for cognitive status and negative symptoms using the Mini-Mental State Examination (MMSE) and Positive and Negative Syndrome Scale (PANSS), respectively.""", """ This study assessed the psychopathological effects of participation in a 10-session horticultural therapy program in patients with schizophrenia.""", """The objective of this study was to investigate the efficacy and safety of L-lysine as an adjunctive to risperidone in the treatment of patients with chronic schizophrenia during an 8-week trial. Seventy-two chronic schizophrenia inpatients with a Positive and Negative Syndrome Scale (PANSS) total score of ≥ 60 participated in a randomized, double-blind, placebo-controlled trial in the active phase of their disease and underwent 8 weeks of treatment with either L-lysine (6 g/day) or placebo as an adjunctive to risperidone."""]
    example_answers['Activator'] = ["The mechanism of action is: Activator. The activator type is: a multi-session exercise program.", "The mechanism of action is: activator. The activator type is: a horticultural therapy program.", "The mechanism of action is: Activator. The activator type is: L-lysine."]
    
    example_prompts['Stimulant'] = ["""In the four-site Treatment of Severe Childhood Aggression (TOSCA) study, addition of risperidone to stimulant and parent training moderately improved parent-rated disruptive behavior disorder (DBD) symptoms. This secondary study explores outcomes other than DBD and attention-deficit/hyperactivity disorder (ADHD) as measured by the Child and Adolescent Symptom Inventory-4R (CASI-4R). A total of 168 children ages 6-12 with severe aggression (physical harm), DBD, and ADHD were randomized to parent training plus stimulant plus placebo (basic treatment) or parent training plus stimulant plus risperidone (augmented treatment) for 9 weeks. All received only parent training plus stimulant for the first 3 weeks, then those with room for improvement received a second drug (placebo or risperidone) for 6 weeks.""", """Methylphenidate is a first-line treatment for ADHD; its contribution to sleep problems in adult ADHD is currently unclear. This study investigates (a) subjective sleep disturbances in a group of initially stimulant medication-naïve adults with ADHD and (b) reported changes in sleep problems after 6 weeks of methylphenidate treatment. A prospective, non-randomized, non-blinded, 6-week follow-up study utilising a self-report measure. We found (1) a large difference in reported sleep quality between methylphenidate medication-naïve patients and controls at baseline, (2) a marked improvement in patients after methylphenidate medication, and (3) largest improvement for patients with the poorest reported sleep at baseline. The study indicates that treatment with methylphenidate increases subjective sleep quality for at least some adults with ADHD."""]
    example_answers['Stimulant'] = ["The mechanism of action is: stimulant. The receptor subtype(s) are: stimulant.", "The mechanism of action is: stimulant. The receptor subtype(s) are: stimulant."]
    
    example_prompts['Modulator'] = ["""Dopamine modulates cholinergic cortical excitability in Alzheimer's disease patients""", """Somatostatin and neuropeptide Y (NPY) are neuropeptides with a widespread distribution in the human cerebral cortex. Somatostatin is involved in the regulation of hormone release from the anterior pituitary and may act as a neurotransmitter-modulator. NPY is a potent anxiolytic neuropeptide. Somatostatin and NPY coexist in the cerebral cortex, basal ganglia and in amygdaloid complexes.""", """Previous studies revealed that personality modulates both chronic pain (CP) andADoccurrence and evolution. Moreover, as pain treatments can induce side-effects, non-drugs treatments, such as art interventions, are interesting alternative therapies for decreasing CP in these patients."""]
    example_answers['Modulator'] = ['The mechanism of action is: modulator. The modulator subtype(s) are: cholinergic cortical excitability modulator.', 'The mechanism of action is: modulator. The modulator subtype(s) are: neurotransmitter-modulator', 'The mechanism of action is: modulator. The modulator subtype(s) are: chronic pain (CP) and AD occurrence and evolution modulator']
    
    example_prompts['Positive Modulator'] = ["""ASP4345, a novel dopamine D1 receptor positive allosteric modulator, is being evaluated for the treatment of cognitive impairment associated with schizophrenia (CIAS). """, """The neurosteroid pregnenolone and its sulfated derivative enhance learning and memory in rodents. Pregnenolone sulfate also positively modulates NMDA receptors and could thus ameliorate hypothesized NMDA receptor hypofunction in schizophrenia.""", """AMPA-receptor-positive modulators (Ampakines) facilitate learning and memory in animal models and in preliminary trials in human subjects. CX516 is the first Ampakine to be studied for cognitive enhancement in schizophrenia. """]
    example_answers['Positive Modulator'] = ["The mechanism of action is: positive allosteric modulator. The receptor subtype(s) are: dopamine D1 receptor positive allosteric modulator.", "The mechanism of action is: positive modulator. The receptor subtype(s) are: NMDA receptor positive modulator.", "The mechanism of action is: positive modulator. The receptor subtype(s) are: AMPA receptor (Ampakines) positive modulator."]
    
    example_prompts['Negative Modulator'] = []
    example_answers['Negative Modulator'] = []
        
    example_prompts['Allosteric Modulator'] = []
    example_answers['Allosteric Modulator'] = []
    
    example_prompts['Replacement'] = ["""The authors conducted a randomized, placebo-controlled study of nicotine replacement therapy for the reduction of agitation and aggression in smokers with schizophrenia. Participants were 40 smokers 18-65 years of age admitted to a psychiatric emergency service with a diagnosis of schizophrenia confirmed by the Mini International Neuropsychiatric Interview. Patients were screened for agitation with the excited component subscale of the Positive and Negative Syndrome Scale (PANSS) and for nicotine dependence with the Fagerström Test for Nicotine Dependence. A score of at least 14 on the PANSS excited component subscale and at least 6 on the Fagerström test were required for study eligibility. Participants in the nicotine replacement group received a 21-mg nicotine transdermal patch, and those in the placebo group were treated with a placebo patch. Participants received usual care with antipsychotics. The Agitated Behavior Scale and other agitation measures were administered at baseline and again at 4 and 24 hours.""", """This study used a within-subjects design to investigate the separate and combined effects of sensorimotor replacement for smoking (very low nicotine content [VLNC] cigarettes vs. no cigarettes) and transdermal nicotine replacement (42 mg nicotine [NIC] vs. placebo [PLA] patches) in smokers with schizophrenia (SS; n = 30) and control smokers without psychiatric illness (CS; n = 26). Each session contained a 5-hr controlled administration period in which participants underwent the following conditions, in counterbalanced order: VLNC + NIC, VLNC + PLA, no cigarettes + NIC, no cigarettes + PLA, usual-brand cigarettes + no patches. Next, participants completed measures of cigarette craving, nicotine withdrawal, smoking habit withdrawal, and cigarette subjective effects, followed by a 90-min period of ad libitum usual-brand smoking.""", """"A placebo-controlled, double-blind, crossover study using 17beta-estradiol for replacement therapy and as an adjunct to a naturalistic maintenance antipsychotic treatment was carried out over a period of 8 months. Nineteen women (mean age = 38.0 years, SD = 9.9 years) with schizophrenia were included in the study. Comprehension of metaphoric speech was measured by a lexical decision paradigm, word fluency, and verbal ability by a paper-and-pencil test."""]
    example_answers['Replacement'] = ["The mechanism of action is: replacement. The replacement subtype(s) are: nicotine replacement therapy.", "The mechanism of action is: replacement. The replacement subtype(s) are: sensorimotor replacement and transdermal nicotine replacement.", "The mechanism of action is: replacement. The replacement subtype(s) are: 17beta-estradiol replacement therapy. "]
    
    example_prompts['Antimetabolite'] = ["""It has been reported that drugs which promote the N-Methyl-D-aspartate-type glutamate receptor function by stimulating the glycine modulatory site in the receptor improve negative symptoms and cognitive dysfunction in schizophrenia patients being treated with antipsychotic drugs. We performed a placebo-controlled double-blind crossover study involving 41 schizophrenia patients in which D-cycloserine 50 mg/day was added-on, and the influence of the onset age and association with white matter integrity on MR diffusion tensor imaging were investigated for the first time. The patients were evaluated using the Positive and Negative Syndrome Scale (PANSS), Scale for the Assessment of Negative Symptoms (SANS), Brief Assessment of Cognition in Schizophrenia (BACS), and other scales. D-cycloserine did not improve positive or negative symptoms or cognitive dysfunction in schizophrenia. The investigation in consideration of the onset age suggests that D-cycloserine may aggravate negative symptoms of early-onset schizophrenia. The better treatment effect of D-cycloserine on BACS was observed when the white matter integrity of the sagittal stratum/ cingulum/fornix stria terminalis/genu of corpus callosum/external capsule was higher, and the better treatment effect on PANSS general psychopathology (PANSS-G) was observed when the white matter integrity of the splenium of corpus callosum was higher. In contrast, the better treatment effect of D-cycloserine on PANSS-G and SANS-IV were observed when the white matter integrity of the posterior thalamic radiation (left) was lower. It was suggested that response to D-cycloserine is influenced by the onset age and white matter integrity. UMIN Clinical Trials Registry (number UMIN000000468 ). Registered 18 August 2006.""", """Methotrexate is a commonly used anti-inflammatory and immunosuppressive drug. There is growing evidence that inflammatory processes are involved in the pathogenesis of schizophrenia. In our recent randomised double-blind placebo-controlled clinical trial in Pakistan and Brazil, the addition of minocycline (antibiotic and anti-inflammatory drug) for 1 year to treatment as usual reduced negative symptoms and improved some cognitive measures. A meta-analysis of cytokine changes in the peripheral blood has identified IL-2, IFN-gamma, TNF-alpha and soluble IL-2 receptor as trait markers of schizophrenia because their levels were elevated during acute exacerbations and reduced in remission. This suggests immune activation and an inflammatory syndrome in schizophrenia. Based on the evidence of the strong anti-inflammatory properties of methotrexate, we propose that low-dose methotrexate may be an effective therapy in early schizophrenia.This is a double-blind placebo-controlled study of methotrexate added to treatment as usual for patients suffering from schizophrenia, schizoaffective disorder, psychosis not otherwise specified or schizophreniform disorder. This will be with 72 patients, 36 in each arm over 3 months. There will be screening, randomisation and follow-up visits. Full clinical assessments will be carried out at baseline, 2, 4, 8 and 12 weeks. Social and cognitive assessments will be carried out at baseline and 12 weeks. Methotrexate will be given at a dose of 10 mgs orally once a week for a 3-month period. Evidence suggests inflammatory processes are involved in the pathogenesis of schizophrenia and anti-inflammatory treatments have shown to have some beneficial effects. Methotrexate is a known immunosuppressant and anti-inflammatory drug. The aim of this study is to establish the degree of improvement in positive and negative symptoms, as well as cognitive functioning with the addition of methotrexate to treatment as usual.ClinicalTrials.gov identifier: NCT02074319 (24 February 2014).""", """To date, the ketamine/PCP model of psychosis has been proposed to be one of the best pharmacological models to mimic schizophrenic psychosis in healthy volunteers, since ketamine can induce both positive and negative symptoms of schizophrenia. At subanesthetic doses, ketamine has been reported to primarily block N-methyl-D-aspartate (NMDA) receptor complex giving support to a glutamate deficiency hypothesis in schizophrenia. Positron emission tomography was used to study ketamine-induced psychotic symptom formation in relation to cerebral metabolic alterations in healthy volunteers. Our study shows that NMDA receptor blockade results in a hyperfrontal metabolic pattern. Increased metabolic activity in the frontomedial and anterior cingulate cortex correlated positively with psychotic symptom formation, in particular with ego pathology. Analysis of correlations between syndrome scores and metabolic rate of glucose (CMRglu) or metabolic gradients (ratios) revealed that each psychopathological syndrome was associated with a number of metabolic alterations in cortical and subcortical brain regions, suggesting that not a single brain region, but distributed neuronal networks are involved in acute psychotic symptom formation."""]
    example_answers['Antimetabolite'] = ["The mechanism of action: antimetabolite. The receptor subtype(s) are: glycine modulatory site receptor.", "The mechanism of action: antimetabolite. The receptor subtype(s) are are: IL-2, IFN-gamma, TNF-alpha, and soluble IL-2 receptors.", "The mechanism of action: antimetabolite. The receptor subtype(s) are: N-methyl-D-aspartate (NMDA) receptor."]
    
    example_prompts['Blocker'] = []
    example_answers['Blocker'] = []
    
    example_prompts['Inducer'] = []
    example_answers['Inducer'] = []
    
    print(example_prompts, example_answers)
    parse_all('alz_abstracts.csv', example_prompts,
            example_answers)
