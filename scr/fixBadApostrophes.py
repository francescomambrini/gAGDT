"""
Fix the error in transcoding that transformed all the apostrophes in smooth breathing (\u0313).
This script changes them back to "'"
Writes the result to an xml file with the same title in a subfolder called APOSTR (it must exist!)


Usage:
    python fixBadApostrophes.py <path-to-tb.xml>
"""

from lxml import etree
import re
import sys
import os
from requests import get
import functools

path = sys.argv[1]

#reg = re.compile(r"([\u03b2\u03b3\u03b4\u03b6\u03b8\u03ba\u03bb\u03bc\u03bd\u03be\u03c0\u03c1\u03c3\u03c2\u03c4\u03c6\u03c7\u03c8])\u0313$")
reg = re.compile("\u0313$")

fname = os.path.basename(path)
dirname = os.path.dirname(path)
outname = os.path.join(dirname, "APOSTR", fname)


@functools.lru_cache(maxsize=512)
def is_morph_word(word):
    u = 'http://morph.perseids.org/analysis/word?lang=grc&engine=morpheusgrc&word={}'.format(word)
    j = get(u).json()
    try:
        hasBody = j["RDF"]["Annotation"]["hasBody"]
        isw = True
    except KeyError:
        isw = False
    return isw


x = etree.parse(path)
words = x.xpath("//word")
aps = [w for w in words if w.attrib["form"][-1] == "\u0313"]
for a in aps:
    if is_morph_word(a.attrib["form"]) == False:
        a.attrib["form"] = reg.sub("'", a.attrib["form"])
        print("{}\tcorrected".format(a.attrib["form"]))
    else:
        print("\t{}\tNOT corrected".format(a.attrib["form"]))

for w in words:
    if w.attrib["form"] == "\u0313":
        w.attrib["form"] = "'"

with open(outname, "wb") as out:
    x.write(out, encoding="utf8")
