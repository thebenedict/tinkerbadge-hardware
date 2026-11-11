#!/bin/sh
# Export the design-review evidence set from the current native files.
# Usage: tools/export_design_review.sh   (run from the repository root)
set -e
OUT=exports/design-review-2026-11-10
mkdir -p "$OUT"
q() { "$@" 2>&1 | grep -v -E 'Font|annotation' || true; }
q kicad-cli sch export netlist tinkerbadge.kicad_sch -o "$OUT/tinkerbadge.net"
q kicad-cli sch export pdf tinkerbadge.kicad_sch -o "$OUT/tinkerbadge-schematic.pdf"
q kicad-cli sch erc tinkerbadge.kicad_sch --severity-all --format json -o "$OUT/erc.json"
q kicad-cli sch export bom tinkerbadge.kicad_sch -o "$OUT/bom.csv" \
  --fields 'Reference,Value,Footprint,MPN,${QUANTITY},${DNP}' --labels 'Reference,Value,Footprint,MPN,Qty,DNP' \
  --group-by 'Value,Footprint,MPN,${DNP}' --exclude-dnp
q kicad-cli pcb drc tinkerbadge.kicad_pcb --schematic-parity --severity-all --format json -o "$OUT/drc.json"
q kicad-cli pcb export svg tinkerbadge.kicad_pcb -o "$OUT/front-copper.svg" --layers F.Cu,F.Silkscreen,Edge.Cuts --mode-single --page-size-mode 2 --exclude-drawing-sheet
q kicad-cli pcb export svg tinkerbadge.kicad_pcb -o "$OUT/rear-copper.svg" --layers B.Cu,B.Silkscreen,Edge.Cuts --mode-single --page-size-mode 2 --exclude-drawing-sheet --mirror
q kicad-cli pcb export svg tinkerbadge.kicad_pcb -o "$OUT/inner-ground-1.svg" --layers In1.Cu,Edge.Cuts --mode-single --page-size-mode 2 --exclude-drawing-sheet
q kicad-cli pcb render tinkerbadge.kicad_pcb -o "$OUT/front-3d.png" --side top --width 1800 --height 1400 --quality basic
q kicad-cli pcb render tinkerbadge.kicad_pcb -o "$OUT/rear-3d.png" --side bottom --width 1800 --height 1400 --quality basic
python3 tools/check_schematic_contracts.py "$OUT/tinkerbadge.net" --output "$OUT/endpoint-check.json" > /dev/null
python3 tools/check_schematic_properties.py "$OUT/tinkerbadge.net" --output "$OUT/property-check.json" > /dev/null
shasum -a 256 tinkerbadge.kicad_pcb tinkerbadge.kicad_pro *.kicad_sch docs/design/*_contract.json > "$OUT/sha256.txt"
kicad-cli version > "$OUT/kicad-version.txt"
echo "exported to $OUT"
