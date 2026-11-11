#!/usr/bin/env python3
"""Assign JLCPCB/LCSC part numbers to every fitted part (schematic fields LCSC and MPN).

Part numbers, library class and stock were read from JLCPCB's parts search on
2026-11-10; see docs/design/jlcpcb_release.md. Passives use Basic-library
parts wherever one meets the schematic's stated value and rating. Idempotent.

Usage: assign_jlc_parts.py   (from the repository root, then kicad-cli sch upgrade --force)
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from schlib import Sheet, pval  # noqa: E402

# (LCSC, manufacturer part, class) keyed by "value|package"; B = Basic, E = Extended, P = Preferred Extended
R0603 = {'5.1k': ('C23186', '0603WAF5101T5E'), '30k': ('C22984', '0603WAF3002T5E'), '10k': ('C25804', '0603WAF1002T5E'),
         '82k': ('C23254', '0603WAF8202T5E'), '100k': ('C25803', '0603WAF1003T5E'), '3.3k': ('C22978', '0603WAF3301T5E'),
         '47k': ('C25819', '0603WAF4702T5E'), '56k': ('C23206', '0603WAF5602T5E'), '1k': ('C21190', '0603WAF1001T5E'),
         '470k': ('C23178', '0603WAF4703T5E'), '1M': ('C22935', '0603WAF1004T5E'), '330': ('C23138', '0603WAF3300T5E'),
         '2.2k': ('C4190', '0603WAF2201T5E'), '4.7k': ('C23162', '0603WAF4701T5E'), '100': ('C22775', '0603WAF1000T5E'),
         '200k': ('C25811', '0603WAF2003T5E')}
R0402 = {'10k': ('C25744', '0402WGF1002TCE'), '22R': ('C25092', '0402WGF220JTCE'), '100k': ('C25741', '0402WGF1003TCE')}
BY_REF = {
    'R504': ('C17408', '0805W8F1000T5E'), 'R301': ('C382278', 'FBF05FT-R470-00L'),
    'RT101': ('C2892547', 'KNTC0603/10KF3950'),
    'C202': ('C1525', 'CL05B104KO5NNNC'), 'C203': ('C52923', 'CL05A105KA5NQNC'),
    'C103': ('C29823', '1206B475K500NT'), 'C301': ('C29823', '1206B475K500NT'), 'C302': ('C29823', '1206B475K500NT'),
    'C108': ('C309062', 'CL32B226KAJNNNE'), 'C109': ('C309062', 'CL32B226KAJNNNE'),
    'C201': ('C45783', 'CL21A226MAQNNNE'), 'C409': ('C45783', 'CL21A226MAQNNNE'),
    'C113': ('C1588', 'CL10B102KB8NNNC'), 'C507': ('C107045', 'CC0603JRNPO9BN270'), 'C509': ('C19666', 'CL10A475KO8NNNC'),
    'C511': ('C15849', 'CL10A105KB8NNNC'), 'C515': ('C15849', 'CL10A105KB8NNNC'),
    'D101': ('C19077499', 'SMF6.0A'), 'D102': ('C19077499', 'SMF6.0A'),
    'L101': ('C98415', 'SWPA4020SR47NT'), 'L301': ('C2041717', 'SRN4018-680M'),
    'J102': ('C173752', 'S2B-PH-K-S(LF)(SN)'), 'J502': ('C3320727', 'SFH11-NBPC-D03-ST-BK'),
}
BY_MPN = {
    'USB4105-GF-A': 'C3020560', 'TPD4E05U06DQAR': 'C138714', 'TPS2121RUXR': 'C485916', 'BQ24074RGTR': 'C54313',
    'TPS63802DLAR': 'C2845237', 'TPS22918DBVR': 'C131941', 'ESP32-S3-WROOM-1-N16R8': 'C2913202', 'HSMF-C165': 'C188726',
    'WS2812C-2020-V6': 'C55109522', 'BH1730FVC': 'C79616', 'LIS2DW12TR': 'C189624', 'NT3H2111W0FHKH': 'C710403',
    'IR67-21C/TR8': 'C60109', 'AO3400A': 'C20917', 'IRM-H638T/TR2': 'C91447', 'SM04B-SRSS-TB(LF)(SN)': 'C160404',
    'TPS2553DBVR': 'C55266', 'SKSCLBE010': 'C115361', 'MBR0530T1G': 'C82046', 'SI1308EDL-T1-GE3': 'C469327',
    'TCA9534PWR': 'C783615', 'FH12-24S-0.5SH(55)': 'C202112',
}
HAND_FIT = {'J102', 'J502'}      # through-hole, fitted by hand after SMT to avoid JLC's manual-solder charge


def pick(ref, value, fp, mpn):
    if ref in BY_REF:
        return BY_REF[ref]
    if mpn in BY_MPN:
        return BY_MPN[mpn], mpn
    v = value.replace(' / ', ' ').split()[0] if value else ''
    if ref.startswith('R') and '0603' in fp:
        return R0603[v]
    if ref.startswith('R') and '0402' in fp:
        return R0402[v]
    if ref.startswith('C') and '0603' in fp and v in ('100nF', '100n'):
        return 'C14663', 'CC0603KRX7R9BB104'
    if ref.startswith('C') and '0805' in fp and v in ('1uF', '1u'):
        return 'C28323', 'CL21B105KBFNNNE'
    if ref.startswith('C') and '0805' in fp and v in ('10uF', '10u'):
        return 'C15850', 'CL21A106KAYNNNE'
    return None


def main():
    missing = []
    n = 0
    for name in ('power', 'mcu', 'display', 'lighting', 'peripherals'):
        s = Sheet(f'{name}.kicad_sch')
        for sym in s.symbols():
            ref = pval(sym, 'Reference')
            if ref.startswith(('#', 'TP')) or ref in ('J103', 'AE501'):
                continue
            if ref == 'R112':
                s.set_prop(ref, 'Value', '4.7k 1%')        # unused ILIM setting; any 1.1k-8k value is valid
            if ref == 'L101':
                s.set_prop(ref, 'Footprint', 'Inductor_SMD:L_Changjiang_FNR4020S')
            got = pick(ref, pval(sym, 'Value'), pval(sym, 'Footprint', ''), pval(sym, 'MPN', ''))
            if ref == 'C508':
                continue                                   # DNP trim position
            if got is None:
                missing.append((ref, pval(sym, 'Value')))
                continue
            s.set_prop(ref, 'LCSC', got[0])
            s.set_prop(ref, 'MPN', got[1])
            s.set_prop(ref, 'Assembly', 'hand-fit after SMT' if ref in HAND_FIT else 'JLCPCB SMT')
            n += 1
        s.save()
    print('assigned', n, 'missing', missing)


if __name__ == '__main__':
    main()
