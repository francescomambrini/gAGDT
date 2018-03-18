//Work with Version 0.2

//Let us see all the acc. objects of φημί in the graph DB


//List all the direct objects of verbs. The objects must be nouns and in accusative.
//Return a table with lemma of both obj and verb, ordered by frequency of the couplet (in descending order)
MATCH (h:Token {pos : "verb"})-[r:Dependency{type:'OBJ'}]->(d:Token {pos : "noun", case : "accusative"})
RETURN h.lemma as `Head`, d.lemma as `Dependent`, count(*) as `Tot` ORDER by `Tot` DESC

//Same as before, but in a more verbose style
MATCH (h:Token)-[r:Dependency]->(d:Token)
WHERE  d.pos = "noun" and d.case =  "accusative"
and h.pos = 'verb'
and r.type = 'OBJ'
RETURN h.lemma as `Head`, d.lemma as `Dependent`, count(*) as `Tot` ORDER by `Tot` DESC
