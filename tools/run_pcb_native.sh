#!/bin/zsh
# KiCad pcbnew SaveBoard can rewrite project defaults without full project loading.
# Preserve the authoritative project settings around the isolated native process.
set -eu
cd "$(dirname "$0")/.."
[[ ! -e '~tinkerbadge.kicad_pcb.lck' ]] || { echo 'PCB editor lock present; stop'; exit 2; }
backup=".build/project-settings-preserved-$(date +%s).json"
cp tinkerbadge.kicad_pro "$backup"
restore() { cp "$backup" tinkerbadge.kicad_pro; }
trap restore EXIT
/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/bin/python3 "$@"
