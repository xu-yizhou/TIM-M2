"""
V.2 : splitter tfidfdataframe.py en deux scripts, un qui calcule les poids tf-idf et un qui gère la recherche de similarités
utilisation du vectorizer TF-IDF de scikit-learn sur une dataframe pandas issue des prétraitements (cf. script de parcours)
comparaison de similarités
la question est prétraitée avec treetagger, cf. phrase2conll.py
"""
import warnings

warnings.filterwarnings("ignore")

import markovify
import numpy as np
import spacy
import re
import glob
import sys
import pandas as pd
import pickle
import phrase2conll
from prettytable import PrettyTable
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn import metrics

def generation(id_question):
    #id_answer = id_question.replace("q", "a")
    id_ = id_question.replace(id_question[8:], "")
    dossier = glob.glob(sys.argv[2]+"/*/*/"+id_+"/*.conll")

    with open("corpus_wiki.txt", "r") as f:
        text_a = f.read()
        model_a = markovify.NewlineText(text_a)

        mot_pos = ""

        for file in dossier:
            if "a" in file:
                with open(file, "r") as answer:

                    text_b = answer.read()
                    text_b = text_b.split("\n")

                    for line in text_b:
                        line = line.split("\t")
                        if len(line) == 3:
                            mot_pos = mot_pos + line[0] + " "

                    mot_pos = mot_pos + "."

                    mot_pos = mot_pos.replace(" .", ".")
                    mot_pos = mot_pos.replace("' ", "'")

                    with open("answer.txt", "w") as answer_text:
                        answer_text.write(mot_pos)
                            #answer_text.close()

                    with open("answer.txt", "r") as f2:
                        text_b = f2.read()
                        text_b = text_b.replace("\"", "")
                        #return text_b
                        model_b = markovify.NewlineText(text_b)
                        model_combo = markovify.combine([ model_a, model_b ], [1, 3])

                        answer1 = model_b.make_sentence(tries=140)

                        answer2 = model_combo.make_sentence()


                        if answer1 is not None:
                            return answer1
                        elif answer2 is not None:
                            return answer2
                        else:
                            return "Désolée, je n'ai pas de réponse"


def faux_tokeniseur(qqch):
    """
    permet d'éviter les prétraitements de scikit
    """
    return qqch

def generer_visu(mini_corpus):
    """
    contrôle visualisation des similarités
    """
    for i in mini_corpus.index:
        id = mini_corpus.loc[i, 'id']
        sim = mini_corpus.loc[i, 'simCosine']
        q = ' '.join(mini_corpus.loc[i, 'mots'])
        tab = PrettyTable(["ID", "DISTANCE"])
        tab.add_row([id, sim])
        #reponse_gen, reponse_sim = generation(id)
        print(tab)
        print("QUESTION : {}".format(q))
        print()
        print("RÉPONSE : {}".format(generation(id)))

sep = "-"*70
message = "Usage : python3 {} <dataframe du corpus> <chemin vers le corpus conll>".format(sys.argv[0])
if len(sys.argv) != 3:
	print(sep)
	print("Nombre d'arguments incorrect")
	print(message)
	print(sep)
	exit()
elif not glob.glob(sys.argv[1]):
	print(sep)
	print("{} est introuvable".format(sys.argv[1]))
	print(message)
	print(sep)
	exit()
elif not glob.glob(sys.argv[2]):
	print(sep)
	print("{} est introuvable".format(sys.argv[2]))
	print(message)
	print(sep)
	exit()
else:
	print(sep)
	print("Ouverture de {} en cours".format(sys.argv[1]))
	print(sep)

corpuspd = sys.argv[1]

# on récupère le corpus prétraité (cf. script de parcours)
corpus = pd.read_pickle(corpuspd)
corpus = corpus.set_index(pd.Index(range(0,len(corpus))))

tfidf_fit = pickle.load(open("./tfidf_fit.pickle", "rb"))
tfidf_transform = pickle.load(open("./tfidf_transform.pickle","rb"))

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
print(sep)
print("COSINUS")
print(sep)

simCosine = metrics.pairwise.cosine_distances(tfidf_transform,tfidf_fit.transform([q_lemmes]))
corpus['simCosine'] = simCosine
corpus = corpus.sort_values(by=['simCosine'])
repCosine = corpus[:nb_questions]
generer_visu(repCosine)

print(sep)
print("EUCLIDEAN")
print(sep)

simEuclidean = metrics.pairwise.euclidean_distances(tfidf_transform,tfidf_fit.transform([q_lemmes]))
corpus['simEuclidean'] = simEuclidean
corpus = corpus.sort_values(by=['simEuclidean'])
repEuclidean = corpus[:nb_questions]
generer_visu(repEuclidean)


print(sep)
print("MANHATTAN")
print(sep)

simManhattan = metrics.pairwise.manhattan_distances(tfidf_transform,tfidf_fit.transform([q_lemmes]))
corpus['simManhattan'] = simManhattan
corpus = corpus.sort_values(by=['simManhattan'])
repManhattan = corpus[:nb_questions]
generer_visu(repManhattan)

corpus.drop(columns=['simCosine', 'simEuclidean', 'simManhattan'])
