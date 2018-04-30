#!/bin/env python3

import xml.etree.ElementTree as ET
import numpy
numpy.set_printoptions(precision=2,threshold=1000,suppress=True)
import sys
from getfeatures import features, getfeature
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection  import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.externals import joblib

# call example for predict.py
# python predict.py /Users/YOSS/Desktop/all.xml models/LogisticRegression /tmp/out.txt

# this assumes we already executed train_compare_models.py
# train_compare_models.py is going to save the models inside the 'models' directory'
# for example, the LogisticRegression model will be saved in
# models/LogisticRegression
# the already trained models are then loaded inside of predict.py

fichier_test = sys.argv[1]
fichier_model = sys.argv[2]
fichier_output = sys.argv[3]

print('Reading corpus and finding features')
xmlcorpus = ET.parse(fichier_test)
nodoc = 0

print('Création de la matrice numpy pour x et y')
docs = xmlcorpus.getroot().getchildren()
featurekeys = sorted(list(features.keys()))
x = numpy.zeros((len(docs), len(featurekeys)))
y = numpy.zeros((len(docs)))

print('Insertion des données dans la matrice')
for i in range(len(docs)):
	for j in range(len(featurekeys)):
		doc = docs[i]
		featurename = featurekeys[j]
		x[i,j] = getfeature(doc, featurename)
		fake = 0
		if doc.get('class') == 'fake':
			fake = 1
		# TODO: to go back to binary classification
		# just comment out the two following lines
		if doc.get('class') == 'parodic':
			fake = 2
		y[i] = fake
		
print('Prédiction des classes')
		
model = joblib.load(fichier_model) 
res = model.predict(x)

err = y - res
print ('Score : ', accuracy_score(y, res))
#print ('Score de bonnes réponses : ', accuracy_score(y, res, normalize=False))
#print('Erreur quadratique : ', numpy.linalg.norm(err))

for i in range(len(docs)):
	classpredict = 'trusted'
	if res[i] == 1:
		classpredict = 'fake'
	if res[i] == 2:
		classpredict = 'parodic'
	docs[i].set('classpredict', classpredict)
xmlcorpus.write(open(fichier_output, 'w'), encoding='unicode')