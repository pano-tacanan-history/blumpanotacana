import attr
import pathlib
from clldutils.misc import slug
from pylexibank import Dataset as BaseDataset
from pylexibank import progressbar as pb
from pylexibank import Concept, Language


@attr.s
class CustomConcept(Concept):
    Spanish_Gloss = attr.ib(default=None)
    Portuguese_Gloss = attr.ib(default=None)


@attr.s
class CustomLanguage(Language):
    Core = attr.ib(default=None)


class Dataset(BaseDataset):
    dir = pathlib.Path(__file__).parent
    id = "blumpanotacana"
    concept_class = CustomConcept
    language_class = CustomLanguage

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
            concepts[concept["CONCEPTICON_GLOSS"]] = idx
        args.log.info("added concepts")

        # add language
        languages = {}
        for language in self.languages:
            args.writer.add_language(
                    ID=language["ID"],
                    Name=language["Name"],
                    Glottocode=language["Glottocode"],
                    Core=language["Core"]
                    )
            languages[language["ID"]] = language["Name"]
        args.log.info("added languages")

        # read in data
        data = self.raw_dir.read_csv(
            "filtered_raw.tsv", delimiter="\t", dicts=True
        )
        # add data
        idx = 1
        for entry in pb(data, desc="cldfify", total=len(data)):
            args.writer.add_forms_from_value(
                ID=idx,
                Parameter_ID=concepts[entry["CONCEPTICON_GLOSS"]],
                Language_ID=entry["DOCULECT"],
                Value=entry["VALUE"]
            )
