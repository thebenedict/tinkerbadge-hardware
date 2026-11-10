# Independent MCU source review

Temporary review artifacts below are identified by filename only; these intermediate files are not distributed. Published source outputs and repeatable checks are linked from the [current verification record](verification.md).

Reviewed 2026-11-09. **PASS for MCU physical mappings and support circuit, with an EPD_EN pull-down integration amendment required below.** This is a source-to-contract review, not PCB, firmware, electrical-test or production approval. No CAD was modified.

## Sources and method

Independently reopened the original Espressif module PDF v1.8, physically inspected rendered pages 10–16, 27 and 41, and compared every module pad against the table and top-view drawing. Independently extracted ESP32-S3 chip PDF v2.2 and inspected its RTC table on page 23 (not page 22 in this revision). Inspected hardware-design-guide PDF page 22 (printed page 19), USB RC diagram and USB-OTG ROM table. Read related power-up and IO restrictions. Re-extraction/rendering is in `display_sources`.

## Findings

- All 41 module pad names and net assignments match module pages 10–12. EPAD41 and pads1/40 are GND. Page41 calls EPAD soldering optional for assembly, but if soldered it is ground. The contract correctly includes it.
- N16R8 has 16 MB quad flash and 8 MB octal PSRAM. IO35/36/37 (pads28/29/30) are unavailable and correctly NC. GPIO47/48's 1.8 V caveat applies to R16V-based variants, not N16R8.
- BTN_A_N is pad38/GPIO2/RTC_GPIO2; BTN_B_N is pad4/GPIO4/RTC_GPIO4. Both support RTC-domain wake with correct firmware. No optional 32 kHz crystal is fitted, freeing GPIO15/16. BAT_ADC is pad39/GPIO1/ADC1_CH0.
- USB D− is pad13/GPIO19 and D+ is pad14/GPIO20. R205/R206=22 ohm agrees with hardware-guide 22/33 ohm starting recommendation. USB routing and series-resistor placement near the module remain PCB checks.
- GPIO0 has 10 kohm pull-up and BOOT_N test access; GPIO45/46 have 10 kohm pull-downs. This selects SPI boot, permits joint download with GPIO0 low/GPIO46 low, and preserves default 3.3 V VDD_SPI selection. Hold straps for at least3 ms after EN rises.
- GPIO3 NC is acceptable only with default EFUSE_STRAP_JTAG_SEL=0, which explicitly ignores GPIO3 (module p16). If strap-based JTAG selection is later enabled, page15 requires a defined external level. No eFuse change is implied or authorized.
- GPIO40/MTDO (pad33) is EPD_EN. Hardware-guide table12 confirms USB-OTG download ROM drives it HIGH, powering the display in recovery. Display R307 holds reset low. GPIO39/MTCK and GPIO38 go LOW; GPIO21/41/42 become inputs. Recovery testing must include these effects. EPD_EN is not guaranteed low throughout ROM boot.
- **Integration amendment:** Initial contracts contained no external EPD_EN pull-down although power.md claimed one. TPS22918 p3 prohibits floating ON. Add R207=100 kohm from EPD_EN to GND for MCU high-impedance reset/deep-sleep states. This does not override the known ROM HIGH state.
- EN 10 kohm/1 uF matches module p41; minimum rail stabilization before EN high and minimum low reset pulse are each50 us (p16). Test actual ramp/brownout; RC is not a universal slow-ramp supervisor.
- Module recommended supply3.0–3.6 V, nominal3.3 V, with external current capability at least500 mA (p27). 22 uF+100 nF bypass matches p41. Supply transient/current adequacy remains a separate power review.
- Panel BUSY's VOH>=0.8VCI meets MCU VIH>=0.75VDD when switch/trace droop is below6.25% of core supply. Shared3.3 V is appropriate; measure peak transients. Ground pull-down does not back-power the panel.

## Complete pad comparison

| Physical pad | Manufacturer name | Contract net |
|---|---|---|
| 1 | GND | GND |
| 2 | 3V3 | +3V3 |
| 3 | EN | MCU_EN |
| 4 | IO4 | BTN_B_N |
| 5 | IO5 | USB_PRESENT_N |
| 6 | IO6 | DOCK_PRESENT_N |
| 7 | IO7 | MOTION_INT1 |
| 8 | IO15 | EPD_BUSY |
| 9 | IO16 | EXT_SDA |
| 10 | IO17 | IR_TX |
| 11 | IO18 | IR_RX_N |
| 12 | IO8 | I2C_SDA |
| 13 | IO19 | MCU_USB_DM |
| 14 | IO20 | MCU_USB_DP |
| 15 | IO3 | NC |
| 16 | IO46 | STRAP46 |
| 17 | IO9 | I2C_SCL |
| 18 | IO10 | EPD_CS_N |
| 19 | IO11 | EPD_MOSI |
| 20 | IO12 | EPD_SCK |
| 21 | IO13 | EPD_DC |
| 22 | IO14 | EPD_RST_N |
| 23 | IO21 | RGB_DATA |
| 24 | IO47 | SAO_GPIO2 |
| 25 | IO48 | NFC_FD_N |
| 26 | IO45 | STRAP45 |
| 27 | IO0 | BOOT_N |
| 28 | IO35 | NC |
| 29 | IO36 | NC |
| 30 | IO37 | NC |
| 31 | IO38 | PWR_LED_G |
| 32 | IO39 | PWR_LED_R |
| 33 | IO40 | EPD_EN |
| 34 | IO41 | EXT_SCL |
| 35 | IO42 | SAO_GPIO1 |
| 36 | RXD0 | UART_RX |
| 37 | TXD0 | UART_TX |
| 38 | IO2 | BTN_A_N |
| 39 | IO1 | BAT_ADC |
| 40 | GND | GND |
| 41 | EPAD | GND |

## Reviewed SHA-256 before R207 amendment

- `docs/design/mcu_contract.json`: `a1ab392cf0740d9198a10d8e183b0fbfbbb0aad368870d050f7f5884623d1a8f`
- `docs/components/ESP32-S3-WROOM-1-N16R8.json`: `93d6d22f211f42a3297432d390822f50d64c644964d8c61ce08d44a1b18eea5a`
- `docs/datasheets/esp32-s3-wroom-1_wroom-1u_datasheet_en.pdf`: `27d71971da07c280c6068d08c74720d1a25b8f20cf8494dc1765bdd28d40d435`
- `docs/datasheets/esp32-s3_datasheet_en.pdf`: `2d5a7cb7fd559d8d972bd88db32669c0196d23f22d7afaafb0f63d099b589a3f`
- `docs/datasheets/esp32s3-hardware-design-guidelines.pdf`: `4b3f3a5b3c18b04dd89b2bfce5f6a038cd7574ccd3d54c79c5b4924a8ad9c8ad`

## R207 amendment applied

R207=100 kohm 1% between EPD_EN and GND was added to the MCU contract on 2026-11-09 under the integration owner’s instruction. It is a passive bias addition and changes no physical MCU pad assignment. Endpoints checked. **Final schematic-source review PASS**, with the prototype/recovery gates above. Amended contract SHA-256: `c9603c23ce6b0a902d29ba0c00a2ccd5c10c8b32814e0eff10f720ad48c01a19`.
