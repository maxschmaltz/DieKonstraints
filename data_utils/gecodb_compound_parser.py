# This code is taken and modified from the original DEKOR repository:
# https://github.com/maxschmaltz/DEKOR/blob/main/test/test_gecodb_parser.py.
# Note that the original code was simplified significantly and modified
# to adjust for the new research setting:
# 1. No deletion linkers are taken under consideration, so specifying
# 	linker type became irrelevant for the current research.
#	Instead, a linker can be described as explicit/zero (inferrable directly
# 	by its allomorph realization) and whether it adds an umlaut (
# 	stored as a property of the `Linker` object).
# 2. Allomorphy operations that were only relevant for n-gram models,
#	are removed. Instead, both stems and linkers store their abstract morph
# 	and concrete allomorph realizations directly.
# 3. A few variable name changes for higher linguistic accuracy.


import re
from dataclasses import dataclass, field
from typing import Tuple, List, Optional, Union


DE = "[a-zäöüß]*"   # German alphabet
LINKER_PATTERN = "|".join([
	f"(_\+={DE}_)",
	f"(_\+{DE}_)",
	"(_)"
])    # match any linker
UMLAUTS = {
	"au": "äu",
	"a": "ä",
	"o": "ö",
	"u": "ü"
}


@dataclass
class Stem:

	"""
	A stem component of a `Compound`.

	Parameters
	----------
	morph : `str`
		abstract morpheme representation of the component

	span : `Tuple[int]`
		span of the `allomorph` in the `Compound` lemma

	Attributes
	----------
	allomorph : `str`
		concrete realization of the morpheme;
		after initialization, equals to `morph`;
		is to modify later if needed; the only case when
		`allomorph` is different from `morph` is when
		the stem undergoes umlauting

	Example
	-------
	>>> compound = Compound("gast_+=e_buch")
	>>> compound.components[0].morph
	"gast"
	>>> compound.components[0].allomorph
	"gäst"
	>>> compound.components[0].span
	(0, 4)
	"""

	morph: str = field(compare=True)
	span: Tuple[int] = field(compare=True, kw_only=True)

	# added later
	allomorph: Optional[str] = field(compare=True, init=False)

	def __post_init__(self) -> None:
		self.allomorph = self.morph

	def __repr__(self) -> str:
		return self.morph
	
	def __len__(self) -> int:
		return len(self.morph)


@dataclass
class Linker:

	"""
	A linker component of a `Compound`.

	Parameters
	----------
	gecodb : `str`
		gecodb representation of the component, e.g. "_+n_"

	allomorph : `str`, optional
		concrete realization of the component, e.g. "n";
		since linkers appear in compounds as allomorphs and not morph,
		this attribute (and not `morph`) is always defined for
		explicit linkers (as opposed to stems that appear as morphs
		and not allomorphs in compounds);
		if not provided, equals to empty string

	span : `Tuple[int]`
		span of the component in the `Compound` lemma

	Attributes
	----------
	morph : `str`
		abstract morpheme representation of the component;
		restored automatically after initialization;
		the only two cases when `morph` is different 
		from `allomorph` are _+n_ (morph "en", allomorph "n")
		and _+ns_ (morph "ens", allomorph "ns");
		we do not consider _+s_ and _+es_ allomorphic

	adds_umlaut : `bool`
		whether the linker adds an umlaut to the preceding stem;
		added automatically after initialization

	Example
	-------
	>>> compound = Compound("blume_+n_strauß")
	>>> compound.components[1].gecodb
	"_+n_"
	>>> compound.components[1].morph
	"en"
	>>> compound.components[1].allomorph
	"n"
	>>> compound.components[1].span
	(5, 6)
	>>> compound.components[1].adds_umlaut
	False


	>>> compound = Compound("mutter_+=_zentrum")
	>>> compound.linkers[0].gecodb
	"_+=_"
	>>> compound.linkers[0].morph
	""
	>>> compound.linkers[0].allomorph
	""
	>>> compound.linkers[0].span
	(6, 6)
	>>> compound.linkers[0].adds_umlaut
	True
	"""

	gecodb: str = field(compare=True)
	# even though allomorph is derivable from gecodb,
	# we derive it outside for easier span calculation
	# (otherwise an additional `start` parameter would be needed
	# or the spans would need to be calculated later)
	# and store it here for easier access
	allomorph: Optional[str] = field(compare=True, kw_only=True, default="")
	span: Tuple[int] = field(compare=True, kw_only=True)

	# added later
	morph: Optional[str] = field(compare=True, init=False)
	adds_umlaut: bool = field(compare=True, init=False)

	def __post_init__(self) -> None:
		if not self.allomorph:
			self.allomorph = ""
		# set `morph`
		self.morph = "e" + self.allomorph if self.gecodb in ["_+n_", "_+ns_"] else self.allomorph
		# set `adds_umlaut`
		self.adds_umlaut = "=" in self.gecodb

	def __repr__(self) -> str:
		return self.gecodb
	

def perform_umlaut(morph: str) -> str:

	# find rightmost "umlautable" vowel before the end
	match = re.search("(?<![auoeiyäöü])(au|a|o|u)[^aou]+$", morph)
	if match:

		# the whole substring containing the vowel
		substr_before_umlaut = match.group(0)
		# the vowel itself
		umlaut = match.group(1)
		# perform umlaut in the substring
		substr_after_umlaut = re.sub(
			umlaut,
			UMLAUTS[umlaut],
			substr_before_umlaut
		)

		# adjust realization: perform umlaut
		morph = re.sub(
			f"{substr_before_umlaut}$",
			substr_after_umlaut,
			morph
		)

	return morph	


@dataclass
class Compound:

	"""
	Class for representation of a DeCowDB compound entry.

	Parameters
	----------
	gecodb : `str`
		DeCowDB dataset entry to analyze

	Attributes
	----------
	lemma : `str`
		recovered lemma representation of the compound

	stems : `List[Stem]`
		list of the stems of the compound

	linkers : `List[Linker]`
		list of the linkers of the compound
		
	components : `List[Union[Stem, Linker]]`
		list of the stems and the linkers of the compound, sorted by span

	Example
	-------
	>>> compound = Compound("gast_+=e_buch")
	>>> compound.gecodb
	"gast_+=e_buch"
	>>> compound.lemma
	"gästebuch"
	>>> compound.components
	["gast", "_+=e_", "buch"]
	"""

	gecodb: str = field(compare=True)

	# added later
	lemma: str = field(compare=True, init=False)
	stems: List[Stem] = field(compare=False, init=False)
	linkers: List[Linker] = field(compare=False, init=False)
	components: List[Union[Stem, Linker]] = field(compare=True, init=False)

	def __post_init__(self) -> None:
		self.gecodb = self.gecodb.lower()
		self.stems = []
		self.linkers = []
		self._analyze() # defines .stems, .linkers, .components, .lemma

	def _analyze(self) -> None:

		j = 0

		# split by linkers; capturing groups will store the linkers
		components = re.split(LINKER_PATTERN, self.gecodb)
		for component in components:

			if not component:
				continue  # `None` from capturing group occasionally occurs

			if not "_" in component:    # stem

				self.stems.append(
					Stem(
						morph=component,
						# allomorph will be modified later if needed
						span=(j, j := j + len(component))
					)
				)

			else:	# linker

				if component == "_":
					# zero linker
					linker = Linker(
						gecodb=component,
						span=(j, j)
					)

				else:	# explicit linker

					# capture linker under name "r"
					match = re.match(r"_\+=?(?P<r>!DE!)_".replace("!DE!", DE), component)
					allomorph = match.groupdict().get("r", "")

					linker = Linker(
						gecodb=component,
						allomorph=allomorph,
						span=(j, j := j + len(allomorph))
					)

					if linker.adds_umlaut: # adjust previous stem if needed
						
						prev_stem = self.stems[-1]
						# adjust realization: perform umlaut
						prev_stem.allomorph = perform_umlaut(prev_stem.morph)

				self.linkers.append(linker)

		# sort by span => order of appearance
		self.components = sorted(self.stems + self.linkers, key=lambda c: c.span)
		self.lemma = "".join([component.allomorph for component in self.components])

	def __len__(self) -> int:
		return len(self.components)

	def __repr__(self) -> str:
		return f"{self.lemma} <-- {self.gecodb}"