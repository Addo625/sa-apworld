# 81: The client's /commands live in th11/commands/

Status: done
Blocked by: None

## Problem
The human (2026-10-24): the 18 `/commands` filled the top of `th11/Client.py` (lines 48-276 of 646), mixed with the connection and game loop.

## What to do
- Move them verbatim into `th11/commands/`:
  - `debug.py`: `/probe /memsearch /peek /poke /ptrscan /playerfloats /writelog /selftest`, with `named_patterns`, `MEMSEARCH_CAP`, `DATA_SECTION`, `log_build`;
  - `links.py`: `/deathlink /deathlink_trigger /deathlink_amnesty /receivedeath /ringlink /limits`;
  - `play.py`: `/tracker /messages /itemsound /launch`.
- `commands/__init__.py`'s `TouhouClientProcessor` inherits the three; AP's `CommandMeta` merges base processors' commands. `Client.py` imports it, so existing imports keep working.
- No behaviour change: the same 18 commands register, and the suite passes unchanged.

## Deferred
- None.
