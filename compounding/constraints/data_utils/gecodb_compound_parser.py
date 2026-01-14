"""
Module for parsing the DECOW16 compound dataset.
"""

import re
from dataclasses import dataclass, field
from typing import Tuple, List, Optional, Union, Literal


DE = "[a-zäöüß]*"   # German alphabet
LINK_TYPES = {  # (legacy)
	# links are in parentheses so that when the
	# raw compound is split, links are returns as well
	"addition_umlaut": f"(_\+={DE}_)",  # gast_+=e_buch = Gästebuch, mutter_+=_rente = Mütterrente
	"addition": f"(_\+{DE}_)",          # bund_+es_land = Bundesland
	"zero": "(_)"              # zeit_punkt = Zeitpunkt
}
LINK_PATTERN = '|'.join(LINK_TYPES.values())    # any link
UMLAUTS = {
	'au': 'äu',
	'a': 'ä',
	'o': 'ö',
	'u': 'ü'
}
UMLAUTS_REVERSED = {v: k for k, v in UMLAUTS.items()}


@dataclass
class Stem:

	"""
	A stem component of a `Compound`.

	Attributes
	----------
	component : `str`
		morpheme representation of the component

	realization : `str`, optional
		concrete realization of the component; if not given, equals to `component`

	span : `Tuple[int]`
		span of the component realization in the `Compound` lemma

	Example
	-------
	>>> compound = Compound("gast_+=e_buch")
	>>> compound.components[0].component
	"gast"
	>>> compound.components[0].realization
	"gäst"
	>>> compound.components[0].span
	(0, 4)
	"""

	component: str = field(compare=True)
	realization: Optional[str] = field(compare=True, default=None)
	span: Tuple[int] = field(compare=True, kw_only=True)
	# further features

	def __post_init__(self) -> None:
		if not self.realization:
			self.realization = self.component

	def __repr__(self) -> str:
		return self.component


@dataclass
class Link:

	"""
	A link component of a `Compound`.

	Attributes
	----------
	component : `str`
		decodb representation of the component, e.g. "_+er_"

	realization : `str`, optional
		concrete realization of the component, e.g. "er"; if not given, equals to an empty string

	span : `Tuple[int]`
		span of the component in the `Compound` lemma

	type : `str`
		type of the link according to the COW dataset

	Example
	-------
	>>> compound = Compound("mutter_+=_rente")
	>>> compound.components[1].component
	"_+=_"
	>>> compound.components[1].realization
	""
	>>> compound.components[1].span
	(6, 6)
	>>> compound.components[1].type
	"addition_umlaut"
	"""

	component: str = field(compare=True)
	realization: Optional[str] = field(compare=True, default=None)
	span: Tuple[int] = field(compare=True, kw_only=True)
	type: Literal["addition_umlaut", "addition", "zero"] = field(compare=True, kw_only=True)
	# further features

	def __post_init__(self) -> None:
		if not self.realization:
			self.realization = ""

	def __repr__(self) -> str:
		return self.component


@dataclass
class Compound:

	"""
	Class for representation of a COW compound entry.

	Parameters
	----------
	raw : `str`
		COW dataset entry to analyze

	Attributes
	----------
	lemma : `str`
		recovered lemma representation of the compound

	stems : `List[Stem]`
		list of the stems of the compound

	links : `List[Link]`
		list of the links of the compound
		
	components : `List[Union[Stem, Link]]`
		list of the stems and the links of the compound, sorted by span

	Example
	-------
	>>> compound = Compound("gast_+=e_buch")
	>>> compound.raw
	"gast_+=e_buch"
	>>> compound.lemma
	"gästebuch"
	>>> compound.components
	["gast", "_+=e", "buch"]
	"""

	raw: str = field(compare=True)
	lemma: str = field(compare=True, init=False)
	stems: List[Stem] = field(compare=False, init=False)
	links: List[Link] = field(compare=False, init=False)
	components: List[Union[Stem, Link]] = field(compare=True, init=False)

	def __post_init__(self) -> None:
		self._analyze(self.raw) # defines .stems, .links, .components, .lemma

	def _get_stem_obj(self, component: str) -> Stem:
		stem = Stem(
			component=component,
			# realization is just as the component at first, will be modified later if needed
			span=(self.j, self.j + len(component)),
		)
		self.j += len(component)
		return stem
	
	def _get_link_info(self, link: str) -> Tuple[str]:

		"""
		Determines realization and type of the link.

		Parameters
		----------
		link : `str`
			string to analyze

		Returns
		-------
		`Tuple[str]`
			the link itself, it's realization, and it's type
		"""

		for link_type, pattern in LINK_TYPES.items():
			match = re.match(
				pattern.replace(DE, f'(?P<r>{DE})'), # add parenthesis to pattern to capture links under name "r"
				link
			)
			if match:
				# match will return 3 spans: the span of the whole match,
				# the span of the first capturing group that we use to return
				# the links when splitting a raw compound (same as the whole match),
				# and the last span is the realization of the component
				# that we capture in (DE)
				realization = match.groupdict().get("r", "")  # in zero, there is no group "r"
				return link, realization, link_type

	def _get_link_obj(self, component: str) -> Link:
		component, realization, link_type = self._get_link_info(component)
		link = Link(
			component=component,
			realization=realization,
			span=(self.j, self.j + len(realization)),
			type=link_type
		)
		self.j += len(realization)
		return link
	
	def _perform_umlaut(self, string: str) -> str:

		"""
		Performs rightmost (!) umlaut, like "altstadt" --> "altstädt".

		Parameters
		----------
		string : `str`
			string to perform umlaut over

		Returns
		-------
		`str`
			string after performing umlaut (input string if not applicable)
		"""

		match = re.search("(au|a|o|u)[^aou]+$", string)
		if match:
			# the whole suffix containing the vowel
			suffix_before_umlaut = match.group(0)
			# the vowel itself
			umlaut = match.group(1)
			# perform umlaut in the suffix
			suffix_after_umlaut = re.sub(
				umlaut,
				UMLAUTS[umlaut],
				suffix_before_umlaut
			)
			# adjust realization: perform umlaut
			string = re.sub(
				f'{suffix_before_umlaut}$',
				suffix_after_umlaut,
				string
			)
		return string
	
	def _fuse_link(self, link: Link) -> None:
		# build the lemma by fusing currently processed part with incoming links;
		# that includes, for example, umlaut and deletion processing, zero and so on;
		# adjust previous stem
		previous_stem = self.stems[-1]
		if link.type == "addition_umlaut":
			# search for the closest to the link "umlautable" vowel;
			# will return 2 matches (if finds anything):
			# the whole suffix with umlaut, and the vowel itself (in the capturing group)
			previous_stem.realization = self._perform_umlaut(previous_stem.component)

	def _analyze(self, raw: str) -> None:
		raw = raw.lower()
		self.stems = []
		self.links = []
		self.j = 0  # global scope of index to be available from anywhere in the class
		# split by links; capturing groups will store the links
		components = re.split(LINK_PATTERN, raw)
		for component in components:
			if not component: continue  # `None` from capturing group occasionally occurs
			if not '_' in component:    # stem
				stem = self._get_stem_obj(component)
				self.stems.append(stem)
			else:
				link = self._get_link_obj(component)
				self._fuse_link(link) # adjust previous stem if needed
				self.links.append(link)
		del self.j
		self.components = sorted(self.stems + self.links, key=lambda c: c.span) # sort by span => order of appearance
		self.lemma = ''.join([component.realization for component in self.components])

	def __len__(self) -> int:
		return len(self.components)

	def __repr__(self) -> str:
		return f"{self.lemma} <-- {self.raw}"