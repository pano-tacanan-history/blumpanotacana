from __future__ import unicode_literals, print_function, division
from lingpy import Wordlist, LexStat, Alignments
from lingpy.convert.strings import write_nexus
from lexibank_blumpanotacana import Dataset as BPT
from lingpy.compare.partial import *
from lingpy.sequence.sound_classes import ipa2tokens

# load the wordlist
ds = BPT()

wl = Wordlist.from_cldf(
    str(ds.cldf_dir.joinpath("cldf-metadata.json").as_posix()),
    # columns to be loaded from CLDF set
    columns=(
        "language_id",
        "language_core",
        "concept_name",
        "segments",
        "form"
        ),
    # a list of tuples of source and target
    namespace=(
        ("language_id", "doculect"),
        ("concept_name", "concept"),
        ("segments", "tokens")
        )
    )


D = {0: [c for c in wl.columns]}
for idx in wl:
    if wl[idx, "language_core"] == "1":
        D[idx] = [wl[idx, c] for c in D[0]]

# print(language_count)
wl = Wordlist(D)

# count number of languages, number of rows, number of concepts
print(
    "Wordlist has {0} languages and {1} concepts across {2} rows.".format(
        wl.width, wl.height, len(wl)))

lex = Partial(wl, segments='tokens', check=False)
lex.partial_cluster(method='sca', threshold=0.45, ref="cogids")

lex = Alignments(lex, ref="cogids")
lex.align(ref="tokens")

lex = LexStat(lex, segments='tokens', check=False)
lex.get_scorer(runs=10000)
lex.cluster(method='lexstat', threshold=0.55, ref="cogid")

lex.output('tsv', filename='analysis/bpt-cogids')

# wl = Wordlist("analysis/bpt-cogids.tsv")
# nexus = write_nexus(wl, ref='cogids', mode='splitstree', filename='analysis/bpt_auto.nex')