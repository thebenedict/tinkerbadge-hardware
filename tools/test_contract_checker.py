#!/usr/bin/env python3
"""Deterministic tests using frozen exported data only; never native CAD."""
import copy
import hashlib
import json
import pathlib
import tempfile
import unittest
from unittest.mock import patch
import check_schematic_contracts as checker

ROOT = pathlib.Path(__file__).resolve().parents[1]
FIXTURE = ROOT / 'tests/fixtures/display_snapshot'

def dump(node):
 return '(' + ' '.join(dump(x) for x in node) + ')' if isinstance(node,list) else json.dumps(node)

def net_with(tree,ref,pin):
 return next(net for net in checker.children(checker.children(tree,'nets')[0],'net')
             if any(checker.val(n,'ref')==ref and checker.val(n,'pin')==pin for n in checker.children(net,'node')))

def node_with(tree,ref,pin):
 return next(n for n in checker.children(net_with(tree,ref,pin),'node') if checker.val(n,'ref')==ref and checker.val(n,'pin')==pin)

class ContractCheckerTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  manifest=json.loads((FIXTURE/'manifest.json').read_text())
  for name,digest in manifest['sha256'].items():
   if hashlib.sha256((FIXTURE/name).read_bytes()).hexdigest()!=digest:
    raise AssertionError('Fixture hash mismatch: '+name)
  cls.source=checker.sexp((FIXTURE/'display.net').read_text())
  cls.contract=json.loads((FIXTURE/'docs/design/display_contract.json').read_text())

 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory(prefix='badge-contract-test-');self.addCleanup(self.tmp.cleanup)
  self.root=pathlib.Path(self.tmp.name);self.path=self.root/'test.net';self.tree=copy.deepcopy(self.source)
  folder=self.root/'docs/design';folder.mkdir(parents=True)
  self.contract_path=folder/'display_contract.json';self.contract_path.write_text(json.dumps(self.contract))
  self.patch=patch.object(checker,'ROOT',self.root);self.patch.start();self.addCleanup(self.patch.stop)

 def run_check(self):
  self.path.write_text(dump(self.tree));return checker.check(self.path,['display'])

 def test_baseline(self):
  result=self.run_check();self.assertEqual(result['status'],'PASS');self.assertEqual(result['expected_endpoints'],95)

 def test_wrong_net_name(self):
  checker.children(net_with(self.tree,'U301','2'),'name')[0][1]='BROKEN_EPD_MOSI'
  self.assertEqual(self.run_check()['status'],'FAIL')

 def test_missing_physical_lead(self):
  n=node_with(self.tree,'J301','1');net_with(self.tree,'J301','1').remove(n)
  result=self.run_check();self.assertTrue(any(i.get('endpoint')==['J301','1'] for i in result['issues']))

 def test_missing_nc_marker(self):
  node=node_with(self.tree,'U301','11');checker.children(node,'pintype')[0][1]='tri_state'
  result=self.run_check();self.assertTrue(any(i.get('endpoint')==['U301','11'] for i in result['issues']))

 def test_same_basename_split(self):
  net=net_with(self.tree,'U301','10');node=node_with(self.tree,'U301','10');net.remove(node)
  checker.children(self.tree,'nets')[0].append(['net',['code','9999'],['name','/disconnected_sheet/GND'],node])
  result=self.run_check();self.assertTrue(any(i.get('error')=='logical net split across actual nets' for i in result['issues']))

 def test_duplicate_list_form_contract_pin(self):
  contract=copy.deepcopy(self.contract);pins=contract['components'][0]['pins'];pins.append(copy.deepcopy(pins[0]))
  self.contract_path.write_text(json.dumps(contract))
  with self.assertRaisesRegex(ValueError,'duplicate contract physical pin J301.1'):self.run_check()

 def test_duplicate_contract_pin_normalized_to_string(self):
  contract=copy.deepcopy(self.contract);pins=contract['components'][0]['pins'];duplicate=copy.deepcopy(pins[0]);duplicate['number']=int(duplicate['number']);pins.append(duplicate)
  self.contract_path.write_text(json.dumps(contract))
  with self.assertRaisesRegex(ValueError,'duplicate contract physical pin'):self.run_check()

 def test_duplicate_exported_endpoint(self):
  net=net_with(self.tree,'U301','2');net.append(copy.deepcopy(node_with(self.tree,'U301','2')))
  with self.assertRaisesRegex(ValueError,'endpoint in multiple nets'):self.run_check()

 def test_missing_component_record(self):
  cs=checker.children(self.tree,'components')[0];cs.remove(next(c for c in checker.children(cs,'comp') if checker.val(c,'ref')=='C301'))
  self.assertIn('C301',self.run_check()['missing_components'])

 def test_unexpected_physical_lead(self):
  net_with(self.tree,'U301','2').append(['node',['ref','U301'],['pin','999'],['pintype','input']])
  result=self.run_check();self.assertTrue(any(i.get('error')=='exported pin absent from contract' for i in result['issues']))

 def test_merged_logical_nets(self):
  a=net_with(self.tree,'U301','2');b=net_with(self.tree,'U301','3');b.extend(copy.deepcopy(checker.children(a,'node')));checker.children(self.tree,'nets')[0].remove(a)
  self.assertEqual(self.run_check()['status'],'FAIL')

 def test_value_is_explicitly_outside_endpoint_scope(self):
  cs=checker.children(self.tree,'components')[0];c=next(c for c in checker.children(cs,'comp') if checker.val(c,'ref')=='R301');checker.children(c,'value')[0][1]='470k WRONG'
  self.assertEqual(self.run_check()['status'],'PASS')

if __name__=='__main__':unittest.main(verbosity=2)
