# Reproduce the functional-block annotation

## Portable generator

Run from the hardware repository root with Python 3.10 or newer. The retained generator is `exports/pcb-review/annotate_functional_blocks_optical.py`, SHA256 `cd897f166d0c2eae1d204b7aa1887535cffc9d04b4794faeb9d6313de25ff9d0`.

Keep the file at that path because it resolves the hardware root relative to itself. The sibling web repository's `scripts/` directory is the default read-only helper source. Set `TINKERBADGE_WEB_SCRIPTS` to another checkout's scripts directory when needed.

## Invocation

Set `CHROME_EXECUTABLE` to your installed Chromium-compatible executable, or pass its path with `--browser`. If neither is set, the generator checks common executable names on PATH and the standard macOS Chrome location. It does not install or download a browser.

```sh
python3 exports/pcb-review/annotate_functional_blocks_optical.py \
  --board tinkerbadge.kicad_pcb \
  --render exports/pcb-review/optical-space/front-components-transparent.png \
  --sha256 8fa1ac386d237944d634cd7b5be0ca3ad3188f87965fbee94499eb1a51859399 \
  --output .build/annotation-check/functional-blocks \
  --rasterize
```

Use a separate output basename for validation so the delivered files are preserved. Omit `--rasterize` to generate the editable SVG and provenance without launching Chromium. The tool does not render KiCad, change CAD or modify the unannotated PNG.

## Validation and dependencies

The portability check used Python 3.13.0 and Google Chrome for Testing 145.0.7632.6, headless at 2460 × 1630 and 1:1 scale. Its PNG and SVG hashes are byte-identical to the delivered annotation. The input native image is 1768 × 1376, SHA256 `09bba58766619f0b6fa9f4902ceed3653ad2917450b0704af521282cd9e5a4e0`.

Read-only helpers are `../tinkerbadge-web/scripts/kicad_source.py` and `render_feature_views.py`; the latter also imports `export_assets.py`. The source contracts, helper hashes, actual native input, calibration anchors, native-group membership and output hashes are recorded in `functional-blocks.json` using repository-relative paths.

The native PNG is embedded byte-for-byte at an integer-pixel translation. Six-hole calibration has maximum residual 0.123249 px. Fourteen readable external callouts and dashed amber reserves form a separate vector layer. The NFC label records the selected rear-copper coil plan while preserving front/inner clearance; no coil copper is implemented or tuned.

The original local-path provenance and generator remain in a historical audit checkpoint excluded from public distribution. The portability update changed execution configuration and evidence paths only, not native CAD, SVG geometry, image pixels or the delivered Library image.
