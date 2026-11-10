#!/usr/bin/env python3
"""Property-checker negative tests using the existing pinned exported fixture."""
import copy,json,pathlib,tempfile,unittest,hashlib
from unittest.mock import patch
import check_schematic_properties as checker
from check_schematic_contracts import sexp,children,val
ROOT=pathlib.Path(__file__).resolve().parents[1];FIXTURE=ROOT/'tests/fixtures/display_snapshot'
def dump(n):return '('+' '.join(dump(x) for x in n)+')' if isinstance(n,list) else json.dumps(n)
class PropertyCheckerTests(unittest.TestCase):
 def setUp(self):
  manifest=json.loads((FIXTURE/'manifest.json').read_text())
  for p,h in manifest['sha256'].items():self.assertEqual(hashlib.sha256((FIXTURE/p).read_bytes()).hexdigest(),h)
  self.tree=sexp((FIXTURE/'display.net').read_text());self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
  self.path=pathlib.Path(self.tmp.name)/'test.net';self.patch=patch.object(checker,'ROOT',FIXTURE);self.patch.start();self.addCleanup(self.patch.stop)
 def comp(self,ref):return next(c for c in children(children(self.tree,'components')[0],'comp') if val(c,'ref')==ref)
 def runcheck(self):self.path.write_text(dump(self.tree));return checker.check(self.path,['display'])
 def test_baseline(self):self.assertEqual(self.runcheck()['status'],'PASS')
 def test_wrong_nominal_value(self):children(self.comp('R301'),'value')[0][1]='470k';self.assertEqual(self.runcheck()['status'],'FAIL')
 def test_wrong_mpn(self):
  p=next(p for p in children(self.comp('U301'),'property') if val(p,'name')=='MPN');children(p,'value')[0][1]='WRONG';self.assertEqual(self.runcheck()['status'],'FAIL')
 def test_wrong_full_rating(self):
  p=next(p for p in children(self.comp('C301'),'property') if val(p,'name')=='Rating');children(p,'value')[0][1]='6.3V X5R';self.assertEqual(self.runcheck()['status'],'FAIL')
 def test_wrong_visible_voltage(self):children(self.comp('C301'),'value')[0][1]='4.7u / 6.3V';self.assertEqual(self.runcheck()['status'],'FAIL')
 def test_unapproved_connector_footprint(self):self.comp('J301').append(['footprint','WRONG:UNAPPROVED']);self.assertEqual(self.runcheck()['status'],'FAIL')
 def test_unit_display_equivalence(self):self.assertEqual(checker.nominal('100nF 10V'),checker.nominal('100n / 10V'));self.assertEqual(checker.nominal('330R 1%'),checker.nominal('330'))
if __name__=='__main__':unittest.main(verbosity=2)
