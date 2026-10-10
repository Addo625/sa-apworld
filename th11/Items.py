from typing import Dict, NamedTuple

from BaseClasses import Item, ItemClassification

from .Variables import *


class TItem(Item):
	game: str = DISPLAY_NAME


class TItemData(NamedTuple):
	category: str
	code: int
	classification: ItemClassification = ItemClassification.filler
	max_quantity: int = 1


# Deferred categories (Normal mode, per-character stages, Extra, Koishi, traps)
# are listed now so their IDs never shift. create_items only uses core ones.
item_table: Dict[str, TItemData] = {
	# Items
	"+1 Life":				TItemData("Items", STARTING_ID + 0, ItemClassification.progression, 8),
	"+0.50 Power":			TItemData("Items", STARTING_ID + 1, ItemClassification.progression, 8),
	"Lower Difficulty":		TItemData("Items", STARTING_ID + 2, ItemClassification.progression, 3),
	"+1 Continue":			TItemData("[Normal] Items", STARTING_ID + 3, ItemClassification.useful, 3),
	"Spell Card Key":		TItemData("Items", STARTING_ID + 4, ItemClassification.progression),

	# Characters
	"Reimu A - Yukari":		TItemData("Characters", STARTING_ID + 100, ItemClassification.progression),
	"Reimu B - Suika":		TItemData("Characters", STARTING_ID + 101, ItemClassification.progression),
	"Reimu C - Aya":		TItemData("Characters", STARTING_ID + 102, ItemClassification.progression),
	"Marisa A - Alice":		TItemData("Characters", STARTING_ID + 103, ItemClassification.progression),
	"Marisa B - Patchouli":	TItemData("Characters", STARTING_ID + 104, ItemClassification.progression),
	"Marisa C - Nitori":	TItemData("Characters", STARTING_ID + 105, ItemClassification.progression),

	# Stages
	"Next Stage":				TItemData("[Global] Stages", STARTING_ID + 200, ItemClassification.progression, 5),
	"[Reimu] Next Stage":		TItemData("[Character] Stages", STARTING_ID + 201, ItemClassification.progression, 5),
	"[Marisa] Next Stage":		TItemData("[Character] Stages", STARTING_ID + 202, ItemClassification.progression, 5),
	"[Reimu A] Next Stage":		TItemData("[Shot Type] Stages", STARTING_ID + 203, ItemClassification.progression, 5),
	"[Reimu B] Next Stage":		TItemData("[Shot Type] Stages", STARTING_ID + 204, ItemClassification.progression, 5),
	"[Reimu C] Next Stage":		TItemData("[Shot Type] Stages", STARTING_ID + 205, ItemClassification.progression, 5),
	"[Marisa A] Next Stage":	TItemData("[Shot Type] Stages", STARTING_ID + 206, ItemClassification.progression, 5),
	"[Marisa B] Next Stage":	TItemData("[Shot Type] Stages", STARTING_ID + 207, ItemClassification.progression, 5),
	"[Marisa C] Next Stage":	TItemData("[Shot Type] Stages", STARTING_ID + 208, ItemClassification.progression, 5),
	"Extra Stage":				TItemData("[Global] Extra Stage", STARTING_ID + 209, ItemClassification.progression),
	"[Reimu] Extra Stage":		TItemData("[Character] Extra Stage", STARTING_ID + 210, ItemClassification.progression),
	"[Marisa] Extra Stage":		TItemData("[Character] Extra Stage", STARTING_ID + 211, ItemClassification.progression),
	"[Reimu A] Extra Stage":	TItemData("[Shot Type] Extra Stage", STARTING_ID + 212, ItemClassification.progression),
	"[Reimu B] Extra Stage":	TItemData("[Shot Type] Extra Stage", STARTING_ID + 213, ItemClassification.progression),
	"[Reimu C] Extra Stage":	TItemData("[Shot Type] Extra Stage", STARTING_ID + 214, ItemClassification.progression),
	"[Marisa A] Extra Stage":	TItemData("[Shot Type] Extra Stage", STARTING_ID + 215, ItemClassification.progression),
	"[Marisa B] Extra Stage":	TItemData("[Shot Type] Extra Stage", STARTING_ID + 216, ItemClassification.progression),
	"[Marisa C] Extra Stage":	TItemData("[Shot Type] Extra Stage", STARTING_ID + 217, ItemClassification.progression),

	# Endings
	"[Reimu] Ending - Utsuho":	TItemData("Endings", STARTING_ID + 300, ItemClassification.progression),
	"[Marisa] Ending - Utsuho":	TItemData("Endings", STARTING_ID + 301, ItemClassification.progression),
	"[Reimu] Ending - Koishi":	TItemData("Endings", STARTING_ID + 302, ItemClassification.progression),
	"[Marisa] Ending - Koishi":	TItemData("Endings", STARTING_ID + 303, ItemClassification.progression),

	# Junk
	"+0.05 Power":	TItemData("Filler", STARTING_ID + 400),

	# Traps
	"-50% Power":		TItemData("Traps", STARTING_ID + 500, ItemClassification.trap),
	"-1 Life":			TItemData("Traps", STARTING_ID + 501, ItemClassification.trap),
	"No Focus":			TItemData("Traps", STARTING_ID + 502, ItemClassification.trap),
	"Reverse Movement":	TItemData("Traps", STARTING_ID + 503, ItemClassification.trap),
	"Aya Speed":		TItemData("Traps", STARTING_ID + 504, ItemClassification.trap),
	"Freeze":			TItemData("Traps", STARTING_ID + 505, ItemClassification.trap),
	"Power Drain":		TItemData("Traps", STARTING_ID + 506, ItemClassification.trap),
}
