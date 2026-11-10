#!/usr/bin/env python3
"""Frozen exported-data regression tests for duplicated Alps contacts; never edits CAD."""
import copy,hashlib,json,pathlib,tempfile,unittest
from unittest.mock import patch
import check_schematic_contracts as endpoints
import check_schematic_properties as properties
from check_schematic_contracts import sexp,children,val
ROOT=pathlib.Path(__file__).resolve().parents[1];FIXTURE=ROOT/'tests/fixtures/alps_buttons_snapshot'
def dump(n):return '('+' '.join(dump(x) for x in n)+')' if isinstance(n,list) else json.dumps(n)
class AlpsButtonsTests(unittest.TestCase):
 def setUp(self):
  manifest=json.loads((FIXTURE/'manifest.json').read_text())
  for p,h in manifest['sha256'].items():self.assertEqual(hashlib.sha256((FIXTURE/p).read_bytes()).hexdigest(),h)
  self.tree=sexp((FIXTURE/'buttons.net').read_text());self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.path=pathlib.Path(self.tmp.name)/'test.net'
 def check(self,checker):
  self.path.write_text(dump(self.tree))
  with patch.object(checker,'ROOT',FIXTURE):return checker.check(self.path,['peripherals'])
 def net(self,ref,pin):return next(n for n in children(children(self.tree,'nets')[0],'net') if any(val(q,'ref')==ref and val(q,'pin')==pin for q in children(n,'node')))
 def comp(self,ref):return next(c for c in children(children(self.tree,'components')[0],'comp') if val(c,'ref')==ref)
 def test_baseline(self):
  self.assertEqual(self.check(endpoints)['status'],'PASS');self.assertEqual(self.check(endpoints)['expected_endpoints'],8);self.assertEqual(self.check(properties)['status'],'PASS')
 def test_old_pin2_to_ground_is_rejected(self):
  n=self.net('SW401','2');q=next(q for q in children(n,'node') if val(q,'ref')=='SW401' and val(q,'pin')=='2');n.remove(q);self.net('SW401','3').append(q);self.assertEqual(self.check(endpoints)['status'],'FAIL')
 def test_missing_duplicate_terminal_is_rejected(self):
  n=self.net('SW402','4');q=next(q for q in children(n,'node') if val(q,'ref')=='SW402' and val(q,'pin')=='4');n.remove(q);self.assertEqual(self.check(endpoints)['status'],'FAIL')
 def test_wrong_ganged_symbol_is_rejected(self):
  s=children(self.comp('SW401'),'libsource')[0];children(s,'lib')[0][1]='Switch';children(s,'part')[0][1]='SW_Push_Dual';self.assertEqual(self.check(properties)['status'],'FAIL')
 def test_unapproved_footprint_is_rejected(self):
  self.comp('SW401').append(['footprint','Button_Switch_SMD:UNREVIEWED']);self.assertEqual(self.check(properties)['status'],'FAIL')
if __name__=='__main__':unittest.main(verbosity=2)
