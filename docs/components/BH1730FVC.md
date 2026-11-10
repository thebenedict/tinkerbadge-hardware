# BH1730FVC component facts

## Source

[Manufacturer PDF](https://fscdn.rohm.com/en/products/databook/datasheet/ic/sensor/light/bh1730fvc-e.pdf), Rev.001, 8 June 2016. URL and SHA256: [source record](../datasheets/BH1730FVC.source.json). Pin diagram p2 and package p19 visually inspected. Manufacturer-targeted errata search found no separate errata sheet; this is not proof none exists.

Supplementary mechanical source: [ROHM WSOF6 package information Rev.005](https://fscdn.rohm.com/en/techdata_basic/ic/package/Jisso_WSOF6-1-2_Rev005s_TR%28MSL3%29.pdf), TSZ02201-WSOF6-1-2, 31 January 2020, p7 actual land-pattern diagram inspected 2026-11-09. [URL and SHA256](../datasheets/WSOF6_ROHM_Rev005.source.json). Six 0.55 x 0.25 mm lands, 0.50 mm row pitch, 2.20 mm inner column gap; no center land or paste because ROHM does not guarantee center-pad connection quality. Exact geometry and generated readback are in [the peripheral footprint review](../design/pcb_peripheral_footprint_review.md).

## Electrical and sequencing facts

- Supply VCC 2.4–3.6 V, DVI 1.65 V–VCC (p3). At selected 3.3 V both pins may share the MCU core rail, provided its entire envelope stays within 2.4–3.6 V.
- Absolute maximum VCC 4.5 V; INT/SDA/DVI/SCL -0.3–7 V; SDA/INT sink 7 mA (p3). Absolute limits do not establish powered-off bus compatibility.
- At DVI >=1.8 V: VIH >=0.7 DVI; VIL <=0.3 DVI. VOL <=0.4 V at 3 mA; I2C <=400 kHz (p4). Fixed 7-bit address 0x29 (p1).
- Measuring current 150 µA typical/200 µA max; power-down 0.85 µA typical/1.5 µA max at stated 3.0 V, 25°C conditions (p4). These are not guaranteed storage totals at final rail extremes.
- All registers reset on power-up. Wait >2 ms after VCC rises above 2.4 V from below 0.4 V; power-off interval >1 ms below 0.4 V (p14). CONTROL resets to power-down; explicitly set power-down after measurements. INT is open drain and initially high impedance (p13).
- No independently specified Ioff guarantee found for live bus with supplies absent. Keep VCC and DVI powered with the MCU bus; do not power-gate just VCC while DVI remains high because VDVI <=VCC applies.

## Project recommendation U501 / SEN-01

Pins 1 and 5 to core rail, each with local 100 nF ceramic to GND as reference p1. Pin3 GND; pin4 I2C_SDA; pin6 I2C_SCL. Shared bus pull-ups to core rail. Pin2 explicit NC because periodic measurement polling suffices. If used later, add pull-up and clear interrupt promptly to avoid added current (p13).

Use duty-cycled one-time measurements and power-down in storage. Place optical aperture away from RGB LEDs, following p14 optical detection region; calibrate visible/IR lux algorithm through final enclosure with LEDs on/off. Review WSOF6 mechanical underside independently before footprint finalization; no assumed solderable EP net. Bench tests: startup at slow/fast ramps, all rail extremes, ambient/self-light discrimination, and power-down current.

## Physical pins

Generated from [BH1730FVC.pins.json](BH1730FVC.pins.json).

| Physical pin | Manufacturer name | Function | Source page |
|---|---|---|---|
| 1 | VCC | Power supply | 2 |
| 2 | INT | Open-drain interrupt; unused may float or connect GND | 2 |
| 3 | GND | Ground | 2 |
| 4 | SDA | I2C data | 2 |
| 5 | DVI | I2C interface supply | 2 |
| 6 | SCL | I2C clock | 2 |

## Review state

Extracted 2026-11-09. Independent source/assignment review required before CAD. Project recommendations below are not the authoritative pinout.

Rail decision update: the first prototype uses one nominal 3.3 V supply shared by MCU, sensors, NFC and LEDs. Keep this part within its specified supply and logic limits; the separately documented below-minimum LED experiment does not relax sensor limits.
