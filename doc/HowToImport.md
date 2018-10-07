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

# Cypher queries

If you're using the method above to allow CSV import, you don't need to specify 
the full path of the file you want to import.

## Preliminary: setting the filenames

```cypher
:params "fsents" : 'file:///tlg0085.tlg003/urn:cts:greekLit:tlg0085.tlg003.perseus-grc2.tbsents.csv',
"ftokens" : 'file:///tlg0085.tlg003/urn:cts:greekLit:tlg0085.tlg003.perseus-grc2.tbtokens.csv',
"fartificials" : 'file:///tlg0085.tlg003/urn:cts:greekLit:tlg0085.tlg003.perseus-grc2.tbartificials.csv',
"frelations" : 'file:///tlg0085.tlg003/urn:cts:greekLit:tlg0085.tlg003.perseus-grc2.relations.csv'

```

## Load sentences
```cypher
LOAD CSV WITH HEADERS FROM $fsents AS sent
FIELDTERMINATOR '\t'
CREATE(:Sentence{ CiteUrn : sent.citeUrn, ExemplarUrn : sent.exemplarUrn, 
Work : sent.work, Author : sent.author, Speaker : sent.speaker, Chronology : sent.chronology,
CtsUrn : sent.ctsUrn})

```

## Load Tokens

```cypher
LOAD CSV WITH HEADERS FROM $ftokens AS row
FIELDTERMINATOR '\t'
CREATE(:Token {CiteUrn : row.citeurn, Form : row.form, Lemma : row.lemma, Rank : row.rank,
Pos : row.pos, Person : row.person, Number : row.number, Tense : row.tense, Mood : row.mood,
Voice : row.voice, Gender : row.gender, Case : row.case, Degree : row.degree,
Postag : row.postag, Head : row.head, OriginalLabel : row.originalLabel,
IsMemberOfCoord : row.isMemberOfCoord, IsMemberOfApos : row.isMemberOfApos,
CtsUrn : row.ctsUrn, ExemplarUrn : row.exemplarUrn})
```

## Load Artificials

```cypher
LOAD CSV WITH HEADERS FROM $fartificials AS row
FIELDTERMINATOR '\t'
CREATE(:Artificial {CiteUrn : row.citeurn, Form : row.form, Rank : row.rank,
Head : row.head, OriginalLabel : row.originalLabel,
IsMemberOfCoord : row.isMemberOfCoord, IsMemberOfApos : row.isMemberOfApos,
ArtificialType : row.ArtificialType})
```

## Load Relations

```cypher
LOAD CSV WITH HEADERS FROM $frelations AS row
FIELDTERMINATOR '\t'
MATCH (h {CiteUrn : row.Source}), (d {CiteUrn : row.Target})
MERGE (h)-[r:GOVERNS {type: row.RelType}]->(d)
```








