"""
NOTE: it is mandatory that the file containing token-to-CTS alignments have a column called URN
with the correct CTS URNs. Of course, it must also have the same number of lines as the tokens in the
treebank xml file

Usage:
    addCtsUrns.py <treebank-file.xml> <cts-alignment.csv>
"""

import pandas as pd
import sys
from lxml import etree
import numpy as np
import os

tbf = sys.argv[1]
cf = sys.argv[2]

cts = pd.read_csv(cf, dtype={"URN" : object})

tb = etree.parse(tbf)
docurn = tb.xpath("//sentence/@document_id")[0]
words = tb.xpath("//word")

assert len(cts) == len(words), "Number of reebank words must be the same as the number of CTS-URNs!"

for w,u in zip(words, cts.URN):
    if u is np.nan:
        continue
    else:
        ctsurn = "{}:{}".format(docurn, u)
        w.attrib["cite"] = ctsurn

outname = os.path.basename(tbf)

with open(os.path.expanduser("~/Desktop/" + outname), "wb") as out:
    tb.write(out, encoding="utf8")

