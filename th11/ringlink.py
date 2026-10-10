"""
RingLink (MoF ring_link_loop/on_ringlink): power read each poll -> rings to send, received rings -> power writes.
One ring is one power unit (0.05), the unit MoF sends. Pure, no memory access.
"""
from . import Variables
from .receive import MAX_POWER, in_run


def delta(prev, state):
	"""prev: last poll's state after the client's own writes (items, traps, received rings), so only the game
	changes power here. -> rings to send, 0 for none."""
	# ponytail: a bomb costs 1.00 power in SA (none in MoF), so bombs send -20; filter drops of exactly 20
	# without a life lost if players find that harsh.
	if not (prev and in_run(prev) and in_run(state)) or None in (prev.power, state.power):
		return 0  # a menu exit or a new run: power is a leftover, not a change
	return state.power - prev.power


def receive(state, amount):
	"""-> writes [(entry, value)] adding `amount` rings to power, within 0..MAX_POWER. Outside a run, dropped (MoF)."""
	if not in_run(state) or state.power is None or not amount:
		return []
	power = min(max(state.power + amount, 0), MAX_POWER)
	return [(Variables.ADDR_POWER, power)] if power != state.power else []
