# TCA9534PWR component facts

## Source and physical package

[TCA9534.pdf](https://www.ti.com/lit/ds/symlink/tca9534.pdf), SCPS197D,September2014 revised October2017; packagePW0016A drawing4220204/B December2023. [Source](https://www.ti.com/lit/ds/symlink/tca9534.pdf). URL, retrieval route and SHA256 are in `TCA9534PWR.source.json` under datasheets.

PW TSSOP16,5.0×4.4mm body,0.65mm pitch,1.2mm max height. 16 pins, no EP. Non-A TCA9534 address base0x20; TCA9534A is a different address variant.

Inspected actual p4 top-view pin table and p39 TSSOP package drawing, peripheral_views/TCA9534-page4.png/TCA9534-page39.png.

| Physical pin | Name | Function | PDF page |
|---|---|---|---|
| 1 | A0 | Address strap | 4 |
| 2 | A1 | Address strap | 4 |
| 3 | A2 | Address strap | 4 |
| 4 | P0 | GPIO | 4 |
| 5 | P1 | GPIO | 4 |
| 6 | P2 | GPIO | 4 |
| 7 | P3 | GPIO | 4 |
| 8 | GND | Ground | 4 |
| 9 | P4 | GPIO | 4 |
| 10 | P5 | GPIO | 4 |
| 11 | P6 | GPIO | 4 |
| 12 | P7 | GPIO | 4 |
| 13 | INT_N | Open-drain interrupt | 4 |
| 14 | SCL | I2C bus | 4 |
| 15 | SDA | I2C bus | 4 |
| 16 | VCC | Supply | 4 |

## Electrical and initialization

Supply1.65–5.5V. SCL/SDA VIH≥0.7VCC,VIL≤0.3VCC; P-port low threshold≤0.2VCC at3–5.5V. Inputs are5V tolerant but SCL/SDA must not exceed VCC in operation or leakage rises (p5footnote). Keep live3.3V with onboardI2C. Standby current0.9µA typical at3.6V; maximum depends input levels (up to4µA listed). No floating inputs.

A0/A1/A2 hardGND gives7-bit0x20. Local100nF+1µF decoupling. P0 CHARGER_CHG_N input; P1 CHARGER_PGOOD_N input; P2 ACC_EN output; P3 ACC_FAULT_N input. P4–P7 unused inputs each100kΩ pulldown; INT explicit NC and status polled, avoiding extra MCU pin. Charger status pull-ups belong to power sheet; FAULT pull-up belongs to TPS2553 support.

Power-up config is all inputs with output latch0xFF. Firmware MUST write safe output latch0x00 before configuring P2 as output (config register0xFB). This avoids an enable pulse. Then set P2 when accessory power is wanted. External ACC_EN100kΩ pulldown holds switch off until configured. Do not write1 to unused input pins and later change their direction accidentally.

No hardware reset pin. Power-on reset requires a real supply cycle; p27 recommended rise0.1–2000ms, fall1–2000ms, re-ramp interval≥1µs at25°C. Partial brownouts may not reset state. Poll/reinitialize registers after reset and manage retained expander outputs when MCU alone resets. Its always-on rail is intentional and avoids I2C backfeed.

## Review state

Extracted 2026-11-09. Electrical source facts and assignments passed [independent review](../design/review_peripherals.md). Connections are maintained in [the peripheral contract](../design/peripherals_contract.json); physical mating, footprints and prototype checks remain separate gates.
