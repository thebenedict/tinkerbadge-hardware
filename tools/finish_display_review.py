import json,pathlib,hashlib,sys,time
sys.path.insert(0,str(pathlib.Path(__file__).parent));from konnect_call import Client,unbox
r=pathlib.Path(__file__).resolve().parents[1];s=str(r/'display.kicad_sch');c=Client()
def run(n,**a):
 q=c.call(n,dict(schematic=s,**a));(r/'.build'/f'mcp-display-finish-{time.time_ns()}-{n}.json').write_text(json.dumps(q,indent=2))
 if q.get('isError'):raise RuntimeError(str(unbox(q)))
 return unbox(q)['result'][0]
def fields(ref,x,y,rot=0):return run('edit_schematic_component',reference=ref,field_placements={'Reference':dict(x=x,y=y,rotation=rot),'Value':dict(x=x,y=y+2.54,rotation=rot)})
try:
 for i in range(301,309):
  ref=f'R{i}'; q=json.load(open(r/'.build/display_pin_locations.json'));comp=next(x for x in q['components'] if x['reference']==ref);fields(ref,comp['component_x']+10.16,comp['component_y']-1.27)
 fields('L301',76.2,142.24,90);fields('C302',129.54,171.45,90)
 fields('D301',161.29,175.26,90);fields('D302',186.69,175.26,90)
 # Prevent C303 ground legend from colliding with the first panel output label.
 # Move only the power-symbol label is not exposed by current API; shorten ground wire via symbol position editing is inappropriate.
 # Instead leave C303 ground at y62.23 and move EPD_GDR label to longer rightward stub in a separate reviewed plan if necessary.
 run('render_schematic_png',output=str(r/'.build/display.png'),width_px=4096)
 n=c.call('export_netlist',dict(board=s,output=str(r/'.build/display.net'),format='kicad'));(r/'.build/display_netlist_result.json').write_text(json.dumps(n,indent=2)); print(unbox(n))
 print(run('run_erc',output=str(r/'.build/display_erc.json'),severity='warning'))
finally:c.close()
p=r/'docs/design/peripherals_contract.json';h=hashlib.sha256(p.read_bytes()).hexdigest()
(r/'docs/design/review_peripherals.md').write_text(f'''# Independent peripheral source and assignment review

Reviewed 9 November 2026 by the integrating schematic worker, independently of the source extractor. Contract SHA-256: `{h}`.

## Outcome

PASS for electrical schematic capture of the 75-component contract. This does not approve PCB footprints, procurement substitutions, manufacturing or prototype performance. CAD pin queryback, disposable symbol/footprint checks and exported-netlist comparison remain separate requirements.

## Original source checks

Original PDF page images, not merely another worker's summary, were inspected:

- Worldsemi WS2812C-2020-V6 p. 2: top/back views and table prove 1 DO, 2 GND, 3 DI, 4 VDD. Eight devices chain output to next input; final output is NC. Minimum supply 3.3 V excludes a nominal 3.3 V rail without margin. The 3.95 V rail and 4.10 V acceptance ceiling give 2.255 V input-high requirement, below the MCU guaranteed high level.
- Broadcom HSMF-C165 p. 2: two independent dies, 1/3 green anode/cathode and 2/4 red anode/cathode, not a common-anode or three-pin device. Separate 2.2 kΩ resistors and grounded cathodes are consistent.
- TI TPS2553 p. 4: DBV mapping differs from DRV. Contract uses 1 IN, 2 GND, 3 active-high EN, 4 open-drain FAULT, 5 ILIM, 6 OUT. The source table specifies 110–150 mA at 210 kΩ; equation/tolerance budget is conservatively 109.18–152.25 mA. The published 50 mA normal combined budget is distinct from this fault limit.
- TI TCA9534 p. 4: all 16 pins match; address straps are grounded. P2 controls the accessory switch with external pulldown; startup defaults to input. P0/P1/P3 read status; INT is intentionally unused and polled. Firmware must reset the output latch before enabling output direction, including after MCU-only resets.
- Everlight IRM-H6XXT p. 1: two separate ground pins, pin 3 OUT and pin 4 VCC. The switched-supply filter and absence of an always-on output pullup prevent an obvious off-state back-power path. IR67-21C p. 2 proves 1 anode and 2 cathode; its high pulse rating is not permission for high-duty carrier. The 100 Ω resistor keeps continuous current below the device rating even during a stuck-on output.
- Xunpu TS-1088 p. 2 shows exactly two interchangeable electrical terminals. The two numbered schematic contacts are project identifiers for an unpolarized switch, not an invented four-pin package.
- ROHM BH1730 p. 2: 1 VCC, 2 optional INT, 3 GND, 4 SDA, 5 DVI, 6 SCL. Both supplies are 3.3 V; INT may be open.
- ST LIS2DW12 Rev. 4 p. 9: bottom-view pin numbering, I²C straps, grounded reserved pin 7, ground pins 6/8, allowed grounding of NC pin 5, VDD 9 and VDD_IO 10 all match. INT1 uses pin 12; INT2 pin 11 is unused.
- NXP NT3H2111 Rev. 3.6 p. 8: transparent top view matches all eight leads. Center metal is explicitly not for soldering. VOUT is left unused; separate antenna terminals and DNP tuning capacitors are correct. Always-on supply avoids assuming an undocumented Ioff property on the shared bus.
- AOS AO3400A Rev. 3.1 p. 1: original top and bottom images prove the index-side terminal is G, the other paired terminal S, and the single opposite terminal D. Numeric 1/2/3 are a documented project/conventional SOT23 mapping, not a printed AOS numbered table. Accept only when the chosen footprint's pad 1/index, 2 and 3 coincide with this physical view. No claim that p. 5 is a package drawing.
- JST SH header and housing diagrams identify Circuit No. 1. The cable drawing uses its own housing view and must not be transferred blindly to the PCB header. Sullins SFH11 drawing establishes geometry but not electrical numbering. Qwiic and SAO logical interfaces remain separate from the physical mating acceptance.

## Electrical review

Reviewed every component and support-part endpoint in the JSON. Local 100 nF bypassing, LED bulk capacitance, defined DIN/enable/gate defaults, active-low buttons with 100 kΩ/100 nF debounce, pullups to the correct powered domain, NFC tuning placeholders and the IR low-side circuit are coherent. Onboard I²C devices remain powered at 3.3 V; the dedicated external bus pulls to switched ACC_3V3. Firmware must disable pulls and release external pins before cutting accessory power. No independently powered add-ons or hot plugging are qualified.

The NTAG typical 195 µA idle current materially limits storage life. Full-white LED current is typical, not a guaranteed system maximum. Firmware scheduling, radio/display peaks, current-limit interactions, optical range, antenna tuning and every footprint/mating view require prototype or later physical verification.
''')
print('Saved independent peripheral review',h)
