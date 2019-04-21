"""
Usage:
    gagdt2conllx.py -p password <work-title>

Options:
    -p password    password for neo4j
"""

from docopt import docopt
from py2neo import Graph
from gagdt.objects import Sentence

args = docopt(__doc__)
title = args["<work-title>"]


g = Graph(password=args["password"])

allsents = Sentence.match(g).where("_.work = " + title)
