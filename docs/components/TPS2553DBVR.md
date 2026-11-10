# TPS2553DBVR component facts

## Source and physical package

[TPS2553.pdf](https://www.ti.com/lit/ds/symlink/tps2553.pdf), SLVS841G, November2008 revised October2026. [Source](https://www.ti.com/lit/ds/symlink/tps2553.pdf). URL, retrieval route and SHA256 are in `TPS2553DBVR.source.json` under datasheets.

DBV SOT-23-6, active-high EN, nonlatching retry version. DBV has six terminals, no EP. DRV/WSON pin order differs.

Inspected p4 DBV top-view/pin table pixels, peripheral_views/TPS2553-page4.png.

| Physical pin | Name | Function | PDF page |
|---|---|---|---|
| 1 | IN | Input supply | 4 |
| 2 | GND | Ground | 4 |
| 3 | EN | Active-high enable | 4 |
| 4 | FAULT_N | Open-drain overcurrent/thermal/reverse fault | 4 |
| 5 | ILIM | Current-limit programming | 4 |
| 6 | OUT | Current-limited switched supply | 4 |

## Electrical and project values

Operating IN2.5–6.5V, absolute all listed pins−0.3…7V. EN low≤0.66V, high≥1.1V. Typical85mΩ switch at25°C; use full-temperature maximum from source in the power budget. Open-drain FAULT requires a pull-up. U505 feeds both accessory ports and IR RX from live3.3V to ACC_3V3.

Use RILIM210kΩ1% to GND. Datasheet electrical table gives110/130/150mA minimum/typical/maximum at210kΩ; allow resistor tolerance on top. Publish50mA normal combined connector load budget including receiver and pull-ups, calculated210kΩ±1% equation bounds109.18–152.25mA; reserve at least155mA upstream fault capacity. This is one shared fault domain, not two independent100mA outputs. Default EN100kΩ to GND; expander drives ACC_EN. FAULT100kΩ to live3.3V. Local input1µF+10µF and output10µF,10V X7R; maintain datasheet minimum0.1µF input. Output100kΩ bleed is a project choice, nominal1s RC before accessory capacitance.

## Sequencing and reverse current

Disabled supply current1µA maximum at source condition. Reverse-voltage comparator trips at approximately95–190mV OUT above IN, response3–7ms, so this is not instantaneous ideal-diode isolation. Listed reverse leakage1µA maximum is a25°C test; qualify full environment. Non-QOD part does not actively discharge output.

Before disabling: stop externalI2C, release SDA/SCL with MCU pulls disabled, set SAO GPIO low or input/no pulls, set IR RX input/no pulls, then deassert ACC_EN. Before use: enable, allow rail/filter settling, then configure outputs and communicate. Wait for discharge before inserting/removing accessories; initial conservative delay≥5s does not guarantee discharge with arbitrary accessory capacitors. No self-powered accessories and no5V signal levels. Do not claim hot-plug qualification. FAULT is polled during powered operation and faults disable the domain; current limiting protects while firmware is asleep or delayed.

## Review state

Extracted 2026-11-09. Electrical source facts and assignments passed [independent review](../design/review_peripherals.md). Connections are maintained in [the peripheral contract](../design/peripherals_contract.json); physical mating, footprints and prototype checks remain separate gates.
