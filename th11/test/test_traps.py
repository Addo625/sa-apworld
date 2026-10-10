from .. import TRAP_OPTIONS
from .. import test as bases

FILLER = "+0.05 Power"
NO_WEIGHTS = {option: 0 for option in TRAP_OPTIONS.values()}


def pool_names(test):
	return [item.name for item in test.multiworld.itempool if item.player == test.player]


class TestTrapsZero(bases.TH11TestBase):
	def test_traps_zero_none(self):
		names = pool_names(self)
		self.assertFalse(set(TRAP_OPTIONS) & set(names))
		self.assertIn(FILLER, names)


class TestTrapsAll(bases.TH11TestBase):
	options = {"traps": 100}

	def test_traps_100_all_filler_are_traps(self):
		names = pool_names(self)
		self.assertNotIn(FILLER, names)
		self.assertTrue(set(TRAP_OPTIONS) & set(names))


class TestTrapWeights(bases.TH11TestBase):
	options = {"traps": 100, **NO_WEIGHTS, "freeze_trap": 10}

	def test_trap_weights_zero_excluded(self):
		names = pool_names(self)
		self.assertIn("Freeze", names)
		self.assertFalse((set(TRAP_OPTIONS) - {"Freeze"}) & set(names))
		self.assertNotIn(FILLER, names)


class TestTrapWeightsAllZero(bases.TH11TestBase):
	options = {"traps": 100, **NO_WEIGHTS}

	def test_no_weights_keeps_filler(self):
		names = pool_names(self)
		self.assertFalse(set(TRAP_OPTIONS) & set(names))
		self.assertIn(FILLER, names)
