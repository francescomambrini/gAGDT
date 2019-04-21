# Allow CSV import from given folder

There are different options to allow imports from CSV file to Neo4j (>3.0). 
I prefer the one where I specify the import folder manually and make neo4j point 
to a custom folder in my home:

* open `neo4j.conf` (if you install it on Debian/Ubuntu with apt, it's in 
`/etc/neo4j`; you need su access to edit!)
* edit `dbms.directories.import=` entering the path you want after the equal sign
* by default the import directory is somehwere like `/var/lib/neo4j/import`. If you're happy 
with that the line should read: `dbms.directories.import=import`
* make sure the line `dbms.security.allow_csv_import_from_file_urls=true` is 
**commented out**
* do not forget to **restart neo4j** (e.g. `sudo service neo4j restart`)

# Using Neo4j Import Tool

See the full documentation [here](https://neo4j.com/docs/operations-manual/current/tutorial/import-tool/)

```bash
neo4j-admin import --nodes:Sentence "~/Documents/gagdt_import/headers/SentenceHeader.csv,~/Documents/gagdt_import/Aesch_Ag/tlg0085.tlg005.perseus-grc1.sentences.csv" \
--nodes:Token "../TokenHeader.csv,tlg0085.tlg005.perseus-grc1.tokens.csv" \
--nodes:Artificial "../ArtificialHeader.csv,tlg0085.tlg005.perseus-grc1.artificials.csv" \
--relationships "../RelationHeader.csv,~/Documents/tlg0085.tlg005.perseus-grc1.relations.csv" \
--delimiter "\t"

```

# Using a cypher script

To execute it:

```bash
 cat import_gagdt.cyph | cypher-shell -u <neo4j-user> -p <your-neo4j-pwd>
```

# Cypher queries

If you're using the method above to allow CSV import, you don't need to specify 
the full path of the file you want to import.

## Preliminary operations

### Setting the filenames

```cypher
:params "fsents" : 'file:///Aesch_Ag/tlg0085.tlg005.perseus-grc1.sentences.csv',
"ftokens" : 'file:///Aesch_Ag/tlg0085.tlg005.perseus-grc1.tokens.csv',
"fartificials" : 'file:///Aesch_Ag/tlg0085.tlg005.perseus-grc1.artificial.csv',
"frelations" : 'file:///Aesch_Ag/tlg0085.tlg005.perseus-grc1.relations.csv'

```

### Setting uniqueness constraints

```cypher
CREATE CONSTRAINT ON (sent:Sentence) ASSERT sent.CiteURN IS UNIQUE

CREATE CONSTRAINT ON (tok:Token) ASSERT tok.CiteURN IS UNIQUE

CREATE CONSTRAINT ON (art:Artificial) ASSERT art.CiteURN IS UNIQUE
```

## Load sentences
```cypher
LOAD CSV WITH HEADERS FROM "file:///Aesch_Ag/tlg0085.tlg005.perseus-grc1.sentences.csv" AS sent
FIELDTERMINATOR '\t'
CREATE(:Sentence{ CiteURN : sent.ID, 
Work : sent.Work, Author : sent.Author, Subdoc : sent.Subdoc,
TextURN : sent.TextURN});

```

## Load Tokens

```cypher
LOAD CSV WITH HEADERS FROM "file:///Aesch_Ag/tlg0085.tlg005.perseus-grc1.tokens.csv" AS row
FIELDTERMINATOR '\t'
CREATE(:Token {CiteURN : row.ID, Form : row.Form, Lemma : row.Lemma, Rank : toInteger(row.Rank),
Postag : row.Postag, 
Pos : row.Pos, Person : row.Person, Number : row.Number, Tense : row.Tense, Mood : row.Mood,
Voice : row.Voice, Gender : row.Gender, Case : row.Case, Degree : row.Degree,
IsMemberOfCoord : toBoolean(row.IsMemberOfCoord), IsMemberOfApos : toBoolean(row.IsMemberOfApos),
TextURN : row.TextURN});
```

## Load Artificials

```cypher
LOAD CSV WITH HEADERS FROM "file:///Aesch_Ag/tlg0085.tlg005.perseus-grc1.artificial.csv" AS row
FIELDTERMINATOR '\t'
CREATE(:Artificial {CiteURN : row.ID, Form : row.Form, Rank : toInteger(row.Rank),
IsMemberOfCoord : toBoolean(row.IsMemberOfCoord), IsMemberOfApos : toBoolean(row.IsMemberOfApos)});

```

## Load Relations

### Dependency

```cypher
LOAD CSV WITH HEADERS FROM "file:///Aesch_Ag/tlg0085.tlg005.perseus-grc1.relations.csv" AS row
FIELDTERMINATOR '\t'
WITH row
WHERE row.RelationType = "syntGoverns"
MATCH (h {CiteURN : row.Source})
MATCH (d {CiteURN : row.Target})
MERGE (h)-[r:GOVERNS {type: row.DepType}]->(d);
```

### IsTokenOf

```cypher
USING PERIODIC COMMIT 1000
LOAD CSV WITH HEADERS FROM "file:///Aesch_Ag/tlg0085.tlg005.perseus-grc1.relations.csv" AS row
FIELDTERMINATOR '\t'
WITH row
WHERE row.RelationType = "isTokenOf" // etc
MATCH (h {CiteURN : row.Source})
MATCH (d {CiteURN : row.Target})
MERGE (h)-[r:IS_TOKEN_OF]->(d);

```






