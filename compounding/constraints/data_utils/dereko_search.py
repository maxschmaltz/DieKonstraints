import os
import requests
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


def dereko_count(lemma: str) -> int:

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

    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        data = response.json()
        return data.get("meta", {}).get("totalResults", -1)
    else:
        return -1