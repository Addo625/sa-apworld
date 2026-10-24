# 77: The client shows only your own item messages by default

Status: done
Blocked by: None

## Problem
Windows 2-player playtest (2026-10-22): "Janania found their +1 Life" appeared in Addo's client. That's standard AP behaviour: the server sends every player's item events (`PrintJSON` type `ItemSend`) to the whole team, and `CommonClient.on_print_json` prints them all. In a multiworld this floods the log with finds unrelated to you.

## What to do
- `TouhouContext.on_print_json` drops item events that `CommonContext.is_uninteresting_item_send` (AP's own helper) says don't concern this slot, unless `/messages all` is set. Chat, hints, joins and goals always show.
- README line. Test: `test_other_players_item_events_hidden_by_default`.

## Deferred
- None.
