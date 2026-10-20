# 56: Block Start from the title menu in Practice-mode seeds

Status: deferred
Blocked by: 55

## Problem
55 makes normal Start runs in a Practice seed send nothing, but the player can still start one and only learns from the client log. The human suggested blocking Start through the menu, as the guard does for locked difficulties.

## What to do
- Find the title menu's cursor for Start (menu 0, `ADDR_MENU_CURSOR`; probe 06 S0 had cursor 0 on Start) and, in Practice seeds, move it off Start (extend `guard.correct`). Needs a probe of the title cursor rows (Start, Extra Start, Practice, ...) through the probe batch.

## Deferred
- None.

## Comments
- 2026-10-20 Claude: batch 61 R3: the title menu (`ADDR_MENU = 0`) has cursor Start 0, Practice 2 (Extra Start 1). Promoting this is now code only: in Practice seeds, `guard.correct` moves a title cursor of 0 to 2.
