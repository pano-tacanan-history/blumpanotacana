# CLDF dataset derived from Blum et al.'s (2024) "A Comparative Wordlist for Investigating Distant Relations Among Languages in Lowland South America"

[![CLDF validation](https://github.com/pano-takanan-history/blumpanotacana/workflows/CLDF-validation/badge.svg)](https://github.com/pano-takanan-history/blumpanotacana/actions?query=workflow%3ACLDF-validation)

## How to cite

If you use these data please cite
- the original source
  > Blum, Frederic and Barrientos, Carlos and Zariquiey, Roberto and List, Johann-Mattis. 2024. A Comparative Wordlist for Investigating Distant Relations Among Languages in Lowland South America. *Scientific Data* 11(92). https://doi.org/10.1038/s41597-024-02928-7
- the derived dataset using the DOI of the [particular released version](../../releases/) you were using

## Description


Comparative wordlist for Panoan and Tacanan languages, as well as a selection of language isolates that have been hypothesized to be related to Pano-Tacanan.

This dataset is licensed under a CC-BY-4.0 license


Conceptlists in Concepticon:
- [Blum-2024-501](https://concepticon.clld.org/contributions/Blum-2024-501)
## Notes

### Installing the necessary dependencies

In a first step, please clone this repository and install the necessary requirements.

```CLI
git clone https://github.com/pano-tacanan-history/blumpanotacana
cd blumpanotacana
pip install -e .
```

You have now access to all relevant packages that are used for the CLDF conversion. For example, you can recreate the CLDF folder with the following command:

`cldfbench lexibank.makecldf lexibank_blumpanotacana.py --concepticon-version=v3.1.0 --glottolog-version=v4.8 --clts-version=v2.2.0`

This command uses the most up-to-date version of the reference catalogues (Concepticon, Glottolog, CLTS) and the raw data, to re-create the CLDF folder.

### Convert the data to SQL to integrate other datasets

To ease the integration with other datasets, we recommend to convert the dataset to SQL. This is easily done by running the following command from pycldf:

`cldf createdb cldf/cldf-metadata.json analysis/blumpanotacana.sqlite3`

As an example, you can easily integrate the data from Grambank. As a pre-requisite, please clone Grambank (<https://github.com/grambank/grambank/tree/v1.0.3>) and create the sqlite-database in the same way as presented above. In order to now retrieve the data of the languages that are both in this dataset and in Grambank, you can use the following code in `sqlite3`:

```SQL
attach 'blumpanotacana.sqlite3' as db1;
attach 'grambank/grambank.sqlite3' as db2;

SELECT count(a.cldf_glottocode) FROM
  db1.LanguageTable a
INNER JOIN
  db2.LanguageTable b 
ON 
  a.cldf_glottocode = b.cldf_glottocode;
```

As you can see from the output, 15 of the 21 languages in the dataset are coded for Grambank. If you want to retrieve the Grambank features for those languages, you can run the following command:

```SQL
SELECT * FROM
  db1.LanguageTable a
INNER JOIN
  db2.ValueTable b 
ON 
  a.cldf_glottocode = b.cldf_languageReference;
```

### Plots from the release paper

The repository contains a series of files that have been used for several plots that have been used in the release publication. The necessary commands are all stored in a Makefile, that can be run directly from the command line. We present three features:

1. Creating a tsv-wordlist from the data
2. Compute the coverage and synonymy across languages
3. Create heatmaps of shared cognacy and shared regularity

In order to run the code, please change your working directory to the `analysis` folder and install the packages that are necessary for replication.

```CLI
cd analysis/
pip install -r requirements.txt
```

#### Create the wordlist

The first command, `make wordlist`, creates a tsv-based wordlist that can be used with EDICTOR (<www.digling.org/edictor>). You can also open the data directly in EDICTOR using the following link: <https://lingulist.de/edev/?file=blumpanotacana.tsv&preview=500&basics=DOCULECT|CONCEPT|TOKENS|COGIDS&publish=true>

You may use this link to visualize the data, but you will not be able to manipulate any annotations online.

Note: If you don't have pyedictor installed set, you can do so running the command `pip install pyedictor` from the command line.

#### Compute the coverage of concepts

Running the command `make coverage` runs the script `s_compute_coverage`, that presents a count of synonymy and coverage of concepts across all languages in the database.

#### Shared cognates across languages

Finally, the command `make heatmap` creates a heatmap visualizing the amount of shared cognacy between languages. For a better understandable visualization, we showcase this for the Panoan languages only. If you want to run this for the whole dataset, you can remove the `-pano` argument from the Makefile.

#### Map of all languages

The R-Script `map.R` adds the code that was used to create the map `map_fig.png`. You can run the code with the following command in the command-line: `make map`. The R-version as well as the versions for the necessary packages are given as a comment in the script, in case the replication fails in the future.

#### Automated extraction of correspondence patterns

We include a script that automatically extracts the correspondence patterns from the dataset. The code uses the [LingRex](https://github.com/lingpy/lingrex)-package and is stored in `s_patterns.py`. You can also run the code via the make-command `make patterns`. The output is stored in `d_patterns.tsv` and can be accessed with all common office applications. The script takes the `bpt_alg.tsv` file as input, which is created from running the `make heatmap` command, including all the filters used in there.



## Statistics


[![CLDF validation](https://github.com/pano-takanan-history/blumpanotacana/workflows/CLDF-validation/badge.svg)](https://github.com/pano-takanan-history/blumpanotacana/actions?query=workflow%3ACLDF-validation)
![Glottolog: 100%](https://img.shields.io/badge/Glottolog-100%25-brightgreen.svg "Glottolog: 100%")
![Concepticon: 100%](https://img.shields.io/badge/Concepticon-100%25-brightgreen.svg "Concepticon: 100%")
![Source: 100%](https://img.shields.io/badge/Source-100%25-brightgreen.svg "Source: 100%")
![BIPA: 100%](https://img.shields.io/badge/BIPA-100%25-brightgreen.svg "BIPA: 100%")
![CLTS SoundClass: 100%](https://img.shields.io/badge/CLTS%20SoundClass-100%25-brightgreen.svg "CLTS SoundClass: 100%")

- **Varieties:** 21 (linked to 19 different Glottocodes)
- **Concepts:** 501 (linked to 501 different Concepticon concept sets)
- **Lexemes:** 10,226
- **Sources:** 14
- **Synonymy:** 1.18
- **Cognacy:** 10,226 cognates in 6,210 cognate sets (4,751 singletons)
- **Cognate Diversity:** 0.59
- **Invalid lexemes:** 0
- **Tokens:** 56,787
- **Segments:** 208 (0 BIPA errors, 0 CLTS sound class errors, 206 CLTS modified)
- **Inventory size (avg):** 36.62

# Contributors

Name | GitHub user | Description | Role |
--- | --- | --- | --- |
Frederic Blum | @FredericBlum | Data collection, CLDF conversion and annotation | Author, Editor |
Carlos M. B. Ugarte | @MuffinLinwist | CLDF conversion and annotation | Author, Editor |
Roberto Zariquiey | | Data collector | Author |
Johann-Mattis List | @LinguList| CLDF conversion | Author |




## CLDF Datasets

The following CLDF datasets are available in [cldf](cldf):

- CLDF [Wordlist](https://github.com/cldf/cldf/tree/master/modules/Wordlist) at [cldf/cldf-metadata.json](cldf/cldf-metadata.json)