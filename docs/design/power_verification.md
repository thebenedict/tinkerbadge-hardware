# Power capture verification

Temporary review artifacts below are identified by filename only; these intermediate files are not distributed. Published source outputs and repeatable checks are linked from the [current verification record](verification.md).

9 November 2026. KiCad 10.0.8. Electrical development capture only.

- Source and assignment review: [review_power.md](review_power.md), including the two-wire, USB shell and [single-3.3 V amendment](review_power_single_3v3.md).
- Independent exported-netlist checker: PASS, 60 components, 195 endpoints, 14 intentional NC endpoints, no missing or extra endpoints.
- Konnect checks: zero unconnected pins, zero floating wire endpoints, zero merged named nets and zero orphan items.
- Root ERC snapshot: errors=0, warnings=1; findings naming power references=1. The current warning is the intentional U502 SDO/SA0 I2C address strap to +3V3; review its original-source justification in the peripheral records. No ERC result establishes prototype or manufacturing readiness.
- Independent capture status: PASS independent electrical, properties and visual capture; matching sheet and contract hashes.
- Disposable symbols were queried and rendered, then actual sheet pins were queried. The final render was inspected and field/ground-stub collisions corrected. See the matching-hash [independent capture review](power_capture_review.md).

## Pinned evidence

- Contract: `20fb7654f96922426fbc6a5b73ef70995b394aab9696421ed483bcbc73615563`
- Power sheet: `377d3afaa8323e6f61d6cef0f8e670254b959091fdc766e32c5c063dad6d121f`
- Power symbol library: `b486d4bd338bc0ad1079db7796dc91832527bd2b5ba9e774a866476a2127228f`
- Exported power netlist: `50fff81ca965032effc1873117facb7b481d832ebbb8d1944f844718fced5edf`

Machine-readable results: [power_verification.json](power_verification.json). Preview: `power_final_reviewed.png`. Native writes were performed only by Konnect; orchestration/results are under `tools/` and the temporary working directory. Successful mutation stages are not idempotent and must not be rerun blindly.

## Build and release gates

Charging is hard-disabled in hardware by fitted R120. J104 remains DNP; fitting a thermistor does not enable or qualify charging. J102 is a logical two-wire interface, not a vendor connector pinout. All power footprints are deliberately unassigned. The accepted single-3.3 V LED prototype exception, exact stock pack, connector polarity/current rating, autonomous temperature qualification, inductor and capacitor MPNs, startup/current-mode transitions, rail/transient limits, ADC brownout behavior, storage draw and thermal performance still require selection or testing. No board layout, manufacturing or production readiness is established.
