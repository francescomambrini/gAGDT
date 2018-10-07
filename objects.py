from py2neo import Graph
from py2neo.ogm import GraphObject, Property, RelatedTo, RelatedFrom
from nltk.parse import DependencyGraph

class GraphAgdtNode(GraphObject):
    """Abstract class for all the gAGDT objects. It inlcudes all property and methods
    that are shared by Sentences, Tokens and Artificials. Do not use it. Use the appropriate class
    (Sentence, Token, Artificial) instead.

    """

    __primarykey__ = "CiteUrn"

    citeUrn = Property(key='CiteUrn')

    governs_tok = RelatedTo("Token", "GOVERNS")
    governs_art = RelatedTo("Artificial", "GOVERNS")


class Sentence(GraphAgdtNode):

    author = Property(key='Author')
    chronology = Property(key="Chronology")
    genre = Property(key="Genre")
    speaker = Property(key="Speaker")
    work = Property(key="Work")
    exemplarUrn = Property(key="ExemplarUrn")

    def _get_nodes(self, graph):
        q = '''MATCH (s:Sentence)-[*]->(n) where s.CiteUrn = '{}' return n order by toInt(n.Rank)'''.format(self.citeUrn)
        cur = graph.run(q)
        return cur

    def _to_dep_graph(self, graph):
        cur = self._get_nodes(graph)
        s = ""
        for c in cur:
            form = c["n"]["Form"]
            pos = c["n"]["Pos"].title() if c["n"]["Pos"] else "None"
            head = c["n"]["Head"]
            lab = c["n"]["OriginalLabel"]
            s += "{} {} {} {}\n".format(form, pos, head, lab)
        return DependencyGraph(s, top_relation_label="PRED")

    def to_dot(self, graph):
        dg = self._to_dep_graph(graph)
        return dg.to_dot()







class Token(GraphAgdtNode):
    isMemberOfCoord = Property(key="IsMemberOfCoord")
    case = Property(key="Case")
    tense = Property(key="Tense")
    original_label = Property(key="OriginalLabel")
    cite = Property(key="Cite")
    postag = Property(key="Postag")
    person = Property(key="Person")
    number = Property(key="Number")
    head = Property(key="Head")
    ne_type = Property(key="NamedEntityType")
    mood = Property(key="Mood")
    pos = Property(key="Pos")
    isMemberOfApos = Property(key="IsMemberOfApos")
    voice = Property(key="Voice")
    degree = Property(key="Degree")
    animacy = Property(key="Animacy")
    form = Property(key="Form")
    gender = Property(key="Gender")
    lemma = Property(key="Lemma")
    rank = Property(key="Rank")


class Artificial(Token):
    artificial_type = Property(key="ArtificialType")