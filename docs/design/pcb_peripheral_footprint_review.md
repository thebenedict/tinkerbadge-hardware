# Peripheral footprint verification

Temporary review artifacts below are identified by filename only; these intermediate files are not distributed. Published source outputs and repeatable checks are linked from the [current verification record](verification.md).

Review date: 2026-11-09. Independent comparison of original manufacturer diagram pixels with installed/local footprint geometry. No schematic, board or footprint library was edited by this reviewer.

**Placement-stage result:** nine component types have compatible installed or source-derived custom geometry. J502 remains unassigned because key-to-pin orientation is unverified. This is not manufacturing, assembly or routing approval.

Coordinates below use footprint top/component view, +X right, +Y down, at footprint rotation 0 degrees. All dimensions are mm. Courtyard bounds are xmin, ymin, xmax, ymax. Source-derived courtyards are engineering choices, not manufacturer guarantees.

Machine-readable source hashes, dimensions, actual file hashes, pad readback and model presence checks: `pcb_peripheral_review.json`.

## Decisions and exact geometry

### D401, D402, D403, D404, D405, D406, D407, D408: WS2812C-2020-V6

Decision: **accept_installed_geometry**. Candidate: `LED_SMD:LED_WS2812B-2020_PLCC4_2.0x2.0mm`.

Nominal body/envelope axes x/y/height: [2.2, 2.0, 0.84]. Courtyard/reserve bounds: [-1.52, -1.25, 1.52, 1.25].

Source: `docs/datasheets/WS2812C-2020-V6.pdf`, pages 2; SHA256 `8465b5176b9f31d77c177c279013e18cfb6f13737fbfbcd724c3562e437cbcf9`. Actual diagrams: `docs/datasheets/peripheral_views/WS2812C-page2.png`.

- Installed B-2020 footprint copper geometry and four-pad numbering are compatible with exact C-2020-V6 drawing after 180-degree rotation relative to the source top-view orientation.

- Source top view: DI/3 upper-left, GND/2 upper-right, VDD/4 lower-left, DO/1 lower-right. Installed footprint orientation is 1 upper-left, 2 lower-left, 3 lower-right, 4 upper-right. Do not mirror.

- Source four square lands are 0.7 x 0.7, inner x gap 1.13 and inner y gap 0.40; centers are therefore +/-0.915 and +/-0.55.

- Footprint name is not a substitution authorization for other WS2812 variants. Confirm component marking against actual pin 1 during assembly; installed generic bevel/stripe is not an independently certified C-V6 package drawing.

- Body including side terminal structure is 2.2 x 2.0; existing 2.0 x 2.0 shorthand component note should not be used as full mechanical envelope.


| Pad | Top-view center x,y | Land width,height | Rotation |
|---|---|---|---|

| 1 | [-0.915, -0.55] | [0.7, 0.7] | 0 deg |

| 2 | [-0.915, 0.55] | [0.7, 0.7] | 0 deg |

| 3 | [0.915, 0.55] | [0.7, 0.7] | 0 deg |

| 4 | [0.915, -0.55] | [0.7, 0.7] | 0 deg |


Actual file snapshot: `/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints/LED_SMD.pretty/LED_WS2812B-2020_PLCC4_2.0x2.0mm.kicad_mod`, SHA256 `dc508cda207304f83f9e0fd9e9e1cad0f42e2e87cb059d8ab9ea73b9702bd10d`. Electrical land/number readback: PASS.



### D409: HSMF-C165

Decision: **custom_geometry_verified**. Candidate: `Tinkerbadge:HSMF-C165`.

Nominal body/envelope axes x/y/height: [1.6, 0.8, 0.5]. Courtyard/reserve bounds: [-1.25, -0.8, 1.25, 0.8].

Source: `docs/datasheets/HSMF-C165_AV02-0584EN.pdf`, pages 2, 7; SHA256 `920539983de9e38efa1043f59639fbec6dbd360e0004761ecfb4e6c552ef725a`. Actual diagrams: `docs/datasheets/peripheral_views/HSMF-page2.png`, `pcb_hsmf_p7.png`.

- No compatible installed four-terminal 0603 footprint established. Generic two-terminal LED_0603 is invalid.

- Source p7 Fig8: lands 0.70 x 0.40; inner gaps 0.60 horizontal and 0.30 vertical. Source p2 has cathode stripe on right.

- Pad 1 green anode upper-left, 2 red anode lower-left, 3 green cathode upper-right, 4 red cathode lower-right.

- Final custom file copper passed readback. Right cathode stripe added and invented package bevel removed; independently verified.


| Pad | Top-view center x,y | Land width,height | Rotation |
|---|---|---|---|

| 1 | [-0.65, -0.35] | [0.7, 0.4] | 0 deg |

| 2 | [-0.65, 0.35] | [0.7, 0.4] | 0 deg |

| 3 | [0.65, -0.35] | [0.7, 0.4] | 0 deg |

| 4 | [0.65, 0.35] | [0.7, 0.4] | 0 deg |


Actual file snapshot: `Tinkerbadge.pretty/HSMF-C165.kicad_mod`, SHA256 `0acf2ebd509f5fa1ac51ddd27e609cf3f7672486eda42cc8a60e558a964b200d`. Electrical land/number readback: PASS.



### SW401, SW402: SKSCLBE010

Decision: **custom_geometry_verified**. Candidate: `Tinkerbadge:SKSCLBE010`.

Nominal body/envelope axes x/y/height: [3.5, 2.9, 1.25]. Courtyard/reserve bounds: [-2.75, -1.7, 2.75, 2.35].

Source: `docs/datasheets/SKSCLBE010_SKSC_catalog.pdf`, pages 1, 2; SHA256 `cc8baff4e324df2cf6a71b9319ab9dbfd9e56d2e589dce392456b8afc99ca5bb`. Actual diagrams: `docs/datasheets/peripheral_views/SKSCLBE010-catalog-p2.png`, `land.png`, `outline.png`.

- Exact SKSCLBE010 catalog row selects Drawing 2. Manufacturer terminal circuit permanently commons horizontal pair 1/2 and pair 3/4; pressing joins pairs.

- Top-view convention: actuator towards +Y; pads 1/2 lower row, 3/4 upper row. Source land pattern outer span 5.0, inner x gap 2.2, outer y span 2.2, inner y gap 0.4 yields 1.4 x 0.9 lands.

- Locating holes are centered at y +/-0.9, not pad-row y +/-0.65; the 0.25 mm offset is important. NPTH hole diameter 0.8 +/-0.05, centers 1.8 +/-0.05 apart; component bosses diameter 0.6 +/-0.1, protrusion 0.5 +/-0.1.

- Main body extends x +/-1.75 and y +/-1.45. Actuator width 1.6 extends from y=1.45 to y=2.10. Full 3.55 mm depth envelope has center y=+0.325 relative to land origin. Do not recenter holes on this envelope.

- No board-edge/cutout requirement was invented. Validate actual switch, edge access, enclosure and mechanical actuation before release. Initial custom file pad numbering and both holes passed readback.


| Pad | Top-view center x,y | Land width,height | Rotation |
|---|---|---|---|

| 1 | [-1.8, 0.65] | [1.4, 0.9] | 0 deg |

| 2 | [1.8, 0.65] | [1.4, 0.9] | 0 deg |

| 3 | [-1.8, -0.65] | [1.4, 0.9] | 0 deg |

| 4 | [1.8, -0.65] | [1.4, 0.9] | 0 deg |


Mechanical holes: [{"number": "", "at_mm": [0, -0.9], "drill_mm": 0.8, "type": "np_thru_hole"}, {"number": "", "at_mm": [0, 0.9], "drill_mm": 0.8, "type": "np_thru_hole"}].


Actual file snapshot: `Tinkerbadge.pretty/SKSCLBE010.kicad_mod`, SHA256 `d7d195335d2923ec63b2ebd0faeb92e00e9ff43b965cf526004bfd511e84fa68`. Electrical land/number readback: PASS.



### U501: BH1730FVC

Decision: **custom_geometry_verified**. Candidate: `Tinkerbadge:BH1730FVC_WSOF6`.

Nominal body/envelope axes x/y/height: [2.6, 1.6, 0.75]. Courtyard/reserve bounds: [-1.9, -1.15, 1.9, 1.15].

Source: `docs/datasheets/BH1730FVC.pdf`, pages 2, 19; SHA256 `012d391bb2712fc3f22d6596e83ad49075e294dd797b5a40634467dc567d0572`. Actual diagrams: `docs/datasheets/peripheral_views/BH1730-p2.png`, `docs/datasheets/peripheral_views/BH1730-p19.png`.

Source: `docs/datasheets/WSOF6_ROHM_Rev005.pdf`, pages 7; SHA256 `ad2aa218a499388d66fd5b040bad15cd7a4605c7a82713ee00d027425facc884`. Actual diagrams: `pcb_wsof6_p7.png`.

- No installed WSOF6 found. Official ROHM supplementary WSOF6 package information Rev005 p7 provides manufacturer land pattern.

- Six lands 0.55 x 0.25; inner horizontal gap 2.20, hence x +/-1.375; vertical pitch 0.50. Datasheet p19 top-view outline rotated clockwise 90 degrees gives pin1 upper-left.

- Body nominal 2.6 x 1.6, maximum including burr 2.8 x 1.8; terminal span 3.0 +/-0.1; height 0.75 max.

- ROHM explicitly omits center pad from land pattern because connection quality is not guaranteed and no electrical connection is required. No center land, paste aperture or numbered pad. Preserve insulation under exposed metal.

- Keep the optical sensing face uncovered and separate it optically from badge LED/IR light. Initial custom copper and omission of EP passed readback.


| Pad | Top-view center x,y | Land width,height | Rotation |
|---|---|---|---|

| 1 | [-1.375, -0.5] | [0.55, 0.25] | 0 deg |

| 2 | [-1.375, 0] | [0.55, 0.25] | 0 deg |

| 3 | [-1.375, 0.5] | [0.55, 0.25] | 0 deg |

| 4 | [1.375, 0.5] | [0.55, 0.25] | 0 deg |

| 5 | [1.375, 0] | [0.55, 0.25] | 0 deg |

| 6 | [1.375, -0.5] | [0.55, 0.25] | 0 deg |


Actual file snapshot: `Tinkerbadge.pretty/BH1730FVC_WSOF6.kicad_mod`, SHA256 `6351d09a8d496431e3f72950a7aa1ab48668a1f268227726ef3c075db028c7a6`. Electrical land/number readback: PASS.



### U502: LIS2DW12TR

Decision: **accept_installed_geometry**. Candidate: `Package_LGA:LGA-12_2x2mm_P0.5mm`.

Nominal body/envelope axes x/y/height: [2.0, 2.0, 0.7]. Courtyard/reserve bounds: [-1.25, -1.25, 1.25, 1.25].

Source: `docs/datasheets/LIS2DW12TR.pdf`, pages 9, 61; SHA256 `87da41966ff6bfe17a47db2c1940173d490aa4dfb7af2cce1a5dd5c0260c8735`. Actual diagrams: `docs/datasheets/peripheral_views/LIS2DW12-p9.png`, `docs/datasheets/peripheral_views/LIS2DW12-p61.png`.

- Installed 12-terminal LGA has correct 2 x 2 body, 0.5 pitch and pin mapping. Source p9 is BOTTOM VIEW and was mirrored to derive the top-view footprint; do not copy the bottom view directly.

- Pin1 upper-left; pins1-4 descend left side, 5/6 along bottom, 7-10 ascend right side, 11/12 along top.

- Package terminals nominal 0.275 x 0.25; installed lands 0.375 x 0.35 expand terminal extent by 0.05 on each side. This is compatible generic library geometry, not an ST certified solder process.

- No EP. Keep away from switch impact/board flex and check ST assembly guidance before fabrication.


| Pad | Top-view center x,y | Land width,height | Rotation |
|---|---|---|---|

| 1 | [-0.7625, -0.75] | [0.375, 0.35] | 0 deg |

| 2 | [-0.7625, -0.25] | [0.375, 0.35] | 0 deg |

| 3 | [-0.7625, 0.25] | [0.375, 0.35] | 0 deg |

| 4 | [-0.7625, 0.75] | [0.375, 0.35] | 0 deg |

| 5 | [-0.25, 0.7625] | [0.375, 0.35] | 90 deg |

| 6 | [0.25, 0.7625] | [0.375, 0.35] | 90 deg |

| 7 | [0.7625, 0.75] | [0.375, 0.35] | 0 deg |

| 8 | [0.7625, 0.25] | [0.375, 0.35] | 0 deg |

| 9 | [0.7625, -0.25] | [0.375, 0.35] | 0 deg |

| 10 | [0.7625, -0.75] | [0.375, 0.35] | 0 deg |

| 11 | [0.25, -0.7625] | [0.375, 0.35] | 90 deg |

| 12 | [-0.25, -0.7625] | [0.375, 0.35] | 90 deg |


Actual file snapshot: `/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints/Package_LGA.pretty/LGA-12_2x2mm_P0.5mm.kicad_mod`, SHA256 `79f95a62dac718b00e4cb6153be82f80b0ed27f9691a674a6cd2ef9eeb26a9cf`. Electrical land/number readback: PASS.



### U503: NT3H2111W0FHKH

Decision: **custom_geometry_verified**. Candidate: `Tinkerbadge:NT3H2111W0FHKH_XQFN8`.

Nominal body/envelope axes x/y/height: [1.6, 1.6, 0.5]. Courtyard/reserve bounds: [-1.1, -1.1, 1.1, 1.1].

Source: `docs/datasheets/NT3H2111W0FHKH.pdf`, pages 8, 70, 71; SHA256 `44a7cbee1220999138538341392aacde5a87aed7a284974328e8297b132a20c8`. Actual diagrams: `docs/datasheets/peripheral_views/NTAG-p8.png`, `docs/datasheets/peripheral_views/NTAG-p70.png`, `pcb_ntag_p71.png`, `pcb_ntag_pad_detail.png`.

- No compatible installed XQFN8 SOT902-3 found. Source p8 transparent TOP VIEW establishes 3 terminals on each side and one terminal at each top/bottom center. This is not a conventional 4+4 QFN.

- P71 OUTER crosshatched rectangles are explicitly solder land plus solder paste: 0.45 x 0.27, from D=0.40 and C=0.22 plus 0.025 per edge. Gray inner package silhouette is not copper. All eight lands share these dimensions; top/bottom rotate 90 degrees.

- P71 gray pin1 silhouette height 0.320 must not be mistaken for an enlarged land or shifted pad. The crosshatched land stays centered on the regular +/-0.5 row.

- Source p71 drawing is rotated 180 degrees relative to p8 top pin view. Custom mapping below uses p8 top view, pin1 upper-left.

- Source occupied area Hx/Hy=1.9. Conservative 2.2 square courtyard is a design choice. Center 0.5 x 0.5 region is NOT a solder land: source p8 says center metal not for soldering. No center copper or paste.


| Pad | Top-view center x,y | Land width,height | Rotation |
|---|---|---|---|

| 1 | [-0.6, -0.5] | [0.45, 0.27] | 0 deg |

| 2 | [-0.6, 0] | [0.45, 0.27] | 0 deg |

| 3 | [-0.6, 0.5] | [0.45, 0.27] | 0 deg |

| 4 | [0, 0.6] | [0.45, 0.27] | 90 deg |

| 5 | [0.6, 0.5] | [0.45, 0.27] | 0 deg |

| 6 | [0.6, 0] | [0.45, 0.27] | 0 deg |

| 7 | [0.6, -0.5] | [0.45, 0.27] | 0 deg |

| 8 | [0, -0.6] | [0.45, 0.27] | 90 deg |


Actual file snapshot: `Tinkerbadge.pretty/NT3H2111W0FHKH_XQFN8.kicad_mod`, SHA256 `c921a2eacb3fa641f30e7a92ea19194b1b6943d076a889da2fa830cb34c6bdf2`. Electrical land/number readback: PASS. Eight rectangular lands and no center pad verified.



### D501: IR67-21C-TR8

Decision: **custom_geometry_verified**. Candidate: `Tinkerbadge:IR67-21C_TR8`.

Nominal body/envelope axes x/y/height: [3.1, 2.7, 1.9]. Courtyard/reserve bounds: [-2.5, -1.7, 2.5, 1.7].

Source: `docs/datasheets/IR67-21C-TR8.pdf`, pages 1, 2; SHA256 `8b0cafbc6c75a60d705c078c8027fea96162e198b8125909d2658e66738f527c`. Actual diagrams: `docs/datasheets/peripheral_views/IR67-page1.png`, `docs/datasheets/peripheral_views/IR67-page2.png`.

- Source p2 top view: pin1 anode left, pin2 cathode right; actual cathode bevel lower-right. Plastic body 3.1 +/-0.2 x 2.7 +/-0.2, overall lead span 3.5 +/-0.2; height 1.9 +/-0.2.

- Source recommended reflow lands 1.5 x 2.6, inner gap 1.5; centers x +/-1.5. No additional paste segmentation specified in source.

- Installed LED_Everlight-SMD3528_3.5x2.8mm_67-21ST is rejected: its unequal 1.1 x 2.1 and 2.1 x 2.1 pads at -1.34/+0.81 are for a different LED.

- Final custom copper passed readback. Initial upper-left/anode F.Fab bevel was corrected to the actual lower-right/cathode side; independently verified.


| Pad | Top-view center x,y | Land width,height | Rotation |
|---|---|---|---|

| 1 | [-1.5, 0] | [1.5, 2.6] | 0 deg |

| 2 | [1.5, 0] | [1.5, 2.6] | 0 deg |


Actual file snapshot: `Tinkerbadge.pretty/IR67-21C_TR8.kicad_mod`, SHA256 `669cd066610b7853315045ac2e06625dd131ac128eb0aabe9688d1aba823f930`. Electrical land/number readback: PASS.



### U504: IRM-H638T-TR2

Decision: **accept_installed_geometry**. Candidate: `OptoDevice:Everlight_IRM-H6xxT`.

Nominal body/envelope axes x/y/height: [4.0, 5.0, 4.0]. Courtyard/reserve bounds: [-4.15, -2.75, 4.15, 2.75].

Source: `docs/datasheets/IRM-H638T-TR2.pdf`, pages 1, 6; SHA256 `6ba15dc59077b2a3357495e5cbfe9b68378a275ae1750e02e77f9d6f2663d22e`. Actual diagrams: `docs/datasheets/peripheral_views/IRM-page1.png`, `docs/datasheets/peripheral_views/IRM-page6.png`.

- Source p6 recommended pads 1.5 x 1.1, x centers +/-3.15 and y +/-1.27. Source p1 pin-labeled photo confirms 1 upper-left,2 lower-left,3 lower-right,4 upper-right.

- Source body 5 x 4 is rotated relative to installed footprint body 4 x 5. Lens lies toward pins1/4 (negative Y in installed orientation); preserve receiving field of view.

- Height 4.0 +/-0.3 including lens; total terminal span 7.0 +/-0.3. Installed F.Fab lens is nominal, not optical performance or enclosure proof. Both ground pins required.


| Pad | Top-view center x,y | Land width,height | Rotation |
|---|---|---|---|

| 1 | [-3.15, -1.27] | [1.5, 1.1] | 0 deg |

| 2 | [-3.15, 1.27] | [1.5, 1.1] | 0 deg |

| 3 | [3.15, 1.27] | [1.5, 1.1] | 0 deg |

| 4 | [3.15, -1.27] | [1.5, 1.1] | 0 deg |


Actual file snapshot: `/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints/OptoDevice.pretty/Everlight_IRM-H6xxT.kicad_mod`, SHA256 `17483dc7a14d93027e8845e692d577e81a53e0eaf71a93f6bfa128cab97081d3`. Electrical land/number readback: PASS.



### J501: SM04B-SRSS-TB(LF)(SN)

Decision: **accept_installed_geometry_after_blank_tab_numbers**. Candidate: `Tinkerbadge:JST_SH_SM04B_ProjectTabs`.

Nominal body/envelope axes x/y/height: [6.0, 4.25, 2.9]. Courtyard/reserve bounds: [-3.9, -3.28, 3.9, 3.28].

Source: `docs/datasheets/SM04B-SRSS-TB.pdf`, pages 1, 2; SHA256 `1d07d13f7829795cd9b66e48f2c31a2cf68881140143480e73596305cabc5606`. Actual diagrams: `docs/datasheets/peripheral_views/SM04B-page1.png`, `docs/datasheets/peripheral_views/SM04B-page2.png`.

- Compatible installed source: Connector_JST:JST_SH_SM04B-SRSS-TB_1x04-1MP_P1.00mm_Horizontal. Copy to project library and blank the two MP pad numbers to preserve mechanical-only tabs contract.

- Source side-entry 4-position version has A=3.0, B=6.0, 1.0 contact pitch. Electrical lands 0.6 x 1.55; mounting lands 1.2 x 1.8.

- Top view has contact1 left at x=-1.5, contact row y=-2.0. Side entry toward +Y. Fab body x +/-3.0 and y -1.675 to 2.575.

- Actual library courtyard is a stepped polygon, bounding box recorded here. Cable insertion/removal space beyond courtyard still required. Confirm Qwiic cable end-to-end orientation before release.

- Initial local file geometry, 1-4 pad numbers, and two empty-string mechanical pad numbers passed readback. Internal footprint name remained original library name; file basename is project ID.


| Pad | Top-view center x,y | Land width,height | Rotation |
|---|---|---|---|

| 1 | [-1.5, -2] | [0.6, 1.55] | 0 deg |

| 2 | [-0.5, -2] | [0.6, 1.55] | 0 deg |

| 3 | [0.5, -2] | [0.6, 1.55] | 0 deg |

| 4 | [1.5, -2] | [0.6, 1.55] | 0 deg |


Mechanical-only mounting pads: [{"number": "", "at_mm": [-2.8, 1.875], "size_mm": [1.2, 1.8], "type": "smd"}, {"number": "", "at_mm": [2.8, 1.875], "size_mm": [1.2, 1.8], "type": "smd"}].


Actual file snapshot: `Tinkerbadge.pretty/JST_SH_SM04B_ProjectTabs.kicad_mod`, SHA256 `e64745900f944d009492fab9b12a2ba4c4ea30431a49330d0e1bf83257304558`. Electrical land/number readback: PASS.



### J502: SFH11-NBPC-D03-ST-BK

Decision: **blocked_key_to_pin_orientation**. Candidate: `NONE: mechanical reserve only`.

Nominal body/envelope axes x/y/height: [12.7, 6.0, 8.5]. Courtyard/reserve bounds: [-6.85, -3.5, 6.85, 4.5].

Source: `docs/datasheets/SFH11-NBPC-D03-ST-BK_official.pdf`, pages 1; SHA256 `8bd076918a6a018206a1cce6969b8decce97273ce50e871fe3e8c839e1e73b40`. Actual diagrams: `docs/datasheets/peripheral_views/SFH11-NBPC-D03-ST-BK-page1.png`, `docs/datasheets/peripheral_views/SAOv2-host.png`.

- No exact installed footprint established. Generic 2x3 sockets have correct contact pitch but wrong body/key envelope and must not be accepted from pitch alone.

- Sullins drawing11160 RevJ: body length B=12.70 +0/-0.20, contact span A=5.08, body width6.00, central key width3.70 projecting1.00, height8.50, straight tail3.20; contact0.60 x 0.40.

- Recommended finished PTH hole diameter1.02, 2.54 contact/row pitch. A hypothetical 1.70 diameter copper pad gives0.34 radial annulus; pad diameter is engineering choice, not source specification.

- Sullins drawing contains no electrical contact numbering. Project SAOv2 author top-view graphic gives odd1/3/5 upper and even2/4/6 lower. It does not independently establish the housing-key side relative to those numbers.

- Key drawn on +Y in the mechanical reserve only. Do not treat that side as verified SAO mating polarity. J502 remains unassigned and reserve its full mechanical envelope until actual keyed mating/continuity check.

- Body plus key envelope is12.7 x7.0. Reserve excludes plugged-in add-on body and required tool/insertion space; determine those before board finalization.


Provisional contact centers, NOT accepted key mapping: [{"number": "1", "at_mm": [-2.54, -1.27]}, {"number": "2", "at_mm": [-2.54, 1.27]}, {"number": "3", "at_mm": [0, -1.27]}, {"number": "4", "at_mm": [0, 1.27]}, {"number": "5", "at_mm": [2.54, -1.27]}, {"number": "6", "at_mm": [2.54, 1.27]}].



## Remaining release gates

- Placement approval and all other workflow gates must be resolved before routing.

- J502 remains unassigned until housing key to SAO numbering and actual mating continuity are verified.

- Final board still needs full mask/silk DRC and assembly text review. The initially insufficient small-part silk outlines were removed and independently read back.

- IR67 lower-right cathode bevel and HSMF right cathode stripe are now corrected and read back. Verify physical component marking during assembly.

- Source-derived custom pads were changed from initial roundrects to rectangular source lands and read back. Stencil, mask, fab tolerances and assembler acceptance remain manufacturing review.

- 3D model presence is not package fit certification. Nominal custom blocks cannot validate enclosure, optical windows, actuation, cable insertion or connector mating.


## Source additions and limits

The official ROHM supplementary WSOF6 package PDF and `.source.json` were archived for the missing BH1730 land-pattern evidence. Manufacturer source PDFs and source metadata were hashed, not inferred from vendor CAD or package names. Sources whose mechanical drawings omit numbering were not granted invented pin assignments. Source drawings and local footprint snapshots are separate evidence; later footprint edits require renewed readback.

## Final generated-output verification

Nine component types now have actual generated/installed file readbacks passing electrical pad number, position, size and rotation checks. No unintended extra pads were found. Both SKSC unnumbered NPTH holes and both JST unnumbered SMT retention tabs also pass. Source-derived custom lands are rectangular, small-part silk outlines were removed, HSMF right cathode stripe was added, and IR67 cathode bevel was corrected to lower-right. J502 remains unassigned, with only a mechanical reserve accepted. Seven candidate model references resolve locally. The installed WS2812B-2020 and Everlight_IRM-H6xxT STEP references are absent from this Mac. This does not invalidate copper geometry but leaves a 3D visual gap. Available/custom models remain nominal visual evidence, not dimensional certification.

The WSOF6 supplemental PDF provenance is synchronized in its `.source.json`, BH1730 source record, BH1730 component source section, and `peripheral_inventory.json`.
