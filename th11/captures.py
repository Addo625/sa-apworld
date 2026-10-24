"""
Spell captures: the live save's per-card capture counts -> capture checks (21's slots). Pure, no memory access.
"""
from .scoredat import CLEAR_SIZE
from .Variables import CAPTURE_CAPS, SHOT_TO_CHARACTER, SHOT_TYPE_LIST, SPELL_CARD_SIZE, SPELL_CLEAR_OFFSET


def count_address(table, shot, card):
	"""Address of `shot`'s capture count for `card`; table: the resolved ADDR_SPELL_CARDS (Reimu A's first record)."""
	return table + SHOT_TYPE_LIST.index(shot) * CLEAR_SIZE + card * SPELL_CARD_SIZE + SPELL_CLEAR_OFFSET


def spell_slot(card):
	"""Card ID -> the attack it is, whatever the difficulty (63). The save's records: 0-1 Kisume Hard/Lunatic, then each
	4 IDs one attack on Easy, Normal, Hard, Lunatic (2-161), then Extra's 13 cards (162-174)."""
	if card < 2:
		return 0
	if card < 162:
		return 1 + (card - 2) // 4
	return 41 + card - 162


def owner(shot, slot_data):
	"""Whose capture slots `shot` fills: "" when shared, the shot with shot_type, else its character."""
	if slot_data.get("capture_slots"):
		return ""
	return shot if slot_data.get("shot_type") else SHOT_TO_CHARACTER[shot]


def capture_location(shot, stage, captured_before, slot_data, sent_names):
	"""-> the capture location a newly captured card sends, or None.
	captured_before: whether the owner captured this spell before in this seed. Only a card new to the owner counts
	(21: the k-th *different* card); it fills the stage's lowest capture check not checked yet. Not "sent + 1": a
	collect or release marks capture checks found out of order, and the next spell then re-sent a checked one forever
	while a lower one (holding a Next Stage) was never sent (Windows playtest, 2026-10-22)."""
	if not slot_data.get("spell_card_keys") or stage not in range(1, 7) or captured_before:
		return None
	slots = min(slot_data.get("captures_per_stage", 0), CAPTURE_CAPS[stage - 1])
	prefix = f"[{owner(shot, slot_data)}] " if owner(shot, slot_data) else ""
	sent = set(sent_names)
	return next((name for k in range(1, slots + 1) if (name := f"{prefix}Stage {stage} - Capture {k}") not in sent), None)
