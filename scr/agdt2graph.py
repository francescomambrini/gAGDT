"""Usage:
    agdt2graph.py cofig-file.json
"""

from lxml import etree
import os
import sys
import inspect
from py2neo import Graph, Node, Relationship
from treebanks import Sentence, Word, Artificial_Token, Morph
from tqdm import tqdm

def _createHeadDep(t):
    """gets a token object (word or artificial);
    returns a tuple (head-address, dependent-address)"""
    add_parts = t.address.split("#")
    return ("{}#{}#{}".format(add_parts[0], add_parts[1], t.head), t.address)


def createRels(Sent, graph):
    """Takes a Sentence object and a Neo4j graph! Note that the nodes must have been already created in the DB"""
    for t in Sent._tokens:
        head_add,dep_add = _createHeadDep(t)
        query = '''MATCH (h),(d)
        WHERE h.address = "%s" AND d.address = "%s"
        CREATE UNIQUE (h)-[r:Dependency{type : "%s"}, original_label: "%s"]->(d)
        RETURN r''' % (head_add, dep_add,t._relation, t.original_label)
#        print(t.form, t._relation)
        graph.run(query)


def setPropDict(obj):
    '''takes an object. Return the list of properties, excluding those that begins with "_"'''
    return {n:v for n,v in inspect.getmembers(obj)
            if n[0] != '_' and not inspect.ismethod(v)}


def toGraphNodes(s):
    '''converts the elements of a sentence into Nodes and Relationships ready to be pushed to a Neo4j db.
    This includes the root node itself!
    '''
    #sent_props = {k:v for k,v in vars(t).items() if k[0] != '_'}
    root = Node("Sentence", **setPropDict(s))
    nodes = [root]
    for t in s._tokens:
        if type(t) is Word:
            n = Node("Token", **setPropDict(t))
        else:
            n = Node("Artificial", **setPropDict(t))
        if t._morphology:
            for k,v in t._morphology.full.items():
                n[k] = v
        nodes.append(n)
    return nodes
    

def createNodes(graph, nodes):
    for n in nodes:
        graph.merge(n)


def import_to_gagdt(graph, etree_tree, **biblio):
    """
    Main function to convert a Treebank file to the gAGDT format and push nodes and relations to the given DB
    :param graph: your db, as a py2neo graph object
    :param etree_tree: a parsed xml file
    :param biblio: a dictionary with additional bibliographic info (author, title, chronology etc)
    :return: None
    """

    sents = etree_tree.xpath("//sentence")
    for s_el in tqdm(sents):
        s = Sentence(s_el, **biblio)
        nodes = toGraphNodes(s)  # toGraphNodes(s)
        for n in nodes:
            graph.merge(n)
        createRels(s, graph)


def _read_config(config_path):
    """
    Read the configurations passed as arguments
    :param config_path: str: path to the config file
    :return: json object
    """
    import json

    with open(config_path) as f:
        j = json.load(f)
    return j


if __name__ == '__main__':
    conf = _read_config(sys.argv[1])
    biblio = conf["biblio"]
    g = Graph(host=conf["host"], password=conf["password"])
    fpath = os.path.join(conf["agdt_root"], conf["fname"])
    x = etree.parse(fpath)
    import_to_gagdt(g, x, **biblio)
