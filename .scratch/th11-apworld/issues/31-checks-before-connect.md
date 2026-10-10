# 31: Checks found before the first connect keep shot-type and difficulty mapping

Status: deferred
Blocked by: 10

## Problem
`detect.step` maps checks with `slot_data`, which the client only has after connecting. Playing before the first connect with `shot_type` or `difficulty_check` queues plain `[<Character>] <check>` IDs; with `difficulty_check` those don't exist in the slot, so the server drops them and the checks are lost (shot_type sends the wrong owner's). Marked with a `ponytail:` comment in `Client.poll`.

## DoD
`cd .ap && ../.venv/bin/python -m pytest worlds/th11/test -q` → exit 0 with the test below.

## Test plan
- Client loop (pure, fake memory): kill the Stage 1 midboss on Hard as Reimu B with `ctx.slot = None`, then connect with `{"shot_type": True, "difficulty_check": True}` → the first poll after connecting sends `[Hard][Reimu B] Kisume - Midboss`. `test_checks_before_connect_use_slot_data`.

## Steps
1. Queue the raw run (stage, run index, character, shot, difficulty) while `slot_data` is empty; map the queue with `detect.location_names` once connected. Remove the `ponytail:` comment.

## Deferred
- None.
