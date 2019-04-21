from py2neo.ogm import GraphObject, Property, RelatedTo, RelatedFrom
from nltk.parse import DependencyGraph

class GraphAgdtNode(GraphObject):
    """Abstract class for all the gAGDT objects. It inlcudes all property and methods
    that are shared by Sentences, Tokens and Artificials. Do not use it. Use the appropriate class
    (Sentence, Token, Artificial) instead.

    """

    __primarykey__ = "address"

    address = Property()
    citeURN = Property(key="CiteURN")

    governs = RelatedTo("Token", "Dependency")
    governs_art = RelatedTo("Artificial", "Dependency")


class Sentence(GraphAgdtNode):

    author = Property()
    chronology = Property()
    genre = Property()
    speaker = Property()
    work = Property()
    exemplarUrn = Property()
    subdoc = Property()
    meter = Property()


    def _get_nodes(self, graph):
        q = '''MATCH (s:Sentence)-[:HasToken]->(n) where s.address = "{}" return n order by toInteger(n.rank)'''.format(self.address)

        cur = graph.run(q)
        return cur

    def _to_dep_graph(self, graph):
        cur = self._get_nodes(graph)
        s = ""
        top_rels = []
        for c in cur:
            form = c["n"]["form"]
            pos = c["n"]["pos"].title() if c["n"]["pos"] else "X"
            head = c["n"]["head"]
            lab = c["n"]["original_label"]
            s += "{} {} {} {}\n".format(form, pos, head, lab)
            if head == 0:
                top_rels.append(lab)
        return DependencyGraph(s, top_relation_label=top_rels[0])

    def to_dot(self, graph):
        dg = self._to_dep_graph(graph)
        return dg.to_dot()



class Token(GraphAgdtNode):
    isMemberOfCoord = Property()
    case = Property()
    tense = Property(key="tense")
    original_label = Property()
    cite = Property(key="cite")
    postag = Property(key="postag")
    person = Property(key="person")
    number = Property(key="number")
    head = Property(key="head")
    ne_type = Property()
    mood = Property(key="mood")
    pos = Property(key="pos")
    isMemberOfApos = Property()
    voice = Property(key="voice")
    degree = Property(key="degree")
    animacy = Property(key="animacy")
    form = Property(key="form")
    gender = Property(key="gender")
    lemma = Property(key="lemma")
    rank = Property(key="rank")


class Artificial(Token):
    artificial_type = Property()