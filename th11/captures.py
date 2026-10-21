"""
Spell captures: the live save's per-card capture counts -> capture checks (21's slots). Pure, no memory access.
"""
import struct

from .Variables import CAPTURE_CAPS, SHOT_TO_CHARACTER, SHOT_TYPE_LIST, SPELL_CARD_COUNT, SPELL_CARD_SIZE, SPELL_CLEAR_OFFSET


def clear_counts(block: bytes):
	"""One shot's card records (SPELL_CARD_COUNT x SPELL_CARD_SIZE bytes) -> capture count per card ID."""
	return [struct.unpack_from("<i", block, card * SPELL_CARD_SIZE + SPELL_CLEAR_OFFSET)[0] for card in range(SPELL_CARD_COUNT)]


def spell_slot(card):
	"""Card ID -> the attack it is, whatever the difficulty (63). The save's records: 0-1 Kisume Hard/Lunatic, then each
	4 IDs one attack on Easy, Normal, Hard, Lunatic (2-161), then Extra's 13 cards (162-174)."""
	if card < 2:
		return 0
	if card < 162:
		return 1 + (card - 2) // 4
	return 41 + card - 162


def slot_cards(slot):
	"""The card IDs of a spell slot."""
	return [card for card in range(SPELL_CARD_COUNT) if spell_slot(card) == slot]


def new_captures(before, after):
	"""Card IDs whose capture count rose."""
	return [card for card, (old, new) in enumerate(zip(before, after)) if new > old]


def owner_shots(shot, slot_data):
	"""Shots whose captures share `shot`'s slots: all six when shared, the shot with shot_type, else its character's."""
	if slot_data.get("capture_slots"):
		return SHOT_TYPE_LIST
	if slot_data.get("shot_type"):
		return [shot]
	return [s for s in SHOT_TYPE_LIST if SHOT_TO_CHARACTER[s] == SHOT_TO_CHARACTER[shot]]


def owner(shot, slot_data):
	"""Whose capture slots `shot` fills: "" when shared, the shot with shot_type, else its character."""
	if slot_data.get("capture_slots"):
		return ""
	return shot if slot_data.get("shot_type") else SHOT_TO_CHARACTER[shot]


def capture_location(shot, stage, captured_before, slot_data, sent_names):
	"""-> the capture location a newly captured card sends, or None.
	captured_before: whether any of owner_shots had captured this card before. Only a card new to the owner counts
	(21: the k-th *different* card); k = the stage's capture checks already sent + 1, up to its slot count."""
	if not slot_data.get("spell_card_keys") or stage not in range(1, 7) or captured_before:
		return None
	slots = min(slot_data.get("captures_per_stage", 0), CAPTURE_CAPS[stage - 1])
	prefix = f"[{owner(shot, slot_data)}] " if owner(shot, slot_data) else ""
	name = f"{prefix}Stage {stage} - Capture "
	k = 1 + sum(1 for sent in sent_names if sent and sent.startswith(name))
	return f"{name}{k}" if k <= slots else None
