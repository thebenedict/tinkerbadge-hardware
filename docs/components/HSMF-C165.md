# HSMF-C165 component facts

## Source and physical package

[HSMF-C165_AV02-0584EN.pdf](https://docs.broadcom.com/doc/AV02-0584EN), AV02-0584EN, 13 May2022. [Source](https://docs.broadcom.com/doc/AV02-0584EN). URL, retrieval route and SHA256 are in `HSMF-C165.source.json` under datasheets.

Four-terminal0603 imperial,1.6×0.8×0.5mm. Two independent LED dies. No internally common pin and no EP.

Inspected p2 actual package/polarity/internal-circuit pixels, peripheral_views/HSMF-page2.png. Cathodes are on marked side.

| Physical pin | Name | Function | PDF page |
|---|---|---|---|
| 1 | A_GREEN | Yellow-green die anode | 2 |
| 2 | A_RED | Red die anode | 2 |
| 3 | K_GREEN | Yellow-green die cathode | 2 |
| 4 | K_RED | Red die cathode | 2 |

## Electrical and connection requirements

Each die20mA and52mW absolute maximum at25°C, derate for temperature;5V reverse maximum is not permission for sustained reverse bias. Forward voltage at20mA is1.6–2.4V,1.9V typical (pp3–4). These are not low-current guaranteed brightness values.

D409: pins3/4 GND. GPIO PWR_LED_G through2.2kΩ1% to pin1; PWR_LED_R through2.2kΩ1% to pin2. Each GPIO has100kΩ pulldown. About0.64mA typical at3.3V with1.9V forward drop; verify visible brightness at lower current. Each GPIO high lights its color, both low means dark. No connection to upstream LED rail or raw battery.

MCU reset/Hi-Z and storage default dark. Preserve the specification's distinct charging, external-powered, low-battery and normal-idle indications in firmware. It is a power/status indicator, not a decorative ninth pixel.

## Review state

Extracted 2026-11-09. Electrical source facts and assignments passed [independent review](../design/review_peripherals.md). Connections are maintained in [the peripheral contract](../design/peripherals_contract.json); physical mating, footprints and prototype checks remain separate gates.
