"""Script that allows you to convert an AGDLT treebank into a series of csv/tsv files.
For each treebank, 4 files are generated:
- list of sentences
- list of words
- list of artificials
- list of relations

These files can then be imported to Neo4j.
The treebank file name must be relative to the root folder defined

Usage:
    agdt2csv.py <config-file.json>

"""


import os
import json
from perseus_nlp_toolkit.reader import AGLDTReader
from perseus_nlp_toolkit.utils import Morph
import sys
from pyCTS import CTS_URN
import csv
from perseus_nlp_toolkit.utils import Word, Artificial


def generate_sent_ctsurns():
    pass



# def generate_urns(doc_urn, anno_sents):
#
#     # get the offsets for all sentences
#     sent_offsets = []
#     for s in anno_sents:
#         toks = [w for w in s if isinstance(w, Word) and w.cite is not None]
#         sent_offsets.append((CTS_URN(toks[0].cite).passage_component.split("-")[0],
#                              CTS_URN(toks[-1].cite).passage_component.split("-")[-1]))
#     cts_urns = []
#     sent_ex_urns = []
#     s_ends = []
#     for start, end in sent_offsets:
#         base_ex_urn = "{}.tbsent.{}".format(doc_urn, start)
#         counter = s_ends.count(start)
#         sent_ex_urns.append("{}.{}".format(base_ex_urn, counter + 1))
#         if start == end:
#             cts_urns.append("{}:{}".format(doc_urn, start))
#         else:
#             cts_urns.append("{}:{}-{}".format(doc_urn, start, end))
#         s_ends.append(end)
#
#     assert len(cts_urns) == len(sent_ex_urns), "List of CTS URN and of Exemplar URN are not of the same length"
#     return sent_ex_urns, cts_urns
#
#
#
#
# def process_sentences(doc_urn, anno_sents, sents_meta, config):
#     """
#     Parameters
#     ----------
#     doc_urn : str
#         the cts urn for the document
#     anno_sents : list
#         list of lists with named tuples (Word or Artificial)
#     sent_meta : named tuple
#         metadata of the list
#
#     Returns
#     -------
#     list : list of lists with the 9 columns of the csv
#     """
#     exurns, ctsurns = generate_urns(doc_urn, anno_sents)
#     assert len(exurns) == len(sents_meta), "List of urns and of metadata do not have the same length"
#     sent_csv = []
#     for meta, exurn, ctsurn in zip(sents_meta, exurns, ctsurns):
#         sent_csv.append([exurn, config["work"], config["author"], meta.subdoc, "",
#                          config["genre"], "", config["chronology"], ctsurn])
#     return sent_csv
#
#

def process_token(tok):

    #
    form = tok.form if tok.form else ""
    lemma = tok.lemma if tok.lemma else ""
    rank = tok.id
    postag = tok.postag if tok.postag else "---------"
    original_label = tok.relation if tok.relation else ""

    # is Member
    label_app = original_label.split("_")[-1]
    isMemberOfCoord = 'true' if label_app == "CO" else 'false'
    isMemberOfApos = 'true' if label_app == "AP" else 'false'

    # Morphs
    m = Morph(postag)
    pos = m.pos
    person = m.person
    number = m.number
    tense = m.tense
    mood = m.mood
    voice = m.voice
    gender = m.gender
    case = m.case
    degree = m.degree


    return  [form, lemma, rank, postag, pos, person, number, tense,
                    mood, voice, gender, case, degree, isMemberOfCoord,
                    isMemberOfApos]



def _create_tok_exurn(cite, line_list):
    c = CTS_URN(cite)
    _offsets = c.passage_component.split("-")
    start,end = _offsets[0], _offsets[-1]
    counter = line_list.count(start) +1
    base = c.get_urn_without_passage()
    s = "{}.tbtokens.{}.{}".format(base, start, counter)
    return s,end

#

#def process_sentence(sent, metadata, line_list):
#    """
#
#     Parameters
#     ----------
#     sent : AGLDTReader annotated sentence
#         an annotated sentence as a named tuple; the format is defined in the AGLDT corpus reader
#
#     Returns
#     -------
#     list (list) : sentence, words, artificials, relations
#
#     """
#     sent_el =

# def process_sentences(anno_sents):
#     """
#     Process a list of annotated sentences, typically a treebank file as read by the `annotated_sents` method
#     of the AGLDT corpurs reader.
#     Return a list with 4 elements: sentences, words, artificials and relations. Each list is in 'tabular format',
#     ready to be written in csv
#
#     Parameters
#     ----------
#     anno_sents : AGLDT annotated sentences
#
#     Returns
#     -------
#     list (list) : sentences, words, artificials and relations
#
#     """
#
#
#
#     return sents,words,arts,relations

def _create_tokenized_cts_urn(document_urn, cite_string, line_list):
    """Create the CTS-URN pointing to the tokenized edition. The URN contains a version ("tokenized") and a
    supplementary citation level (token nr.). E.g.:
        `urn:cts:greekLit:tlg0085.tlg003.perseus-grc2.tokenized:1.1`

    Which means: token 1 of line 1 of the tokenized version of `tlg0085.tlg003.perseus-grc2`.
    The function returns a CTS URN and a line number, ready to be added to the line list; in case of span-tokens, the
    line nr. returned is that of the *end* of the span (so that every other token in that line will be counted
    starting from 2).

    Parameters
    ----------
    document_urn : str
        urn of the digital edition
    cite_string
        cite attribute in the TB file
    line_list
        complete list of the line numbers attached to all the tokens preceding the attual one.

    Returns
    -------
    str : the CTS_URN
    int : the last line nr. in the token cite attribute

    """
    c = CTS_URN(cite_string)
    _offsets = c.passage_component.split("-")
    start, end = _offsets[0], _offsets[-1]
    counter = line_list.count(start) + 1

    # urn:cts:greekLit:tlg0012.tlg001.allen.tokenized:1.1.1
    s = "{}.tokenized:{}.{}".format(document_urn, start, counter)
    return s, end


def _create_cite2urn(collection, version, work_prefix, obj_id):
    assert collection in ["sentences", "tokens", "artificial"], "Unknown collection: {}".format(collection)
    return "urn:cite2:gagdt:{}.v{}:{}_{}".format(collection, version, work_prefix, obj_id)

def _write_csv(outpath, header, lines):
    with open(outpath, "w") as out:
        sent_writer = csv.writer(out, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        sent_writer.writerow(header)
        for i in lines:
            sent_writer.writerow(i)



if __name__ == "__main__":
    from tqdm import tqdm

    # parse the configuration file
    with open(sys.argv[1]) as f:
        config = json.load(f)

    # versioning
    version = config["version"]
    wprefix = config["work_prefix"]

    # read the treebank
    tb = AGLDTReader(config["treebank_root"], config["file_name"])
    ann_sents = tb.annotated_sents(config["file_name"])
    sents_meta = tb.get_sentences_metadata(config["file_name"])
    docurn = sents_meta[0].document_id

    # set the out directory and file name
    out_root = config["output_root"]
    outdir = os.path.join(out_root, wprefix)
    os.makedirs(outdir, exist_ok=True)
    fbasename = docurn.split(":")[-1]

    # start looping over the sentences
    tok_counter = 1
    art_counter = 1
    sents = []
    words = []
    arts = []
    relations = []
    _lines = []
    for i, (annsent, meta) in enumerate(zip(tqdm(ann_sents), sents_meta)):
        sdic = {}
        for e,tok in enumerate(annsent):
            t_line = process_token(tok)
            if isinstance(tok, Word):
                tid = _create_cite2urn("tokens", version, wprefix, tok_counter)
                t_line.insert(0, tid)
                tokurn, lend = _create_tokenized_cts_urn(docurn,tok.cite, _lines)
                _lines.append(lend)
                t_line.append(tokurn)
                tok_counter += 1
                words.append(t_line)
                if tok.id == "1":
                    start_token_counter = CTS_URN(tokurn).passage_component.split("-")[-1]
            elif isinstance(tok, Artificial):
                tid = _create_cite2urn("artificial", version, wprefix, art_counter)
                t_line.insert(0, tid)
                arts.append(t_line)
                art_counter += 1
            sdic[tok.id] = tid
        sid = _create_cite2urn("sentences", version,wprefix, i+1)
        sdic["0"] = sid


        # s: id, ctsurn, speaker, author, title, subdoc
        c = CTS_URN(tokurn).passage_component.split("-")[-1]
        sent_urn = s = "{}.tokenized:{}-{}".format(docurn, start_token_counter, c)
        s = [sid, config["author"], config["work"], meta.subdoc, sent_urn]
        sents.append(s)
        rels = [(sdic[w.head], "syntGoverns", sdic[w.id]) for w in annsent]
        rels.extend( [(wid, "isTokenOf", sdic["0"]) for k,wid in sdic.items() if k != 0] )

        relations.extend(rels)

    # write the CSV's
    sent_file = os.path.join(outdir, fbasename+".sentences.csv")
    _write_csv(sent_file, ["ID", "Author", "Work", "Subdoc", "TextURN"], sents)
    tok_file = os.path.join(outdir, fbasename+".tokens.csv")
    wordshead = ["ID", "Form", "Lemma", "Rank", "Postag", "Pos", "Person", "Number", "Tense", "Mood", "Voice",
                     "Gender", "Case", "Degree", "IsMemberOfCoord", "IsMemberOfApos", "TextURN"]
    _write_csv(tok_file, wordshead, words)
    art_file = os.path.join(outdir, fbasename+".artificial.csv")
    _write_csv(art_file, wordshead, arts)
    rel_file = os.path.join(outdir, fbasename+".relations.csv")
    _write_csv(rel_file, ["Source", "RelationType", "Target"], relations)



#     base_outname = os.path.join(config["out_folder"], docurn)
#
#     sent_start_counter, tok_start_counter = config["start_counters"]
#
#     # write the sentence csv file
#     sents_csv = process_sentences(docurn,ann_sents,sents_meta,config)
#     with open(base_outname + ".tbsents.csv", "w") as out:
#         sent_writer = csv.writer(out, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL)
#         sent_writer.writerow(["citeUrn","exemplarUrn", "work", "author", "subdoc", "metrical_description", "genre", "speaker",
#                            "chronology", "ctsUrn"])
#         for i,s in enumerate(sents_csv):
#             s.insert(0, "urn:cite:gagdt-beta:sentence.{}".format(+ sent_start_counter + i))
#             sent_writer.writerow(s)
#
#     sent_urns = [s[0] for s in sents_csv]
#
#     # Words and Artificials: sentence by sentence:
#     rel_csv = []
#     words_csv = []
#     art_csv = []
#     _lines = []
#     i = 0
#
#     for su,s in zip(sent_urns, ann_sents):
#         sdic = {0 : su}
#         for t in s:
#             wcsv = process_token(t)
#             wcsv.insert(0, "urn:cite:gagdt-beta:token.{}".format(tok_start_counter + i))
#             if isinstance(t, Word):
#                 if t.cite:
#                     wu, lend = _create_tok_exurn(t.cite, _lines)
#                     _lines.append(lend)
#                 else:
#                     wu = ""
#                 wcsv.append(wu)
#                 words_csv.append(wcsv)
#
#             if isinstance(t, Artificial):
#                 wcsv.append("synt_ellipsis")
#                 art_csv.append(wcsv)
#
#
#             i += 1
#             sdic[int(t.id)] = wcsv[0]
#
#         for t in s:
#             # second loop to populate rel_csv
#             dep = sdic[int(t.id)]
#             head = sdic[int(t.head)]
#             rel = t.relation.split("_")[0]
#             rel_csv.append([head, dep, rel])
#
#     with open(base_outname + ".tbtokens.csv", "w") as out:
#         tok_writer = csv.writer(out, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL)
#         tok_writer.writerow(["citeurn", "form", "lemma", "rank", "postag", "pos", "person", "number", "tense",
#                              "mood", "voice", "gender", "case", "degree", "head", "originalLabel", "isMemberOfCoord",
#                              "isMemberOfApos", "ctsUrn", "ne_type", "animacy", "exemplarUrn"])
#
#         for tok in words_csv:
#             tok_writer.writerow(tok)
#
#     with open(base_outname + ".tbartificials.csv", "w") as out:
#         tok_writer = csv.writer(out, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL)
#         tok_writer.writerow(["citeurn", "form", "lemma", "rank", "postag", "pos", "person", "number", "tense",
#                              "mood", "voice", "gender", "case", "degree", "head", "originalLabel", "isMemberOfCoord",
#                              "isMemberOfApos", "ctsUrn", "ne_type", "animacy", "exemplarUrn", "artificialType"])
#
#         for art in art_csv:
#             tok_writer.writerow(art)
#
#     with open(base_outname + ".relations.csv", "w") as out:
#         tok_writer = csv.writer(out, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL)
#         tok_writer.writerow(["Source", "Target", "RelType"])
#         for rel in rel_csv:
#             tok_writer.writerow(rel)


