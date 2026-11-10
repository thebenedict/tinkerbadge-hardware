# Independent endpoint-checker review

Temporary review artifacts below are identified by filename only; these intermediate files are not distributed. Published source outputs and repeatable checks are linked from the [current verification record](verification.md).

2026-11-09. Reviewed the checker and existing four negative tests. The same-basename split-net check correctly prevents separate sheet-local nets from passing merely because their final names match. Missing and unexpected leads, incorrect net names, net merges, absent components and duplicate exported endpoints are rejected.

Found and repaired one fail-closed input defect under integration-owner instruction: list-form contract pins were converted to a dictionary before checking duplicates. The checker now rejects repeated physical numbers first, including numeric/string equivalents. Current reviewed contracts had no such duplicates.

Replaced tests that depended on mutable `display.net` and generated NC-name spelling with a frozen exported-netlist/contract fixture under `tests/fixtures/display_snapshot`. Its manifest pins both hashes; tests verify them and mutate only temporary copies. Twelve deterministic tests pass. Live display, MCU and power exports also still pass the hardened checker. The fixture is test data, not current design authority.

Endpoint PASS is intentionally separate from exact MPN, value, rating, footprint and custom-property correctness, ERC, visual inspection and electrical/prototype qualification. One regression test explicitly demonstrates this boundary by changing a resistor value without changing its endpoints. Separate field audits remain mandatory.

Pre-repair observations, repair hashes and test/fixture evidence are in `contract_checker_review.json`.
