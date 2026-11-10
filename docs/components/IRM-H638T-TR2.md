# IRM-H638T/TR2 component facts

## Source and physical package

[IRM-H638T-TR2.pdf](https://www.everlighteurope.com/custom/files/datasheets/DMO-0000008.pdf), DMO-0000008 Rev3,1 January2025; approval stamp14 January2025. [Source](https://www.everlighteurope.com/custom/files/datasheets/DMO-0000008.pdf). URL, retrieval route and SHA256 are in `IRM-H638T-TR2.source.json` under datasheets.

Four-terminal SMD demodulating IR receiver, H6XXT package. No separate EP. Both ground pins connect. Do not substitute a three-pin remote receiver footprint.

Inspected actual p1 pin-labelled photo, p2 application circuit and p6 package drawing, peripheral_views/IRM-page1.png, IRM-page2.png, IRM-page6.png.

| Physical pin | Name | Function | PDF page |
|---|---|---|---|
| 1 | GND | Ground | 1 |
| 2 | GND | Ground | 1 |
| 3 | OUT | Active-low demodulated output with internal pull-up | 1 |
| 4 | VCC | Supply | 1 |

## Electrical and support requirements

Operating2.7–5.5V; absolute supply6V; operating−20…80°C. Supply current0.4mA typical/0.7mA maximum with no signal. Output high≥VCC−0.4V at source current≤1µA; low≤0.5V at sink≤2mA. Match input loading and thresholds accordingly.

U504 pin4 receives IR_RX_3V3 from ACC_3V3 through100Ω, with4.7µF10V and100nF local to pins4/1/2. Source p2 requires47–220Ω and≥2.2µF close to pins. Pin3 directly reaches IR_RX_N MCU input, no pull-up to always-on rail. Internal pull-up avoids a powered-off backfeed path; MCU internal pull-up must be disabled before power gating. At3.3V and0.7mA the100Ω drop is0.07V; source rail tolerance must still leave≥2.7V. Allow≥10ms after enable as an initial settling delay, then validate startup false pulses; no guaranteed startup delay was located.

## Protocol conditions

38kHz matched carrier. Manufacturer minimum burst12cycles, minimum gap16cycles (p1), plus AGC/long-burst limitations in source test section. Use short bounded bursts, one-third carrier duty, collision-aware packet protocol and CRC. Raw amplitude and range are not measured. Test direct sunlight, LED interference, receiver saturation and simultaneous nearby transmitters. Receiver is off in storage with accessory domain.

## Review state

Extracted 2026-11-09. Electrical source facts and assignments passed [independent review](../design/review_peripherals.md). Connections are maintained in [the peripheral contract](../design/peripherals_contract.json); physical mating, footprints and prototype checks remain separate gates.
