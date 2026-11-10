# First routing review artifacts

Pinned native board: `dafa93e938c3cc8b44d3bd1bc96028d27d44f320e9012c124e3212df88432e70`. This is an incomplete first pass with 48 unconnected reports, nine missing footprints and five existing geometric DRC findings. Read `../../../docs/design/first_routing_pass_review.md` for scope and decisions.

- `front-components.png`: native top view, panel/battery/socket models hidden for inspection.
- `front-with-display.png` and `rear-with-battery.png`: native review envelopes visible.
- `raised-display-perspective.png`: angled assembly review.
- `routing-overview.png`: front, mirrored rear and two inner ground layers.
- `routing-closeups.png`: native copper close-ups. Corresponding SVGs retain zoomable geometry.
- `drc.json`, `remaining-connections.json`, `routing-delta-check.json` and the other JSON files record the validation scope and exact source hashes.

Generate layer views with `python3 tools/render_first_routing_review.py BOARD OUTPUT` from the repository root. `KICAD_CLI` and `CHROME_EXECUTABLE` can override the installed executables. For 3D views, make isolated rendering copies with `tools/create_compact_pcb_preview.py` under the native KiCad wrapper, then use `kicad-cli pcb render`. The perspective uses `--rotate '325,0,20'`. Rendering copies change review-model visibility only and are not fabrication sources.

The manifest pins source and artifact bytes. The live CAD, not the rendering derivative, is authoritative. No manufacturing outputs or parts order were generated.
