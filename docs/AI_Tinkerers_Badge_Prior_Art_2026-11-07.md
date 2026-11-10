# AI Tinkerers Badge Prior Art and Research Brief

Research date: 2026-11-07  
Status: Exploratory research, not an approved specification or implementation plan  
Audience: Michael and future hardware, firmware, mechanical, and software implementation agents

## Purpose and conclusions

This compilation records the current badge concept and maps useful prior art to the decisions it leaves open. It favors published design files, working products, conference deployments, vendor documentation, and explicit licenses over attractive renders or unverified claims. No component, architecture, budget, production quantity, or privacy policy is selected by this document.

The strongest starting references serve different purposes: Badge.team for conference operations and extensibility; the CDC Badge for ESP32-S3 e-paper hardware and mechanical source; GxEPD2 and Waveshare for a conventional SPI display route; EPDiy, Inkplate, and Open Book for larger e-paper and reader architecture; OpenBeacon and SocioPatterns for the limits of proximity inference; and official KiCad tools for reproducible checks and exports. These are research leads to combine selectively, not a recommendation to clone one complete badge.

Three issues should be resolved early in any later design phase:

1. **Physical size must distinguish active display, glass, carrier board, and finished enclosure.** The candidate 3.7-inch Waveshare mono panel is substantially wider than a strict three-inch overall badge envelope.
2. **A four-hour battery target depends on radio and LED behavior, not just e-paper.** A persistent image does not mean the rest of the badge is asleep. Loaner storage between events is a separate power requirement.
3. **Proximity and contact exchange are separate features.** Being within radio range is neither evidence of a conversation nor consent to exchange personal details.

## Current concept to preserve

The following is the exploratory brief from the conversation, not a settled requirement set:

- An open-source badge for AI Tinkerers meetups, useful both as identification and as an invitation to tinker.
- E-paper with roughly a three-inch long edge; a 3.7-inch-diagonal Waveshare panel is a candidate.
- ESP32-S3 with PSRAM as a starting candidate, not a committed MCU or module SKU.
- Approximately four hours of meetup use between charges.
- A rechargeable loaner pool, potentially with a charging dock, plus personal units available at cost; speakers may keep theirs.
- A transparent or translucent enclosure.
- A top role-indicator LED bar and roughly three to five affinity LEDs.
- Optional, privacy-aware proximity behavior and intentional contact exchange.
- An agent-assisted specification-to-KiCad process, reusable Harvest tooling, and a possible future web pipeline producing 3D views, schematics, and a BOM.
- Research only at this stage. No confirmed budget, batch size, final feature set, manufacturing partner, privacy policy, or procurement instruction.

“Harvest” is retained as a project/tooling reference from the brief. Its actual repository, APIs, and existing capabilities were not inspected here; nothing below assumes those capabilities already exist.

## How to use the references

- **Established reference** means a released tool, documented product, or prior conference deployment. It does not mean a design is still stocked or production-ready today.
- **Prototype reference** means useful published work whose claimed behavior, maintenance, or deployment needs further validation.
- **License verified** means the linked license or explicit primary-source license statement was read. It does not mean every submodule, font, artwork, datasheet, or vendor binary inherits that license.
- Before copying any implementation, pin the exact repository commit, retain notices, inspect dependencies, and record file-level exceptions. Before ordering, recheck actual part numbers, availability, revision, and supplier drawing.
- Public visibility alone is not permission to reuse. Hardware files, firmware, enclosure CAD, documentation, and branding must be checked separately.

## Suggested reading order

| Decision or subsystem | Start with |
|---|---|
| Exact small-display fit and update behavior | Display comparison, Waveshare, GxEPD2 |
| Conference badge UX and maintainability | SHA2017, MCH2022, Badger, Badgeware |
| S3 integration and extensibility | CDC Badge, flow3r, Tildagon |
| Alternative e-reader display architecture | EPDiy, Inkplate, Open Book |
| Discovery versus deliberate sharing | SocioPatterns, OpenBeacon, BLE, ESP-NOW, NFC, QR |
| Transparent enclosure and loaner operation | Badgeware, YAPP, Threejs deployment lessons, power section |
| Agent-assisted design and web outputs | KiCad CLI/IPC, SKiDL, atopile, specific MCP implementations |

## Display candidates and physical dimensions

The candidate Waveshare 3.7-inch mono panel has a supported GxEPD2 driver, but its active width, glass width, and carrier width are all different. “3.7-inch” is a diagonal category, not enough to select a controller or footprint. The four-color (G) version is not interchangeable. The following comparison is especially important before defining the outer badge outline.


Dimensions are millimetres; the active area, bare panel, and carrier board are different envelopes. These are official published specifications, not live inventory checks.

| Candidate | Pixels/color | Active area | Bare panel | Carrier board | Published refresh |
|---|---|---|---|---|---|
| Waveshare 3.7 mono | 480 × 280, mono/4 gray | 81.12 × 47.32 | 93.3 × 54.9 × 0.78 | 96.5 × 58 | 3 s |
| Waveshare 3.7 (G) | 416 × 240, red/yellow/black/white | 81.54 × 47.04 | 92.99 × 53 × 1 | 96 × 57 | 20 s normal; 12 s fast |
| Waveshare 3.52 mono | 360 × 240, mono | 74.51 × 49.67 | 80.68 × 54.41 × 1.18 | 86.5 × 57 | 1.5 s |
| Waveshare 2.9 mono | 296 × 128, mono/4 gray in current docs | 66.89 × 29.05 | 79 × 36.7 × 1.05 | 89.5 × 38 | 3 s |

Sources: [3.7 mono](https://docs.waveshare.net/3.7inch_e-Paper_HAT/), [3.7 G](https://docs.waveshare.net/3.7inch_e-Paper_HAT%2B_G/), [3.52 mono](https://docs.waveshare.net/3.52inch_e-Paper_HAT/), [2.9 mono](https://docs.waveshare.net/2.9inch_e-Paper_Module/).

**Interpretation:** 3.52-inch mono is a plausible geometric alternative if “3 inches” means the active long edge (74.51 mm ≈ 2.93 in), though even its bare panel is 80.68 mm (3.18 in). Its supplier distinguishes flashing GC full refresh from faster nonflashing DU full refresh, with accumulated ghosting requiring GC cleanup. Driver compatibility needs a separate spike. The 2.9-inch family gives a narrower name-tag shape; its V1/V2/V3 firmware differences reinforce the need to lock a revision.

A 480 × 280 one-bit framebuffer is **16,800 bytes**; a two-bit image is **33,600 bytes**, before previous-frame copies and application overhead. These are calculated values, not vendor RAM requirements. PSRAM may be useful for networking and apps, but this display alone does not prove it necessary.

## Conference badges and e-paper platforms

### SHA2017: closest mature conference-badge precedent

SHA2017 combined an ESP-WROOM-32 with 128 Mbit flash, a DKE DEPG0290B1 e-paper panel, capacitive controls via MPR121, expansion facilities, and battery power. Its current hardware documentation explicitly records that the original panel became hard to obtain and documents a GDEH029A1 replacement plus a persistent firmware selection flag. This is valuable evidence that a badge fleet needs a panel-revision identity, not merely a screen-size setting. [Hardware documentation](https://badge.team/docs/badges/sha2017/hardware/)

The PCB repository provides Eagle board/schematic sources, schematic and assembly PDFs, and a revisioned BOM. Its root license is **MIT**. Original firmware is **Apache-2.0 for original code**, but the license explicitly preserves dependency licenses and flags **uGFX as free for non-commercial use**. Do not describe that entire historical firmware image as permissively reusable for buy-at-cost units without a component audit. [PCB and artifacts](https://github.com/SHA2017-badge/PCB), [PCB license](https://github.com/SHA2017-badge/PCB/blob/master/LICENSE), [firmware license with exceptions](https://github.com/SHA2017-badge/Firmware/blob/master/LICENSE)

### MCH2022: provisioning and app-platform precedent

MCH2022 uses an ESP32-WROVER-E with 16 MB flash/8 MB PSRAM, an RP2040 for USB and board-management functions, and an iCE40UP5K FPGA. It is an LCD gaming-style badge, not e-paper. The RP2040 supplies dual serial, WebUSB and HID functions; the project publishes app templates, a Hatchery app store, firmware downloads, and production autoflasher resources. For a loaner pool, these recovery and provisioning flows are more relevant than reproducing its three-processor architecture. [Badge overview](https://badge.team/docs/badges/mch2022/), [project resource map](https://github.com/badgeteam/mch2022-project)

Hardware includes KiCad, BOM, Gerbers, and schematic PDF under **CERN-OHL-P-2.0**; the repository is now archived. ESP32 launcher original code is **MIT**. The RP2040 README assigns its original portions **MIT**, with named **BSD-3-Clause** bootloader/infrared dependencies and MIT dependencies. This does not establish a blanket license for the separate FPGA and BadgePython repositories. [Hardware/license](https://github.com/badgeteam/mch2022-badge-hardware), [launcher license](https://github.com/badgeteam/mch2022-firmware-esp32/blob/master/LICENSE), [RP2040 component licensing](https://github.com/badgeteam/mch2022-firmware-rp2040/blob/master/README.md)

### Camp 2023 flow3r: ESP32-S3 application and expansion precedent

The official flow3r hardware page specifies ESP32-S3 at 240 MHz, 8 MiB SPI RAM, 16 MiB flash, a round 240 × 240 GC9A01-compatible display, USB-C, capacitive petals, audio, microSD, 40 RGB LEDs, and a 2000 mAh battery. This is a useful proof of an ambitious ESP32-S3/MicroPython badge ecosystem, but its LCD/audio/LED load does not establish an e-paper badge's battery life. [Official hardware specifications](https://docs.flow3r.garden/badge/hardware_specs.html)

The official firmware is **LGPL-3.0**, with a detailed third-party license inventory including MicroPython/TinyUSB MIT, GC9A01/Bosch libraries BSD-3-Clause, and ESP-IDF Apache-2.0. Docs include app, firmware-update, networking, and extension interfaces. **Hardware license and fabrication-package completeness were not verified**: the hardware GitLab source could not be fetched in this pass. Treat it as verified firmware/platform prior art, not an approved hardware source. [License inventory](https://docs.flow3r.garden/badge/license.html), [documentation index](https://docs.flow3r.garden/), [build/source instructions](https://docs.flow3r.garden/os/guide/development.html)

### Tildagon: reusable base and add-on ecosystem

Tildagon's public repositories separate the base board, hexpansion designs, datasheets, and a pins/BOM spreadsheet. Current software has an ESP32-S3 build target, MicroPython-based applications, a web flasher, and documented development flows. Its most useful lesson is the reusable base plus explicit expansion interface, rather than a display choice. Current documentation also includes later Spaceagon work, so pin the intended board generation when studying it. [Hardware repository](https://github.com/emfcamp/badge-2024-hardware), [software/build instructions](https://github.com/emfcamp/badge-2024-software/blob/main/README.md), [app documentation](https://tildagon.badge.emfcamp.org/tildagon-apps/)

Observed licenses: **CERN-OHL-P-2.0** for both `tildagon-base` and `hexpansion`; the root explicitly disclaims licensing authority over bundled supplier datasheets. Current software root is **MIT**, with submodules requiring separate review. Some community add-ons use other licenses; their labels must not be attributed to the base. [Base license](https://github.com/emfcamp/badge-2024-hardware/blob/main/tildagon-base/LICENSE.txt), [hexpansion license](https://github.com/emfcamp/badge-2024-hardware/blob/main/hexpansion/LICENSE.txt), [scope warning](https://github.com/emfcamp/badge-2024-hardware/blob/main/LICENSE.txt), [software license](https://github.com/emfcamp/badge-2024-software/blob/main/LICENSE)

### GxEPD2: conventional SPI display driver option

GxEPD2 is an Arduino library for many Good Display/Waveshare SPI panels, using Adafruit_GFX and optionally paged buffers to reduce RAM needs. It has an exact `GxEPD2_370_TC1` driver for **ED037TC1, SSD1677, 280 × 480**, declaring full/fast partial update. The header's nominal full/partial durations are 1000/800 ms, with example measured timings; these are software parameters/observations, **not** a promised refresh rate or equivalent to Waveshare's 3-second four-gray specification. `powerOff()` and `hibernate()` are implemented interfaces. [Project](https://github.com/ZinggJM/GxEPD2), [exact driver](https://github.com/ZinggJM/GxEPD2/blob/master/src/epd/GxEPD2_370_TC1.h)

The repository license is **GPLv3**. The README records supplier-derived waveforms, panel-specific quirks, 3.3 V raw-panel requirements, reset-circuit differences, and says upstream does not accept pull requests. A maintained application fork and exact dependency/license manifest may therefore be needed. Hardware and supplier datasheets are not made open by this library license. [License](https://github.com/ZinggJM/GxEPD2/blob/master/LICENSE), [compatibility notes](https://github.com/ZinggJM/GxEPD2/blob/master/README.md)

### EPDiy: parallel e-reader-panel alternative, not a SPI substitute

EPDiy drives bare replacement e-reader panels; V7 uses ESP32-S3, earlier versions ESP32. It supports 16-level grayscale, LiPo charging, and low-sleep-power designs. Supported/tested examples include 6-inch ED060SC4 (800 × 600), 6-inch ED060XC3 (758 × 1024), and 9.7-inch ED097TC2 (1200 × 825). The 4.7-inch ED047TC1 entry is explicitly tied to the LILYGO 4.7-inch board. These parallel-display designs are architecturally different from the small SPI ED037TC1 path. [Primary README and panel matrix](https://github.com/vroland/epdiy/blob/main/README.md)

KiCad sources and generated Gerbers, BOM, pick-and-place, schematic PDFs and 3D models are published. Default hardware licensing is **CC-BY-SA-4.0 unless otherwise specified**; firmware/examples are **LGPLv3**, utilities **MIT**, with a separate weather-example exception. Caveats include per-panel VCOM calibration, connector adapters, tested-versus-assumed compatibility, and slower V7 refresh under Arduino's cache configuration. [Hardware source/licensing](https://github.com/vroland/epdiy-hardware/blob/main/README.md), [manufacturing artifacts](https://vroland.github.io/epdiy-hardware/)

### Inkplate: comparatively complete open e-reader-panel hardware

Inkplate 6 v2 is an ESP32-based 6-inch recycled e-reader display platform. The hardware README advertises grayscale, partial updates, approximately 1.26-second refresh and 264 ms partial update; those platform-specific figures should not be transferred to another panel. Its explicit recycled-panel caveat is relevant to cosmetic quality, procurement and replacements. This is better as a reference for the e-paper power/display subsystem and release package than as a wearable-size design. [Hardware README](https://github.com/SolderedElectronics/Soldered-Inkplate-6-hardware-design/blob/main/README.md)

The repository publishes versioned KiCad files and output folders for BOM, schematic PDF, STEP and Gerbers. Hardware is **TAPR Open Hardware License v1.0**, while the Inkplate Arduino library is **LGPLv3**. TAPR's source/distribution obligations and explicit exclusion of firmware from hardware-license scope matter if reusing its circuits or selling units. Verify the exact Inkplate model and revision, as the family spans different processors and displays. [Hardware license](https://github.com/SolderedElectronics/Soldered-Inkplate-6-hardware-design/blob/main/LICENSE.md), [library](https://github.com/SolderedElectronics/Inkplate-Arduino-library), [library license](https://github.com/SolderedElectronics/Inkplate-Arduino-library/blob/master/LICENSE)

### The Open Book: hand-assembly and comprehensible design precedent

The current main-branch Open Book reboot is Raspberry Pi Pico-based, powered by AAA batteries, using a **GDEW042T2 4.2-inch grayscale panel**, microSD, buttons, and a separate castellated e-paper driver. The creator explicitly warns against substituting the tri-color panel. It is optimized for low part count and hand assembly, not a small rechargeable badge. [Project README](https://github.com/joeycastillo/The-Open-Book/blob/main/README.md)

Artifacts include a KiCad main-board project, Eagle driver-board sources, fabrication ZIPs and parts lists; the original design is preserved on a separate branch. The main project's observed root license is **CC-BY-SA-4.0** and the separate `libros` firmware is **MIT**. The README says different components may have different licenses, so individual libraries/assets still need checking. Especially useful ideas are the separate display-driver module, explanatory silkscreen/documentation, and a build route suitable for community workshops. [Hardware license](https://github.com/joeycastillo/The-Open-Book/blob/main/LICENSE.md), [libros license](https://github.com/joeycastillo/libros/blob/main/LICENSE.md), [assembly/use documentation](https://www.oddlyspecificobjects.com/projects/openbook/)

### Pimoroni Badger 2040: mature e-paper badge UX, retired product

Badger 2040 combines RP2040, 2 MB flash, a **2.9-inch 296 × 128** display, five front buttons, USB-C, Qwiic/STEMMA QT, and a battery connector. Its overall dimensions are 85.6 × 48.7 × 10 mm including connectors. Official documentation offers schematics/mechanical drawings, firmware UF2s and C++/MicroPython examples. **Pimoroni now says it no longer stocks this product**, so this is prior art, not a supply assumption. [Official product documentation](https://shop.pimoroni.com/products/badger-2040)

The Badger firmware/examples repository and `pimoroni-pico` root are **MIT**. A complete separately licensed PCB manufacturing-source package was not established; do not infer open-hardware reproduction rights from public schematics. It has **no LiPo charging circuit and no battery protection**, and the vendor advises a protected cell plus mechanical protection if using LiPo. Those omissions are crucial for a proposed dock-charged loaner fleet. [Firmware/artifacts](https://github.com/pimoroni/badger2040), [firmware license](https://github.com/pimoroni/badger2040/blob/main/LICENSE), [C++ license](https://github.com/pimoroni/pimoroni-pico/blob/main/LICENSE)

### Waveshare 3.7-inch: supplier module and reference driver

The mono HAT, SKU **18057**, specifies SPI, 480 × 280 pixels, four grayscale levels, 3-second refresh, typical 50 mW refresh power, and 0–55 °C operation. Its 3.3/5 V module input specification must not be confused with a bare panel's 3.3 V requirements. The official page prominently warns that repeated flexing can break the fragile FPC. Its very small advertised display sleep current is **not the current of an ESP32 badge or whole HAT system**. [Supplier specifications](https://docs.waveshare.net/3.7inch_e-Paper_HAT/)

Supplier `EPD_3in7.c` includes waveform tables and an **MIT-style permission/disclaimer header**. That establishes terms for that file, not for the panel hardware, all repository dependencies, or a copyable PCB. The exact panel/controller mapping is corroborated by GxEPD2. Stock, sustained refresh life, and long-term panel availability remain unverified. [Supplier driver](https://github.com/waveshareteam/e-Paper/blob/master/RaspberryPi_JetsonNano/c/lib/e-Paper/EPD_3in7.c), [panel/controller identification](https://github.com/ZinggJM/GxEPD2/blob/master/src/epd/GxEPD2_370_TC1.h)


### CDC Badge

**Reference:** [RIAT CDC Badge hardware repository](https://github.com/riatlabs/cdc-badge), [hardware license](https://github.com/riatlabs/cdc-badge/blob/main/LICENSE), [firmware checklist](https://github.com/riatlabs/cdc-badge/blob/main/docs/firmware-checklist.md).

The project combines ESP32-S3, an e-paper display with frontlight, a single-cell LiPo connection, a keypad, and a TROPIC01 secure element. It publishes KiCad schematics/layout, documentation, and printable cases. Its hardware repository is CERN-OHL-P-2.0. Linked firmware projects are separate license surfaces.

**Relevance:** A close integration reference for power, display, buttons, expansion, enclosure, and recovery/debug access. Its secure element, keypad, and expansion count are not implied requirements for this badge. The repository documents the secure element as a material sleep-current contributor, an example of why board-level power matters more than MCU headline sleep current. Treat its complex feature set as a source of subsystems, not a minimum design.

### GitHub Universe and Pimoroni Badgeware

**References:** [Universe badge repository](https://github.com/badger/home), [repository license](https://github.com/badger/home/blob/main/LICENSE), [Badgeware hardware and interaction guide](https://github.com/pimoroni/badgeware-docs/blob/main/introduction/meet-your-badge.md).

The current Universe repository separates 2026, 2025, and earlier e-ink resources. It explicitly warns that the legacy simulator/API does not model the newer generation. The repository is MIT-licensed, but this does not establish permission for every underlying commercial board or enclosure design.

Badgeware provides a useful finished-product benchmark: a clear polycarbonate shell, PCB lanyard anchor, desk-standing form, rechargeable wireless platform, and independently driven white LEDs shining through the case. The documentation gives an 84 × 76 × 20 mm enclosed form factor. This is a strong reference for the proposed translucent treatment and beginner-friendly programming experience, even when the display and MCU differ. Inspect the correct generation rather than mixing pinouts, dimensions, or app APIs.

### Threejs Paris speaker badge

**References:** [firmware and deployment account](https://github.com/hervestudio/firmware-badge), [firmware license](https://github.com/hervestudio/firmware-badge/blob/main/LICENSE), [enclosure files and lessons](https://github.com/hervestudio/Speaker-Badge-enclosure), [enclosure license](https://github.com/hervestudio/Speaker-Badge-enclosure/blob/main/LICENSE).

The authors describe a 40-badge speaker deployment plus 10 spares using ESP32-S3 with PSRAM, a round TFT, ESP-NOW encounters, QR information, phone-based setup, OTA maintenance, and a browser emulator compiled from the real firmware. Firmware is MIT, with explicit exceptions for fonts. Public enclosure STLs have a separate MIT license; the editable generator is linked separately and must be checked before reuse.

**Relevance:** Particularly useful for shared firmware/simulator logic and fleet workflows. Its TFT animation workload is not an e-paper model, and broadcasting identity/game scores should not be copied into a privacy-aware system by default.

The enclosure account reports that an always-connected boost converter continued drawing current after the event and depleted stored cells. This is a concrete reason to validate storage/off behavior for loaners and retained personal units, not merely four-hour runtime. Treat the reported failure as that project's experience, not a diagnosis of every charger design.

### Twilio SIGNAL Hackpack v4

**References:** [hardware release](https://github.com/twilio/hackpack-v4-hardware), [Solderpad 2.0 license](https://github.com/twilio/hackpack-v4-hardware/blob/master/LICENSE).

This older Raspberry Pi Zero W conference badge publishes KiCad 5 source, Gerbers, BOM, schematic, firmware links, and assembly exceptions. Hardware is Solderpad Hardware Licence 2.0, a wrapper around Apache 2.0. It is less relevant as an MCU or low-power design, but a good example of a handoff that includes source, manufacturing outputs, and the awkward assembly details that otherwise remain in someone's head. Historical sourcing instructions are not a current BOM.

## Networking and contact exchange prior art


### SocioPatterns: experimentally evaluated face-to-face sensing

**Source:** [Cattuto et al., Dynamics of Person-to-Person Interactions from Distributed RFID Sensor Networks, PLOS ONE (2010)](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0011596), particularly Materials and Methods, “Distributed proximity sensing.”

The study used OpenBeacon-derived nRF24L01+ active RFID tags, bidirectional low-power packets, and chest-level placement. The lowest power restricted exchange to approximately 1–1.5 m; body absorption made the exchange directional. The authors report greater than 99% assessment probability over 20-second intervals for their configured platform and discuss crowded-room checks. Deployments included 25, 405, and 575 participants. Tags reported to installed readers and a central collection system.

**Useful reuse:** experimental method, separation between local detection and infrastructure reporting, and evaluation design. **Limits:** historical custom active RFID, not evidence that ordinary BLE RSSI or ESP-NOW reproduces the result; not a conversation detector. The paper is a research source, not a verified software/hardware license grant. Its consent and non-identification procedures are important context, not a ready-made privacy policy for this badge.

### OpenBeacon-ng: available wearable hardware and firmware

**Project:** [meriac/openbeacon-ng](https://github.com/meriac/openbeacon-ng). **Hardware license:** [hardware/readme.md](https://github.com/meriac/openbeacon-ng/blob/master/hardware/readme.md). **Code evidence:** [root LICENSE](https://github.com/meriac/openbeacon-ng/blob/master/LICENSE) and [proximity firmware main.c header](https://github.com/meriac/openbeacon-ng/blob/master/firmware/nRF51/tag-proximity/src/main.c).

The repository contains nRF51822-based proximity-tag hardware, firmware, host tooling, and reader documentation. It explicitly distinguishes location beacons from tag-to-tag proximity detection. The README's newer range/resolution claims are project claims, not the same experiment as the 2010 SocioPatterns paper.

**Verified licensing:** hardware is **CC BY-SA 4.0**; the inspected proximity firmware source specifies **GPL-3.0-or-later**, and the root carries GPLv3. Preserve the relevant license, attribution, source and share-alike obligations when adapting/distributing. Audit other files and dependencies individually. Older OpenBeacon websites describe earlier GPLv2 generations; do not substitute that license for this repository. **Useful reuse:** architecture, tag mechanics, protocol ideas, and explicitly licensed design material. **Limits:** old Nordic platform, not a drop-in S3 design or phone-compatible BLE contact protocol merely because the chip supports BLE.

### Espressif ESP-NOW and the S3/C6/H2 choice

**Protocol:** [ESP-IDF ESP-NOW reference](https://docs.espressif.com/projects/esp-idf/en/stable/esp32/api-reference/network/esp_now.html). **Phone-free example:** [Espressif ESP-NOW overview](https://www.espressif.com/en/news/ESP-NOW). **License:** [ESP-IDF LICENSE](https://github.com/espressif/esp-idf/blob/master/LICENSE), [copyright/dependency exceptions](https://github.com/espressif/esp-idf/blob/master/docs/en/COPYRIGHT.rst).

ESP-NOW carries data in vendor-specific Wi-Fi action frames without association to an access point. Current documentation describes peer/channel coordination, optional CCMP encryption for paired unicast, no multicast encryption, and application acknowledgements when application-level delivery matters. The inspected ESP32 stable page gives 20 paired peers and up to 17 encrypted peers, default 7; these are target/version-specific constraints, not a cap on all broadcast listeners. Radio reception or a successful MAC send is not proof of application delivery or physical closeness.

**Verified licensing:** ESP-IDF original source is **Apache-2.0**; third-party components and individual headers may differ. This is not a blanket license for every binary dependency or Espressif board.

**SoC evidence:** [ESP32-S3](https://www.espressif.com/en/products/socs/esp32-s3/) has 2.4 GHz 802.11b/g/n, Bluetooth LE 5, dual LX7 cores and PSRAM support. [ESP32-C6](https://www.espressif.com/en/products/socs/esp32-c6) adds 802.15.4 and Wi-Fi 6; [ESP32-H2](https://www.espressif.com/en/products/socs/esp32-h2) provides BLE/802.15.4, not Wi-Fi. Thus H2 alone is not an ESP-NOW endpoint. C6 is not a pin-compatible S3 substitute; compare memory, peripherals and workload separately.

**Important S3 coexistence evidence:** [official S3 RF coexistence matrix](https://docs.espressif.com/projects/esp-idf/en/latest/esp32s3/api-guides/coexist.html) shows time-sharing of one RF path, with ESP-NOW RX/BLE coexistence supported in station mode. The documentation cautions that custom connectionless power-saving parameters need substantial coexistence testing. Do not read generic introductory references to 802.15.4 as an S3 feature.

### Bluetooth SIG: BLE transport versus ranging

**Sources:** [Bluetooth LE primer](https://www.bluetooth.com/bluetooth-le-primer/), [Bluetooth Channel Sounding overview and FAQ](https://www.bluetooth.com/learn-about-bluetooth/feature-enhancements/channel-sounding/).

BLE has established advertising and connection-oriented data transport. The SIG explicitly describes RSSI-based distance estimation as a proxy and distinguishes it from Channel Sounding. Channel Sounding uses phase/time observations, needs support at both ends, and leaves the distance algorithm to the application. The FAQ says a new PHY may require a chip upgrade. Do not promise that S3, C6, H2, or arbitrary existing phones acquire precise ranging through a firmware change.

**Useful reuse:** BLE discovery plus an authenticated application exchange is a practical candidate for badges and optional phone apps. **Limits:** test actual phone OS support and background behavior; a supported BLE version does not mean every optional feature is implemented. Discovery, bonding, and data-sharing permission are different states. These official technical pages are references, **not a reusable firmware or hardware license**; assess the selected BLE stack's license separately.

### NFC Forum: intentional tap and NDEF

**Source:** [NFC technical overview](https://nfc-forum.org/learn/nfc-technology/).

NFC operates at 13.56 MHz. The Forum describes a typical range up to 2 cm, tap-oriented interaction, reader/writer and card-emulation modes, and NDEF records containing URLs or contact data. A passive tag can be batteryless. A phone reading a passive badge tag is different from two powered badges performing peer-to-peer exchange.

**Useful reuse:** a passive NDEF URL tag is an appealing low-complexity optional phone entry point. **Limits:** badge-to-badge NFC requires suitable reader/target hardware and role design; two ordinary passive tags cannot exchange data with each other. Confirm real phone behavior rather than assuming generic peer-to-peer support. Short range is not authentication or an anti-copying guarantee. This page is a standards explainer, **not an open-source chip/board/code license**; NFC hardware, libraries and specification access have separate terms.

### Nayuki QR Code generator: small, explicitly licensed payload generation

**Project/source/license:** [C qrcodegen.h](https://github.com/nayuki/QR-Code-generator/blob/master/c/qrcodegen.h), [repository](https://github.com/nayuki/QR-Code-generator).

The C source header includes the full **MIT license** and supports encoding text/binary payloads into QR Model 2 symbols with selectable error correction. This is directly reusable encoding code with notice retention. It does not implement a contact-management service, camera scanner, encryption or user consent.

**Useful reuse:** render an intentionally displayed short URL or token using a display already on the badge; avoid adding a radio solely for that interaction. **Limits:** this is usually phone-to-badge-display interaction unless the other badge has a camera/scanner. A static QR containing personal data can be photographed and copied. A URL may require connectivity; use a deliberately chosen offline payload or defer synchronization if offline operation matters. Validate scan success at actual screen size, contrast, refresh behavior and event lighting.

### Comparison of candidate interaction methods


| Option | Practical role | Phone-free? | What it does not establish |
|---|---|---|---|
| BLE advertisements plus an application exchange | Opt-in discovery and optional phone interoperability | Badge-to-badge operation can be phone-free | Accurate range, actual conversation, or consent from merely receiving advertisements |
| ESP-NOW | Fast local badge messaging, games, event signals | Yes; no access point is needed for the local link | Normal phone interoperability, fine ranging, or application delivery without acknowledgements |
| NFC tag/reader | Deliberate tap interaction | Yes only if badge hardware supports the necessary active roles | Passive-tag-to-passive-tag exchange, secret identity, or universal phone peer-to-peer support |
| Displayed QR | Lowest-complexity intentional phone handoff when a screen exists | Usually no; a reader/camera is needed | Mutual consent, privacy of visible payloads, or network access |
| SocioPatterns-style sensing | Research into calibrated face-to-face proximity | Detection can be local; historical deployment used readers | Transfer of published accuracy to a different board, enclosure or crowd |

These are engineering interpretations of the sources above. The phone-facing path should remain separate from an ESP-NOW link; consider BLE, a normal Wi-Fi service, QR, NFC, USB, or a gateway if a phone must later retrieve data. Avoid advertising a seamless no-app browser workflow before testing the actual browsers/operating systems.

### Privacy and validation requirements

- Separate “visible/discoverable,” “exchange contact,” and “save interaction history” controls. Default-off logging is a reasonable candidate consistent with the stated opt-in direction, not an already selected UX.
- Prefer event-scoped pseudonymous identifiers and minimal payloads. Do not broadcast names, email addresses or permanent profile identifiers just to detect nearby badges. Rotating a radio address does not help if the application payload remains uniquely identifying.
- Treat encounter graphs as potentially identifying even without names. Specify who can resolve identifiers, whether anything leaves the badge, deletion behavior, retention, and whether both participants opt in.
- A deliberate button/tap/scan plus a confirmation screen can support intentional exchange. Authenticate/confirm the intended peer; proximity thresholds alone are vulnerable to false positives and impersonation.
- Test missed encounters, false positives, distance bins, wearer orientation, badge placement, crowd density, enclosure effects, Wi-Fi interference and simultaneous traffic. Label outputs “nearby” or “radio encounter” until stronger claims are validated.
- Four-hour meetup operation needs a measured power budget under realistic scan/receive/display activity, with margin. Marketing battery-life examples for occasional remote-control transmitters do not establish continuous-discovery badge runtime.

## Agent-assisted KiCad and PCB workflows

### Official KiCad CLI: checks, preview outputs, fabrication exports

**Commands:** [KiCad 10.0 CLI manual](https://docs.kicad.org/10.0/en/cli/cli.html). **Licensing:** [KiCad program/documentation licenses](https://www.kicad.org/about/licenses/), [library exception](https://www.kicad.org/libraries/license/).

The CLI supports schematic ERC/BOM/netlist/PDF/SVG and PCB DRC/Gerber/drill/position/STEP/GLB exports. DRC supports JSON reports, schematic parity, severity filters, zone refill, and `--exit-code-violations`; ERC has a corresponding failure exit option. Jobsets can collect repeatable output tasks. This is a strong basis for future server-side artifact generation and CI.

**Licensing:** KiCad code is mostly **GPL-3.0-or-later**, with third-party exceptions. Documentation is GPL-3.0-or-later or CC BY 3.0-or-later. Official libraries are **CC BY-SA 4.0 with an explicit design/output exception**: merely using them does not impose that license or attribution on the resulting design. Redistributing library collections retains share-alike and attribution obligations. Third-party libraries need separate review.

**Limit:** a passing rule check verifies encoded rules, not unstated electrical intent, thermal safety, RF performance or manufacturer acceptance.

### Official KiCad IPC API: preferred direction for new integrations

**Source:** [IPC API for add-on developers](https://dev-docs.kicad.org/en/apis-and-binding/ipc-api/for-addon-developers/).

KiCad introduced IPC in 9.0 as a more stable, language-independent interface. The current official documentation makes a crucial version distinction: **KiCad 9 and 10** IPC connects to a running GUI, supports the PCB editor, and does not handle plotting/export. **KiCad 11** adds headless CLI server operation, export support and schematic-editor plugins. Do not silently use master/11 documentation while promising a stable 9/10 deployment.

**Useful reuse:** live board inspection/editing, with official CLI alongside it for stable-version checks/exports. **Limits:** API coverage is still evolving; pin KiCad, client bindings, commands and tests. Do not assume the API supports every GUI operation. The program license is described in record 7; independently inspect the selected client-library license before bundling it. No autonomous electrical-design correctness is claimed by the API.

### Official pcbnew/SWIG automation: existing capability, transition risk

**Source:** [KiCad PCB Python bindings](https://dev-docs.kicad.org/en/apis-and-binding/pcbnew/index.html).

The documented `pcbnew` Python bindings can load/manipulate/save PCB files without a running PCB editor and have a substantial plugin history. KiCad explicitly calls this a raw binding layer rather than a stable API. The page says it is deprecated from 9.0 and currently planned for removal in 11.0; new development should use IPC.

**Useful reuse:** pragmatic automation of an existing version-pinned workflow, particularly if tools already depend on it. **Limits:** major-version coupling and migration work; historical PCB bindings are not a schematic API. A web pipeline should isolate this backend behind versioned artifact contracts rather than encode it everywhere. KiCad's program license applies to KiCad code; inspect any wrapper separately. This is a documented legacy interface, not proof that every third-party script using it is reliable.

### SKiDL: mature circuit-as-Python lineage

**Project:** [SKiDL README](https://github.com/devbisme/skidl/blob/master/README.md). **License:** [MIT LICENSE](https://github.com/devbisme/skidl/blob/master/LICENSE).

SKiDL describes circuits as Python, produces KiCad netlists, provides electrical-rule checks, and supports reusable/hierarchical circuit modules. The current README also advertises editable KiCad schematics and SVG output for KiCad 6–10; older summaries claiming it can *only* emit netlists are now incomplete.

**Useful reuse:** explicit connectivity, tested parametrized blocks, code review and generated design variants. **Verified licensing:** **MIT** for SKiDL, with required notices. That does not relicense imported symbols, footprints, models, user circuit modules, or third-party dependencies. **Limits:** the library does not establish that a generated circuit is electrically appropriate or a PCB is correctly routed. Evaluate schematic-generation readability and target-version compatibility on a small known circuit before using it as a future production pipeline foundation. No SKiDL execution or output validation was performed in this research.

### atopile: declarative electronics and reusable modules

**Project:** [atopile README](https://github.com/atopile/atopile/blob/main/README.md). **License:** [MIT LICENSE](https://github.com/atopile/atopile/blob/main/LICENSE).

atopile supplies a declarative electronics language, compiler and toolchain with units, tolerances, assertions, component constraints and reusable modules. Its documented workflow updates KiCad layout files and still identifies placement/routing in KiCad as a distinct step, followed by checks and manufacturing outputs.

**Useful reuse:** an agent-friendly textual source of design intent, reusable verified modules and version control. **Verified licensing:** **MIT** for this repository. Registry packages, examples, generated/downloaded assets, parts data and dependencies need their own license checks. **Limits:** do not infer autonomous correct layout or a human-readable traditional schematic deliverable from the ability to build a PCB file. If the future web pipeline must emit a schematic, verify that exact artifact independently. It is a promising option to benchmark, not a selected replacement for KiCad or “Harvest.” No build was run here.

### KiCad MCP servers: integration prior art, not a correctness oracle

**Specific project:** [mixelpixx/KiCAD-MCP-Server README](https://github.com/mixelpixx/KiCAD-MCP-Server/blob/main/README.md). **License:** [MIT LICENSE](https://github.com/mixelpixx/KiCAD-MCP-Server/blob/main/LICENSE). **Successor license distinction:** [Konnect LICENSE, AGPLv3](https://github.com/mixelpixx/Konnect/blob/main/LICENSE).

This project exposes schematic/PCB/parts/manufacturing operations to agents via MCP. Its own current release notes document fixes for consequential problems, including Gerber export previously reporting files without writing them, malformed schematic data, and failed routing imports previously reported as successful. This transparency makes it useful prior art, while reinforcing independent output validation.

**Verified licensing:** the inspected Python/TypeScript repository is **MIT**. Its README points to a Rust/IPC successor, Konnect, whose LICENSE is **AGPLv3**, not MIT; assess network-service obligations before reuse. Many unrelated repositories share “kicad-mcp” names, so specify owner, repository and commit. **Assessment:** experimental integration candidate for this badge until locally tested, not established end-to-end autonomous engineering. Pin versions, use disposable test projects, compare native exports/netlists, and rerun official checks. No server was installed or benchmarked.

### Reproducible checks for a future implementation


This is a proposed review process, not implementation or a selected toolchain:

1. **Define the artifact contract first.** Preserve native schematic, PCB and project files; exact part/footprint/model references; a BOM with manufacturer part numbers and DNP/variant state; a machine-readable netlist; and versioned build settings. Generated previews are secondary views of the same revision.
2. **Pin the build.** Record tool versions, library snapshots, package/dependency locks and source commit. Run in a clean environment without implicit machine-local library paths. If “Harvest” already supplies any of these outputs, inspect its real contract before choosing an adapter.
3. **Compare meaning, not just file existence.** Check component counts, reference designators, pin-to-net mapping, variants and board/schematic parity. Ensure generated artifacts correspond to the reviewed revision, not stale files.
4. **Run native checks.** Preserve ERC/DRC reports, rule settings and explicit waivers. Refill zones for the checked release. Generate schematic PDF/SVG, board renders/3D, Gerbers, drills, BOM and placement files from that same revision.
5. **Human engineering review remains a release gate.** Inspect power-tree limits, regulator stability, battery protection/charging, USB and ESD, boot/strap pins, connector polarity, decoupling, analog/RF paths, antenna keepout, mechanical tolerances, part availability and assembly orientation. Validate every sourced footprint against the actual part drawing.
6. **Fabricator and prototype review.** Confirm the chosen manufacturer's rules and stackup, inspect exported CAM data independently, and obtain assembly-specific BOM/position conventions. Prototype and measure current, temperature, charging, RF behavior and the four-hour usage profile before committing to a batch.

The reusable asset should be a tested, documented module plus its assumptions and evidence, not merely a prompt or generated board. Choosing an open-source license for new badge code/hardware is a separate project decision; tool licenses do not automatically license the resulting design.

## Enclosure and industrial design prior art


### Parametric enclosure tooling

[YAPP Box](https://github.com/mrWheel/YAPP_Box) is an established OpenSCAD generator for PCB-sized enclosures. It exposes board dimensions, clearances, standoffs, cutouts, snap joins, and screw/insert features. Its [MIT license](https://github.com/mrWheel/YAPP_Box/blob/main/LICENSE) permits reuse with the required notices. This is a useful route for a text-driven, diffable mechanical prototype. It is not an automatic design-for-manufacture or fit validator.

[Inkplate 6PLUS hardware](https://github.com/SolderedElectronics/Inkplate-6PLUS-Hardware) includes a “3D printable case” directory alongside schematic/Gerber/BOM material. It is a useful packaging reference for a display, frontlight, touch layer, and battery. The visible root tree did not establish a standalone license for those case assets, so do not copy them on the strength of “open source” wording alone.

The [CDC hardware repository](https://github.com/riatlabs/cdc-badge) and [Threejs enclosure repository](https://github.com/hervestudio/Speaker-Badge-enclosure) provide more badge-specific examples. Source CAD is more adaptable than STL-only geometry; an STL is a manufacturing mesh, not a substitute for a dimensioned source model.

### Candidate construction approaches

These are engineering options inferred from the references, not selected materials or validated designs:

| Approach | What it makes easy | What needs checking |
|---|---|---|
| Exposed PCB with a rear cover | Visible electronics, low part count, easy probing | Glass protection, sharp edges, battery protection, sweat and snagging |
| Laser-cut clear plates and spacers | Flat transparent look, fast small-batch iteration | Edge finish, dust, FPC protection, screw count, lanyard loads |
| Printed translucent shell | Fast geometry changes, integrated bosses and light partitions | Layer visibility, optical diffusion, tolerance, impact and heat behavior |
| Printed frame with clear front window | Separate structural and optical functions | Window glare, scratching, bezel pressure, extra assembly |
| Molded clear or translucent shell | Repeatability and polished finish at sufficient volume | Tooling cost, draft, wall thickness, ejection, supplier DFM and minimum order |

A prototype should test the display in the actual optical stack. A clear window can add reflections; translucent material useful for LEDs should not obscure the name display. A small diffuser or partition per indicator may make three to five affinities more legible than one undivided glow.

### Mechanical and radio checks for a later phase

- Use the exact glass, carrier-board, FPC, connector, and battery drawings. Protect the display edge and flex cable from lanyard loads and enclosure compression.
- Preserve charging and recovery access without routine disassembly. Separate a real battery disconnect/ship state from a software screen-off state.
- Provide a replaceable wear path for a loaner pool: battery, lanyard, fasteners, and scratched window should not force total replacement.
- Place the antenna with the enclosure, battery, display, LEDs, and worn body in mind. Espressif's [ESP32-S3 layout guidance](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32s3/pcb-layout-design.html) recommends antenna clearance, explicitly considers the housing, and requires end-product range/throughput testing. A transparent shell is not proof of RF neutrality.
- Convey roles/affinities with text, position, or symbols as well as color. This applies the [W3C use-of-color principle](https://www.w3.org/WAI/WCAG22/Understanding/use-of-color.html) to the physical interface; it is not a claim of hardware WCAG certification.

## Power and loaner fleet research


### Power path and charging references

[TI BQ24074](https://www.ti.com/product/BQ24074) is an established one-cell charger reference with power-path management, thermal regulation, and battery-temperature monitoring. [Microchip MCP73871](https://www.microchip.com/en-us/product/mcp73871) and [Adafruit's explanation of load sharing](https://learn.adafruit.com/usb-dc-and-solar-lipoly-charger/using-the-charger) illustrate why running a device while charging is a distinct design problem. These are comparison references, not chosen ICs, and product documentation is not an open-hardware license.

For a later schematic review, distinguish the charger, cell protection, system power path, regulator, fuel gauge, and storage disconnect. A board advertised as a “LiPo charger” does not establish that all those functions exist. Charging current and temperature limits must follow the actual cell and charger documentation.

### Four-hour use is a measurement requirement

Do not infer capacity from the e-paper's static-image power alone. Measure representative operating states: radio advertising, scanning, connection bursts, display refresh, worst-case LED brightness, user interaction, charging, and storage/off. Document average battery-side current and peak demand, including regulator losses and voltage drop.

For an explicitly illustrative calculation only, 80 mA average at the battery over four hours consumes 320 mAh. Reserving 25% of nominal capacity would imply at least about 427 mAh before additional aging, temperature, and measurement margins. **80 mA is an assumption, not a prediction for this badge.** The correct capacity may change substantially after radio/LED tests.

### Dock and fleet questions

No complete, verified multi-badge charging dock was selected by this research. A later comparison should include ordinary USB charging as a baseline and a keyed contact dock as a separate subsystem. For a contact dock, evaluate polarity protection, exposed-contact shorts, per-slot fault isolation, contact wear/cleaning, insertion tolerance, and aggregate supply/thermal load. Do not simply parallel cells or charger outputs.

The operational design should cover:

- Inventory identity separate from attendee identity.
- Charge/readiness indication that a volunteer can understand quickly.
- A reversible provisioning flow for a new borrower.
- Removal of the prior borrower's contact data, proximity history, Wi-Fi settings, and stale e-paper content before reissue.
- Recoverable firmware updates and a known-good offline experience when venue Wi-Fi fails.
- A storage state and periodic inspection policy appropriate to the chosen cells.
- A personal-unit handoff that explains ownership, update access, reset, and how to stop broadcasts.

These are proposed evaluation criteria, not established policy or authorization to collect attendee data.

## Reuse and licensing checklist

Treat licensing as an input to architecture, not a cleanup task after code is copied.

- Record licenses independently for hardware source, firmware, bootloader, display driver, enclosure source, fonts, icons, documentation, and manufacturing outputs.
- For permissive licenses, retain required notices and check patent/trademark terms where relevant. MIT does not make unrelated branding or assets reusable.
- For GPL/LGPL or reciprocal hardware licenses, determine the obligations for the actual combined work and distribution method. Selling units at cost or lending them does not by itself eliminate license obligations.
- Do not mistake a license on a design tool for a license on every design generated with it; conversely, embedded libraries, reference designs, or templates can carry their own terms into a deliverable.
- A vendor datasheet or downloadable schematic is evidence, not necessarily a grant to redistribute the document or copy all design assets.
- Keep a license inventory and corresponding source package for anything actually shipped. The summaries here are engineering screening notes, not legal clearance.

## Open decisions for Michael

These questions organize later work. None is a blocker to using this research, and none has been answered implicitly by including a reference.

1. **Display envelope:** Is “three inches” the desired active display width, bare panel width, or complete badge width? Is the four-color alternative worth slower refresh and a separate software path?
2. **Primary purpose:** Is the first version mainly a readable name badge, a playful social device, or a hardware development platform? Which functions must survive without a phone or venue network?
3. **Radio interaction:** Is coarse nearby discovery enough? Does contact exchange require a button gesture on both badges, a phone scan, or an NFC tap? What feedback proves it completed?
4. **Privacy:** What may be broadcast, stored locally, uploaded, and retained? Are there different policies for optional affinity signals, contact details, and encounter history?
5. **Power:** How bright and continuous are the LEDs? How often is the screen updated? How long must a charged unit remain ready in storage?
6. **Fleet model:** How many loaners, who provisions/resets them, and does the dock need data as well as power? What is the repair and battery replacement policy?
7. **Cost target:** What are the prototype and production quantities, acceptable assembled cost, acceptable volunteer assembly time, and spare allowance?
8. **Openness:** Is the intended release permissive, reciprocal, or mixed by subsystem? How much firmware/library copyleft is acceptable?
9. **Harvest integration:** Which existing tools, repositories, schemas, and accepted outputs should be reused? What is a later web interface allowed to generate or submit automatically?

## Suggested evidence before a later hardware commitment

This is a research agenda, not an instruction to start implementation or order parts.

| Evidence | What it resolves |
|---|---|
| Full-scale paper layout and physical stack dimensions | Whether the name, QR code, indicators, lanyard, glass, and battery fit comfortably |
| Candidate display test with exact panel and revision | Legibility, grayscale behavior, ghosting, refresh latency, and supported partial updates |
| Battery-side current traces across intended modes | Four-hour runtime, peak supply demand, LED/radio cost, and storage drain |
| Worn-device radio test in a realistic crowd | False proximity, body shielding, coexistence, range, and battery tradeoffs |
| Consent and exchange interaction trial | Whether attendees understand discovery versus sharing and can withdraw or clear data |
| Enclosure fit and handling trial | Display pressure, FPC clearance, buttons, glare, diffusion, lanyard strain, repairability |
| Small fleet provisioning and reset rehearsal | Check-in workload, stale identities, offline operation, recovery, and returned-unit readiness |
| Complete license and supply audit | Whether selected files may be reused and parts can be sourced consistently |

## Handoff contract for future implementation work

An implementation agent should read this file as a source map and unresolved design brief. It should not promote candidates to requirements, assume procurement permission, or present unbuilt designs as validated hardware.

Before editing a hardware repository, establish the approved scope and produce a versioned specification that records:

- Required, optional, and explicitly deferred features.
- Exact display and MCU/module part numbers, revisions, interfaces, and verified pin constraints.
- Dimensioned mechanical stack, PCB outline, mounting/lanyard locations, connector orientation, antenna and battery keepouts.
- Power modes, target runtime, storage behavior, charger/cell constraints, and measured or explicitly assumed currents.
- Protocol roles, exchanged fields, consent states, identity lifetime, retention, reset, and update/recovery behavior.
- Toolchain versions, dependency commits, library paths, licenses, and reproducible build commands.
- Acceptance criteria for schematic review, ERC, DRC, firmware tests, simulator limitations, mechanical fit, power, RF, and manufacturing review.

A later reproducible release would normally contain editable schematic and PCB source, a readable schematic export, BOM with manufacturer part numbers and approved alternatives, placement data, fabrication outputs, 3D board/enclosure source and exports, firmware source/build artifacts, programming and test instructions, license notices, and check reports. Generate those from one reviewed revision. A good-looking 3D render or a clean DRC report alone does not establish electrical correctness or safe production readiness.

## Research limits

This compilation does not include a costed BOM, stock reservation, component purchase, prototype, schematic, PCB, enclosure design, firmware build, radio measurement, battery validation, manufacturing review, regulatory assessment, or legal opinion. Source repositories and vendor pages can change after the research date; refresh them and pin revisions before reuse. Where a license or hardware asset was not established, the corresponding entry says so rather than treating the missing evidence as permission.
