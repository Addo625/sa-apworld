#!/usr/bin/env bash
# Zip th11/ into dist/th11.apworld, without tests and caches.
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

mkdir -p dist
rm -f dist/th11.apworld
zip -qr dist/th11.apworld th11 -x '*/__pycache__/*' 'th11/test/*' '*.DS_Store'
echo dist/th11.apworld
