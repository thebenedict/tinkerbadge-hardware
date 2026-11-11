#!/usr/bin/env python3
"""Remove dangling tracks/vias reported by KiCad DRC, keeping any whose removal
would open a connection. KiCad Python.

KiCad flags some T-junction joins as dangling, so each batch is verified:
the batch is removed on a scratch copy, DRC is rerun, and it is only kept if
the unconnected count did not rise. Failing batches are bisected.

Usage: pcb_prune_dangling.py board.kicad_pcb
"""
import json
import shutil
import subprocess
import sys

import pcbnew


def drc(path):
    out = path + '.drc.json'
    subprocess.run(['kicad-cli', 'pcb', 'drc', path, '--severity-all', '--format', 'json', '-o', out], capture_output=True)
    return json.load(open(out))


def remove(path, ids):
    b = pcbnew.LoadBoard(path)
    for t in list(b.GetTracks()):
        if t.m_Uuid.AsString() in ids:
            b.RemoveNative(t)
    pcbnew.ZONE_FILLER(b).Fill(b.Zones())
    pcbnew.SaveBoard(path, b)


def main(board):
    scratch = board.replace('.kicad_pcb', '.prune_tmp.kicad_pcb')
    d = drc(board)
    base = len(d['unconnected_items'])
    ids = sorted({i['uuid'] for v in d['violations'] if v['type'] in ('track_dangling', 'via_dangling') for i in v['items']})
    kept = 0

    def attempt(batch):
        nonlocal kept
        if not batch:
            return
        shutil.copy(board, scratch)
        remove(scratch, set(batch))
        if len(drc(scratch)['unconnected_items']) <= base:
            shutil.copy(scratch, board)
            kept += len(batch)
        elif len(batch) > 1:
            attempt(batch[:len(batch) // 2])
            attempt(batch[len(batch) // 2:])

    attempt(ids)
    print('dangling reported', len(ids), 'removed', kept, 'unconnected baseline', base)


if __name__ == '__main__':
    main(sys.argv[1])
