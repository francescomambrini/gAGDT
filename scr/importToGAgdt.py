#!/usr/bin/env/ python
from lxml import etree
import os
from py2neo import Graph
import treebanks as tb
import agdt2graph as a2g

#Customize here!
biblio = {"author" : "Aeschylus",
          "genre" : "tragedy", 
          "chronology" : "5th BCE",
          "work" : "Persians",
          "meter" : ""}

fname = "tlg0085.tlg002.perseus-grc2.tb.xml"

g = Graph(password="boston4ever")

agdt_folder = "/Users/fmambrini/Documents/lavoro/treebank/files/AGDT2.X/PerseusDL-treebank_data-96df3cc/v2.1/Greek/texts"
path = os.path.join(agdt_folder, fname)
assert os.path.exists(path), "File does not exist!"

x = etree.parse(path)
sents = x.xpath("//sentence")
print(len(sents))

i=1
#
for i, s_el in enumerate(sents):
    print("Working with sentence n. ", i+1)
    s = tb.Sentence(s_el, **biblio)
    nodes = a2g.toGraphNodes(s) #toGraphNodes(s)
    for n in nodes:
        g.merge(n)
    a2g.createRels(s, g)