from sentence_transformers import SentenceTransformer
import torch

model = SentenceTransformer('paraphrase-MiniLM-L6-v2')

sentence1 = ['histamine H5 receptor antagonist']
sentence2 = ['serotonin-5-HT1A receptor partial agonist']
sentence3 = ['histamine H5 receptor']

embedding1 = torch.from_numpy(model.encode(sentence1))
embedding2 = torch.from_numpy(model.encode(sentence2))
embedding3 = torch.from_numpy(model.encode(sentence3))

print(embedding1, embedding2)

cos = torch.nn.CosineSimilarity(dim=1, eps=1e-6)

print(cos(embedding1, embedding2), cos(embedding2, embedding3), cos(embedding1, embedding3))


# Idea: take every output
# create embedding using sentence transformer
# then run a clustering algorithm to join similar things! (defined by cosine similarity)

moas = []

def get_similarity(a, b):
    embedding_a = torch.from_numpy(model.encode(a))
    embedding_b = torch.from_numpy(model.encode(b))
    return cos(embedding_a, embedding_b)

def cluster_stuff(MoA_list):
    clusters = {} 
    threshold = 0.85 # have to hyerparameter tune this
    for ele in MoA_list:
        best = 0.0
        cluster_to_match = ""
        for compare_cluster in clusters:
            if get_similarity(compare_cluster, ele) > best:
                best = get_similarity(compare_cluster, ele)
                cluster_to_match = compare_cluster
        if best > threshold:
            clusters[cluster_to_match].append(ele)
        else:
            clusters[ele[0]] = [ele]
    print(clusters)
cluster_stuff(moas) 
