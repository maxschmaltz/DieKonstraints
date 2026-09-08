import pandas as pd
import yaml
from collections import defaultdict
from typing import Optional


def load_constraints(
	constr_path: str,
	load_data_specs: Optional[bool]=False
) -> dict:
	with open(constr_path, encoding="utf-8") as f:
		yamls = list(yaml.safe_load_all(f))
		constraints: dict = yamls[-1]["constraints"]
		data_specs: dict = yamls[-2]["datasets"]
	return (
		(constraints, data_specs) if load_data_specs
		else constraints
	)


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
) -> pd.DataFrame:
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


def load_appl_ind(
	appl_ind_path: str,
	target_dname: Optional[str],
	constr_path: Optional[str],
	remove_na_columns: Optional[bool]=True,
	remove_unconfirmed: Optional[bool]=True,
	remove_missing: Optional[bool]=True,
	verbose: Optional[bool]=True
) -> pd.DataFrame:

	# load
	appl_ind = pd.read_csv(
		appl_ind_path,
		sep="\t",
		header=0,
		index_col=0
	)

	if remove_na_columns:
		appl_ind.dropna(axis=1, how="all", inplace=True)

	if not remove_unconfirmed or remove_missing:
		return appl_ind

	assert (
		(target_dname, constr_path),
		"`target_dname` and `constr_path` required for filtering."
	)

	constraints = load_constraints(constr_path)

	# remove unconfirmed constraints and/or missing constraints
	for c_id, constr in constraints.items():
		to_remove = False
		if target_dname not in constr["measures"]:
			if remove_missing:
				to_remove = True
				message = f"Removed {c_id} from {target_dname}: not implemented."
		else:
			item_reg = constr["measures"][target_dname]["regularity"]["item"]
			if remove_unconfirmed and (item_reg < 0.5):
				to_remove = True
				message = f"Removed {c_id} from {target_dname} at item reg {item_reg}."
		if to_remove:
			appl_ind.drop(
				columns=[
					f"{c_id}_{sfx}"
					for sfx in ["item", "is_applicable", "applies"]
				],
				inplace=True,
				errors="ignore"	# in case removed already
			)
			if verbose:
				print(message)