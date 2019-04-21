from py2neo import Graph, Node, Relationship
import sys

"""Usage: converRelations.py <db-password>
"""

pwd = sys.argv[1]
graph = Graph(host='pagdt.dainst.org', password=pwd)
cur = graph.run("MATCH ()-[r]->() RETURN type(r) as `Rel`, count(*) as `Count`")
for c in cur:
    rel = c["Rel"]
    if rel == 'DGOV':
        continue
    else:
        q = '''MATCH (h)-[r]->(d)
               where type(r) = '%s'
               MERGE (h)-[newr : Dependency {type : type(r), original_label :  d.original_label }]->(d)
               DELETE r
               RETURN count(*) 
        ''' % rel
        graph.run(q)
