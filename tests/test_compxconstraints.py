import unittest

import pandas as pd

from comp_modeling.compxconstraints import CompXConstraints, constraints, DNAME

appl_ind_path = "resources/semrel_comp_corp_study-private/gecodb_v07_gn_appl_ind.tsv"

# load constraint applicability index
appl_ind = pd.read_csv(
	appl_ind_path,
	sep="\t",
	header=0,
	index_col=0
)

# remove unconfirmed constraints; missing constraints
# are ignored by `CompXConstraints`
appl_ind.dropna(axis=1, how="all", inplace=True)  # drop columns with NAs
for c_id, constr in constraints.items():
	to_remove = False
	if DNAME in constr["measures"]:
		item_reg = constr["measures"][DNAME]["regularity"]["item"]
		if item_reg < 0.5:
			appl_ind.drop(
				columns=[
					f"{c_id}_{sfx}"
					for sfx in ["item", "is_applicable", "applies"]
				],
				inplace=True,
				# errors="ignore"
			)
		print(f"Removed {c_id} from {DNAME} at item reg {item_reg}.")


class TestCompXConstraintsLinkers(unittest.TestCase):

	def test_compxconstraints_0(self):
		comp = "blume_+n_topf"
		appl_row = appl_ind.loc[comp]
		cxc = CompXConstraints(appl_row)
		# true linker
		self.assertTrue(cxc.comp.linkers[0].gecodb == "_+n_")
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
			"_+en_": [
				{
					"c_id": "p2l:phon_fin:schwa$-en|def-en",
					"item_reg": 0.764,
					"item_cvg": 0.171
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
					"c_id": "l2p:s|tend_cmpx_phon",
					"item_reg": 0.688,
					"item_cvg": 0.285
				},
				{
					"c_id": "l2p:s|smpx_mn",
					"item_reg": 0.979,
					"item_cvg": 0.026
				},
				{
					"c_id": "l2p:s|f_cmpx",
					"item_reg": 0.997,
					"item_cvg": 0.202
				}
			],
			"_+e_": [
				{
					"c_id": "l2p:e|par",
					"item_reg": 0.968,
					"item_cvg": 0.009
				},
				{
					"c_id": "l2p:e|#stressed_syl",
					"item_reg": 1.0,
					"item_cvg": 0.009
				}
			],
			"_+=er_": [
				{
					"c_id": "l2p:er|par",
					"item_reg": 1.0,
					"item_cvg": 0.009
				},
				{
					"c_id": "l2p:er|#stressed_syl",
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
		appl_row = appl_ind.loc[comp]
		cxc = CompXConstraints(appl_row)
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
				},
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
				},
				{
					"c_id": "l2p:er|smpx",
					"item_reg": 0.903,
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


	def test_compxconstraints_2(self):
		comp = "stern_+en_himmel"
		appl_row = appl_ind.loc[comp]
		cxc = CompXConstraints(appl_row)
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
				},
				{
					"c_id": "p2l:decl_cl:pl:#e-0|def-0",
					"item_reg": 0.754,
					"item_cvg": 0.162
				}
			],
			"_+en_": [
				{
					"c_id": "l2p:en|non_par_m",
					"item_reg": 0.786,
					"item_cvg": 0.001
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
					"c_id": "l2p:s|tend_cmpx_phon",
					"item_reg": 0.688,
					"item_cvg": 0.285
				},
				{
					"c_id": "l2p:s|tend_!sonority",
					"item_reg": 0.547,
					"item_cvg": 0.026
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
			"_+=_": [
				{
					"c_id": "l2p:0_uml",
					"item_reg": 1.0,
					"item_cvg": 0.001
				}
			]
		})