# Contract-checker fixture

This is a frozen KiCad-exported netlist and its matching reviewed contract, captured for deterministic checker tests. They are test data, not current design authority. The manifest pins both SHA-256 hashes. Tests verify hashes and use this isolated contract snapshot rather than mutable temporary build artifacts or the current design contract.

Regenerate this fixture only deliberately after reviewing a new source/export pair, and update the manifest together. Test mutations occur only in temporary directories. Never treat this fixture as native KiCad source or use it to generate manufacturing files.

Endpoint checking does not validate MPN, value, voltage/tolerance, footprint, custom metadata or electrical performance; those require the separate source, field, ERC, visual and prototype checks.
