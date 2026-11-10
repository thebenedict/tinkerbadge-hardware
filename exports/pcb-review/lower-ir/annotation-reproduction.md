# Reproduce the lower-IR annotation

Updated 10 November 2026. The canonical board is tinkerbadge.kicad_pcb, SHA-256 a7ac2778f423c3847b9a3a6200f00446d6a960bbee242b6ef8da7aff5ed24b84.

## Inputs and tools

Run from the hardware repository root. Keep annotate_functional_blocks_lower_ir.py at its recorded path below; it locates that root from its own directory.

- Python 3.10 or later. The recorded run used Python 3.13.0.
- The sibling tinkerbadge-web/scripts directory, including its imported helper modules. Set TINKERBADGE_WEB_SCRIPTS to your own scripts directory if the checkouts are elsewhere. The generator records helper paths relative to the hardware root.
- A Chromium-compatible browser. Set CHROME_EXECUTABLE to your own executable, or pass --browser. The generator also searches standard browser commands and the normal macOS Chrome location. No personal cache path is required.
- The existing native front-components-transparent.png, 1768 × 1376 pixels. Its SHA-256 is 99230b74ccd18e9f15c34a6152786001be3f11443ed2f5786e905d174e6937f2.
- The pinned board and the three component contracts recorded in functional-blocks.json.

The approved PNG was rasterized with Google Chrome for Testing 145.0.7632.6 at 1×. Browser version and installed Helvetica/Arial font resolution can affect raster bytes.

## Generate a separate check output

Configure CHROME_EXECUTABLE for your machine, then run:

    python3 exports/pcb-review/lower-ir/annotate_functional_blocks_lower_ir.py \
      --board tinkerbadge.kicad_pcb \
      --render exports/pcb-review/lower-ir/front-components-transparent.png \
      --sha256 a7ac2778f423c3847b9a3a6200f00446d6a960bbee242b6ef8da7aff5ed24b84 \
      --output .build/lower-ir-annotation-check/functional-blocks \
      --rasterize

Omit --rasterize to generate only SVG and JSON. The command writes to a separate scratch directory and does not overwrite the approved files. It reads the board and native render without changing them.

## Validation and provenance

The SVG embeds the native PNG bytes unchanged at 1:1 scale, translated by (321, 144) pixels. Six native mounting holes establish the transform; the largest residual is 0.12325 pixels. The generator checks board SHA-256, asymmetric outline orientation, all 14 blocks, five native group memberships, optical source-contract membership, and the IR leader against 176 front courtyards. Ambient light and infrared remain separate. The NFC labels retain the planned rear copper coil and front/inner-layer keepout; no coil geometry is drawn.

The generation-time reproduction-check PNG, SVG and JSON were byte-identical on 10 November 2026. After the candidate was applied, the canonical JSON board path was changed from .build/lower-ir-one-sided/tinkerbadge.kicad_pcb to tinkerbadge.kicad_pcb. Both paths identified the same board bytes. The archived check JSON retains the former path; all its other content still matches.

functional-blocks.json preserves the helper hashes actually used to generate the approved artifact. The current render_feature_views.py differs from that helper only in its unused BOARD_SHA constant. Its generation hash is ddbb7f3c88020b0df25f718f2f40c3d09e129d577542b0452147598cfee78a16; the later observed hash is fef2d7f3e16f33aa2e189789a98d25368893898e9ad3890e6f180a5cdf0da590. No current-tool regeneration was performed during the documentation-only handoff. A new run records its actual helper hash, so its JSON will differ accordingly.

The approved outputs remain:

- PNG: 177f9ee372a9df21abb63f4b37f2b3ac7da904656174e82207198ce367c991bf
- SVG: d2a87b7d7b6c3b74c5e8ee60bdea1d95dbe3b1a19cd4a0170f5b74a7bffc8077
- Lower-IR generator: 46d202beedd81676561679e5b8feb4c39be88b68d3c577d0f42c5dce3bc4581b

Compare scratch outputs and inspect the image before replacing an approved artifact. annotation-validation.json records the completed visual and pixel checks; these annotation checks do not establish routing or fabrication readiness.
