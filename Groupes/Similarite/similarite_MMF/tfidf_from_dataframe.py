"""
V.1 : utilisation du vectorizer TF-IDF de scikit-learn sur une dataframe pandas issue des prétraitements (cf. script de parcours)
comparaison de similarités
la question est prétraitée avec treetagger, cf. phrase2conll.py
"""
import warnings

warnings.filterwarnings("ignore")

import pandas as pd
import phrase2conll
from prettytable import PrettyTable
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn import metrics


def faux_tokeniseur(qqch):
    """
    permet d'éviter les prétraitements de scikit
    """
    return qqch

def generer_visu(sim_matrix, sim):
    """
    contrôle visualisation des similarités
    """
    q = ' '.join(corpus.mots[list(sim_matrix).index(sim)])
    tab = PrettyTable(["ID", "DISTANCE"])
    tab.add_row([corpus.id[list(sim_matrix).index(sim)], sim[0]])
    print(tab)
    print("QUESTION : {}".format(q))

transition = "*"*70

# on récupère le corpus prétraité (cf. script de parcours)
corpus = pd.read_pickle("./corpuspd.pkl")

print("Format de la dataframe :\n{}".format(corpus.head()))

# poids TF-IDF
tfidf = TfidfVectorizer(analyzer='word',tokenizer=faux_tokeniseur,preprocessor=faux_tokeniseur,token_pattern=None)
tfidf.fit(corpus.lemmes)
# print(tfidf.vocabulary_)

question = input("Posez une question : ")
assert question, "Question vide"

# appel phrase2conll pour gérer question
q_lemmes = []
for l in phrase2conll.main(question).rstrip().split(' '):
    q_lemmes.append(l.split("/")[2])

print("Question lemmatisée : ", q_lemmes)

nb_questions = int(input("Nombre de réponses à sélectionner (entre 1 et 10) : "))
assert 0 < nb_questions < 11, "ENTRE 1 ET 10"

# calcul et comparaison des similarités
print(transition, "COSINE", transition)

simCosine = metrics.pairwise.cosine_distances(tfidf.transform(corpus.lemmes),tfidf.transform([q_lemmes]))

for sim in sorted(list(simCosine), reverse=False)[:nb_questions]:
    generer_visu(simCosine, sim)


print(transition, "EUCLIDEAN", transition)

simEuclidean = metrics.pairwise.euclidean_distances(tfidf.transform(corpus.lemmes),tfidf.transform([q_lemmes]))

for sim in sorted(list(simEuclidean), reverse=False)[:nb_questions]:
    generer_visu(simEuclidean, sim)

print(transition, "MANHATTAN", transition)

simManhattan = metrics.pairwise.manhattan_distances(tfidf.transform(corpus.lemmes),tfidf.transform([q_lemmes]))

for sim in sorted(list(simManhattan), reverse=False)[:nb_questions]:
    generer_visu(simManhattan, sim)