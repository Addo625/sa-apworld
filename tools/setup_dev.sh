#!/usr/bin/env bash
# Dev AP checkout + venv for the th11 world. Safe to re-run.
set -euo pipefail
cd "$(dirname "$0")/.."

tag=$(cat tools/AP_VERSION)
[ -d .ap ] || git clone --depth 1 --branch "$tag" https://github.com/ArchipelagoMW/Archipelago .ap
[ -d .venv ] || python3.12 -m venv .venv
.venv/bin/pip install -q -r .ap/requirements.txt pytest
ln -sfn ../../th11 .ap/worlds/th11
