import attr
from collections import defaultdict
import pathlib
from clldutils.misc import slug
from pylexibank import Dataset as BaseDataset
from pylexibank import progressbar as pb
from pylexibank import Concept, Language, Lexeme
from pyedictor import fetch
from lingpy import Wordlist


@attr.s
class CustomConcept(Concept):
    Spanish_Gloss = attr.ib(default=None)
    Portuguese_Gloss = attr.ib(default=None)

@attr.s
class CustomLanguage(Language):
    SubGroup = attr.ib(default=None)

@attr.s
class CustomLexeme(Lexeme):
    Borrowing = attr.ib(default=None)
    Partial_Cognacy = attr.ib(default=None)


class Dataset(BaseDataset):
    dir = pathlib.Path(__file__).parent
    id = "blumpanotacana"
    concept_class = CustomConcept
    language_class = CustomLanguage
    lexeme_class = CustomLexeme


    def cmd_download(self, args):
        print("updating ...")
        with open(self.raw_dir.joinpath("raw.tsv"), "w", encoding="utf-8") as f:
            f.write(
                fetch(
                    "blumpanotacana",
                    columns=[
                        "CONCEPT",
                        "DOCULECT",
                        "SUBGROUP",
                        "FORM",
                        "VALUE",
                        "TOKENS",
                        "COGID",
                        "COGIDS",
                        "ALIGNMENT",
                        "MORPHEMES",
                        "BORROWING",
                        "NOTE"
                    ],
                    base_url="http://lingulist.de/edev"
                )
            )

    def cmd_makecldf(self, args):
        # add bib
        args.writer.add_sources()
        args.log.info("added sources")

        # add concept
        concepts = {}
        for concept in self.concepts:
            idx = slug(concept["ENGLISH"])
            args.writer.add_concept(
                    ID=idx,
                    Name=concept["ENGLISH"],
                    Spanish_Gloss=concept["SPANISH"],
                    Portuguese_Gloss=concept["PORTUGUESE"],
                    Concepticon_ID=concept["CONCEPTICON_ID"],
                    Concepticon_Gloss=concept["CONCEPTICON_GLOSS"]
                    )
            concepts[concept["ENGLISH"]] = idx
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
            "morphemes",
            "borrowing",
            "note"
            ),
            desc="cldfify"
        ):
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
                    Segments=tokens,
                    Cognacy=cogid,
                    Partial_Cognacy=" ".join([str(x) for x in cogids]),
                    Comment=note,
                    Borrowing=borrowing
                )

                args.writer.add_cognate(
                    lexeme=lexeme,
                    Cognateset_ID=cogid
                    )
