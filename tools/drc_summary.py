#!/usr/bin/env python3
"""Run KiCad DRC with schematic parity and print a compact summary. Usage: drc_summary.py board out.json [-v]"""
import collections
import json
import subprocess
import sys

board, out = sys.argv[1], sys.argv[2]
subprocess.run(['kicad-cli', 'pcb', 'drc', board, '--schematic-parity', '--severity-all', '--format', 'json', '-o', out], capture_output=True)
d = json.load(open(out))
print('violations', dict(collections.Counter(v['type'] for v in d['violations'])))
print('unconnected', len(d['unconnected_items']), 'parity', len(d.get('schematic_parity', [])))
if '-v' in sys.argv:
    for v in d['violations']:
        if v['type'] not in ('track_dangling', 'via_dangling', 'silk_overlap', 'silk_over_copper', 'text_height', 'silk_edge_clearance'):
            print(' ', v['type'], '|', v['description'][:70], [(i['description'][:45], round(i['pos']['x'], 2), round(i['pos']['y'], 2)) for i in v['items']])
    for v in d['unconnected_items']:
        print('  open', [(i['description'][:55], round(i['pos']['x'], 2), round(i['pos']['y'], 2)) for i in v['items']])
    for v in d.get('schematic_parity', []):
        print('  parity', v['description'][:90], [i['description'][:30] for i in v['items']])
