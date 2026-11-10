# MCU circuit decisions

See [component facts](../components/ESP32-S3-WROOM-1-N16R8.md) and `mcu_contract.json`. Use the JSON as the maintained assignment source. 33 exposed usable GPIOs include boot straps and UART; 29 non-strapping GPIOs are fully allocated with UART retained. A TCA9534PWR on the onboard I2C bus handles charger status and accessory enable/fault. There is no spare general-purpose GPIO commitment.

Dock identity uses authenticated radio/USB firmware and a separately sensed dock contact, not power delivery alone. Physical dock communications remain a subsequent design decision; no automatic erasure is implied by presence.
