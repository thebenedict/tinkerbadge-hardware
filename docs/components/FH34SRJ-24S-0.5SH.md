# FH34SRJ-24S-0.5SH(50) component facts

Hirose FH34SRJ series, 24 positions, 0.5 mm pitch, 1.0 mm above the board, back-flip actuator, **top and bottom contact**. LCSC/JLCPCB C324726. Selected on 11 November 2026 as J301 in place of the bottom-contact FH12-24S-0.5SH(55).

Source: Hirose FH34SRJ catalogue dated Nov.1.2018, 12 pages, SHA-256 `072e59cf…22df7`; URL and hash in [the source record](../datasheets/FH34SRJ-24S-0.5SH.source.json). Pages 3 (connector dimensions) and 4 (PCB pattern, FPC dimensions) were read as rendered images.

## Why this part

The panel drawing names Panasonic AYF532435 (Y5B series), which JLCPCB does not stock. Both parts are 0.5 mm pitch, 1.0 mm high, back-flip, dual-contact connectors for 0.3 mm FPC, and their recommended FPC ends agree:

| | Panasonic Y5B, 24 pin | Hirose FH34SRJ, 24 pin |
|---|---|---|
| FPC width | 12.5 ±0.05 mm (A + 1) | 12.5 ±0.05 mm (G) |
| FPC thickness | 0.30 ±0.03 mm | 0.3 ±0.03 mm |
| Exposed conductor | 1.50 mm min | 1.5 ±0.3 mm |
| Stiffener | 2.50 mm min | 2.5 ±0.3 mm |
| Contact | top and bottom | top and bottom |

A dual-contact connector accepts the panel's flex whichever face its conductors are on, so the contact-side question in the display records no longer decides whether the board works.

## Land pattern (catalogue p4)

- 24 signal lands, 0.3 ±0.05 mm wide × 0.8 ±0.05 mm long, 0.5 mm pitch, 11.5 mm between the first and last (dimension B).
- Two metal-fitting lands, 0.4 × 0.8 mm: 13.1 mm between inner edges (E), 13.9 mm between outer edges (F).
- 3.3 ±0.05 mm from the outer edge of the signal lands to the outer edge of the fitting lands.
- Body 14.0 mm long (A), 3.8 mm deep overall, 2.9 mm housing depth.
- The FPC enters from the fitting-land side; the solder tails and the actuator hinge are on the opposite side.
- Contact No.1 is at the right-hand end when the connector is viewed from above with the tails at the top.

## Pad numbering on this board

The footprint `Tinkerbadge:Hirose_FH34SRJ-24S-0.5SH_PanelOrder` numbers its pads in **panel order**, not Hirose contact order: pad *n* is Hirose contact 25 − *n*.

The reasoning, from the panel drawing (Waveshare 3.7-inch specification, mechanical drawing and detail A):

1. In the panel's front view the flex leaves the left short edge, with pin 1 at the top and pin 24 at the bottom. Its contact end is centred on the glass: 27.5 mm from either long edge, measured from the drawing.
2. The badge mounts the panel with the flex on the right, a 180° in-plane rotation, so pin 1 is at the bottom.
3. The flex folds under the glass about an axis parallel to the short edge. That keeps every conductor at the same height on the board, so pin 1 is still at the bottom where it meets the connector.
4. The connector's mouth faces the right board edge. In that orientation Hirose contact No.1 is at the top.

So panel pin 1 meets Hirose contact 24. J301 sits at (199.4, 137.45), centred on the glass, rotated 90°.

This is derived from drawings. **Dry-fit a real panel before ordering boards**: check that the flex reaches, that pin 1 lands where the footprint expects it, and that the actuator can be closed with the panel tilted up.

## Flex path

Glass edge at x = 202.65, underside 4.5 mm above the board; connector mouth at x = 201.2, about 0.4 mm above the board. With a 2.15 mm bend radius the fold uses about 6.8 mm of the 13.8 ±0.3 mm flex and the loop reaches x ≈ 206.5, inside the board edge at 210. The 12.5 mm-wide flex end spans y = 131.2–143.7; the USB receptacle shell ends at y = 130.5, leaving about 0.7 mm beside the stiffened end.
