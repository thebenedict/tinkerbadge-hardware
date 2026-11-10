# NT3H2111W0FHKH component facts

## Sources

[Datasheet source record](NT3H2111W0FHKH.pins.json), Rev.3.6, 21 July 2023; [errata source record](../datasheets/NT3H2111W0FHKH-errata.source.json), Rev.4.1, 30 October 2025. Exact URLs and SHA256 in corresponding `.source.json` files. H suffix is ordering/packing variant; selected XQFN8 mapping is p8–9, not another family package.

## Electrical and power-state facts

- VCC 1.67–3.6 V (p68 Table42), compatible with core rail only when entire envelope <=3.6 V. I2C VIH >=0.7VCC, VIL <=0.3VCC, VOL <=0.4 V at 3 mA for VCC>2 V. Absolute maximum VCC and FD/SDA/SCL 4.6 V (p67).
- Powered idle current 195 µA typical at 3.3 V; active 400 kHz current max240 µA at 3.3 V (p68). No register-selected ultra-low-power state established. Leaving VCC powered throughout storage is an explicit ~195 µA typical baseline cost, not sensor-like sleep.
- Passive RF EEPROM operation and FD need no VCC. SRAM/mirror/pass-through do need VCC (p20/§8.3, p34 §8.4, p58/§11). Preserve EEPROM NDEF for passive reading and disable SRAM mirroring/pass-through in storage.
- FD is open drain, powered by RF; reference p35 Fig12 permits pull-up to application 1.2–3.6 V with Rpu>2k. Use 10k to live MCU core rail, direct MCU interrupt input for RF transition monitoring.
- Datasheet I2C leakage lacks explicit powered-off Ioff guarantee; absolute max4.6 V alone does not prove safe live bus with VCC absent. Keep NTAG powered on common rail in first schematic. A future switch requires independent bus backfeed validation/isolation and startup glitch management.

## Project recommendation U503 / NFC-01

Pin6 core rail with local 100 nF ceramic decoupling (engineering choice); pin2 GND; pin3 I2C_SCL; pin5 I2C_SDA; pin4 NFC_FD plus 10k pull-up; pin7 VOUT explicit NC, no tie to core rail; pins1/8 dedicated NFC_LA/NFC_LB loop. Center metal not soldered or assigned a net. Default 7-bit I2C address0x55 (stored address byte0xAA, programmable).

Antenna is a separate 13.56 MHz tuned PCB loop. Input capacitance 50pF typical (44–56pF table42). First-order L=1/(4*pi²*f²*C) gives about2.75µH at50pF before PCB/package stray capacitance; this is a starting calculation, not an accepted coil. Provide DNP parallel tuning-cap footprints across LA/LB, keepouts and final loaded tuning with display, battery and enclosure. No energy harvesting load: leave VOUT NC. If harvesting is later used, §8.6 requires total VOUT capacitance typically150nF–220nF maximum, startup load limiting and RF-dependent power budget; re-review before connecting anything.

## Mandatory errata handling

- Rev4.1 pp2–8: RF toggles during I2C can corrupt EEPROM, configuration and address. Use STOP then START separated by >=50µs, not repeated START. Capture both FD edges; guard each frame before/after by20µs plus actual FD latency; abort/retry if transition detected. FD latency depends on circuit; characterize it.
- Check EEPROM_WR_BUSY with5ms timeout; release I2C_LOCKED after access, use session registers for runtime control; verify config and readback. Do not apply irreversible REG_LOCK=0x03 during prototype merely because errata recommends final personalization locking.
- Fast-mode SCL high >950ns and low >1.3µs (p7): verify MCU timing, not merely nominal400kHz clock.
- Power-up pulls SDA/SCL low temporarily. Power simultaneously with other targets or quiesce shared bus and ignore pulses for1ms (p9).
- RF arrival can cause NAK: retry, then VCC reset, then RF reset in that order (pp10–11). Common-rail prototype has no independent VCC reset; report recovery requiring whole-board restart, never disturb another bus device blindly. Address corruption recovery scanning must distinguish other devices on the shared bus before writing address byte.

Prototype gate: verify passive NDEF/FD with MCU asleep and battery absent; no field-induced rise on core rail; confirm read/write recovery under RF toggling; tune coil in assembled enclosure; measure powered-storage current.

## Physical pins

Generated from [NT3H2111W0FHKH.pins.json](NT3H2111W0FHKH.pins.json).

| Physical pin | Manufacturer name | Function | Source page |
|---|---|---|---|
| 1 | LA | RF antenna terminal A | 9 |
| 2 | VSS | Ground | 9 |
| 3 | SCL | I2C clock | 9 |
| 4 | FD | RF-powered open-drain field detection | 9 |
| 5 | SDA | I2C data | 9 |
| 6 | VCC | External supply input | 9 |
| 7 | VOUT | RF energy harvesting output | 9 |
| 8 | LB | RF antenna terminal B | 9 |

## Review state

Extracted 2026-11-09. Independent source/assignment review required before CAD. Project recommendations below are not the authoritative pinout.

Rail decision update: the first prototype uses one nominal 3.3 V supply shared by MCU, sensors, NFC and LEDs. Keep this part within its specified supply and logic limits; the separately documented below-minimum LED experiment does not relax sensor limits.
