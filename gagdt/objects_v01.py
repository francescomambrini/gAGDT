"""
OGM implementation to work with gAGDT v. 0.1
"""

from py2neo.ogm import GraphObject, Property, RelatedTo, RelatedFrom, Related, RelatedObjects
from py2neo import Graph, Node, Relationship
from py2neo.types import remote
import sys
import time
import re

from nltk.parse import DependencyGraph

import logging

class MyFilter(object):
    def __init__(self, level):
        self.__level = level

    def filter(self, logRecord):
        return logRecord.levelno <= self.__level


#mylogger = logging.getLogger('mylogger')
#formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s', datefmt='%a, %d %b %Y %H:%M:%S')
#handler = logging.FileHandler('gAGDT_CHANGES.log')
#handler.setLevel(logging.INFO)
#handler.setFormatter(formatter)
#mylogger.setLevel(logging.INFO)

#handler.addFilter(MyFilter(logging.INFO))
#mylogger.addHandler(handler)

thismodule = sys.modules[__name__]
types = ["Sentence", "Token", "Artificial"]
        
class GraphAgdtNode(GraphObject):
    """Abstract class for all the gAGDT objects. It inlcudes all property and methods
    that are shared by Sentences, Tokens and Artificials. Do not use it. Use the appropriate class
    (Sentence, Token, Artificial) instead.
    
    """
    
    __primarykey__ = "address"
    
    address = Property()
    modified_on = Property()
    
    @property
    def _graph(self):
        return remote(self.__ogm__.node).graph
    @property
    def node(self):
        return self.__ogm__.node
    
    @property
    def dependents(self):
        dependents  = []
        q = '''match (n)-[r]->(d) where n.address = "{}" return type(r) as Rel, labels(d)[0] as DepNodeType, d.address as DepAddress'''.format(self.address)
        c = self._graph.run(q)
        while c.forward():
            res = c.current()
            dependents.append(res)
        return dependents
    
    @property
    def _logger(self):
        loglevel = logging.INFO
        l = logging.getLogger(__name__)
        if not getattr(l, 'handler_set', None):
            l.setLevel(logging.INFO)
            handler = logging.FileHandler('gAGDT_CHANGES.log')
            formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s', datefmt='%a, %d %b %Y %H:%M:%S')
            handler.setFormatter(formatter)
            handler.addFilter(MyFilter(logging.INFO))
            l.addHandler(handler)
            l.setLevel(loglevel)
            l.handler_set = True
        return l  

       
    def detachRelation(self, rel_type, dep_omg, log=True):
        """Detach a dependency relation with label rel_type going from the current to dep_omg.
        
        Parameters
        ----------
        rel_type : str
            the label of the relation to be detached
        dep_omg : gagdt.Node
            the child node to detach from the current node
        log : bool
            True to write the operation to the log file
            
        Returns
        -------
        none    
            
        """
        old_rel = self._graph.match_one(self.node, rel_type, dep_omg.node, bidirectional=True)
        self._graph.separate(old_rel )
        if log:
            self._logger.info("{} detached from {}".format(self.node["address"], dep_omg.node["address"]))

        
    def attachDep(self, rel_type, dep_omg, dep_original_label = None, log=True):
        """Create a new dependency relation going from the current node to the dep_omg.
        A new relation is created where the current node is the head and 
        
        Parameters
        ----------
        rel_type : str
            the label of the relation to be created
            
        dep_omg : gagdt.Node
            the child node to attach to the current node
        
        """

        rel = Relationship(self.node, rel_type, dep_omg.node)
        if log:
            self._logger.info("{} attached to {}".format(dep_omg.node["address"], self.node["address"]))
        
        self._graph.create(rel)
        
        dep_omg.head = self.node["rank"]

        if dep_original_label:
            dep_omg.original_label = dep_original_label
        
        self._graph.push(dep_omg)
        
        
    def has_unattached_nodes(self):
        """Check whether there are nodes that belong to the sentence 
        (i.e. have the same sent_id in the address), but are not attached to any
        of the sentence nodes
        """
        
        raise NotImplementedError("Work in progress!")
    
    
    def updateProperty(self, log=True, **kwargs):
        """Updates the specified properties of the current node. Pass the dictionary of the properties to update
        as **kwargs.
        Write them as a dictionary of property : new_value

        Parameters
        ----------
        log : bool
            True to write the changes to the log file

        **kwargs
            Arbitrary keyword arguments.

        Returns
        -------
        None

        """

        for k,v in kwargs.items():
            self.node[k] = v
            if log:
                self._logger.info("node {}: {} set to {}".format(self.node["address"], k, v))
                
        self._graph.push(self.node)

        
    def deleteNode(self, log=True):
        if log:
            self._logger.info("node {}: deleted from graph".format(self.node["address"]))

        self._graph.delete(self.node)
        
    def logCreate(self):
        self._logger.info("node {} created".format(self.node["address"]))


class Sentence(GraphAgdtNode):

    author = Property()
    chronology = Property()
    genre = Property()
    meter = Property()
    sent_id = Property()
    speaker = Property()
    subdoc = Property()
    work = Property()
    
    
    def _query_sent(self, method="desc", include_artificial=True, **kwargs):
        """
        Parameters
        ----------
        include_artificial : bool
            Set to False if you want only Tokens to be returned (e.g. in string representation)  
            
        method : str
            the method to get all the nodes in the sentence. The options are:
            - desc (default): get all the descendants of the Sentence node
            - by_id: get all the nodes whose address contains the sentence id of s 

        **kwargs:
            formatted as { property to be returned : column name for the results }

        Returns
        -------
        cursor
             a cursor with the results
        """
        assert method in ["desc", "by_id"], "Method must be either 'desc' or 'by_id'"
        
        if include_artificial:
            tok_type = "n"
        else:
            tok_type = "n:Token"
        
        return_statement = ",".join(["{} as {}".format(k,v) for k,v in kwargs.items()])
        
        if method == 'by_id':
            reg = self.address.split("#")[:-1] + ["[0-9]+"]
            reg = "#".join(reg)
            q = '''match (n)
              WHERE (n:Token OR n:Artificial)
              and n.address =~ "{}"
              return {} ORDER BY toInt(n.rank)'''.format(reg, return_statement)
            
        else:
            q = '''match ({})<-[*]-(s:Sentence) 
            where s.address = "{}" 
            return {} ORDER BY toInt(n.rank)
            '''.format(tok_type,self.address, return_statement)
        
        c = self._graph.run(q)
        return c
    
    
    def to_string(self, value="form"):
        """Returns the sentence as a string/sequence of node properties. If default "form"
        is selected, the linear sentence is returned (with no formatting of punctuation).
        
        Parameters
        ----------
        value : str
            The node property that you want to chain. Default: n.form

        Returns
        -------
        str
             the sentence as a sequence of the selected node property. Nodes are ordered according to their rank
        """
        c = self._query_sent(include_artificial=False, **{"n." + value  : "word"})
        st = " ".join([r["word"] for r in c])
        return re.sub(r'\s([,:.·])', r'\1', st)
    
    
    def _reformat_artificial_form(self, res_list):
        pass
        
        
    def _to_list_form(self, include_artificial=True, **kwargs):
        """Return a list of the tokens in the sentence; each token is a tuple with a py2neo Record, 
        holding the requested properties. Node address and node-type are added by default!
        Useful to get the nodes for CoNLL or Malt-tab representation
        """
        kwargs["n.address"] = "address"
        kwargs["labels(n)"] = "type"
        c = self._query_sent(include_artificial=include_artificial, **kwargs)
        res = []
        
        for r in c:
            t = (r[v] for v in kwargs.values())
            res.append(r)
        return res
        

    def to_dictionary(self):
        """Maps the sentence to a dictionary rank:address
        """
        c = self._query_sent(method="by_id", **{"n.rank" : "rank", "n.address" : "address"})
        d = {int(r["rank"]) : r["address"] for r in c}
        d[0] = self.address
        return d

        
    def to_malt_tab(self):
        """Represents the sentence as a string in malt-tab format.
        Malt-tab format serializes the sentence as a sequence of token, one per line.
        Each lines is formatted as:
        form (required) < postag (required) < head (optional) < deprel (optional).
        Malt-tab can be used to construct a minimalistic DependencyGraph object
        in NLTK.
        """
        word_list = self._to_list_form()

        raise NotImplementedError("Work in progress!")
        
    
    def to_tabular(self):
        """
        Returns the tokens of the sentence in a tabular format.
        
        Returns:
        --------
        list (tuples)
        
        """
        return_statement = '''d.rank as `rank`, d.form as `form`, labels(d)[0] as `type`, 
        d.head as `head`, type(r) as `relation`, d.original_label as `label`, 
        d.isMemberOfCoord as `coord`, d.isMemberOfApos as `apos`
        ORDER BY toInt(d.rank)'''

        q = '''match (d)<-[*]-(s:Sentence) 
        match (d)<-[r]-(h)
        where s.address = "{}" 
        return {}'''.format(self.address, return_statement)
        c = self._graph.run(q)
        
        tab = []
        
        for r in c:
            t = (r["rank"], r["form"], r["type"], r["head"], 
            r["relation"], r["label"], r["coord"], r["apos"])
            tab.append(t)
        return tab
    
    
    def to_dependendency_graph(self):
        """
        Returns the sentence as an NLTK dependency graph. Useful if you want to use the DOT
        visualization of the dependency graph or `triples` that returns
        all the dependency triplets of a sentence as tuples: (form_head, dependency_label, form_dependent).
        Refer to the class documentation of nltk.parse.DependencyGraph for more details.
        """

        d = {"labels(n)" : "type" , 
            "n.form" : "form", "n.pos" : "pos",
            "n.head" : "head", "n.original_label" : "label" }
        c = self._query_sent(include_artificial=True, **d)
        s = ""
        try:
            top_lab = [d["Rel"] for d in self.dependents if d["Rel"] != "AuxK"][0]
        except IndexError:
        # default to pred
            top_lab = "PRED"
        
        for e in c:
            if e["type"][0] == "Artificial":
                form = "*" + e["form"]
            else:
                form = e["form"]
            s = s + "{}\t{}\t{}\t{}\n".format(form, e["pos"], e["head"], e["label"])
            
        return DependencyGraph(s, top_relation_label=top_lab)
        
    
    def create_new_sent_node(self, node_type, rank, reorder=True, **kwargs):
        """Create a new node with the rank given. 
        The address of the new node is generated sequentially adding 1 to the last available address.
        Note that this will introduce a mismatch between address and rank.
        If reorder = True, than the following tokens are updated.
        Note this will totally screw up the syntactic annotation, so you'll have to redo it almost from scratches
        """

        address_ranks = sorted([int(a.split("#")[-1]) for a in self.to_dictionary().values() ])
        last_addr = address_ranks[-1]
        
        if node_type == "artificial":
            new = Artificial(**kwargs)
        elif node_type == "token":
            new = Token(**kwargs)
        else:
            raise ValueError("Node type {} unknown: use token or artificial".format(node_type))    
        
        add = self.address.split("#")[:-1] + [last_addr]
        new.address = "#".join(add)
        
        # create the node
        self._graph.create(new)
        
    
    def update_from_csv(self,csv_path):
        """
        Update the nodes of the sentence from a full CSV representation of nodes and node properties.
        The csv file must be a tab-separated representation of a single sentence with one column for each
        of the possible values of a
        Parameters
        ----------
        csv_path

        Returns
        -------

        """
        import pandas as pd
        
        df = pd.read_csv(csv_path, sep="\t")
        df.set_index("rank", inplace=True)
    
        
    def update_from_tabular(self, tabsent, logging=True):
        """Update the syntactic strucutre (and all the appropriate node attributes)
        starting from a conll-like tabular structure. The tabular representation must have
        the following structure:

        1 	ἀεὶ 	8 	ADV
        2	*[0]	8	COORD
        3	ἐχθρῶν	2	ATR_CO
        
        1st column: rank; 2nd column: form; 3rd column: full, ALGDT-style label
        The fields must be tab-separated, with \n at the end; no blank line is admitted. 
        Final end-line after the last element is optional.
        
        Artificial nodes have a * prepended to the form (as in 2).
        
        IMPORTANT: All the node must already exist, they must be of the right kind, and
        they must have the correct ranking or an Assertion error will be raised!
        
        Parameters
        ----------
        tabsent : str
            string representation of the sentence. See Docstring for information
            on the format
        
        """
        toks = [l.split("\t") for l in tabsent.split("\n") if l != ""]
        
        # retrieve the old sentence elements
        oldsent = list(self._query_sent(method="by_id", **{"n.rank" : 'rank', 
                          'n.address' : 'address', 'n.form' : 'form', 'n.head' : 'head', 
                          'n.original_label' : 'label'}))
        
        assert len(toks) == len(oldsent), "Missmatch between the existing sentence and the new tabular form"
        
        dict_address = self.to_dictionary()
        # get the list of nodes as dictionary rank : address
        node_dic = self.to_dictionary()
        
        #for rank,address in node_dic.items():
        for old,new in zip(oldsent, toks):
            oldaddr = old['address']
            newaddr = dict_address[int(new[0])]
            
            assert old['form'] == new[1], "The form of the word ({}) is not the same of the token in tabular sentence ({})".format(
                    old[1], new[1])
            assert oldaddr == newaddr, "The addresses of old and new token do not match"
            
            # detach node from the current head
            q = '''MATCH (h)-[r]->(d)
            where d.address = "{}"
            and h.address = "{}"
            delete r'''.format(oldaddr, dict_address[int(old[3])], old[4])
            self._graph.run(q)
            
            newlabel = new[3].split("_")[0]
            
            # create the new relation
            create = '''MATCH (h),(d)
            where d.address = "{}"
            and h.address = "{}"
            CREATE (h)-[r:{}]->(d)
            '''.format(newaddr, dict_address[int(new[2])], newlabel)
            self._graph.run(create)
            
            #update the properties of the node
            isCoord = 1 if "_CO" in new[3] else 0
            isAp = 1 if "_AP" in new[3] else 0
            q = '''MATCH (n)
            where n.address = "{}"
            SET n.isMemberOfCoord = '{}', n.isMemberOfApos = '{}',  
            n.head = '{}', n.original_label = "{}" '''.format(newaddr, 
                     isCoord, isAp, new[2], new[3])
            self._graph.run(q)
            
            #logging
            if logging:
                if new[2] != new[3]:
                    self._logger.info("{} attached to {}".format(dict_address[int(new[0])], dict_address[int(new[2])]))
                
                
                if new[-1] != old[5]:
                    self._logger.info("node {}: original_label set to {}".format(dict_address[int(new[0])], new[3]))
                
        
        # detach all nodes from their current head
        # reattach
        
        # Node attributes that must be taken care of:
        # - isMemberOfApos
        # - isMemberOfCoord
        # - head
        # - original_label
        
        

    
    

class Token(GraphAgdtNode):
    
    isMemberOfCoord = Property()
    cid = Property()
    case = Property()
    tense = Property()
    original_label = Property()
    cite = Property()
    postag = Property()
    person = Property()
    number = Property()
    head = Property()
    ne_type = Property()
    mood = Property()
    pos = Property()
    isMemberOfApos = Property()
    voice = Property()
    degree = Property()
    animacy = Property()
    form = Property()
    gender = Property()
    lemma = Property()
    rank = Property()
    
    #just here for debugging purposes
    atrs = RelatedTo("Token", "ATR")
    
    @property
    def head_node(self):
        head  = None
        q = '''match (n)<-[r]-(h) where n.address = "{}" return type(r) as Rel, labels(h)[0] as HeadNodeType, h.address as HeadAddress'''.format(self.address)
        c = self._graph.run(q)
        while c.forward():
            res = c.current()
            head = res
        return head


class Artificial(Token):
    artificial_type = Property()
        
    #tokens = RelatedTo("Token")
    #artificials = RelatedTo("Artificial")
    
    #tokens = RelatedFrom("Token")
    #artificials = RelatedFrom("Artificial")
    #sentence = RelatedFrom("Sentence")
