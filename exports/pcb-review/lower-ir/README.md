# Lower IR placement review

Native PCB SHA256 `a7ac2778f423c3847b9a3a6200f00446d6a960bbee242b6ef8da7aff5ed24b84`, KiCad 10.0.8. Updated 10 November 2026.

The complete nine-part IR circuit is repacked below the display and above/between D405 and D406. U504 is at (137.75,168.5),180°; D501 at (150,168.5),0°. All other parts, outlines, groups and keepouts are unchanged. The glass ends at y164.9, leaving receiver/emitter courtyard gaps of 0.805/1.855 mm. The forward optical faces remain exposed; final angular coverage, isolation and enclosure fit remain to test.

Independent native comparison restores all 186 complete footprint records after inverse poses, and independent DRC finds no new failure. Existing findings remain: four USB hole errors, one silk-edge warning, 390 unrouted items and nine missing footprints. Contract/property checks pass; ERC has zero errors and its existing one warning. No routing was added.

The receiver filter and transmitter driver remain local. Use dedicated local ground vias and continuous return paths; longer MCU signal routes are manageable but not yet laid out. The unresolved dock reservation is not a certified contact/tail fit.

The user-selected NFC plan remains an integral B.Cu coil with front/inner clearances and front-side tag/tuning parts. No antenna copper or tuned geometry exists. Human placement review and the outstanding RF/flex/optical/parts/manufacturing gates remain.
