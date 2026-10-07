#!/usr/bin/env bash
# Zip th11/ into dist/th11.apworld, without tests and caches.
set -euo pipefail
cd "$(dirname "$0")/.."

mkdir -p dist
rm -f dist/th11.apworld
zip -qr dist/th11.apworld th11 -x '*/__pycache__/*' 'th11/test/*' '*.DS_Store'
echo dist/th11.apworld
