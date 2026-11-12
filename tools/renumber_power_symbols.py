#!/usr/bin/env python3
"""Give power and flag symbols references that are unique across the sheets. Idempotent.

Each sheet was drawn with its own #PWR001... sequence, so KiCad reported "annotation
errors" on every netlist export. Power symbols are not components; this changes no
net and no part reference. Sheet n gets #PWRn01, #PWRn02, ...

Usage: renumber_power_symbols.py [DIR]   (then kicad-cli sch upgrade --force on each sheet)
"""
import pathlib
import re
import sys

SHEETS = ['power', 'mcu', 'display', 'lighting', 'peripherals']


def main(root='.'):
    for index, name in enumerate(SHEETS, 1):
        path = pathlib.Path(root) / f'{name}.kicad_sch'
        text = path.read_text()
        changed = 0
        for prefix in ('#PWR', '#FLG'):
            old = sorted(set(re.findall(r'\(reference "(%s\d+)"\)' % re.escape(prefix), text)),
                         key=lambda r: int(r[len(prefix):]))
            for ref in old:
                if text.count(f'(reference "{ref}")') != 1:
                    raise SystemExit(f'{name}: {ref} is used more than once on the sheet')
            new = {ref: f'{prefix}{index}{n:02d}' for n, ref in enumerate(old, 1)}
            if all(k == v for k, v in new.items()):
                continue
            # two passes through a placeholder so a new number never collides with an old one
            for ref in old:
                text = text.replace(f'"{ref}"', f'"\x00{new[ref]}"')
                changed += 1
            text = text.replace('"\x00', '"')
        path.write_text(text)
        print(name, 'renumbered', changed)


if __name__ == '__main__':
    main(*sys.argv[1:2])
