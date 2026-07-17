import pandas as pd
from collections import defaultdict
from typing import Optional, Tuple


def load_celex(celex_path: str) -> pd.DataFrame:
	return pd.read_csv(
        celex_path,
        sep="\t",
        dtype=str,
        header=0,
        index_col="lemma"
    )


def load_gecodb(gecodb_path: str) -> pd.DataFrame:
	return pd.read_csv(
        gecodb_path,
        sep="\t",
        dtype=defaultdict(
			# default: str
            lambda: str,
            **{
				# freqs and prods for v06 and v07
                f"{prx}_freq": int
                for prx in ["comp", "n1", "n1_mass", "n2"]
            },
			# v06 and v07
            n1_prod="int",
			# v07
			is_pll="bool",
			umlaut_applied="bool"
        ),
        header=0,
        index_col=0
    )


def load_sp18(
	sp18_path: str,
	index_col: Optional[str]="gecodb"
) -> Tuple[pd.DataFrame, dict]:
	return pd.read_csv(
		sp18_path,
		sep="\t",
		header=0,
		index_col=index_col,
		# all str, WC int, is linker pluralic bool
		dtype=defaultdict(
			lambda: str,
			wc="int",
			is_linker_pl="bool"
		),
		# = csv.QUOTE_NONE, separate by tabs only
		quoting=3
	)