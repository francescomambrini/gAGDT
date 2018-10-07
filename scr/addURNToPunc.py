"""This is a simple script that try to guess the correct CTS URNs for punctuation marks.
Strangely enough, punctuation marks don't have a "cite" property in the current AGLDT distribution. However, CTS URNs
are required for each textual token (i.e. token that is not an artificially reconstructed node) to be inserted into
the gAGDT. Also, it makes sense that punctuation marks receive their own CTS URN, as they correspond to portion of a
text within the digital edition the URN points to.

Normally, the most common punctuation marks, as "," or ".", belong to the same line or text part as the preceding
tokens, but there are exceptions that are not so easy to predict (open quotes, dagger and cruces etc).

This scripts prints out the number of unassigned cite elements, for manual check.

Usage:
    python addURNToPunc.py <path-to-file.xml>

"""

from lxml import etree
import sys
import os

path = sys.argv[1]
x = etree.parse(path)

fname = os.path.basename(path)
dirname = "/home/francesco/cltk_data/greek/agdt/gold/xml/PUNCT_URN/"
outname = os.path.join(dirname, fname)

nonstarting = [";", ";", "-", ":", ",", "·", "·", "."]

sents = x.xpath("//sentence")

notcorrected = []

for s in sents:
    words = s.xpath("word")
    cites = [c for c in s.xpath("word/@cite") if c != ""]
    for w in words:
        print(s.attrib["id"],w.attrib["id"])
        try:
            c = w.attrib["cite"]
        except KeyError:
            continue
        if c == "":
            if w.attrib["id"] == "1":
                w.attrib["cite"] = cites[0]
                #notcorrected.append((s.attrib["id"], w.attrib["id"]))
                continue
            else:
            # if w.attrib["form"] in nonstarting:
                realc = words[int(w.attrib["id"]) -2].attrib["cite"]
                w.attrib["cite"] = realc
            #else:
            #    notcorrected.append((s.attrib["id"], w.attrib["id"]))

with open(outname, "wb") as out:
    x.write(out, encoding="utf8")

#with open("/home/francesco/cltk_data/greek/agdt/gold/xml/PUNCT_URN/NOT_CORRECTED.txt", 'a') as out:
#    for n in notcorrected:
#        out.write("sent\t{}\tword\t{}still empty".format(n[0], n[1]))