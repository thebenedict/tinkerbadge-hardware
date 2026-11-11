#!/bin/sh
# Rebuild the post-review schematic and synced (unrouted-delta) board from the pre-review commit.
set -e
PY=/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3
BASE=${BASE:-3c8a60e}
git checkout $BASE -- display.kicad_sch peripherals.kicad_sch power.kicad_sch tinkerbadge.kicad_sch lighting.kicad_sch mcu.kicad_sch tinkerbadge.kicad_pcb
python3 tools/create_review_footprints.py
python3 tools/apply_design_review_schematic.py
kicad-cli sch upgrade --force tinkerbadge.kicad_sch 2>&1 | grep -v Font || true
mkdir -p .build
kicad-cli sch export netlist tinkerbadge.kicad_sch -o .build/review.net 2>&1 | grep -v -E 'Font|annot' || true
$PY tools/sync_board_design_review.py .build/review.net tinkerbadge.kicad_pcb 2>&1 | grep -v -E 'wxApp|swig' || true
$PY tools/pcb_apply_routes.py tinkerbadge.kicad_pcb docs/design/routing/manual_switch_nodes.json 2>&1 | grep -v -E 'wxApp|swig' || true
$PY tools/pcb_apply_routes.py tinkerbadge.kicad_pcb docs/design/routing/manual_usb_display.json 2>&1 | grep -v -E 'wxApp|swig' || true
$PY tools/pcb_dump.py tinkerbadge.kicad_pcb .build/board.json 2>&1 | grep -v -E 'wxApp|swig' || true
