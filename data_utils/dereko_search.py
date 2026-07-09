import os
import requests
import json
from bs4 import BeautifulSoup
import pandas as pd
from tqdm import tqdm, tqdm_notebook
from dotenv import load_dotenv
from collections import defaultdict
from typing import Optional, Tuple

load_dotenv()


# DeReKo is the biggest corpus of contemporary German language,
# hosted at the Institut für Deutsche Sprache (IDS) in Mannheim, Germany:
# https://www.ids-mannheim.de/digspra/pb-s1/projekte/korpora/.
# It consists of hundreds of sub-corpora from various sources,
# including newspapers, magazines, books, web data, etc.:
# https://www.ids-mannheim.de/digspra/pb-s1/projekte/korpora/archiv-1/.
# While DeReKo is not openly available for download, its largest part
# is accessible via the COSMAS II and KorAP search interfaces:
# https://www.ids-mannheim.de/digspra/pb-s1/projekte/korpora/verfuegbarkeit/.
# 1. COSMAS II is a collection of 624 corpora -- mostly DeReKo sub-corpora
#   as well as some other corpora:
#   https://www2.ids-mannheim.de/cosmas2/uebersicht.html
#   https://www2.ids-mannheim.de/cosmas2/projekt/referenz/korpora.html
#   COSMOS II- orpora are organized into 18 archives, from which
#   we are interested in the W-Archivs: main written archive W-Archiv
#   as well its later extensions W2-W4:
#   https://www2.ids-mannheim.de/cosmas2/projekt/referenz/archive.html.
#   From these corpora, we will be using D-Korpora (called corp-d in KorAP):
#   pre-defined collection of COSMOS II corpora of German origin
#   (excluding Austrian, Swiss and Luxembourish sources to avoid regionalisms).
#   COSMAS II is searchable via its web interface:
#   https://cosmas2.ids-mannheim.de/cosmas2-web/faces/investigation/archive.xhtml.
# 2. KorAP is a more modern corpus search interface, which is designed to
#   continue the work of COSMAS II:
#   https://www.ids-mannheim.de/digspra/pb-s1/projekte/korap/.
#   It provides access to the W-Archivs from COSMAS II as well as to
#   additional regional corpora:
#   https://korap.ids-mannheim.de/doc/corpus?embedded=True.
#   KorAP is accessible via its web interface: https://korap.ids-mannheim.de,
#   Python API (wrapper over R): https://github.com/KorAP/PythonKorAPClient,
#   https://pypi.org/project/KorAPClient/,
#   and REST API: https://korap.ids-mannheim.de/api/v1.0/openapi/.
# We choose KorAP over COSMAS II for the following reasons:
# 1. It is more modern and actively maintained: as of the end of Jan 2026,
#   KorAP is already querying DeReKo-KorAP-2026-I, while COSMAS II is still
#   on Deutsches Referenzkorpus DeReKo-2025-I.
# 2. KorAP web interface is more user-friendly and functional than COSMAS II,
#   in particular, it supports several query languages including COSMAS II.
# 3. KorAP web interface is more or less well-documented, as opposed to COSMAS II:
#   https://korap.ids-mannheim.de/doc?embedded=True.
# 4. Only KorAP provides Python and REST APIs for automated querying; they are
#   also sufficiently documented.
# However, Python API turned out to be quite limited in functionality
# (e.g., no support for complex queries with corpus constraints),
# is slow and seems unreliable: the origin of its returned frequency values
# is somewhat unclear as none of the web interfaces return the same values.
# Therefore, we decided to use the REST API directly via requests.


# API endpoint
base_url = "https://korap.ids-mannheim.de/api/v1.0"

headers = {
    "accept": "*/*",
    # setup:
    # 1. Get a client ID and client secret by registering an application
    #   at https://korap.ids-mannheim.de/settings/oauth. Save them
    #   in the .env under any name, you will need them
    #   to obtain an auth code in the next step.
    # 2. Authorize at https://korap.ids-mannheim.de/api/v1.0/openapi/
    #   using the obtained client ID and client secret. In the scope,
    #   select "search" in any case, and "match_info" in case
    #   linguistic annotations are required.
    # 3. Click "Try it out" of the /search endpoint, then "Execute" with
    #   any query (e.g., "test"). In the automatically generated curl command,
    #   you will see the bearer token.
    # 4. Set the obtained bearer token in the .env file as KORAP_AUTH_CODE
    # 5. IMPORTANT! The bearer token seems to reset every 24h or something,
    #   make sure to update timely to avoid errors with the API requests
    "Authorization": f"Bearer {os.getenv('KORAP_AUTH_CODE')}"
}

# Note: after receiving a notice from the IDS Mannheim support team,
# we learned that our async requests were causing issues on their servers,
# and so we provide only synchronous version now.
# For async verions, refer to
# https://github.com/maxschmaltz/DieKonstraints/blob/comp_constr_corp_study_mar26/data_utils/dereko_search.py

def _retrieve_dereko_lemma(match_id: str) -> str:

    # The API uses the matchID as a part of the url;
    # weirdly, its appearance in the responce JSON,
    # in the API documentation and in the url is different.
    # Let us consider the following match id from the response JSON:
    # match-B11/SEP/00005-p331-332.
    # It consists of four parts corresponding to the following API
    # docu arguments:
    # 1. corpus_id (B11)
    # 2. document_id (SEP)
    # 3. text_id (00005)
    # 4. match_id (p331-332)
    # However, to retrieve the match infos, we need to use the following url:
    # https://korap.ids-mannheim.de/api/v1.0/corpus/B11/SEP/00005/p331-332?...,
    # so that text_id and match_id are separated by a slash, not a dash.
    # Therefore, we need to remove the "match-" prefix and 
    # replace the last but one dash with a slash in the match id to get the required url.
    # Note that there are incremental properties `corpusSigle`, `docSigle`, and `textSigle`
    # (B11, B11/SEP, and B11/SEP/00005 in our example, correspondingly) that are also present
    # in the match info responce JSON, which can be used to compose the url as well,
    # but since the matchID is always present in the search response, we can use it directly.
    url_suffix = "/".join(match_id.replace("match-", "").split("-", 1))

    params = {
        "foundry": "tt", # text tagger with linguistic annotations
        "layer": "l"    # lemma layer
    }

    try:
        response = requests.get(
            url=f"{base_url}/corpus/{url_suffix}",
            headers=headers,
            params=params,
            timeout=30
        )
        if response.status_code == 200:
            data = response.json()
            # the annotations are all available only as HTML in the snippet;
            # more specifically, the match is marked by the <mark> tag,
            # and the lemma is available in the title of the <span> tag inside the <mark>:
            # <mark><span title=\"tt/l:Apfelbaum\">Apfelbäume</span></mark>
            html = data["snippet"]
            soup = BeautifulSoup(html, "html.parser")
            span = soup.find("mark").find("span", title=True)
            return span["title"].split("tt/l:")[-1]
        else:
            return
    except:
        return


def _get_dereko_count(
    inp: str,
    resolve_sz: bool,
    is_base: bool
) -> Tuple[int, Optional[str], Optional[str]]:

    # docu available under
    # https://korap.ids-mannheim.de/api/v1.0/openapi/
    # https://korap.ids-mannheim.de (Hilfe -> API)

    # we have two variants of search: either by lemma (`is_base=True`)
    # or by wordform (`is_base=False`); in the first case,
    # straigtforward search by "[base=lemma]" is performed,
    # and no further manipulations are needed; in the second case,
    # if we do not know the lemma of the searched wordform and want to resolve it,
    # we additionally request the first match in the corpus, and try to
    # retrieve the lemma from there with the /corpus endpoint,
    # and then perform the search by lemma
    params = {
        # see https://korap.ids-mannheim.de (Hilfe -> Anfragesprachen -> Poliqarp+)
        # (alternatively https://korap.ids-mannheim.de/doc/ql/poliqarp-plus?embedded=True)
        "q": f"[base={inp}]" if is_base else inp,   # lemma or wordform
        "ql": "poliqarp",
        "cq": (
            # all open- and close-source corpora (closed are 
            # available via authorization); this expression is composed automatically
            # by the KorAP web interface after authorization
            "(availability=/CC.*/ | availability=/ACA.*/ | availability=/QAO-NC/) "
            # only German corpora (Austrian, Luxembourish and Swiss excluded
            # to avoid catching regionalisms)
            "& referTo corp-d "
            # entries after 1970 to avoid historical language
            "& creationDate since 1970"
        ),
        # don't show anything so we can get faster response
        "context": "1-token,1-token",
        "engine": "lucene",
        # get exactly 1 match if we need to resolve the lemma
        "count": "0" if is_base else "1",
        "page": "1",
        "offset": "0",
        "cutoff": "false",
        "access-rewrite-disabled": "false",
        "show-tokens": "false",
        "show-snippet": "false"
    }

    try:

        response = requests.get(
            url=f"{base_url}/search",
            headers=headers,
            params=params,
            timeout=30
        )

        if response.status_code != 200:
            return -1, None, None

        data = response.json()
        count = data.get("meta", {}).get("totalResults", -1)

        # special case with eszett,
        # which is encoded as ss in CELEX
        if count == 0 and "ss" in inp and resolve_sz:
            sz_inp = inp.replace("ss", "ß")
            sz_count, sz_lemma, sz_match_id = _get_dereko_count(
                sz_inp,
                resolve_sz=False,
                is_base=is_base
            )
            if sz_count > 0:
                # it means that the inp with ß is correct
                sz_count += 0.3   # signalize of the replacement
            return sz_count, sz_lemma, sz_match_id

        if (not is_base) and data["matches"]:
            # try to resolve lemma
            match_id = data["matches"][0]["matchID"]
            lemma = _retrieve_dereko_lemma(match_id)
            if lemma:
                # perform the search by lemma
                count, _, _ = _get_dereko_count(
                    lemma,
                    # can't be True here, since we
                    # already resolved eszett above
                    resolve_sz=False,
                    is_base=True
                )
                # otherwise, lemma and match_id will be
                # rewritten to None if directly returning
                # the results of the search with `is_base=True`
                return count, lemma, match_id
            # else: lemma is already None

        else:
            # either None for non-lemmatized
            # with no matches: signalize of
            # the absence of the lemma in DeReKo,
            # or None for lemmatized search,
            # in which case lemma is ignored anyways
            lemma, match_id = None, None

        return count, lemma, match_id
    
    except Exception as e:
        return -1, None, None
    

def get_dereko_counts(
    inputs: list[str],
    resolve_sz: Optional[bool]=False,
    is_base: Optional[bool]=True,
    # if running from a Jupyter notebook,
    # adjust the path and the progress bar
    # correspondingly
    from_nb: Optional[bool]=False,
    nb_depth: Optional[int]=1
) -> Tuple[list[int], list[str]]:
    
    # since querying DeReKo can be time-consuming and resource-intensive,
    # we cache the frequency counts in a separate TSV file 
    # that stores word counts for both the CELEX nouns and the GeCoDB compounds

    # in this version, we also add optional lemma retrieval functionality;
    # for this version, we create a dedicated cache file that stores
    # both the retrieved lemmas and the word counts of the retrived lemmata
    # whenever possible, wordforms otherwise; the reason to separate
    # the cache files is that when `is_base=False, resolve_base=True`,
    # we have to make a request to DeReKo even if a homograph entry
    # is present in the first cache to make sure that the lemma is correct

    cache_path_prxf = "lemmatized" if is_base else "nlemmatized"
    cache_path = (
        # the version from [Shmalts:2026] is stored in
        # 'resources/comp_constr_corp_study_mar26/dereko_de_geq70_counts.tsv'
        # and was copied to the 'developed' folder for further extension
        "resources/developed"
        f"/dereko_de_geq70_counts_{cache_path_prxf}.tsv"
    )
    if from_nb:
        cache_path = "../" * nb_depth + cache_path
    if os.path.exists(cache_path):
        cache_df = pd.read_csv(
            cache_path,
            sep="\t",
            header=0,
            index_col="entry",
            # to be able to store decimal part for 'ß' cases
            dtype=defaultdict(lambda: str, wc="float")
        )
    else:
        # empty wc df
        columns = ["entry", "wc"] if is_base else ["entry", "lemma", "wc", "match_id"]
        cache_df = pd.DataFrame(columns=columns).set_index("entry")

    uncached_entries = list(set(inputs) - set(cache_df.index))

    if uncached_entries:

        _tqdm = tqdm if not from_nb else tqdm_notebook
        for inp in _tqdm(uncached_entries, desc="Fetching uncached frequencies from KorAP"):

            count, lemma, match_id = _get_dereko_count(
                inp,
                resolve_sz=resolve_sz,
                is_base=is_base
            )

            if count == -1:
                print("Aborting frequency retrieval due to an error with KorAP API.")
                # this will lead to an error when fetching all freqs,
                # which is the desired behavior here
                # since the recommendation from IDS Mannheim support team
                # is to stop querying for some time in case of errors
                break

            # count for lemma is lemma is not None, otherwise count for wordform
            cache_df.loc[inp, "wc"] = count
            if not is_base:
                cache_df.loc[inp, "lemma"] = lemma
                cache_df.loc[inp, "match_id"] = match_id

        cache_df.sort_index(inplace=True)
        cache_df.to_csv(
            cache_path,
            sep="\t",
            header=True,
            index=True,
            index_label="entry"
        )

    all_freqs = cache_df.loc[inputs, "wc"].tolist()
    dereko_lemmata = cache_df.loc[inputs, "lemma"].tolist() \
        if not is_base else inputs

    return all_freqs, dereko_lemmata


def _get_dereko_matches(inp: str) -> list:

    # docu available under
    # https://korap.ids-mannheim.de/api/v1.0/openapi/
    # https://korap.ids-mannheim.de (Hilfe -> API)

    params = {
        # see https://korap.ids-mannheim.de (Hilfe -> Anfragesprachen -> Poliqarp+)
        # (alternatively https://korap.ids-mannheim.de/doc/ql/poliqarp-plus?embedded=True)
        "q": f"[base={inp}]",   # lemma
        "ql": "poliqarp",
        "cq": (
            # all open- and close-source corpora (closed are 
            # available via authorization); this expression is composed automatically
            # by the KorAP web interface after authorization
            "(availability=/CC.*/ | availability=/ACA.*/ | availability=/QAO-NC/) "
            # only German corpora (Austrian, Luxembourish and Swiss excluded
            # to avoid catching regionalisms)
            "& pubPlaceKey=DE "
            # only press (avoid typos etc.)
            "& textType=/(:*[Zz]eitung|Zeitschrift|Magazin).*/ "
            # entries after 1970 to avoid historical language
            "& creationDate since 1970"
        ),
        # longer passages to be sure to contain all the necessary context
        "context": "30-token,30-token",
        "engine": "lucene",
        # get up to 10 matches
        "count": "10",
        "page": "1",
        "offset": "0",
        "cutoff": "false",
        "access-rewrite-disabled": "false",
        "show-tokens": "false",
        # will retrieve the context from there
        "show-snippet": "true"
    }

    try:

        matches = []

        response = requests.get(
            url=f"{base_url}/search",
            headers=headers,
            params=params,
            timeout=30
        )

        if response.status_code != 200:
            return

        data = response.json()
        for match in data["matches"]:
            html = match["snippet"]
            soup = BeautifulSoup(html, "html.parser")
            # empty spans
            for span in soup.find_all("span", {"class": "more"}):
                span.extract()
            lc = soup.find("span", {"class": "context-left"}).string
            rc = soup.find("span", {"class": "context-right"}).string
            hit = soup.find("span", {"class": "match"}).string
            if not all([lc, rc, hit]):
                continue
            match_info = {
                "id": match["matchID"],
                "lc": lc,
                "match": hit,
                "rc": rc
            }
            matches.append(match_info)

        return matches
    
    except Exception as e:
        return


def get_dereko_matches(
    inputs: list[str],
    # if running from a Jupyter notebook,
    # adjust the path and the progress bar
    # correspondingly
    from_nb: Optional[bool]=False,
    nb_depth: Optional[int]=1
) -> dict:
    
    # since querying DeReKo can be time-consuming and resource-intensive,
    # we cache the matches in a separate JSON file
    cache_path = "resources/developed/dereko_de_geq70_matches.tsv"
    if from_nb:
        cache_path = "../" * nb_depth + cache_path
    if os.path.exists(cache_path):
        with open(cache_path, encoding="utf-8") as c:
            cache_dict = json.load(c)
    else:
        cache_dict = {}

    uncached_entries = list(set(inputs) - set(cache_dict.keys()))

    if uncached_entries:

        _tqdm = tqdm if not from_nb else tqdm_notebook
        for inp in _tqdm(uncached_entries, desc="Fetching uncached matches from KorAP"):

            match_dict = _get_dereko_matches(inp)

            if match_dict is None:
                print("Aborting matches retrieval due to an error with KorAP API.")
                # this will lead to an error when fetching all matches,
                # which is the desired behavior here
                # since the recommendation from IDS Mannheim support team
                # is to stop querying for some time in case of errors
                break

            cache_dict[inp] = match_dict

        cache_dict = {
            k: cache_dict[k]
            for k in sorted(cache_dict)
        }
        
        with open(cache_path, "w", encoding="utf-8") as c:
            json.dump(cache_dict, c, indent=4, ensure_ascii=False)

    return {
        k: v for k, v in cache_dict.items()
        if k in inputs
    }