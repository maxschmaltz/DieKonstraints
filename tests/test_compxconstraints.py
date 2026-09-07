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

	def test_compxconstraints_linker_0(self):
		comp = "blume_+n_topf"
		appl_row = appl_ind.loc[comp]
		cxc = CompXConstraints(appl_row)
		# true linker
		self.assertEqual(cxc.comp.linkers[0].gecodb, "_+n_")
		self.assertEqual(cxc.true, "_+en_")
		# acceptable linkers
		self.assertEqual(cxc.acceptable_linkers, {
			"_": [
				{
					"c_id": "def-0",
					"confidence": 0.573,
					"cvg": 1.0
				}
			],
			"_+en_": [
				{
					"c_id": "p2l:phon_fin:schwa$-en|def-en",
					"confidence": 0.764,
					"cvg": 0.171
				}
			]
		})
		# unacceptable linkers
		self.assertEqual(cxc.unacceptable_linkers, {
			"_+s_": [
				{
					"c_id": "l2p:s|tend_cmpx_morph",
					"confidence": 0.907,
					"cvg": 0.285
				},
				{
					"c_id": "l2p:s|tend_cmpx_phon",
					"confidence": 0.688,
					"cvg": 0.285
				},
				{
					"c_id": "l2p:s|smpx_mn",
					"confidence": 0.979,
					"cvg": 0.026
				},
				{
					"c_id": "l2p:s|f_cmpx",
					"confidence": 0.997,
					"cvg": 0.202
				}
			],
			"_+e_": [
				{
					"c_id": "l2p:e|par",
					"confidence": 0.968,
					"cvg": 0.009
				},
				{
					"c_id": "l2p:e|#stressed_syl",
					"confidence": 1.0,
					"cvg": 0.009
				}
			],
			"_+=er_": [
				{
					"c_id": "l2p:er|par",
					"confidence": 1.0,
					"cvg": 0.009
				},
				{
					"c_id": "l2p:er|#stressed_syl",
					"confidence": 1.0,
					"cvg": 0.009
				}
			],
			"_+=e_": [
				{
					"c_id": "l2p:e_uml",
					"confidence": 1.0,
					"cvg": 0.003
				}
			],
			"_+es_": [
				{
					"c_id": "l2p:es|mono_syl",
					"confidence": 0.972,
					"cvg": 0.01
				}
			],
			"_+=_": [
				{
					"c_id": "l2p:0_uml",
					"confidence": 1.0,
					"cvg": 0.001
				}
			]
		})
            

	def test_compxconstraints_linker_1(self):
		comp = "beruf_+s_erfahrung"
		appl_row = appl_ind.loc[comp]
		cxc = CompXConstraints(appl_row)
		# true linker
		self.assertEqual(cxc.comp.linkers[0].gecodb, "_+s_")
		self.assertEqual(cxc.true, "_+s_")
		# acceptable linkers
		self.assertEqual(cxc.acceptable_linkers, {
			"_": [
				{
					"c_id": "def-0",
					"confidence": 0.573,
					"cvg": 1.0
				},
				{
					"c_id": "p2l:decl_cl:pl:#e-0|def-0",
					"confidence": 0.754,
					"cvg": 0.162
				}
			],
			"_+s_": [
				{
					"c_id": "p2l:drv:prx_deverb-s",
					"confidence": 0.649,
					"cvg": 0.159
				}
			]
		})
		# unacceptable linkers
		self.assertEqual(cxc.unacceptable_linkers, {
			"_+en_": [
				{
					"c_id": "l2p:en|par",
					"confidence": 0.985,
					"cvg": 0.152
				}
			],
			"_+e_": [
				{
					"c_id": "l2p:e|smpx",
					"confidence": 0.806,
					"cvg": 0.009
				}
			],
			"_+=er_": [
				{
					"c_id": "l2p:er|par",
					"confidence": 1.0,
					"cvg": 0.009
				},
				{
					"c_id": "l2p:er|smpx",
					"confidence": 0.903,
					"cvg": 0.009
				}
			],
			"_+=e_": [
				{
					"c_id": "l2p:e_uml",
					"confidence": 1.0,
					"cvg": 0.003
				}
			],
			"_+=_": [
				{
					"c_id": "l2p:0_uml",
					"confidence": 1.0,
					"cvg": 0.001
				}
			]
		})


	def test_compxconstraints_linker_2(self):
		comp = "stern_+en_himmel"
		appl_row = appl_ind.loc[comp]
		cxc = CompXConstraints(appl_row)
		# true linker
		self.assertEqual(cxc.comp.linkers[0].gecodb, "_+en_")
		self.assertEqual(cxc.true, "_+en_")
		# acceptable linkers
		self.assertEqual(cxc.acceptable_linkers, {
			"_": [
				{
					"c_id": "def-0",
					"confidence": 0.573,
					"cvg": 1.0
				},
				{
					"c_id": "p2l:decl_cl:pl:#e-0|def-0",
					"confidence": 0.754,
					"cvg": 0.162
				}
			],
			"_+en_": [
				{
					"c_id": "l2p:en|non_par_m",
					"confidence": 0.786,
					"cvg": 0.001
				}
			]
		})
		# unacceptable linkers
		self.assertEqual(cxc.unacceptable_linkers, {
			"_+s_": [
				{
					"c_id": "l2p:s|tend_cmpx_morph",
					"confidence": 0.907,
					"cvg": 0.285
				},
				{
					"c_id": "l2p:s|tend_cmpx_phon",
					"confidence": 0.688,
					"cvg": 0.285
				},
				{
					"c_id": "l2p:s|tend_!sonority",
					"confidence": 0.547,
					"cvg": 0.026
				}
			],
			"_+en_": [
				{
					"c_id": "l2p:en|par",
					"confidence": 0.985,
					"cvg": 0.152
				}
			],
			"_+=er_": [
				{
					"c_id": "l2p:er|par",
					"confidence": 1.0,
					"cvg": 0.009
				}
			],
			"_+=e_": [
				{
					"c_id": "l2p:e_uml",
					"confidence": 1.0,
					"cvg": 0.003
				}
			],
			"_+=_": [
				{
					"c_id": "l2p:0_uml",
					"confidence": 1.0,
					"cvg": 0.001
				}
			]
		})

	def test_compxconstraints_linker_3(self):
		# distributed confidence
		distr_c_id = "p2l:decl_cl:pl:#er-0/er|def-0/er"
		comp = "kind_+er_wagen"
		appl_row = appl_ind.loc[comp]
		cxc = CompXConstraints(appl_row)
		er_constr_shard_0 = [
			dic for dic in cxc.acceptable_linkers["_"]
			if dic["c_id"] == "p2l:decl_cl:pl:#er-0/er|def-0/er"
		][0]
		er_constr_shard_1 = [
			dic for dic in cxc.acceptable_linkers["_+=er_"]
			if dic["c_id"] == "p2l:decl_cl:pl:#er-0/er|def-0/er"
		][0]
		self.assertTrue(
			er_constr_shard_0["confidence"] ==
			er_constr_shard_1["confidence"] ==
			round(
				constraints[distr_c_id]["measures"][DNAME]["regularity"]["item"] / 2, 3
			) == 0.407
		)


class TestCompXConstraintsAlbrightHayes(unittest.TestCase):

	def test_compxconstraints_ah_00(self):
		comp = "land_+es_regierung"
		appl_row = appl_ind.loc[comp]
		cxc = CompXConstraints(appl_row)
		cxc.predict(
			method="albright_hayes",
			constr_cooperation=False,
			restrict_with_l2p=False
		)
		self.assertEqual(cxc.preds, ["_"])
		self.assertEqual(cxc.pred_conf, 0.573)
		self.assertEqual(cxc.pred_cvg, 1.0)

	def test_compxconstraints_ah_01(self):
		comp = "land_+es_regierung"
		appl_row = appl_ind.loc[comp]
		cxc = CompXConstraints(appl_row)
		cxc.predict(
			method="albright_hayes",
			constr_cooperation=True,
			restrict_with_l2p=False
		)
		self.assertEqual(cxc.preds, ["_"])
		self.assertEqual(cxc.pred_conf, 0.98)
		self.assertEqual(cxc.pred_cvg, 1.021)


	def test_compxconstraints_ah_10(self):
			comp = "jugend_schutz"
			appl_row = appl_ind.loc[comp]
			cxc = CompXConstraints(appl_row)
			cxc.predict(
				method="albright_hayes",
				constr_cooperation=False,
				restrict_with_l2p=False
			)
			self.assertEqual(cxc.preds, ["_+s_"])
	
	def test_compxconstraints_ah_11(self):
		comp = "jugend_schutz"
		appl_row = appl_ind.loc[comp]
		cxc = CompXConstraints(appl_row)
		cxc.predict(
			method="albright_hayes",
			constr_cooperation=False,
			restrict_with_l2p=True
		)
		self.assertEqual(cxc.preds, ["_"])
		expected_removals = {
			"_+s_": {
				"c_id": "l2p:s|f_cmpx",
				"confidence": 0.997,
				"cvg": 0.202
			}
		}
		self.assertEqual(cxc.l2p_removals, expected_removals)

	def test_compxconstraints_ah_12(self):
		comp = "jugend_schutz"
		appl_row = appl_ind.loc[comp]
		cxc = CompXConstraints(appl_row)
		cxc.predict(
			method="albright_hayes",
			constr_cooperation=True,
			restrict_with_l2p=True
		)
		self.assertEqual(cxc.preds, ["_"])
		expected_removals = {
			"_+s_": [
				{
					"c_id": "l2p:s|tend_cmpx_morph",
					"confidence": 0.907,
					"cvg": 0.285
				},
				{
					"c_id": "l2p:s|tend_cmpx_phon",
					"confidence": 0.688,
					"cvg": 0.285
				},
				{
					"c_id": "l2p:s|smpx_mn",
					"confidence": 0.979,
					"cvg": 0.026
				},
				{
					"c_id": "l2p:s|f_cmpx",
					"confidence": 0.997,
					"cvg": 0.202
				}
			]
		}
		self.assertEqual(cxc.l2p_removals, expected_removals)