from lxml import etree
import re
import os
from py2neo import Graph, Node, Relationship

def reverseDict(dic):
    return {v: k for k, v in dic.items()}


pos = {'-' : '-',
           "d" : 'adverb',
           'n' : 'noun',
           'm' : 'numeral',
           'p' : 'pron',
           'v' : 'verb',
           't' : 'verb', 
           'x' : 'irregular',
           'l' : 'article',
           'e' : 'exclamation',
           'a' : 'adjective',
           'r' : 'preposition',
           'c' : 'conjunction',
           'g' : 'adverb',
           'u' : 'punctuation',
           'i' : 'irregular',
       }

person = {'1' : "1st", '-' : '-', '3' : '3rd' , '2' : '2nd'}
number = {'s' : 'singular', '-' : '-', 'p' : 'plural', 'd' : 'dual'}
tense = reverseDict({'imperfect' : 'i',
                     'future' : 'f',
                     'perfect' : 'r',
                     '-' : '-',
                     'future_perfect' : 't',
                     'aorist' : 'a',
                     'pluperfect' : 'l',
                     'present' : 'p'})
mood = reverseDict({'optative' : 'o', '-' : '-', 'imperative' : 'm', 'indicative' : 'i', 'infinitive' : 'n', 'subjunctive' : 's', 'participle' : 'p'})
voice = reverseDict({'middle' : 'm',
                     'passive' : 'p',
                     '-' : '-' ,
                     'mediopassive' : 'e',
                     'active' : 'a'})
gender = reverseDict({'neuter' : 'n', 'masculine' : 'm', 'feminine' : 'f', '-' : '-'})
case = reverseDict({'accusative' : 'a',
                    'nominative' : 'n', 
                    'vocative' : 'v', 
                    '-' : '-', 
                    'dative' : 'd', 
                    'genitive' : 'g'})
degree = reverseDict({'superl' : 's', '-' : '-', 'comp' : 'c'})


def _setPropIfThere(el, p):
    """generic function that tries to set a proprety by accessing the appropriate XML attribute;
    if the attribute is not there, an empty string is returned.
    This is used for properties like "cite" or "cid" that might
    or might not be set for all files"""
    try:
        s = el.attrib[p]
    except KeyError:
        s = None
    return s


class Sentence():
    def __init__(self, el, **kwargs):
        """Takes a parsed xml sentence element, returns a Sentence object with a series of properties defined.
        Optionally, you can pass a series of keyword:value pairs, including:
        - author
        - title of the work
        - genre
        - chronology
        - meter"""
        self._element = el
        self._raw = etree.tostring(el, encoding="UTF-8").decode("utf8")
        self._doc_id = el.attrib["document_id"]
        self.sent_id = el.attrib["id"]
        self.subdoc = el.attrib["subdoc"]
        self._artificials = [t for t in self._tokens if type(t) is Artificial_Token]
        self._words = [t for t in self._tokens if type(t) is Word]
        self._stats = (len(self._tokens), len(self._artificials), len(self._tokens) - len(self._artificials))
        self.address = self._doc_id.split(":")[-1] + "#" + self.sent_id + "#" + '0'
        
        #Some bibliographic information
        self.author = kwargs.pop("author", None)
        self.work = kwargs.pop("work", None)
        self.genre = kwargs.pop("genre", None)
        self.chronology = kwargs.pop("chronology", None)
        
        #Content-related information
        self.speaker = kwargs.pop("speaker", "")
        self.meter = kwargs.pop("meter", "")
        
    def _isArtificial(self, t):
        try:
            t.attrib["artificial"]
            return(True)
        except KeyError:
            return(False)

    @property    
    def _tokens(self):
        tokens = []
        toks = self._element.xpath("word")
        for t in toks:
            if self._isArtificial(t):
                tokens.append(Artificial_Token(t))
            else:
                tokens.append(Word(t))
        return tokens
    
    
    def printStats(self):
        print('''Total tokens:\t{};\nWords:\t{};\nArtificial nodes:\t{}'''.format(self._stats[0],
                                                                                 self._stats[2], self._stats[1]))
    
    def __str__(self):
        '''returns the plain sentence'''
        return ' '.join([s.form for s in self._tokens if type(s) is Word])


class Token():
    '''Super-class for both words and artificial nodes. All that is common to both should go here'''
    def __init__(self, word_element):
        self._element = word_element
        self._raw =  etree.tostring(word_element, encoding="UTF-8").decode("utf8")
        self._token_id = word_element.attrib["id"]
        self.rank = self._token_id
        self.form = word_element.attrib["form"]
        #the original relation tag
        self.original_label = word_element.attrib["relation"]
        #the relation tag split in the components:
        #e.g. "SBJ_AP_CO" > [SBJ, AP, CO]
        self._rel_components = self.original_label.split("_")
        self.head = word_element.attrib["head"]
        self._relation = self._rel_components[0]
        #it might not be there for artificial!
        self._lemma_original = _setPropIfThere(word_element, "lemma")
        self.postag = _setPropIfThere(word_element, "postag")

        #Getter
        #self.lemma
        #self.address
        #self._morphology
        
    def setIsMember(self, tag):
        assert tag in ["AP", "CO"],"the appendix tag must be either AP or CO!"
        if tag in self._rel_components:
            return 1
        else:
            return 0
        
    @property
    def lemma(self):
        if self._lemma_original is not None:
            return re.sub('[0-9]+$', '', self._lemma_original)
        else:
            return None
    @property
    def address(self):
        sent = self._element.getparent()
        return "{}#{}#{}".format(sent.attrib["document_id"].split(":")[-1], sent.attrib["id"], self._token_id)
    
    @property
    def _morphology(self):
        if self.postag == None:
            return None 
        else:
            return Morph(self.postag)


class Word(Token):
    def __init__(self, word_element):
        Token.__init__(self, word_element)
        #These might not be there!
        self.cid = _setPropIfThere(word_element, "cid")
        self.cite = _setPropIfThere(word_element, "cite")
        self.isMemberOfCoord = Token.setIsMember(self, "CO")
        self.isMemberOfApos = Token.setIsMember(self, "AP")

        #Semantics
        #to be implemented
        self.ne_type = ''
        self.animacy = ''


class Artificial_Token(Token):
    def __init__(self, word_element):
        Token.__init__(self, word_element)
        self._insertion_id = word_element.attrib["insertion_id"]
        self.artificial_type = word_element.attrib["artificial"]
        self.isMemberOfCoord = Token.setIsMember(self, "CO")
        self.isMemberOfApos = Token.setIsMember(self, "AP")


class Morph():
    def __init__(self, tag):
        assert len(tag) == 9, "Tag: {} is invalid".format(tag)
        self.pos = pos[tag[0]]
        self.person = person[tag[1]]
        self.number = number[tag[2]]
        self.tense = tense[tag[3]] 
        self.mood = mood[tag[4]]
        self.voice = voice[tag[5]] 
        self.gender = gender[tag[6]]
        self.case = case[tag[7]]
        self.degree = degree[tag[8]]
        
    @property
    def full(self):
        return {'pos' : self.pos,
               'person' : self.person,
               'number' : self.number,
               'tense' : self.tense,
               'mood' : self.mood,
               'voice' : self.voice,
               'gender' : self.gender,
               'case' : self.case,
               'degree' : self.degree,
               }
