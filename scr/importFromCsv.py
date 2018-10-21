"""
Insert data from CSV files into a Neo4j DB

Usage:
    importFromCsv.py [--host <host> -u <username>] -p <password> <path-to-dir-or-file>

Options:
    --host HOST    the host of the Neo4j DB [default: localhost]
    -u USER        the username [default: neo4j]
    -p PWD         your password for the user

"""

from docopt import docopt
import os
from glob import glob
from py2neo import Graph
import logging

logging.getLogger().setLevel(logging.INFO)

def ord_files(fname):
    if ".sentences.csv"  in fname:
        return 0
    elif ".tokens.csv" in fname:
        return 1
    elif ".artificial.csv"  in fname:
        return 2
    elif ".relations.csv" in fname:
        return 3
    else:
        raise ValueError("{} is not a recognized file".format(fname))


def import_file(filname, host, user, pwd):
    d,f = os.path.split(filname)
    fname = os.path.join("file:///", os.path.basename(d), f)

    g = Graph(host=host, user=user, password=pwd)

    msg = "Adding nodes from file {}".format(f)

    if ".sentences.csv" in fname:
        q = '''LOAD CSV WITH HEADERS FROM "%s" AS sent
            FIELDTERMINATOR '\t'
            CREATE(:Sentence{ CiteURN : sent.ID, 
            Work : sent.Work, Author : sent.Author, Subdoc : sent.Subdoc,
            TextURN : sent.TextURN})
        ''' % fname
    elif ".tokens.csv" in fname:
        q = '''LOAD CSV WITH HEADERS FROM "%s" AS row
            FIELDTERMINATOR '\t'
            CREATE(:Token {CiteURN : row.ID, Form : row.Form, Lemma : row.Lemma, Rank : toInteger(row.Rank),
            Postag : row.Postag, 
            Pos : row.Pos, Person : row.Person, Number : row.Number, Tense : row.Tense, Mood : row.Mood,
            Voice : row.Voice, Gender : row.Gender, Case : row.Case, Degree : row.Degree,
            IsMemberOfCoord : toBoolean(row.IsMemberOfCoord), IsMemberOfApos : toBoolean(row.IsMemberOfApos),
            TextURN : row.TextURN})
        ''' % fname
    elif ".artificial.csv" in fname:
        q = '''LOAD CSV WITH HEADERS FROM "%s" AS row
            FIELDTERMINATOR '\t'
            CREATE(:Artificial {CiteURN : row.ID, Form : row.Form, Rank : toInteger(row.Rank),
            IsMemberOfCoord : toBoolean(row.IsMemberOfCoord), IsMemberOfApos : toBoolean(row.IsMemberOfApos)})
        ''' % fname

    elif ".relations.csv" in fname:
        q = '''USING PERIODIC COMMIT 2500
            LOAD CSV WITH HEADERS FROM "%s" AS row
            FIELDTERMINATOR '\t'
            WITH row
            WHERE row.RelationType = "syntGoverns"
            MATCH (h {CiteURN : row.Source})
            MATCH (d {CiteURN : row.Target})
            MERGE (h)-[r:GOVERNS {type: row.DepType}]->(d);
        ''' % fname

        q1 = '''USING PERIODIC COMMIT 2500
            LOAD CSV WITH HEADERS FROM "%s" AS row
            FIELDTERMINATOR '\t'
            WITH row
            WHERE row.RelationType = "isTokenOf" 
            MATCH (h {CiteURN : row.Source})
            MATCH (d {CiteURN : row.Target})
            MERGE (h)-[r:IS_TOKEN_OF]->(d)
        '''
        msg = "Adding dependency relationships from {}".format(f)

    else:
        raise ValueError("{} is not a recognized file".format(f))

    logging.info(msg)
    g.run(q)


    if ".relations.csv" in fname:
        logging.info("Adding is_token_of relationships from {}".format(f))
        g.run(q1)



if __name__ == '__main__':
    logging.info("Starting...")

    arguments = docopt(__doc__, version='0.1')
    pth = arguments["<path-to-dir-or-file>"]
    host = arguments["--host"]
    user = arguments["-u"]
    pwd = arguments["-p"]

    if os.path.isdir(pth):
        fs = glob(os.path.join(pth, "*.csv"))
        fs.sort(key=ord_files)
        logging.info("working with a folder")
    else:
        logging.info("Working with a file")
        fs = [pth]

    for f in fs:
        import_file(f, host, user, pwd)