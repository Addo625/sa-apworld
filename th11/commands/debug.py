"""
Debug and diagnosis commands: memory probes for the probe batches, write logging, and build checks.
"""
from MultiServer import mark_raw
from CommonClient import ClientCommandProcessor, logger

from .. import Variables, probe
from ..Variables import GAME_NAME, PROBE_TABLE
from ..patching import build_name, selftest
from ..probe import float_candidates, format_probe, memsearch, parse_address, parse_pattern, ptrscan, read_entry

MEMSEARCH_CAP = 50
DATA_SECTION = (0xA2000, 0xCAE40)  # th11.exe .data, base-relative (0x4A2000-0x4CAE40, ticket 28)


def named_patterns() -> dict:
	"""name -> hex from memsearch_patterns.json next to the AP install (written by tools/scoredat.py --patterns); {} if absent."""
	import json
	from Utils import user_path
	try:
		with open(user_path("memsearch_patterns.json")) as f:
			return json.load(f)
	except (OSError, ValueError):
		return {}


def log_build(controller):
	"""Name the running th11.exe's build, so players can tell at a glance whether their copy is the one the addresses
	were sourced on (all copies from one zip match; Steam's wrapper is a different file)."""
	import hashlib
	path = controller.exe_path()
	try:
		with open(path, "rb") as f:
			digest = hashlib.sha256(f.read()).hexdigest()
	except (OSError, TypeError) as e:
		logger.info(f"{GAME_NAME}: build not checked ({e})")
		return
	name = build_name(digest)
	if name:
		logger.info(f"{GAME_NAME}: {name}")
	else:
		logger.warning(f"{GAME_NAME}: unknown build (SHA-256 {digest}). The client's addresses come from v1.00a (original): "
			f"run /selftest, and report the result with this line")


class DebugCommands(ClientCommandProcessor):
	def _cmd_probe(self):
		"""Attach to th11.exe and print every address table entry"""
		from ..gameController import gameController
		try:
			controller = gameController()
		except Exception as e:
			logger.error(f"Cannot attach to {GAME_NAME}: {e}")
			return False
		logger.info(format_probe(controller, PROBE_TABLE))
		return True

	@mark_raw
	def _cmd_memsearch(self, pattern_text: str = ""):
		"""Search th11.exe's memory for hex bytes (spaces ok; `00*12` repeats a byte), or a pattern name from memsearch_patterns.json (tools/scoredat.py --patterns)"""
		from ..gameController import gameController
		name = pattern_text.strip()
		try:
			named = named_patterns()
			pattern = bytes.fromhex(named[name]) if name in named else parse_pattern(pattern_text)
		except ValueError:
			pattern = b""
		if not pattern:
			names = ", ".join(sorted(named_patterns())) or "none yet"
			logger.error(f"Usage: /memsearch <hex bytes, e.g. 00*4 0101 00*6> or a pattern name ({names})")
			return False
		try:
			controller = gameController()
			regions = controller.readable_regions()
		except Exception as e:
			logger.error(f"Cannot attach to {GAME_NAME}: {e}")
			return False
		found = memsearch(controller, regions, pattern, MEMSEARCH_CAP)
		logger.info(f"{len(found)} match(es) in {len(regions)} regions" + (f" (capped at {MEMSEARCH_CAP})" if len(found) >= MEMSEARCH_CAP else ""))
		for address in found:
			logger.info(f"  0x{address:08X} (base + 0x{address - controller.base_address:X})")
		return True

	def _cmd_peek(self, hex_address: str = "", count: str = "16"):
		"""Print count bytes at a hex address; offsets allowed, e.g. 029605CC-5A4 (count is decimal)"""
		from ..gameController import gameController
		try:
			address, count = parse_address(hex_address), int(count)
		except ValueError:
			logger.error("Usage: /peek <hex address> [count]")
			return False
		try:
			data = gameController().read_bytes(address, count)
		except Exception as e:
			logger.error(f"Cannot read {GAME_NAME} at 0x{address:08X}: {e}")
			return False
		logger.info(f"0x{address:08X}: {data.hex(' ')}")
		return True

	def _cmd_poke(self, hex_address: str = "", hex_bytes: str = ""):
		"""Debug: write hex bytes at a hex address (offsets allowed: 029605CC+45), only as a probe request says"""
		from ..gameController import gameController
		try:
			address, data = parse_address(hex_address), bytes.fromhex(hex_bytes)
		except ValueError:
			data = b""
		if not data:
			logger.error("Usage: /poke <hex address> <hex bytes>")
			return False
		try:
			controller = gameController()
			before = controller.read_bytes(address, len(data))
			controller.write_bytes(address, data)
		except Exception as e:
			logger.error(f"Cannot write {GAME_NAME} at 0x{address:08X}: {e}")
			return False
		logger.info(f"0x{address:08X}: {before.hex(' ')} -> {data.hex(' ')}")
		return True

	def _cmd_ptrscan(self, hex_address: str = "", hex_range: str = "1000"):
		"""List static pointers in th11.exe's .data into [address - range, address] (find a heap struct's owner)"""
		from ..gameController import gameController
		try:
			target, window = parse_address(hex_address), int(hex_range, 16)
		except ValueError:
			logger.error("Usage: /ptrscan <hex address> [hex range]")
			return False
		try:
			controller = gameController()
			start, end = (controller.base_address + offset for offset in DATA_SECTION)
			found = ptrscan(controller, start, end, target, window)
		except Exception as e:
			logger.error(f"Cannot scan {GAME_NAME}'s .data: {e}")
			return False
		logger.info(f"{len(found)} pointer(s) into [0x{target - window:08X}, 0x{target:08X}]")
		for address, value in found:
			logger.info(f"  0x{address:08X} (base + 0x{address - controller.base_address:X}) -> 0x{value:08X} (target - 0x{target - value:X})")
		return True

	def _cmd_playerfloats(self, count: str = "1000"):
		"""Print speed-like floats in the first count (hex) bytes of the player object, to find its speed fields"""
		from ..gameController import gameController
		try:
			controller = gameController()
			player = read_entry(controller, Variables.ADDR_PLAYER_PTR)
			data = controller.read_bytes(player, int(count, 16))  # player None or 0 raises
		except Exception as e:
			logger.error(f"Cannot read the player object (in a stage?): {e}")
			return False
		lines = [f"Player object at 0x{player:08X}"]
		lines += [f"  +0x{offset:X} = {value:g} (addr 0x{player + offset:08X})" for offset, value in float_candidates(data)]
		logger.info("\n".join(lines))  # one message, like /probe: copies in one go
		return True

	def _cmd_writelog(self, state: str = ""):
		"""Debug: log every client write to the game on/off (off by default), only as a probe request says"""
		if state not in ("on", "off"):
			logger.info(f"Write log is {'on' if probe.write_log else 'off'}. Usage: /writelog on|off")
			return False
		probe.write_log = state == "on"
		logger.info(f"Write log {state}")
		return True

	def _cmd_selftest(self):
		"""Check th11.exe: its build, and every code site the client patches (original, patched by the client, or changed)"""
		from ..gameController import gameController
		try:
			controller = gameController()
		except Exception as e:
			logger.error(f"Cannot attach to {GAME_NAME}: {e}")
			return False
		log_build(controller)
		for line in selftest(controller):
			logger.info(line)
		return True
