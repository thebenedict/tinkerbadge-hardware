# ESP32-S3-WROOM-1-N16R8

Working implementation candidate. Source: module datasheet v1.8 pp10–16,27–28,41–45; chip datasheet v2.2 §2.3.2; current Espressif hardware guidelines §1.3.13. PDFs and hashes: [inventory](../datasheets/mcu_inventory.json).

## Physical pins

Generated from ESP32-S3-WROOM-1-N16R8.json. Package pin numbers are not GPIO numbers. Top-view diagram inspected; pad41 is the exposed ground island and includes several same-number copper lands in the standard footprint.

| Pad | Manufacturer function | GPIO | RTC/wake domain | Restriction |
|---|---|---|---|---|
| 1 | GND |  |  |  |
| 2 | 3V3 |  |  |  |
| 3 | EN |  |  |  |
| 4 | IO4 | 4 | RTC_GPIO |  |
| 5 | IO5 | 5 | RTC_GPIO |  |
| 6 | IO6 | 6 | RTC_GPIO |  |
| 7 | IO7 | 7 | RTC_GPIO |  |
| 8 | IO15 | 15 | RTC_GPIO |  |
| 9 | IO16 | 16 | RTC_GPIO |  |
| 10 | IO17 | 17 | RTC_GPIO |  |
| 11 | IO18 | 18 | RTC_GPIO |  |
| 12 | IO8 | 8 | RTC_GPIO |  |
| 13 | IO19 | 19 | RTC_GPIO |  |
| 14 | IO20 | 20 | RTC_GPIO |  |
| 15 | IO3 | 3 | RTC_GPIO | boot strap; excluded from accessory I/O |
| 16 | IO46 | 46 |  | boot strap; excluded from accessory I/O |
| 17 | IO9 | 9 | RTC_GPIO |  |
| 18 | IO10 | 10 | RTC_GPIO |  |
| 19 | IO11 | 11 | RTC_GPIO |  |
| 20 | IO12 | 12 | RTC_GPIO |  |
| 21 | IO13 | 13 | RTC_GPIO |  |
| 22 | IO14 | 14 | RTC_GPIO |  |
| 23 | IO21 | 21 | RTC_GPIO |  |
| 24 | IO47 | 47 |  |  |
| 25 | IO48 | 48 |  |  |
| 26 | IO45 | 45 |  | boot strap; excluded from accessory I/O |
| 27 | IO0 | 0 | RTC_GPIO | boot strap; excluded from accessory I/O |
| 28 | IO35 | 35 |  | N16R8 octal PSRAM; no user connection |
| 29 | IO36 | 36 |  | N16R8 octal PSRAM; no user connection |
| 30 | IO37 | 37 |  | N16R8 octal PSRAM; no user connection |
| 31 | IO38 | 38 |  |  |
| 32 | IO39 | 39 |  |  |
| 33 | IO40 | 40 |  |  |
| 34 | IO41 | 41 |  |  |
| 35 | IO42 | 42 |  |  |
| 36 | RXD0 | 44 |  |  |
| 37 | TXD0 | 43 |  |  |
| 38 | IO2 | 2 | RTC_GPIO |  |
| 39 | IO1 | 1 | RTC_GPIO |  |
| 40 | GND |  |  |  |
| 41 | EPAD |  |  |  |

## Electrical and support contract

- Module supply recommended3.0–3.6V; design+3V3. Source must deliver at least500mA for module according to table6-2. Typical RF peaks are355mA Wi-Fi /344mA BLE at specified conditions, not guaranteed maxima.
- Pin2 gets22µF bulk plus100nF local; ground pins1/40/41 connected. EN gets10k to3V3 and1µF toground, matching module p41 recommended reset delay. Scope EN timing and brownout behavior.
- GPIO0 BOOT10k pullup; GPIO45/46 each10k pulldown. Boot/download pads andEN are independent from the two user buttons. No eFuse changes are authorized or required.
- NativeUSB19/20 each22Ω series, with connectorESD on power sheet. UART43/44 remain accessible. USB attach/detach uses independently sensedVBUS; device firmware must disable pullup withoutVBUS.
- Guaranteed digital thresholds in table6-3 are VIH≥0.75VDD, VOH≥0.8VDD (high-impedance load), VIL≤0.25VDD andVOL≤0.1VDD. Current/temperature qualifications must not be extrapolated from typical values.
- GPIO2 button is RTC_GPIO2, suitable for external RTC wake. Configure EXT0 low wake, wait for release/debounce before sleeping, and do not enable source-present low-level wake when it is already asserted. GPIO4 button andGPIO5/6 presence are alsoRTC-domain candidates. No insertion wake is promised until firmware-tested.
- GPIO7 motion is RTC-capable but motion wake is disabled in storage. NFC field detect usesGPIO48 and is polled/interrupt during awake operation; no storage wake guarantee.
- ROMUSB-OTG download may driveGPIO38/39 low andGPIO40 high (hardwareguidelines table12). StatusLEDs on38/39 staydark;40 is thereforeEPD powerenable, where high is benign. GPIO41/42 are inputs in that ROM path.
- GPIO35–37 must remainNC for N16R8PSRAM. GPIO47/48 are3.3V forN16R8; do not substituteN16R16V whose47/48 domain is1.8V.
- Preserve antenna keepout from module drawing and placement guide, including display/battery/enclosure metal. Footprint checked through Konnect; PCB placement and prototypeRF tests remain pending.

## Review state

Physical pin map, candidate assignment and support values await independent source review before placing U201. Bench gates: power/EN transients, nativeUSB recovery, button wake/release, statusdark reset/sleep, RF coexistence and4h workload.
