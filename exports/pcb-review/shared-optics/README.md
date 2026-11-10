# Shared passive optical window placement

Native board SHA256 `ddf824f2a59bc82568bbb03bcb3f89959f2ee12638b380790207739273c1844d`, KiCad 10.0.8, 10 November 2026.

Four poses changed: U501 (143.5,170.5),90°; C501 (143.5,174.75),270°; C502 (143.5,166.25),90°; R504 (150.75,172),180°. The lower ALS and IR receiver can share a visible/940 nm-transmitting aperture; isolate the IR emitter in a separate optical segment and keep RGB diffuser light out. This is a PCB placement, not a finished enclosure.

Independent native checks preserve all complete footprint, net, model, group, outline and keepout records after inverse poses. No new courtyard, copper-edge or keepout violation was found. Existing four USB hole errors, one silk-edge warning, 390 unconnected items and nine missing footprints remain.

The move improves aperture grouping and the ALS view past the display. It does not increase distance from visible LEDs; optical barriers and integration-time-aware self-light tests are required. All four native views were inspected. Detailed evidence is in `../../../docs/design/shared_passive_optics_review.md`. No routing or publication is authorized by this checkpoint.
