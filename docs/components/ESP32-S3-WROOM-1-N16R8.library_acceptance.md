# MCU library acceptance

Temporary review artifacts below are identified by filename only; these intermediate files are not distributed. Published source outputs and repeatable checks are linked from the [current verification record](../design/verification.md).

2026-11-09. Exact Espressif ESP32-S3-WROOM-1-N16R8; module source v1.8, URL and source hash in review_mcu.md. Standard symbol and footprint: RF_Module:ESP32-S3-WROOM-1. **Accepted for schematic association**, not PCB placement/manufacture.

Queried symbol and footprint, placed disposable instances through Konnect MCP in `mcu_symbolcheck`, read both back, rendered symbol PNG and footprint SVG/PNG, and inspected actual images against original top/bottom drawings pp10/42. Antenna is up; pin1 top-left, down left to14, along bottom15–26, up right27–40. No mirror or numbering reversal. USB_D−/USB_D+ are explicit functional aliases for manufacturer IO19/IO20; symbol GND41 aliases manufacturer EPAD41, electrically ground. Hidden co-located GND40/41 pins remain in the41-pin symbol and exported netlist.

Counts:41 logical electrical pads/functions;40 perimeter pads each once, plus13 physical pad41 objects (one3.9mm square copper region and12 grounded thermal vias,0.6mm annulus/0.2mm drill). Nine unnumbered0.9mm square F.Paste-only apertures are not electrical leads. Source EPAD's nine contact regions share ground; footprint uses a continuous ground land with segmented paste. No mounting holes. Peripheral pads1.5x0.9mm on1.27mm pitch. Body18x25.5mm and offset EPAD match the source view. Exact paste/via process and antenna clearance are PCB/manufacturing gates.

MCP board readback source was saved file; IPC was unreachable and this new disposable board had no editor lock. No main board was touched. Logs: `mcu_disposable_results.jsonl`; library queries `mcu_query_results.jsonl`. Source placement fields rendered with a value/VDD overlap in the disposable default, so main schematic field positions must be corrected and freshly inspected.

| Datasheet lead | Function | Symbol number/name/type | Footprint pad | Local X,Y mm | View/direction | Source |
|---|---|---|---|---|---|---|
|1|GND|1 / GND / power_in|1|-8.750, -5.260|top/component, antenna up|module pp10–12,42|
|2|3V3|2 / 3V3 / power_in|2|-8.750, -3.990|top/component, antenna up|module pp10–12,42|
|3|EN|3 / EN / input|3|-8.750, -2.720|top/component, antenna up|module pp10–12,42|
|4|IO4|4 / IO4 / bidirectional|4|-8.750, -1.450|top/component, antenna up|module pp10–12,42|
|5|IO5|5 / IO5 / bidirectional|5|-8.750, -0.180|top/component, antenna up|module pp10–12,42|
|6|IO6|6 / IO6 / bidirectional|6|-8.750, 1.090|top/component, antenna up|module pp10–12,42|
|7|IO7|7 / IO7 / bidirectional|7|-8.750, 2.360|top/component, antenna up|module pp10–12,42|
|8|IO15|8 / IO15 / bidirectional|8|-8.750, 3.630|top/component, antenna up|module pp10–12,42|
|9|IO16|9 / IO16 / bidirectional|9|-8.750, 4.900|top/component, antenna up|module pp10–12,42|
|10|IO17|10 / IO17 / bidirectional|10|-8.750, 6.170|top/component, antenna up|module pp10–12,42|
|11|IO18|11 / IO18 / bidirectional|11|-8.750, 7.440|top/component, antenna up|module pp10–12,42|
|12|IO8|12 / IO8 / bidirectional|12|-8.750, 8.710|top/component, antenna up|module pp10–12,42|
|13|IO19|13 / USB_D- / bidirectional|13|-8.750, 9.980|top/component, antenna up|module pp10–12,42|
|14|IO20|14 / USB_D+ / bidirectional|14|-8.750, 11.250|top/component, antenna up|module pp10–12,42|
|15|IO3|15 / IO3 / bidirectional|15|-6.985, 12.500|top/component, antenna up|module pp10–12,42|
|16|IO46|16 / IO46 / bidirectional|16|-5.715, 12.500|top/component, antenna up|module pp10–12,42|
|17|IO9|17 / IO9 / bidirectional|17|-4.445, 12.500|top/component, antenna up|module pp10–12,42|
|18|IO10|18 / IO10 / bidirectional|18|-3.175, 12.500|top/component, antenna up|module pp10–12,42|
|19|IO11|19 / IO11 / bidirectional|19|-1.905, 12.500|top/component, antenna up|module pp10–12,42|
|20|IO12|20 / IO12 / bidirectional|20|-0.635, 12.500|top/component, antenna up|module pp10–12,42|
|21|IO13|21 / IO13 / bidirectional|21|0.635, 12.500|top/component, antenna up|module pp10–12,42|
|22|IO14|22 / IO14 / bidirectional|22|1.905, 12.500|top/component, antenna up|module pp10–12,42|
|23|IO21|23 / IO21 / bidirectional|23|3.175, 12.500|top/component, antenna up|module pp10–12,42|
|24|IO47|24 / IO47 / bidirectional|24|4.445, 12.500|top/component, antenna up|module pp10–12,42|
|25|IO48|25 / IO48 / bidirectional|25|5.715, 12.500|top/component, antenna up|module pp10–12,42|
|26|IO45|26 / IO45 / bidirectional|26|6.985, 12.500|top/component, antenna up|module pp10–12,42|
|27|IO0|27 / IO0 / bidirectional|27|8.750, 11.250|top/component, antenna up|module pp10–12,42|
|28|IO35|28 / IO35 / bidirectional|28|8.750, 9.980|top/component, antenna up|module pp10–12,42|
|29|IO36|29 / IO36 / bidirectional|29|8.750, 8.710|top/component, antenna up|module pp10–12,42|
|30|IO37|30 / IO37 / bidirectional|30|8.750, 7.440|top/component, antenna up|module pp10–12,42|
|31|IO38|31 / IO38 / bidirectional|31|8.750, 6.170|top/component, antenna up|module pp10–12,42|
|32|IO39|32 / IO39 / bidirectional|32|8.750, 4.900|top/component, antenna up|module pp10–12,42|
|33|IO40|33 / IO40 / bidirectional|33|8.750, 3.630|top/component, antenna up|module pp10–12,42|
|34|IO41|34 / IO41 / bidirectional|34|8.750, 2.360|top/component, antenna up|module pp10–12,42|
|35|IO42|35 / IO42 / bidirectional|35|8.750, 1.090|top/component, antenna up|module pp10–12,42|
|36|RXD0|36 / RXD0 / bidirectional|36|8.750, -0.180|top/component, antenna up|module pp10–12,42|
|37|TXD0|37 / TXD0 / bidirectional|37|8.750, -1.450|top/component, antenna up|module pp10–12,42|
|38|IO2|38 / IO2 / bidirectional|38|8.750, -2.720|top/component, antenna up|module pp10–12,42|
|39|IO1|39 / IO1 / bidirectional|39|8.750, -3.990|top/component, antenna up|module pp10–12,42|
|40|GND|40 / GND / passive|40|8.750, -5.260|top/component, antenna up|module pp10–12,42|
|41|EPAD|41 / GND / passive|41|-2.900, 1.760|top/component, antenna up|module pp10–12,42|
|41|EPAD|41 / GND / passive|41|-2.900, 3.160|top/component, antenna up|module pp10–12,42|
|41|EPAD|41 / GND / passive|41|-2.200, 1.060|top/component, antenna up|module pp10–12,42|
|41|EPAD|41 / GND / passive|41|-2.200, 2.460|top/component, antenna up|module pp10–12,42|
|41|EPAD|41 / GND / passive|41|-2.200, 3.860|top/component, antenna up|module pp10–12,42|
|41|EPAD|41 / GND / passive|41|-1.500, 1.760|top/component, antenna up|module pp10–12,42|
|41|EPAD|41 / GND / passive|41|-1.500, 2.460|top/component, antenna up|module pp10–12,42|
|41|EPAD|41 / GND / passive|41|-1.500, 3.160|top/component, antenna up|module pp10–12,42|
|41|EPAD|41 / GND / passive|41|-0.800, 1.060|top/component, antenna up|module pp10–12,42|
|41|EPAD|41 / GND / passive|41|-0.800, 2.460|top/component, antenna up|module pp10–12,42|
|41|EPAD|41 / GND / passive|41|-0.800, 3.860|top/component, antenna up|module pp10–12,42|
|41|EPAD|41 / GND / passive|41|-0.100, 1.760|top/component, antenna up|module pp10–12,42|
|41|EPAD|41 / GND / passive|41|-0.100, 3.160|top/component, antenna up|module pp10–12,42|
