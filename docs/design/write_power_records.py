#!/usr/bin/env python3
"""Render human-readable power records from the maintained JSON sources.

Run from any directory: python3 docs/design/write_power_records.py
This script does not change the source facts or assignments.
"""
import json
from pathlib import Path

root = Path(__file__).resolve().parents[2]
facts = json.loads((root / 'docs/components/power_facts.json').read_text())
contract = json.loads((root / 'docs/design/power_contract.json').read_text())
for component in facts:
    filename = Path(component['source']).name
    pages = ', '.join(map(str, component['critical_pages'])) or 'not available'
    lines = [f"# {component['mpn']}", '', f"Status: {component['review_status']}", '',
             f"Package: {component['package']}", '',
             f"Source: [{filename}](../datasheets/{filename}). Critical PDF pages: {pages}.", '',
             'Pin facts are generated from `power_facts.json`. Project assignments are separate in `../design/power_contract.json`.', '',
             '| Physical pin/pad | Manufacturer function | Meaning |', '|---|---|---|']
    lines.extend(f"| {p['number']} | {p['name']} | {p['function']} |" for p in component['pins'])
    if component.get('selection_status'):
        lines.extend(['', 'Selection: ' + component['selection_status']])
    lines.extend(['', '## Design-relevant facts', ''])
    lines.extend('- ' + note for note in component['notes'])
    lines.extend(['', 'Project circuit and power-state decisions: [power.md](../design/power.md).'])
    (root / 'docs/components' / (component['mpn'] + '.md')).write_text('\n'.join(lines) + '\n')
lines = ['# Power project pin assignments', '',
         'Generated from `power_contract.json`. Manufacturer facts remain in `../components/power_facts.json`; shared AO3400A facts are in `../components/AO3400A.pins.json`.', '',
         contract['interfaces']['no_connects'], '', 'Review status: ' + contract['review_status'], '']
for component in contract['components']:
    lines.extend([f"## {component['ref']} — {component['mpn'] or 'Logical interface'}", '',
                  'Status: ' + component['status'], '', '| Physical pin/pad | Project net |', '|---|---|'])
    lines.extend(f"| {pin} | {net if net is not None else 'NC / blocked as status states'} |" for pin, net in component['pins'].items())
    lines.append('')
lines.extend(['## Support parts', '', '| Ref | Value | Pin 1 net | Pin 2 net | Notes |', '|---|---|---|---|---|'])
for part in contract['two_terminal_support']:
    lines.append(f"| {part['ref']} | {part['value']} | {part['pins']['1']} | {part['pins']['2']} | {part['note']} |")
lines.extend(['', '## Unresolved gates', ''])
lines.extend('- ' + blocker for blocker in contract['blockers'])
(root / 'docs/design/power_pinouts.md').write_text('\n'.join(lines) + '\n')
print(f"Rendered {len(facts)} component records, {len(contract['components'])} assignments and {len(contract['two_terminal_support'])} support parts.")
