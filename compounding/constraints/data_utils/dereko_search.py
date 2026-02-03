import os
import asyncio
import aiohttp
import pandas as pd
from tqdm.asyncio import tqdm_asyncio
from dotenv import load_dotenv

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
url = "https://korap.ids-mannheim.de/api/v1.0/search"

headers = {
    "accept": "*/*",
    # prerequisites:
    # 1. Get a client ID and client secret by registering an application
    #   at https://korap.ids-mannheim.de/settings/oauth
    # 2. Authorize at https://korap.ids-mannheim.de/api/v1.0/openapi/
    # 3. Set the obtained auth code in the .env file as KORAP_AUTH_CODE
    "Authorization": f"Bearer {os.getenv('KORAP_AUTH_CODE')}"
}


async def _get_dereko_count(
    session: aiohttp.ClientSession, 
    semaphore: asyncio.Semaphore,
    lemma: str
) -> int:

    # docu available under
    # https://korap.ids-mannheim.de/api/v1.0/openapi/
    # https://korap.ids-mannheim.de (Hilfe -> API)
    params = {
        # see https://korap.ids-mannheim.de (Hilfe -> Anfragesprachen -> Poliqarp+)
        # (alternatively https://korap.ids-mannheim.de/doc/ql/poliqarp-plus?embedded=True)
        "q": f"[base={lemma}]",   # lemma
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
        "count": "0",
        "page": "1",
        "offset": "0",
        "cutoff": "false",
        "access-rewrite-disabled": "false",
        "show-tokens": "false",
        "show-snippet": "false"
    }

    try:
        async with semaphore:  # limit concurrent requests
            async with session.get(
                url,
                headers=headers,
                params=params,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    count = data.get("meta", {}).get("totalResults", -1)
                else:
                    return -1
        # release semaphore;
        # special case with eszett,
        # which is encoded as ss in CELEX
        if count == 0 and "ss" in lemma:
            sz_lemma = lemma.replace("ss", "ß")
            sz_count = await _get_dereko_count(
                session, semaphore, sz_lemma
            )
            if sz_count > 0:
                # it means that the lemma ß is correct
                return sz_count + 0.3   # signalize of the replacement
        return count
    except:
        return -1
        

async def get_dereko_count(
    session: aiohttp.ClientSession,
    semaphore: asyncio.Semaphore,
    lemma: str,
    freq_df: pd.DataFrame
) -> int:
    if lemma in freq_df.index:
        return freq_df.loc[lemma, "freq"]
    else:
        count = await _get_dereko_count(session, semaphore, lemma)
        # append to freq_df
        freq_df.loc[lemma] = count
        return count
    

async def get_dereko_counts(lemmas: list[str]) -> list[int]:

    # since querying DeReKo can be time-consuming and resource-intensive,
    # we cache the frequency counts in a separate TSV file shared with GeCoDB compounds;
    # moreover, to remain consistent with the count retrieval, we replace
    # original GeCoDB compound frequencies with the ones obtained
    # under the same procedure as for CELEX nouns, so we offload the frequency
    # retrieval to this separate module

    outpath = "resources/custom/compounding/intermediate_data"
    os.makedirs(outpath, exist_ok=True)

    freq_path = os.path.join(outpath, "dereko_de_geq70_counts.tsv")

    if os.path.exists(freq_path):
        freq_df = pd.read_csv(
            freq_path,
            sep="\t",
            header=0,
            index_col="entry",  # both lemmas and compounds
            # to be able to store decimal part for 'ß' cases
            dtype={"entry": str, "freq": float}
        )
    else:
        # empty freq df
        freq_df = pd.DataFrame(columns=["entry", "freq"]).set_index("entry")

    max_requests = 50  
    semaphore = asyncio.Semaphore(max_requests)  # limit concurrent requests
    connector = aiohttp.TCPConnector(limit=max_requests, limit_per_host=max_requests)
    
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = [
            get_dereko_count(session, semaphore, lemma, freq_df) 
            for lemma in lemmas
        ]
        
        freqs = await tqdm_asyncio.gather(*tasks, desc="Fetching frequencies from KorAP")

    freq_df.to_csv(
        freq_path,
        sep="\t",
        header=True,
        index=True,
        index_label="entry"
    )

    return freqs