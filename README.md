# Introduction

## What is it?

The gAGDT is a graph database containing the Greek texts of Perseus' 
[Ancient Greek and Latin Dependendency Treebank](http://perseusdl.github.io/treebank_data/). 
We also include some (tentative) code to use the OGM interface of the python library `py2neo`, as well as 
a few Jupyter notebook to document the types of Cypher query and operation I perform.

## Is it the whole AGDT?
Not yet. For now, I have only converted the following authors or texts:
* *Iliad* and *Odyssey*
* Aeschylus
* Sophocles


## Is it the same as the original AGLDT?
Not quite! What I love of graph databases is their flexibility in terms of schema and extensions. In other word, I can easily 
add different layers of annotations or different types of relations between treebank words to integrate the morpho-syntactic annotation 
of the original treebank.

This is precisely what I would like to do. I have tentatively introduced some properties of nodes to integrate semantic or prosodic/literary information, 
such as `meter` or `animacy`. But these properties at the moment are empty.

A couple of extensions that *are* actually implemented are the following:
* Chronology (property of sentences)
* Genre (property of sentences)
* Speaker (property of sentences)

`speaker`, in particular, is a very useful feature! Especially for dramatic texts, it allows you to search sentences by the (literary) character that utters them. 
Some of the work needed to enrich the nodes of the treebanks with this information layer and a discussion of the research questions that can be enabled by such an extension 
will be object of a forthcoming paper. I'll update the reference as soon as the paper is published. 

Note, however, a couple of limitations:
* speaker information are implemented for Sophocles (all) and for some Aeschylus
* as I have taken the speakers from the TEI editions on the Perseus Digital Library, the characters's names are in Greek!

## What is the schema of the DB.
Better documentation will come. For now, I write some basic information on the nodes, properties and relations.

### Nodes
The db has 3 types of nodes:
* `Sentence`: representing the root of the treebank and holding the properties that belong to the whole utterance or even the whole text 
(e.g. chronology, author, work, genre, span of lines or text references coverd by them).
* `Token`: the actual token corresponding to "words" attested in the digital edition of reference (or very informally: the words of the texts)
* `Artificial`: reconstructed nodes that govern elliptical constructions.

Note the properties of tokens (and artificials) are very redundant. For example, I store the full 9-position morphological tag of words (e.g. `v1sria---`) and each of 
the 9 properties that are condensed in this string: in this case, `pos` = `verb`, `person` = `1s` etc. This is a bit verbose and maybe harder to maintain (if you change a property 
you should also update the corresponding "legacy" property). But it is very handy for format exchange and for querying: after all, it's much easier to write a query where you ask:

```cypher

MATCH (n:Token)
WHERE n.pos = 'verb'

```

Then to always write regexps to match the nth position of a 9-character string...

### Relations

At this moment, only dependency relations with one of the labels of the AGDT are represented.

I have chosen to define each of the labels as a type of relation. This means that `PRED` is a relation type of the gAGDT. 
This is a very foolish idea that should be changed ASAP! What prompted me to implement such a poor design was the idea of enabling users to write easy cypher queries such as:

```cypher
MATCH (h:Token)-[SBJ]->(d:Token)

```

instead of something like:

```cypher
MATCH (h:Token)-[Dependency {type : "SBJ"}]->(d:Token)
```
But it is a terrible idea, especially if you want to introduce

A note on **Coordination** and **Apposition**. They are **NOT** included in the labels / type or relations. So a coordinated subject will be linked to the verb via `SBJ` not `SBJ_CO`. The fact that it belongs to a coordinated structure or an apposition is recorded at the node level in two boolean properties:
* `isMemberOfCoord` (0 or 1)
* `isMemberOfApos` (0 or 1)

I had this idea from the PDT and it is a much better way of implementing coordination and apposition than to use the appendix to the label!

## What is the license of these data?
The AGLDT is distributed under a CC BY-SA 3.0 license. And so is gAGDT. Please, refer to the [AGDT page](https://github.com/PerseusDL/treebank_data/blob/master/v2.1/Greek/README.MD#annotators) for a full list of the annotators that should be credited with the annotation of the those texts. They should thanked and praised for their effort...
