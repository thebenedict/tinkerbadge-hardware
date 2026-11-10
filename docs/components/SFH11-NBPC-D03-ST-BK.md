# SFH11-NBPC-D03-ST-BK component facts

## Source and physical package

[SFH11-NBPC-D03-ST-BK_official.pdf](https://drawings-pdf.s3.amazonaws.com/11160.pdf), Sullins drawing11160 RevJ,12 May2015. [Source](https://drawings-pdf.s3.amazonaws.com/11160.pdf). URL, retrieval route and SHA256 are in `SFH11-NBPC-D03-ST-BK.source.json` under datasheets.

Keyed female2×3 straight through-hole socket,2.54mm row/contact pitch. Six isolated contacts. Factory drawing has no pad numbers; project numbers follow author SAOv2 host convention. No EP.

Inspected exact manufacturer drawing from its product-page link and SAO author top-view pin graphic (peripheral_views/SFH11-NBPC-D03-ST-BK-page1.png and SAOv2-host.png). Keyed housing orientation must be checked against actual mating add-on before footprint release.

| Physical pin | Name | Function | PDF page |
|---|---|---|---|
| 1 | CONTACT_1 | Project SAO contact, upper-left top/mating view | 1 |
| 2 | CONTACT_2 | Project SAO contact, lower-left top/mating view | 1 |
| 3 | CONTACT_3 | Project SAO contact, upper-middle | 1 |
| 4 | CONTACT_4 | Project SAO contact, lower-middle | 1 |
| 5 | CONTACT_5 | Project SAO contact, upper-right | 1 |
| 6 | CONTACT_6 | Project SAO contact, lower-right | 1 |

## Mechanical and electrical facts

D03 means three positions per row, six contacts. Straight tail3.2mm, nominal body length12.70mm, housing width6mm plus key, height8.5mm; recommended hole1.02mm. Contact rated3A is not badge power allowance. Black keyed female host; mate with correctly oriented male add-on. Source product page: https://www.sullinscorp.com/product/?pn=SFH11-NBPC-D03-ST-BK .

## SAO assignment

Author specification: https://hackaday.io/project/175182-simple-add-ons-sao . Top/mating view numbered odd1,3,5 across upper row and even2,4,6 across lower row:1=3.3V,2=GND,3=SDA,4=SCL,5=GPIO1,6=GPIO2. J502 uses ACC_3V3/GND/EXT_SDA/EXT_SCL/SAO_GPIO1/SAO_GPIO2. Socket key/cavity cannot be inferred from generic2×3 symbol or a rear-side add-on drawing; validate mirrored mating geometry against source before layout.

Share50mA normal total accessory budget with Qwiic and IR RX. No5V or self-powered accessories; power down and release all signal pins before insertion. Keep adequate mechanical clearance from glass, loop antenna and enclosure. Mixed through-hole assembly and retention need manufacturing review.

## Review state

Extracted 2026-11-09. Electrical source facts and assignments passed [independent review](../design/review_peripherals.md). Connections are maintained in [the peripheral contract](../design/peripherals_contract.json); physical mating, footprints and prototype checks remain separate gates.
