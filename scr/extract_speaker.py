"""Usage:
    python extract_speaker.py <path-to-tei.xml> <path-to-treebank.xml>

"""

# coding: utf-8
from lxml import etree
import sys
import os

x = etree.parse(sys.argv[1])
ns = {"tei" : "http://www.tei-c.org/ns/1.0"}
ls = x.xpath("//tei:l", namespaces=ns)

#load the treebank
tb = etree.parse(sys.argv[2])
sents = tb.xpath("//sentence")

firstcts = []
for s in sents:
    for w in s:
        try:
            c = w.attrib["cite"].split(":")[-1]
            break
        except KeyError:
            continue
    firstcts.append(c)
    
assert len(firstcts) == len(sents)

speakers = []
for c in firstcts:
    try:
        e = [l for l in ls if l.attrib["n"] == c.split("-")[0]][0]
    except IndexError:
        print("CTS passage {} not found".format(c))
        continue
    sp = e.getparent()[0].text
    speakers.append(sp)
    

with open(os.path.expanduser("~/Desktop/speakers.csv"), "w") as out:
    for sp in speakers:
        out.write(sp + "\n")