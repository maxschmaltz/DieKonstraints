import os
import pandas as pd
from scipy.stats import chi2_contingency
from statsmodels.stats.contingency_tables import Table
import math
from typing import Tuple, Optional, Union
from types import FunctionType

from data_utils.load_datasets import load_sp18


sp18_extpe_path = "resources/developed/sp18/extpe"
sp18_intpe_path = "resources/developed/sp18/intpe"

resdir_extpe = "out/extpe_sp18"
resdir_intpe = "out/intpe_sp18"


def get_load_sp18(intpe: bool) -> FunctionType:

	sp18_path = sp18_intpe_path if intpe else sp18_extpe_path
	index_col = "gecodb" if intpe else "const_comb"

	def _load_sp18(name: str) -> pd.DataFrame:
		return load_sp18(
			os.path.join(sp18_path, f"{name}.tsv"),
			index_col
		)

	return _load_sp18


def savetsv(
	df: Union[pd.DataFrame, pd.Series],
	outdir: str,
	name: str
) -> None:
	df.to_csv(
		os.path.join(outdir, f"{name}.tsv"),
		sep="\t",
		index=True,
		header=True
	)


def calc_pll_shares(
    sp18_sample: pd.DataFrame,
	groupby: str,
	target_col: str,
	label_pfx: str,
	label_1: str,
	label_2: str
) -> Tuple[pd.DataFrame, pd.DataFrame]:

    # calculate absolute counts and shares of compounds 
    # with pluralic linkers against predictors;
	# `label_1` is supposed to produce more PLL than `label_2`
    sp18_sample_pll_counts_data = {}
    for item, group in sp18_sample.groupby(groupby):
		# reverse order: from less to more
        for label in [label_2, label_1]:
            sp18_sample_pll_counts_data[(item, label_pfx + label)] = {
                "l_sg": len(
                    group[(group[target_col] == label) &
                    (~group["is_linker_pl"])]
                ),
                "l_pl": len(
                    group[(group[target_col] == label) &
                    (group["is_linker_pl"])]
                )
            }

    sp18_sample_pllcounts = pd.DataFrame(sp18_sample_pll_counts_data).T
    sp18_sample_pllcounts["pl_share"] = sp18_sample_pllcounts["l_pl"] / (
        sp18_sample_pllcounts["l_sg"] + sp18_sample_pllcounts["l_pl"]
    )

	# reverse order: from less to more
    sp18_sample_pllshares = sp18_sample_pllcounts \
        .unstack()["pl_share"]  \
        [[label_pfx + label_2, label_pfx + label_1]]

    return sp18_sample_pllcounts, sp18_sample_pllshares


def sp18_orig_analysis(
    contingency_table: pd.DataFrame,
	label_pfx: str,
    label_1: str,
    label_2: str
) -> pd.DataFrame:

    # Methodology from the original [schaefer_pankratz_2018:26] paper:
    # 0. Create contingency 2x2 table:
    # non-pluralic vs. pluralic linker, vs. the investigated predictor.
    # 1. Perform the chi-squared test of independence over the table
    # to assess the statistical significance of the association between
    # the Pl form of N2 and the presence of a pluralic linker in N1.
    # 2. Perform the Cramer's V test to assess the strength
    # of the association.
    # 3. Inspect symmetrical standardized residuals to identify
    # the cells that contribute to the association, and in which direction.

    # Note that label 1 is the label of the dataset where
    # we expect a larger share of pluralic linkers.


    # 1. Perform the chi-squared test.

    # even though I didn't find the original R code
    # of [schaefer_pankratz_2018] for this experiment,
    # the `chi2_contingency` function from `scipy.stats`
    # produced the same results as in the paper
    # on the same contingency table, so we can be
    # confident that we are replicating the same analysis
    chi2_res = chi2_contingency(contingency_table)

    if True in (chi2_res.expected_freq <= 5).flatten():
        # never happens with this data, so no Monte Carlo replacement
        # is needed as reported in [schaefer_pankratz_2018:27]
        pass

    # 2. Perform the Cramer's V test to assess 
    # the strength of the association.

    # the original R code for Cramer's V is available in
    # linkingelements/Data/R/functions.R, and is as follows:
    # 
    #   cramer.v <- function(chisq) {
    #       unname(sqrt(chisq$statistic/(sum(chisq$observed)*min(dim(chisq$observed)-1))))
    #   }
    #
    # we will reconstruct it in Python:
    #   dim(chisq$observed) -> ic_alt_nipe_sg_l_ct.shape
    #
    #   min(dim(chisq$observed)-1) -> min(
    #       ic_alt_nipe_sg_l_ct.shape[0] - 1,
    #       ic_alt_nipe_sg_l_ct.shape[1] - 1
    #   )
    # 
    #   sum(chisq$observed) -> ic_alt_nipe_sg_l_ct.values.sum()
    #
    #   unname -> [irrelevant for Python]
    cramer_v_val = math.sqrt(
        chi2_res.statistic / (
            contingency_table.values.sum() *
            min(
                contingency_table.shape[0] - 1,
                contingency_table.shape[1] - 1
            )
        )
    )

    # DEPRECATED: for 2x2 contingency tables, Cohen's W
    # is effectively identical to Cramer's V
    # # the original R code for Cohen's W is available in
    # # linkingelements/Data/R/functions.R, and is as follows:
    # # 
    # #   # cohen.w <- function(chisq) {
    # #       cramer.v(chisq) * sqrt(min(dim(chisq$observed)-1))
    # #   }
    # cohen_w_val = cramer_v_val * math.sqrt(
    #     min(
    #         contingency_table.shape[0] - 1,
    #         contingency_table.shape[1] - 1
    #     )
    # )

    # 3. Inspect symmetrical standardized residuals to identify
    # the cells that contribute to the association, and in which direction.

    # even though I didn't find the original R code
    # of [schaefer_pankratz_2018] for this experiment,
    # the `standardized_resids` property of
    # `statsmodels.stats.contingency_tables.Table`
    # produced the same results as in the paper
    # on the same contingency table, so we can be
    # confident that we are replicating the same analysis
    resids = Table(contingency_table)    \
        .standardized_resids.round(3)
    
    chi2df = pd.Series(
        data={
            "N": contingency_table.values.sum(),
            "df": chi2_res.dof,
            "chi2": chi2_res.statistic.round(3),
            "p": chi2_res.pvalue,
            "cramer_v": round(cramer_v_val, 3),
            # we expect a larger share of pluralic linkers with label_1,
            # so we expect a positive residual in `resids_cong`
            "resids_cong": resids.loc["l_pl", label_pfx + label_1].item(),
            "resids_incong": resids.loc["l_pl", label_pfx + label_2].item()
        }
    ).round(3)

    return chi2df


def run_onesample_study(
	sp18_sample: pd.DataFrame,
	groupby,
	target_col,
	label_pfx,
    label_1: str,
    label_2: str,
	outdir: Optional[str]=None
) -> Tuple[
	pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.Series
]:
	
	# this function compares the shares of pluralic linkers in compounds
	# in Sg vs. Pl forms in a given sample,
	# following the original Schäfer & Pankratz 2018 method

	# calculate absolute counts and shares of compounds 
	# with pluralic linkers in Sg vs. Pl forms
	sp18_sample_pllcounts, sp18_sample_pllshares = calc_pll_shares(
		sp18_sample,
		groupby,
		target_col,
		label_pfx,
		label_1,
		label_2
	)

	# shares desc
	sp18_sample_pllshares_desc = sp18_sample_pllshares.describe()

	# create contingency table replicating [schaefer_pankratz_2018:26]
	# n1_pl_marker (non- vs. pluralic linker) x predictor;
	# replicating the original table, predictor `label_1` is
	# expected to produce more PLL than `label_2`
	contingency_table = sp18_sample_pllcounts \
		.groupby(level=1)[["l_sg", "l_pl"]].sum()   \
		.T  \
		[[label_pfx + label_1, label_pfx + label_2]]	# orig order: more-less expected PLL
	# perform the original analysis from [schaefer_pankratz_2018:26]
	chi2df = sp18_orig_analysis(
		contingency_table,
		label_pfx=label_pfx,
		label_1=label_1,
		label_2=label_2
	)

	if outdir:
		os.makedirs(outdir, exist_ok=True)
		for df, name in [
			(sp18_sample_pllcounts, "pllcounts"),
			(sp18_sample_pllshares, "pllshares"),
			(sp18_sample_pllshares_desc.round(3), "pllshares_desc"),
			(contingency_table, "contingency_table"),
			(chi2df, "chi2")
		]:
			savetsv(df, outdir, name)

	return (
		sp18_sample_pllcounts, sp18_sample_pllshares, 
		sp18_sample_pllshares_desc,
		contingency_table, chi2df
	)


def run_twosamples_study(
	sp18_sample_1: pd.DataFrame,
	sp18_sample_2: pd.DataFrame,
	groupby,
	target_col,
	label_1_calc_shares: str,
	label_2_calc_shares: str,
	label_1: str,
	label_2: str,
	target_predictor: str,
	outdir: Optional[str]=None
) -> Tuple[
	pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.Series
]:
	
	# this function modifies the original Schäfer & Pankratz 2018 method
	# to compare the shares of the pluralic linker
	# in compounds in the Pl (or Sg) form from two different samples;
	# the sample in which the larger share of the pluralic linker
	# is expected should be passed as `sp18_sample_1`

	# calculate absolute counts of linker in compounds in Pl forms
	pllcounts_1, pllshares_1 = calc_pll_shares(
		sp18_sample_1,
		groupby,
		target_col,
		label_pfx="",
		label_1=label_1_calc_shares,
		label_2=label_2_calc_shares
	)
	pllcounts_2, pllshares_2 = calc_pll_shares(
		sp18_sample_2,
		groupby,
		target_col,
		label_pfx="",
		label_1=label_1_calc_shares,
		label_2=label_2_calc_shares
	)
	# extract only values from target predictor
	pllcounts_1 = pllcounts_1.swaplevel(0, 1).loc[target_predictor]
	pllcounts_2 = pllcounts_2.swaplevel(0, 1).loc[target_predictor]
	# since we have different portions of data,
	# some constituent combinations will be
	# non-existent in one of the samples; force
	# mask them with NaN before joining
	all_ccs = pllcounts_1.index.union(pllcounts_2.index)
	pllcounts_1 = pllcounts_1.reindex(all_ccs)
	pllcounts_2 = pllcounts_2.reindex(all_ccs)
	sp18_samples_pllcounts = pd.concat(
		(pllcounts_1, pllcounts_2),
		keys=[label_1, label_2]
	).swaplevel(0, 1)	\
	.sort_index(level=0, sort_remaining=False)
		
	# shares desc
	pllshares_1 = pllshares_1[target_predictor]
	pllshares_1.name = label_1
	pllshares_2 = pllshares_2[target_predictor]
	pllshares_2.name = label_2
	sp18_samples_pllshares = pd.concat((pllshares_1, pllshares_2), axis=1)
	sp18_samples_pllshares_desc = sp18_samples_pllshares.describe()

	# contingency table replicating [schaefer_pankratz_2018:26]
	# n1_pl_marker (non- vs. pluralic linker) x investigated variable;
	# following [schaefer_pankratz_2018:26], label 1 labels the sample
	# where we expect to see a larger share of pluralic linkers
	contingency_table = sp18_samples_pllcounts \
		.groupby(level=1)[["l_sg", "l_pl"]].sum()   \
		.T	\
		[[label_1, label_2]]	# orig: num_pl, num_sg
	# perform the original analysis from [schaefer_pankratz_2018:26]
	chi2df = sp18_orig_analysis(
		contingency_table,
		label_pfx="",
		label_1=label_1,	# orig: num_pl
		label_2=label_2		# orig: num_sg
	)

	if outdir:
		os.makedirs(outdir, exist_ok=True)
		for df, name in [
			(sp18_samples_pllcounts, "pllcounts"),
			(sp18_samples_pllshares, "pllshares"),
			(sp18_samples_pllshares_desc.round(3), "pllshares_desc"),
			(contingency_table, "contingency_table"),
			(chi2df, "chi2")
		]:
			savetsv(df, outdir, name)

	return (
		sp18_samples_pllcounts, sp18_samples_pllshares, 
		sp18_samples_pllshares_desc,
		contingency_table, chi2df
	)