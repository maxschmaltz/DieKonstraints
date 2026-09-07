import unittest

import os
import pandas as pd

from comp_modeling.compxconstraints import (CompXConstraints, data_specs)

appl_ind_dir = "resources/semrel_comp_corp_study-private/constr_appl_indices"

# load constraint applicability indices
appl_inds = {
    k: pd.read_csv(
        os.path.join(appl_ind_dir, f"{k}.tsv"),
        sep="\t",
        header=0,
        index_col=0
    )
    for k in data_specs
}


class TestCompXConstraintsLinkers(unittest.TestCase):

	def test_compxconstraints_0(self):
		comp = "instrument_+en_bau"
		dname = "gecodb_v07_gn"
		appl_row = appl_inds[dname].loc[comp]
		cxc = CompXConstraints(appl_row, dname)
		# true linker
		self.assertTrue(cxc.comp.linkers[0].gecodb == "_+en_")
		self.assertTrue(cxc.true == "_+en_")
		# acceptable linkers
		self.assertTrue(cxc.acceptable_linkers == {
			"_": [
				{
					"c_id": "def-0",
					"item_reg": 0.573,
					"item_cvg": 1.0
				}
			],
			"_+e_": [
				{
					"c_id": "p2l:decl_cl:pl:#e-0|def-0",
					"item_reg": 0.754,
					"item_cvg": 0.162
				}
			]
		})
		# unacceptable linkers
		self.assertTrue(cxc.unacceptable_linkers == {
			"_+s_": [
				{
					"c_id": "l2p:s|tend_cmpx_morph",
					"item_reg": 0.907,
					"item_cvg": 0.285
				}
			],
			"_+en_": [
				{
					"c_id": "l2p:en|par",
					"item_reg": 0.985,
					"item_cvg": 0.152
				}
			],
			"_+=er_": [
				{
					"c_id": "l2p:er|par",
					"item_reg": 1.0,
					"item_cvg": 0.009
				}
			],
			"_+=e_": [
				{
					"c_id": "l2p:e_uml",
					"item_reg": 1.0,
					"item_cvg": 0.003
				}
			],
			"_+es_": [
				{
					"c_id": "l2p:es|mono_syl",
					"item_reg": 0.972,
					"item_cvg": 0.01
				}
			],
			"_+=_": [
				{
					"c_id": "l2p:0_uml",
					"item_reg": 1.0,
					"item_cvg": 0.001
				}
			]
		})
		

	def test_compxconstraints_1(self):
		comp = "beruf_+s_erfahrung"
		dname = "gecodb_v07_gn"
		appl_row = appl_inds[dname].loc[comp]
		cxc = CompXConstraints(appl_row, dname)
		# true linker
		self.assertTrue(cxc.comp.linkers[0].gecodb == "_+s_")
		self.assertTrue(cxc.true == "_+s_")
		# acceptable linkers
		self.assertTrue(cxc.acceptable_linkers == {
			"_": [
				{
					"c_id": "def-0",
					"item_reg": 0.573,
					"item_cvg": 1.0
				}
			],
			"_+e_": [
				{
					"c_id": "p2l:decl_cl:pl:#e-0|def-0",
					"item_reg": 0.754,
					"item_cvg": 0.162
				}
			],
			"_+s_": [
				{
					"c_id": "p2l:drv:prx_deverb-s",
					"item_reg": 0.649,
					"item_cvg": 0.159
				}
			]
		})
		# unacceptable linkers
		self.assertTrue(cxc.unacceptable_linkers == {
			"_+en_": [
				{
					"c_id": "l2p:en|par",
					"item_reg": 0.985,
					"item_cvg": 0.152
				},
				{
					"c_id": "l2p:en|non_par_m",
					"item_reg": 0.786,
					"item_cvg": 0.001
				}
			],
			"_+e_": [
				{
					"c_id": "l2p:e|smpx",
					"item_reg": 0.806,
					"item_cvg": 0.009
				}
			],
			"_+=er_": [
				{
					"c_id": "l2p:er|par",
					"item_reg": 1.0,
					"item_cvg": 0.009
				}
			],
			"_+=e_": [
				{
					"c_id": "l2p:e_uml",
					"item_reg": 1.0,
					"item_cvg": 0.003
				}
			],
			"_+es_": [
				{
					"c_id": "l2p:es|mono_syl",
					"item_reg": 0.972,
					"item_cvg": 0.01
				}
			],
			"_+=_": [
				{
					"c_id": "l2p:0_uml",
					"item_reg": 1.0,
					"item_cvg": 0.001
				}
			]
		})


	def test_compxconstraints_2(self):
		comp = "kind_+er_wagen"
		dname = "sp18_pl_constr"
		appl_row = appl_inds[dname].loc[comp]
		cxc = CompXConstraints(appl_row, dname)
		# true linker
		self.assertTrue(cxc.comp.linkers[0].gecodb == "_+er_")
		self.assertTrue(cxc.true == "_+er_")
		# acceptable linkers
		self.assertTrue(cxc.acceptable_linkers == {
			"_": [
				{
					"c_id": "def-0",
					"item_reg": 0.573,
					"item_cvg": 1.0
				},
				{
					"c_id": "p2l:decl_cl:pl:#er-0/er|def-0/e",
					"item_reg": 0.815,
					"item_cvg": 0.021
				},
				{
					"c_id": "p2l:decl_cl:pl:#er-0/er|!pl_interpr-0",
					"item_reg": 0.622,
					"item_cvg": 0.171
				}
			],
			"_+=er_": [
				{
					"c_id": "p2l:decl_cl:pl:#er-0/er|def-0/e",
					"item_reg": 0.815,
					"item_cvg": 0.021
				}
			]
		})
		# unacceptable linkers
		self.assertTrue(cxc.unacceptable_linkers == {
			"_+s_": [
				{
					"c_id": "l2p:s|tend_cmpx_morph",
					"item_reg": 0.907,
					"item_cvg": 0.285
				},
				{
					"c_id": "l2p:s|tend:cmpx_phon",
					"item_reg": 0.607,
					"item_cvg": 0.27
				}
			],
			"_+en_": [
				{
					"c_id": "l2p:en|par",
					"item_reg": 0.985,
					"item_cvg": 0.152
				}
			],
			"_+e_": [
				{
					"c_id": "l2p:e|par",
					"item_reg": 0.968,
					"item_cvg": 0.009
				}
			],
			"_+=e_": [
				{
					"c_id": "l2p:e_uml",
					"item_reg": 1.0,
					"item_cvg": 0.003
				}
			],
			"_+=_": [
				{
					"c_id": "l2p:0_uml",
					"item_reg": 1.0,
					"item_cvg": 0.001
				}
			]
		})