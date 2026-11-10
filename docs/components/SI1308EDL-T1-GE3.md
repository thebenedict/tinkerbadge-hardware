# SI1308EDL-T1-GE3

Selected replacement for the BOM’s reference-only -BE3 suffix. Vishay PTN-SIL-029-2026 page 3 row 1 explicitly recommends -GE3. Datasheet 63399 Rev C page 1 specifies that ordering suffix and verifies the same device’s G/S/D map, 30 V drain rating, ±12 V gate rating, 0.185 Ω maximum at VGS = 2.5 V, and 1.4 nC typical gate charge. Procurement and prototype switching validation remain open.

See [display circuit decisions](../design/display.md) for voltage margins, support values, boot/off-state behavior, and release gates.

## Physical pin facts

Source: [SI1308EDL.pdf](https://www.vishay.com/docs/63399/si1308edl.pdf). 63399; S14-1997 Rev C; 2014-10-06; 11 PDF pages. Machine-readable source: [SI1308EDL-T1-GE3.pins.json](SI1308EDL-T1-GE3.pins.json).

| Pin | Manufacturer function | Type | PDF page |
|---|---|---|---|
| 1 | G: Gate | input | 1 |
| 2 | S: Source | passive | 1 |
| 3 | D: Drain | passive | 1 |

Status: source facts and electrical assignments independently reviewed; see [display review](../design/review_display.md). Physical and prototype gates are listed in [library acceptance](display_library_acceptance.md).
