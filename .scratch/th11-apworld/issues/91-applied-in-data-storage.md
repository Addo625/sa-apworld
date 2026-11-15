# 91: received lives, power and traps apply once across client restarts

Status: done
Blocked by: None

## Problem
`items_applied` and `traps_seen` lived only in the client (the `ponytail:` at `receive.py:145`). A fresh client starts both at 0, so restarting it mid-run applied every `+1 Life` and `+0.50 Power` received again, up to the caps (a cheat), and queued every trap received again (the player suffers).

## DoD
- `pytest worlds/th11/test -q` passes with the tests below.
- In game (optional): receive a +1 Life in a run, restart the client, reconnect: the lives don't change.

## Design
- Both counts are kept in server data storage, `th11_applied_<team>_<slot>` and `th11_traps_<team>_<slot>`, as captures are (`capture_key`). `Connected` subscribes to them (`set_notify`); a new seed drops the old room's values first.
- Until both have arrived, items and traps wait, as they do outside a run. Then each local count becomes `max(local, stored)`.
- A count that grows is stored with a `max` Set **after** that tick's memory writes, so a crash in between replays one tick's items rather than losing them.

## Test plan
- `test_client.test_restarted_client_applies_items_once`: stored counts at the total → no lives write, no trap, nothing sent; counts not arrived → nothing applied; one item and one trap new → only those, and `max` Sets with the total; a new room (nothing stored) → everything once.
- `test_client.test_connected_waits_for_this_rooms_counts`: Connected subscribes; a new seed drops the old counts, a reconnect keeps them.

## Steps
1. `Client`: `count_keys`, subscribe on Connected, gate and store in `poll`. 2. Test helpers model a connected client whose counts arrived. 3. Tests, install.

## Deferred
- `traps_seen` counts traps queued, not fired, so a client restarted before a queued trap fires drops it (`ponytail:` in `Client.poll`). Upgrade: store the queue.
- Two clients on one slot (37's DeathLink test) now share the counts: the second game doesn't get items the first applied.
