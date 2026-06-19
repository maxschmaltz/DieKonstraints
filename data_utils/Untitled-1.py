# %%
import os
import pandas as pd
from uuid import uuid4
from tqdm.asyncio import tqdm
import re
from collections import defaultdict
import math
from typing import Optional, Tuple

# %%
from gecodb_compound_parser import Compound, perform_umlaut
from dereko_search import get_dereko_counts

# %%
sp18_path = "resources/schaefer_pankratz_2018/Concordance.full.csv"
celex_gml_path = "resources/Celex/german/gml/gml.cd"
celex_gmw_path = "resources/Celex/german/gmw/gmw.cd"

outdir = "resources/developed/sp18"

outcsv_args = {
    "sep": "\t",
    "index": True,
    "header": True
}

# %%
sp18 = pd.read_csv(
    sp18_path,
    sep="\t",
    header=0,
    index_col="Match",
    dtype=defaultdict(lambda: str, LE="int"),   # all str, LE int
    quoting=3   # = csv.QUOTE_NONE, separate by tabs only
)
sp18.head()

# %%
def umlambda(x: str) -> str:
    x = x.lower()
    x = re.sub("(?<![aeiouy])ae", "ä", x, flags=re.IGNORECASE)
    x = re.sub("(?<![aeiouy])oe", "ö", x, flags=re.IGNORECASE)
    x = re.sub("(?<![aeiouy])ue", "ü", x, flags=re.IGNORECASE)
    return x

# %%
gml = pd.read_csv(
    celex_gml_path,
    sep="\\",
    header=None,
    dtype=str,
    usecols=[0, 1],
    names=["id", "lemma"],
    index_col="id"
).dropna()

# keep only nouns
gml = gml[gml["lemma"].str[0].str.isupper()]

gml

# %%
gmw = pd.read_csv(
    celex_gmw_path,
    sep="\\",
    header=None,
    dtype=str,
    usecols=[1, 3, 4],
    names=["wordform", "id", "forms"],
    index_col="id"
).dropna()

gmw

# %%
# joining will automatically drop non-noun wordforms,
# because they have no lemma in gml
gmwl = gmw.join(gml["lemma"], how="inner")  \
    .reset_index(drop=True)  \
    .set_index("wordform")  \
    .sort_index()

gmwl.index = gmwl.index.map(umlambda)
gmwl["lemma"] = gmwl["lemma"].map(umlambda)
gmwl = gmwl[["lemma", "forms"]]

gmwl

# %%
# Comparing the original Match column values with
# with reconstructions from `parse_sp18_comp()`
# (before lemmatization to NomSg with the help of CELEX2!)
# during development of this module
# revealed 154 mismatches in compounds built from
# six different N1. Manual inspection of these mismatches revealed that
# some compounds with N1s 'Dämon', 'Gerät', 'Geräusch', 'Schloss'
# were spelled alternatively, and that compounds
# with N1s 'Auge' and 'Birne' productively exhibit
# alternation between _+n_ and _-e_ (!).
# See more in 'resources/developed/sp18/leftovers/mismatches.csv'.
# Thus, we will correct
# the spellings of the first four N1s and remove
# all compounds with the last two N1s.

# After these two changes, all reconstructed compounds
# after `parse_sp18_comp()` do match the original Match column
# (before lemmatization to NomSg with the help of CELEX2!).

# correct spellings
for old, new in [
    ("Daemon", "Dämon"),
    ("Geraet", "Gerät"),
    ("Geraeusch", "Geräusch"),
    ("Schloß", "Schloss")
]:
    sp18.index = sp18.index.map(
        lambda x: x.replace(old, new)
        if x.startswith(old) else x
    )

# remove compounds with N1s 'Auge' (N=185) and 'Birne' (N=200)
sp18 = sp18[~sp18["N1Lemma"].isin(["Auge", "Birne"])]

# %%
# drop NaN (2 rows only)
sp18 = sp18.dropna()

# %%
# extract document metadata from the dataset;
# most probably, we won't need it (also
# many URLs are now down, anyways),
# so by decomposing the dataframe, we can
# reduce processing effort; on the other hand,
# joining the metadata back to the main dataframe
# is easy, so we can always do it later if needed

# first, join the left and right contexts into a single column,
# drop the original columns, and assign a unique id to each context
sp18["context"] = sp18.LC + " " + sp18.index + " " + sp18.RC
sp18.drop(columns=["LC", "RC"], inplace=True)
sp18["context_id"] = [str(uuid4()) for _ in range(len(sp18))]
sp18.head()

# %%
# now, extract the document metadata
# into a separate dataframe
sp18_meta = sp18[
        ["context_id", "DocID", "DocURL", "SentID"]
    ]   \
    .rename(
        columns={"DocID": "doc_id", "DocURL": "url", "SentID": "sent_n"}
    )   \
    .reset_index(drop=True) \
    .set_index("context_id")    \
    .sort_index()

sp18_meta.to_csv(
    os.path.join(outdir, "sp18_meta.tsv"),
    **outcsv_args
)
sp18_meta.head()

# %%
# finally, drop the metadata columns
# from the main dataframe
sp18.drop(columns=["DocID", "DocURL", "SentID"], inplace=True)
sp18.head()

# %%
# First, we need to be able to reconstruct the whole
# compound composition. We need that for three reasons:
# 1. To be able to revert the compounds to NomSg,
# which, in its turn, is required to identify duplicates;
# 2. Beside duplicates removal, we will also be able to
# identify contrastive pairs from the same constituents
# but with pluralic vs. non-pluralic linkers. This would
# be needed to assess the external plural effect
# following the method suggested in [pankratz_2017:20]
# (even though the examples are given for the internal plural effect).
# There is a change that the findings with this approach
# will be different as in [schaefer_pankratz_2018:26] since they
# do not contrast such pairs but rather compare all compounds in Pl forms
# to those in Sg forms.
# 3. Finally, similarly to [shmalts_2026], we would want
# to filter out the constituents not present in CELEX-nouns.

def lemmatize_n2(n2: str, expected_num: str) -> str:
    if n2 not in gmwl.index:
        return n2, False
    n2s = gmwl.loc[n2]
    if isinstance(n2s, pd.Series):  # one row found
        return n2s["lemma"], True
    else:
        if n2s.lemma.nunique() == 1:
            # one variant, ok
            return n2s.lemma.iloc[0], True
        else:
            # try finding a variant
            # that would correspond
            # to the annotated number of N2
            ncode = "P" if expected_num == "pl" else "S"
            matching_n2s = n2s[n2s["forms"].str.contains(ncode)]
            if matching_n2s.lemma.nunique() == 1:
                # one variant, ok
                return matching_n2s.lemma.iloc[0], True
    # otherwise: multiple variants matching the expected number,
    # unreliable parsing
    return n2, False


def parse_sp18_comp(
    comp: str,
    n1: str,
    pl_marker: str,
    has_linker: bool,
    n2_num: str,
    pbar: tqdm
) -> Tuple[str, str, str, str, bool]:

    pl_gc_template = "_+={pl_marker}_" if "U" in pl_marker else "_+{pl_marker}_"
    maybe_uml = perform_umlaut if ("U" in pl_marker and has_linker) else lambda x: x
    pl_marker = pl_marker.replace("U", "")
    # Schäfer & Pankratz 2018 only consider two
    # contrastive options: zero linker vs. pluralic linker;
    # are other non-pluralic linkers present in the dataset?
    linker = pl_marker if has_linker else ""
    n1_cstem = maybe_uml(n1) + linker
    n2 = re.sub(f"^{n1_cstem}", "", comp)

    # now, take the resulting n2 and lemmatize it to NomSg with the help of CELEX2
    n2, is_lemmatized = lemmatize_n2(n2, expected_num=n2_num)

    # gecodb style
    pl_gc = pl_gc_template.format(pl_marker=pl_marker)
    gecodb = f"{n1}{pl_gc if has_linker else '_'}{n2}"

    # recover lemma
    lemma = Compound(gecodb).lemma

    pbar.update(1)

    return gecodb, lemma, pl_gc, n2, is_lemmatized

# %%
sp18.index = sp18.index.map(str.lower)
for col in ["N1Lemma", "N2Num", "N2Typ"]:
    sp18[col] = sp18[col].map(str.lower)
sp18.head()

# %%
with tqdm(total=len(sp18), desc="Lemmatizing compounds") as pbar:
    sp18["gecodb"], sp18["lemma"], sp18["n1_pl_marker"],    \
    sp18["n2"], sp18["is_lemmatized"] = zip(
        *sp18.apply(
            lambda row: parse_sp18_comp(
                comp=row.name,
                n1=row["N1Lemma"],
                pl_marker=row["N1Pl"],
                has_linker=int(row["LE"]),
                n2_num=row["N2Num"],
                pbar=pbar
            ),
            axis=1
        )
    )

sp18.head()

# %%
# Retrieve word counts from DeReKo; we have two scenarios:
# Lemmatized compounds may be searched directly;
# Non-lemmatized compounds will be first searched as a simple text search;
# if there are matches, the lemma annotation will be retrieved
# from the first match, and a consequent search for the retrieved lemma
# will be performed. This, the search will accomplish two goals:
# 1. It will allow us to retrieve counts for both lemmatized compounds
# (total word count of all wordforms) and counts for non-lemmatized compounds
# (only total count of the corresponding wordform).
# 2. It will partly retrieve the lemma annotation for non-lemmatized compounds.


def dereko_wrapper(
    input_lemmata: list[str],
    batch_size: Optional[int]=1000,
    **kwargs
) -> Tuple[list[int], list[str]]:

    # get dereko WCs; run in batches to enforce regular caching;
    # the cache is stored in 
    # resources/comp_constr_corp_study_mar26/dereko_de_geq70_counts.tsv
    freqs = []
    output_lemmata = []

    progress_bar = tqdm(
        total=math.ceil(len(input_lemmata) / batch_size),
        desc="Retrieving KorAP frequencies in batches"
    )

    for batch_start in range(0, len(input_lemmata), batch_size):
        batch = input_lemmata[batch_start:batch_start + batch_size]
        batch_freqs, batch_lemmata = get_dereko_counts(batch, **kwargs)
        freqs.extend(batch_freqs)
        output_lemmata.extend(batch_lemmata)
        progress_bar.update(1)
        
    return freqs, output_lemmata

# %%
# get counts for lemmatized compounds
input_lemmata_l = sp18[sp18["is_lemmatized"]].lemma \
    .map(str.capitalize).unique().tolist()

# get counts for lemmatized compounds
freqs_l, _ = dereko_wrapper(
    input_lemmata_l,
    resolve_sz=True,
    is_base=True
)

# get counts for non-lemmatized compounds
input_lemmata_nl = sp18[~sp18["is_lemmatized"]].lemma \
    .map(str.capitalize).unique().tolist()

# get counts for lemmatized compounds
freqs_nl, output_lemmata = dereko_wrapper(
    input_lemmata_nl,
    resolve_sz=True,
    is_base=False
)