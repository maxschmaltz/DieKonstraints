import os

from data_utils.load_datasets import (
    load_constraints,
    load_gecodb,
    load_appl_ind,
    save_tsv_generic
)
from comp_modeling.compxconstraints import CompXConstraints


# python3 -m data_utils.prepare_merged_geco_sp_appl_ind
def main():

    # While semantics serves only as a soft cue in German nominal compounding,
    # the pluralic linkers are by far only produced by semantic constraints.
    # When trying to predict the linkers of GeCoDB_v07_GN with the constraints
    # implemented only over this dataset (so no pluralic constraints),
    # we ended up with producing only _, _+s_, and _+en_. In order to
    # increase our predictive power, we merge the applicability indices
    # of the constraints over GeCoDB_v07_GN and SP18_Pl_Constr obtained
    # from the second corpus study.

    constr_path = "constraints/constraints_all_revised.yaml"
    constraints = load_constraints(constr_path)

    appl_inds_dir = "resources/semrel_comp_corp_study-private/appl_inds"
    # (N=48976)
    dname = "gecodb_v07_gn"
    gecodb_appl_ind = load_appl_ind(
        os.path.join(appl_inds_dir, f"{dname}_appl_ind.tsv"),
        constraints=constraints,
        remove_na_columns=True,
        remove_unconfirmed=True,
        remove_missing=True,
        verbose=False
    )
    # (2294)
    dname = "sp18_pl_constr"
    sp18_appl_ind = load_appl_ind(
        os.path.join(appl_inds_dir, f"{dname}_appl_ind.tsv"),
        constraints=constraints,
        remove_na_columns=True,
        remove_unconfirmed=True,
        remove_missing=True,
        verbose=False
    )

    # (N=882)
    merged_appl_ind = gecodb_appl_ind.join(
        sp18_appl_ind,
        how="inner",
        # in case of conflicts, prefer GeCoDB_v07
        # (actually, there is only one conflict on
        # the default constraint)
        rsuffix="_to_remove"
    )

    # item is unimportant here
    to_remove = [
        col for col in merged_appl_ind.columns
        if col.endswith("_item") or col.endswith("_to_remove")
    ]
    merged_appl_ind.drop(columns=to_remove, inplace=True)

    # add escaped linkers
    gecodb_path = "resources/semrel_comp_corp_study-private/gecodb_v07_gn.tsv"
    gecodb = load_gecodb(gecodb_path)
    linkers = gecodb.loc[merged_appl_ind.index, "linker"].map(CompXConstraints.esc)
    merged_appl_ind.insert(0, "linker", linkers)

    outdir = "resources/developed"
    os.makedirs(outdir, exist_ok=True)
    save_tsv_generic(
        merged_appl_ind,
        os.path.join(outdir, "merged_geco_sp_appl_ind.tsv")
    )


if __name__ == "__main__":
    main()
