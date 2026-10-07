#!/usr/bin/env bash
# Prove AP generates from dist/th11.apworld, not the dev symlink.
set -euo pipefail
cd "$(dirname "$0")/.."
root=$PWD
game=$(.venv/bin/python -c 'import json; print(json.load(open("th11/archipelago.json"))["game"])')

tools/build_apworld.sh
tmp=$(mktemp -d)
restore() {
	ln -sfn ../../th11 "$root/.ap/worlds/th11"
	rm -f "$root/.ap/custom_worlds/th11.apworld"
	rm -rf "$tmp"
}
trap restore EXIT

# AP refuses a game registered twice, so the symlink must go.
rm .ap/worlds/th11
cp dist/th11.apworld .ap/custom_worlds/
# Its own players dir, so only this YAML is generated.
cp examples/th11.yaml "$tmp/"
touch "$tmp/marker"

cd .ap
# Skip ModuleUpdate: it prompts to pip-install other worlds' requirements.
export SKIP_REQUIREMENTS_UPDATE=1
../.venv/bin/python Generate.py --player_files_path "$tmp" </dev/null
file=$(../.venv/bin/python -c 'import sys, worlds; print(worlds.AutoWorld.AutoWorldRegister.world_types[sys.argv[1]].__file__)' "$game")
case $file in
	*custom_worlds*) echo "apworld loaded from custom_worlds: $file" ;;
	*) echo "th11 world loaded from $file, not custom_worlds" >&2; exit 1 ;;
esac
out=$(find output -name 'AP_*.zip' -newer "$tmp/marker")
[ -n "$out" ] || { echo "no new AP_*.zip in .ap/output" >&2; exit 1; }
echo ".ap/$out"
