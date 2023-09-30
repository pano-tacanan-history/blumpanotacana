"""
Producing heatmaps for comparison of shared cognacy.
"""
import argparse
import re
import matplotlib as mpl
from lingpy import LexStat, Alignments, Wordlist
from lingpy.convert.plot import plot_heatmap
from lingpy.read.qlc import reduce_alignment
from lingpy.sequence.sound_classes import tokens2class
from lingrex.copar import CoPaR
from lingreg.checks import identify_regular
from lingrex.util import prep_wordlist


# settings and major table
NAME = "blumpanotacana"
COUNT = 0
WORD = 0.75
PATTERN = 3


def clean_slash(x):
    """Cleans slash annotation from EDICTOR."""
    cleaned = []
    for segment in x:
        if "/" in segment:
            after_slash = re.split("/", segment)[1]
            cleaned.append(after_slash)
        else:
            cleaned.append(segment)

    return cleaned


def get_copar(filename, min_refs=3, ref="cogid", structure="structure"):
    """Function that compiles a CoPaR object and clusters all sites."""
    copar = CoPaR(
        filename, transcription="form", ref=ref, structure=structure,
        min_refs=min_refs)
    copar.get_sites()
    copar.cluster_sites()
    copar.sites_to_pattern()

    return copar


def preprocessing(copar):
    """Identifying the regular words in wlist."""
    wl_reg = identify_regular(
        copar,
        pattern_threshold=PATTERN,
        ref="cogid",
        regularity_col="regularity"
        )

    wl_reg = LexStat(wl_reg)

    return wl_reg


def shared_reg(lng_a, lng_b, wlist):
    """Computes the pairwise regularity between languages."""
    cognate_pairs = 0
    same_cogid = 0
    reg_count = 0
    counter = 0

    pairs = (lng_a, lng_b) if (lng_a, lng_b) in wlist.pairs else (lng_b, lng_a)
    # print(wlist.pairs[pairs])
    for idx_a, idx_b in wlist.pairs[pairs]:
        if lng_a == "Movima" and lng_b == "Tacana":
            counter += 1
            print(wlist[idx_a])
            print(wlist[idx_b])
            print("----")
            print(counter)

        # gives the pair of cogids, not an individual cogid
        for cogid_a in wlist[idx_a, 'cogids']:
            for cogid_b in wlist[idx_b, 'cogids']:
                cognate_pairs += 1
                if cogid_a == cogid_b:
                    same_cogid += 1
                    reg = wlist[idx_a, 'regularity'], wlist[idx_b, 'regularity']
                    if reg[0] > WORD:
                        reg_count += 1
    if same_cogid != 0 and cognate_pairs != 0:
        shared_regularity = reg_count/same_cogid
        shared_cognates = same_cogid/cognate_pairs
    else:
        shared_regularity = 0
        shared_cognates = 0
    # print(lng_a, lng_b, shared_cognates)

    return shared_regularity, shared_cognates


def create_plot(setting="cognate", only_pano=True):
    wl = Wordlist("d_blumpanotacana.tsv")

    # Select Pano subset only
    if only_pano is True:
        D = {0: [c for c in wl.columns]}  # defines the header
        for idx in wl:
            if wl[idx, "subgroup"] == "Pano":
                D[idx] = [wl[idx, c] for c in D[0]]
        wl = Wordlist(D)

    wordlist = prep_wordlist(wl)
    alms = Alignments(wordlist, ref="cogids", transcription="tokens")

    dct = {}
    for idx, msa in alms.msa["cogids"].items():
        # print(alms.msa["cogids"][idx])
        msa_reduced = []
        for site in msa["alignment"]:
            reduced = reduce_alignment([site])[0]
            reduced = clean_slash(reduced)
            msa_reduced.append(reduced)
        for i, row in enumerate(msa_reduced):
            dct[msa["ID"][i]] = row

    alms.add_entries("tokens", dct,
                    lambda x: " ".join([y for y in x if y != "-"]),
                    override=True)
    alms.add_entries("alignment", dct,
                    lambda x: " ".join([y for y in x]),
                    override=True)
    alms.add_entries("structure", "tokens",
                    lambda x: tokens2class(x.split(" "), "cv"))

    alms.output("tsv", filename="bpt_alg")
    #######

    cop = get_copar("bpt_alg.tsv", ref="cogid", structure="structure", min_refs=3)
    cop.calculate("tree")
    TREE = str(cop.tree)

    reg_words = preprocessing(cop)

    matrix = [[0 for i in reg_words.language] for j in reg_words.language]

    mode = 1
    description = "Shared cognacy between language pairs"

    for j, lang_a in enumerate(reg_words.language):
        for k, lang_b in enumerate(reg_words.language):
            if j < k:
                matrix[j][k] = shared_reg(lang_a, lang_b, reg_words)[mode]
                matrix[k][j] = shared_reg(lang_a, lang_b, reg_words)[mode]

            elif j == k:
                matrix[j][k] = 1

    outputname = "shared_" + setting

    plot_heatmap(reg_words, filename=outputname, tree=TREE,
                 vmin=0.0, vmax=0.7, cmap=mpl.colormaps['viridis'],
                 colorbar_label=description, matrix=matrix,
                 )


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-pano",
                        action='store_true',
                        help="Choose if you want to compute the heatmaps only for Panoan languages.")
    args = parser.parse_args()
    create_plot("cognates", only_pano=args.pano)
