import struct
import unittest
from unittest import mock

from .. import TRAP_OPTIONS, Variables
from .. import test as bases
from ..probe import float_candidates
from ..state import GameState
from ..traps import DRAIN_SECONDS, ENTER_DELAY, SPEED_ENTRIES, TIMED, TrapState, tick

FILLER = "+0.05 Power"
NO_WEIGHTS = {option: 0 for option in TRAP_OPTIONS.values()}
SPEEDS = (4.5, 2.0, 3.2, 1.4)
T0 = 100.0  # first tick in the run
LIVE = T0 + ENTER_DELAY  # traps fire from here


def run(lives=3, power=40, in_game=True):
	return GameState(in_game, False, None, None, 1, 1, "Reimu", "Reimu A", lives, power)


def fired(*names, state=None, speeds=SPEEDS):
	"""A TrapState that entered the run at T0, ticked once at LIVE with `names` queued."""
	traps = TrapState()
	tick(traps, T0, state or run(), speeds)
	traps.queue = list(names)
	return traps, tick(traps, LIVE, state or run(), speeds)


class TestInstantTraps(unittest.TestCase):
	def test_half_power(self):
		self.assertEqual(fired("-50% Power", state=run(power=41))[1], ([(Variables.ADDR_POWER, 20)], None))

	def test_life_minus_one(self):
		self.assertEqual(fired("-1 Life", state=run(lives=3))[1], ([(Variables.ADDR_LIVES, 2)], None))

	def test_life_never_kills(self):
		self.assertEqual(fired("-1 Life", state=run(lives=0))[1], ([], None))

	def test_one_trap_per_tick(self):
		traps, first = fired("-1 Life", "-1 Life", state=run(lives=3))
		self.assertEqual(first, ([(Variables.ADDR_LIVES, 2)], None))
		self.assertEqual(tick(traps, LIVE + 0.5, run(lives=2), SPEEDS), ([(Variables.ADDR_LIVES, 1)], None))
		self.assertEqual(traps.queue, [])

	def test_power_drain_per_second_then_stops(self):
		traps, first = fired("Power Drain", state=run(power=40))
		self.assertEqual(first, ([(Variables.ADDR_POWER, 39)], None))
		self.assertEqual(tick(traps, LIVE + 0.5, run(power=39), SPEEDS), ([], None))  # under a second
		self.assertEqual(tick(traps, LIVE + 1, run(power=39), SPEEDS), ([(Variables.ADDR_POWER, 38)], None))
		self.assertEqual(tick(traps, LIVE + DRAIN_SECONDS, run(power=20), SPEEDS), ([], None))

	def test_power_drain_stops_at_zero(self):
		self.assertEqual(fired("Power Drain", state=run(power=0))[1], ([], None))


class TestSpeedTraps(unittest.TestCase):
	def setUp(self):
		offsets = dict(zip(SPEED_ENTRIES, (0x3D4, 0x3D8, 0x3DC, 0x3E0)))  # MoF's layout, standing in for 35's
		patcher = mock.patch.multiple(Variables, **{name: [Variables.ADDR_PLAYER_PTR, offset] for name, offset in offsets.items()})
		patcher.start()
		self.addCleanup(patcher.stop)

	def check(self, name, trapped):
		traps, first = fired(name)
		self.assertEqual(first, ([], trapped))
		self.assertEqual(tick(traps, LIVE + TIMED[name] - 0.5, run(), trapped), ([], None))
		self.assertEqual(tick(traps, LIVE + TIMED[name], run(), trapped), ([], SPEEDS))  # restored
		self.assertIsNone(traps.speed)

	def test_no_focus(self):
		self.check("No Focus", (4.5, 4.5, 3.2, 3.2))

	def test_reverse_movement(self):
		self.check("Reverse Movement", (-4.5, -2.0, -3.2, -1.4))

	def test_aya_speed(self):
		self.check("Aya Speed", (9.0, 1.0, 6.4, 0.7))

	def test_freeze(self):
		self.check("Freeze", (0.0, 0.0, 0.0, 0.0))

	def test_one_speed_trap_at_a_time(self):
		traps, first = fired("Freeze", "No Focus")
		self.assertEqual(first, ([], (0.0, 0.0, 0.0, 0.0)))
		self.assertEqual(traps.queue, ["No Focus"])
		# Freeze expires: No Focus starts from the restored speeds, not the frozen ones.
		self.assertEqual(tick(traps, LIVE + TIMED["Freeze"], run(), (0.0, 0.0, 0.0, 0.0)), ([], (4.5, 4.5, 3.2, 3.2)))
		self.assertEqual(traps.speed[2], SPEEDS)

	def test_forgotten_without_writes_on_leaving_the_run(self):
		traps, _ = fired("Reverse Movement")
		self.assertEqual(tick(traps, LIVE + 1, run(in_game=False), (-4.5, -2.0, -3.2, -1.4)), ([], None))
		self.assertIsNone(traps.speed)

	def test_unreadable_speeds_keep_the_trap_queued(self):
		traps, first = fired("Freeze", "-1 Life", speeds=None)
		self.assertEqual(first, ([(Variables.ADDR_LIVES, 2)], None))  # the instant trap goes first
		self.assertEqual(traps.queue, ["Freeze"])
		self.assertEqual(tick(traps, LIVE + 1, run(), SPEEDS), ([], (0.0, 0.0, 0.0, 0.0)))

	def test_expiry_waits_for_readable_speeds(self):
		traps, _ = fired("Freeze")
		self.assertEqual(tick(traps, LIVE + TIMED["Freeze"], run(), None), ([], None))
		self.assertEqual(tick(traps, LIVE + TIMED["Freeze"] + 1, run(), (0.0, 0.0, 0.0, 0.0)), ([], SPEEDS))


class TestUnsourcedSpeeds(unittest.TestCase):
	def test_unsourced_speeds_drop_the_trap(self):
		traps, first = fired("Freeze", speeds=None)
		self.assertEqual(first, ([], None))
		self.assertEqual(traps.queue, [])


class TestTrapQueue(unittest.TestCase):
	def test_queued_outside_a_run_fire_on_entering(self):
		traps = TrapState()
		traps.queue = ["-1 Life"]
		self.assertEqual(tick(traps, T0, run(in_game=False), None), ([], None))
		self.assertEqual(tick(traps, T0 + 1, run(lives=-1), None), ([], None))  # game over isn't a run
		self.assertEqual(tick(traps, T0 + 2, run(), None), ([], None))  # entered: waits ENTER_DELAY
		self.assertEqual(tick(traps, T0 + 2 + ENTER_DELAY, run(lives=3), None), ([(Variables.ADDR_LIVES, 2)], None))
		self.assertEqual(traps.queue, [])


class TestFloatCandidates(unittest.TestCase):
	def test_finds_speed_like_floats(self):
		data = struct.pack("<5f", 0.0, 4.5, 1e9, -2.0, 0.01) + b"\x01"
		self.assertEqual(float_candidates(data), [(4, 4.5), (12, -2.0)])


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
