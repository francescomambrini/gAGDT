//Work with Version 0.2


//search for any lemma, e.g. φθογγή; returns the graph of the nodes (limit to 10)
MATCH (n:Token{lemma:"φθογγή"})
RETURN n Limit 10

//lemma φθογγή: what are the most used forms?
MATCH (n:Token{lemma:"φθογγή"})
RETURN n.form as Form, count(*) as Count order by Count desc

//find substantival infinitives used as subjects
MATCH (h)-[r:Dependency{type:"SBJ"}]->(n:Token{mood:"infinitive"})
return h,r,n limit 10

//infinitives used as subjects: most frequent governing verbs
MATCH (v:Token{pos : "verb"})-[r:Dependency{type:"SBJ"}]->(n:Token{mood:"infinitive"})
return v.lemma as GoverningVerb, count(*) as Total order by Total desc

//infinitives as subjects: how many are governed by an *elided* verb?
MATCH (v:Artificial)-[r:Dependency{type:"SBJ"}]->(n:Token{mood:"infinitive"})
RETURN v.lemma as GoverningVerb, count(*) as Total

//genitive absolutes
MATCH (n{mood:"participle"})-[:Dependency{type:"SBJ"}]->(d{case:"genitive"})
RETURN n.cite, n.form, d.form

//genitive absolutes (advanced)
//we a participle and its (optional) subjects down to a couple of layers
MATCH (n{mood:"participle", case:"genitive"})-[:Dependency*1..2{type:"SBJ"}]->(d{case:"genitive"})
RETURN n.cite, n.form, d.form

//Verb-Subject order with main PREDs
MATCH (s:Sentence)-[{type:"PRED"}]->(v:Token)
with v
match (sub:Token)<-[{type:"SBJ"}]-(v)-[{type:"OBJ"}]->(obj:Token)
where sub.pos =~ "(noun|adjective|pron)"
and obj.pos =~ "(noun|adjective|pron)"
return
CASE
WHEN v.rank < sub.rank
THEN 'VS'
ELSE 'SV' END AS results, count(*)

//how many main pred's have subject?
MATCH (s:Sentence{author:"Homer"})-[{type:"PRED"}]->(v:Token{pos:"verb"})-[{type:"SBJ"}]->(:Token)
with count(distinct(v)) as WithSBJ
MATCH (s:Sentence{author:"Homer"})-[{type:"PRED"}]->(v:Token{pos:"verb"})
where not (v)-[{type:"SBJ"}]->(:Token)
with count(*) as NoSBJ, WithSBJ
return WithSBJ as `With Sb expressed`, NoSBJ as `No Sb expressed`, WithSBJ+NoSBJ as `Total`

//Syntax and order: search for "subject-verb-object" word order (limit to Sophocles' Ajax)
MATCH (sent:Sentence)-[*]->(v:Token)
WHERE sent.author = "Sophocles" and
sent.work = "Ajax"
WITH v
MATCH (s:Token)<-[:Dependency{type:"SBJ"}]-(v)-[:Dependency{type:"OBJ"}]->(o:Token)
WHERE v.pos = "verb" and
s.rank < v.rank and
v.rank < o.rank
RETURN v.cite as Passage, s.rank, v.rank, o.rank

//non projectivity (still at draft level)
MATCH (S:Sentence)-[*]->(a:Token)-[:Dependency]->(b:Token)
with S,a,b
match (S)-[*]->(c)
where (c.rank < a.rank and c.rank > b.rank) or
(c.rank > a.rank and c.rank < b.rank)
and not (a)-[*]->(c)
return b.rank, b.form, c.rank, c.form, a.rank, a.form limit 5

