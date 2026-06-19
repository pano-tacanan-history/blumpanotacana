import dataclasses
from typing import Optional
from collections import defaultdict
import pathlib
from clldutils.misc import slug
from pylexibank import Dataset as BaseDataset
from pylexibank import progressbar as pb
from pylexibank import Concept, Language, Lexeme
from lingpy import Wordlist

def unmerge(sequence):
    out = []
    for tok in sequence:
        out += tok.split('.')
    return out


@dataclasses.dataclass
class CustomConcept(Concept):
    Spanish_Gloss: Optional[str] = None


@dataclasses.dataclass
class CustomLanguage(Language):
    SubGroup: Optional[str] = None


@dataclasses.dataclass
class CustomLexeme(Lexeme):
    Borrowing: Optional[str] = None
    Partial_Cognacy: Optional[str] = None
    Alignment: Optional[str] = None
    Morphemes: Optional[str] = None
    GroupedSounds: Optional[str] = None


class Dataset(BaseDataset):
    dir = pathlib.Path(__file__).parent
    id = "blumpanotacana"
    concept_class = CustomConcept
    language_class = CustomLanguage
    lexeme_class = CustomLexeme

    def cmd_makecldf(self, args):
        # add bib
        args.writer.add_sources()
        args.log.info("added sources")

        # add concept
        concepts = {}
        for concept in self.conceptlists[0].concepts.values():
            idx = concept.id.split("-")[-1] + "_" + slug(concept.english)
            args.writer.add_concept(
                ID=idx,
                Name=concept.english,
                Spanish_Gloss=concept.attributes["spanish"],
                Concepticon_ID=concept.concepticon_id,
                Concepticon_Gloss=concept.concepticon_gloss,
            )

            concepts[concept.english] = idx

        args.log.info("added concepts")

        # add language
        languages = {}
        sources = defaultdict()
        for language in self.languages:
            args.writer.add_language(
                    ID=language["ID"],
                    Name=language["Name"],
                    Glottocode=language["Glottocode"],
                    SubGroup=language["SubGroup"]
                    )
            languages[language["ID"]] = language["Name"]
            sources[language["ID"]] = language["Source"]
        args.log.info("added languages")

        errors = set()
        wl = Wordlist(str(self.raw_dir.joinpath("raw.tsv")))

        N = {}
        for idx, cogids, morphemes in wl.iter_rows("cogids", "morphemes"):
            new_cogids = []
            if morphemes:
                for cogid, morpheme in zip(cogids, morphemes):
                    if not morpheme.startswith("_"):
                        new_cogids += [cogid]
            else:
                new_cogids = [c for c in cogids if c]

            if new_cogids == []:
                new_cogids = [c for c in cogids if c]

            N[idx] = " ".join([str(x) for x in new_cogids])
        wl.add_entries("cog", N, lambda x: x, override=True)
        wl.renumber("cog")  # creates numeric cogid

        # add data
        for (
            idx,
            concept,
            language,
            form,
            value,
            tokens,
            cogid,
            cogids,
            alignment,
            morphemes,
            borrowing,
            note
        ) in pb(
            wl.iter_rows(
            "concept",
            "doculect",
            "form",
            "value",
            "tokens",
            "cogid",
            "cogids",
            "alignment",
            "morphemes",
            "borrowing",
            "note"
            ),
            desc="cldfify"
        ):
            if morphemes == []:
                morphemes = ["?"]
            if language not in languages:
                errors.add(("language", language))
            elif concept not in concepts:
                errors.add(("concept", concept))
            elif tokens:
                lexeme = args.writer.add_form_with_segments(
                    Parameter_ID=concepts[concept],
                    Language_ID=language,
                    Form=form.strip(),
                    Value=value.strip() or form.strip(),
                    Segments=unmerge(tokens),
                    GroupedSounds=tokens,
                    Cognacy=cogid,
                    Partial_Cognacy=" ".join([str(x) for x in cogids]),
                    Alignment=" ".join(alignment),
                    Morphemes=" ".join(morphemes),
                    Comment=note,
                    Borrowing=borrowing,
                    Source=sources[language]
                )

                args.writer.add_cognate(
                    lexeme=lexeme,
                    Cognateset_ID=cogid,
                    Alignment=alignment,
                    Alignment_Method="false",
                    Alignment_Source="expert"
                    )
