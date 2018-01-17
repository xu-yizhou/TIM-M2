#!/bin/env python3

import glob, xml.etree.ElementTree as ET

alldocs = ET.Element('corpus')
for xmlfile in glob.glob('../Corpus/*.xml'):
	print('Opening', xmlfile)
	xmlcorpus = ET.parse(xmlfile)
	for doc in xmlcorpus.getroot():
		alldocs.append(doc)

print('Output file')
ET.ElementTree(alldocs).write('all.xml', encoding="UTF-8")
