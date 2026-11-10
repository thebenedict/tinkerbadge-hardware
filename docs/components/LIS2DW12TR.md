# LIS2DW12TR component facts

## Sources and visual check

[Archived ST manufacturer PDF](https://datasheet.lcsc.com/datasheet/pdf/faa0f1ff935ff2be849a090ec963fd19.pdf?productCode=C189624), DocID029682 Rev4, September2017, downloaded through exact LCSC C189624 listing. [Source record](../datasheets/LIS2DW12TR.source.json) records manufacturer URL, mirror URL and SHA256. Inspected actual rendered p9 Fig2/Table2 pin map and p61 Fig18 package geometry:12 contacts, no EP. Newer ST DS11811 Rev9 September2024 was also consulted as manufacturer web PDF text; local download failed. Its p4 pin map agrees with archived Rev4 p9. References below refer to Rev9 unless explicitly marked Rev4. No separate manufacturer errata found in targeted search on2026-11-09.

## Electrical facts

- VDD 1.62–3.6 V; VDD_IO 1.62 V to VDD+0.1 V (p7 Table4). Both may share selected 3.3 V core rail (must remain <=3.6 V). Rev9 specifies VIH >=0.7 VDD_IO, VIL <=0.3 VDD_IO; archived Rev4 p13 is stricter at VIH >=0.8 VDD_IO and VIL <=0.2 VDD_IO. Use the stricter thresholds for compatibility review.; digital VOL <=0.2 V and VOH >=VDD_IO-0.2 V at 4 mA (p7).
- Absolute supply maximum 4.8 V; control-pin input maximum VDD_IO+0.3 V (p12). Do not drive bus into fully unpowered I/O. Datasheet specifically permits VDD removal with VDD_IO maintained without blocking the bus (p7 note2, p19).
- Power-down current 50 nA typical, low-power-mode1 0.38 µA at 1.6 Hz and 1 µA at 12.5 Hz, high-performance 90 µA typical (p7; typical is not guaranteed). Wake detection needs active measurement, not power-down.
- Pins2/3 internally pulled up (p4–5); choose SA0 high, address 0x19, to avoid DC current through internal pull-up. Alternative SA0 low gives 0x18.
- INT1 and INT2 default push-pull low (p20 Table12). Route INT1 to retained MCU wake input, configure active-high wake behavior before enabling wake; disable motion interrupt/storage wake during transport. Unused INT2 left NC.

## Project recommendation U502 / SEN-02

Pins2/3/9/10 core rail; pin1 I2C_SCL; pin4 I2C_SDA; pins5/6/7/8 GND (pin5 grounding permitted, pin7 required). Pin12 IMU_INT1; pin11 NC. Reference p19 Fig6 shows 100 nF plus 10 µF at VDD and 100 nF at VDD_IO, all close to pins. Use 10 µF X5R/X7R ceramic with adequate effective capacitance as a documented implementation substitution for the reference aluminum bulk capacitor. Shared bus pull-ups to same live core rail; no independent sensor power gate. Power-down by ODR=0000; establish startup settling and software-reset timing from full archived source before firmware release. Bench tests: motion wake in event mode, no wake in storage, supply ramp/recovery, current, and axis orientation.

## Physical pins

Generated from [LIS2DW12TR.pins.json](LIS2DW12TR.pins.json).

| Physical pin | Manufacturer name | Function | Source page |
|---|---|---|---|
| 1 | SCL/SPC | I2C clock / SPI clock | 9 |
| 2 | CS | Tie VDD_IO for I2C; internally pulled up | 9 |
| 3 | SDO/SA0 | SPI output / I2C address LSB; internally pulled up | 9 |
| 4 | SDA/SDI/SDO | I2C data / SPI data | 9 |
| 5 | NC | Internally unconnected; may tie VDD, VDD_IO or GND | 9 |
| 6 | GND | Ground | 9 |
| 7 | RES | Must connect GND | 9 |
| 8 | GND | Ground | 9 |
| 9 | VDD | Core power | 9 |
| 10 | VDD_IO | I/O power | 9 |
| 11 | INT2 | Interrupt2 / optional single-conversion clock input | 9 |
| 12 | INT1 | Interrupt1 | 9 |

## Review state

Extracted 2026-11-09. Independent source/assignment review required before CAD. Project recommendations below are not the authoritative pinout.

Rail decision update: the first prototype uses one nominal 3.3 V supply shared by MCU, sensors, NFC and LEDs. Keep this part within its specified supply and logic limits; the separately documented below-minimum LED experiment does not relax sensor limits.
