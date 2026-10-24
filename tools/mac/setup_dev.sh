#!/usr/bin/env bash
# Dev AP checkout + venv for the th11 world. Safe to re-run.
set -euo pipefail
cd "$(dirname "$0")/../.."
# Keep a double-clicked window open; skipped when another script calls this one, or with no terminal.
pause_at_end() {
	if [ -z "${TH11_NESTED:-}" ] && [ -t 0 ]; then
		read -r -n 1 -s -p "Press any key to close..." </dev/tty || true
		echo
	fi
}
trap pause_at_end EXIT

tag=$(cat tools/AP_VERSION)
[ -d .ap ] || git clone --depth 1 --branch "$tag" https://github.com/ArchipelagoMW/Archipelago .ap
[ -d .venv ] || python3.12 -m venv .venv
.venv/bin/pip install -q -r .ap/requirements.txt pytest
ln -sfn ../../th11 .ap/worlds/th11
