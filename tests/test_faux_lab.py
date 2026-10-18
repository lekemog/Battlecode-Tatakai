import importlib.util
from pathlib import Path
import unittest
spec=importlib.util.spec_from_file_location('lab',Path(__file__).resolve().parents[1]/'tools/faux_lab.py')
lab=importlib.util.module_from_spec(spec);spec.loader.exec_module(lab)

class LabTests(unittest.TestCase):
    def test_family_does_not_dilute_a_hard_counter(self):
        rows=[{'a':'main','b':o,'map':'rows','status':'complete','match':{'outcome':outcome}}
              for o,outcome in [('fz_hunt','teamA'),('fz_hunt_v3','teamB')]]
        s=lab.summarize(rows,'main',['fz_hunt','fz_hunt_v3'],1)
        self.assertEqual(s['family_checks_completed'],1)
        self.assertEqual(s['family_checks_passed'],0)
        rows[1]['status']='failed'
        self.assertEqual(lab.summarize(rows,'main',['fz_hunt','fz_hunt_v3'],1)['family_checks_completed'],0)
    def test_missing_horizon_is_missing(self):
        t={'sampleCount':3,'runs':[{'duration':2,'value':'10'},{'duration':1,'value':'20'}]}
        self.assertEqual(lab.at(t,2),20)
        self.assertIsNone(lab.at(t,3))
    def test_gold_tiebreak_not_gem_margin(self):
        d={'match':{'outcome':'teamB'},'teams':[{'team':'teamA','submittedGems':'0'},{'team':'teamB','submittedGems':'0'}]}
        self.assertEqual(lab.parse(d)['match']['outcome'],'teamB')
        self.assertIsNone(lab.parse(d)['teamA']['horizon_sample_indices']['300']['gold'])
    def test_event_count_is_not_event_amount(self):
        d={'match':{'outcome':'teamA'},'teams':[{'team':'teamA','submittedGems':'1000'},{'team':'teamB','submittedGems':'50'}],
           'events':[{'kind':'gemLoss','owner':{'team':'teamA'},'entries':[{'value':'42','amount':0}]}]}
        self.assertEqual(lab.parse(d)['teamA']['gem_loss_event_sum'],42)

if __name__=='__main__':unittest.main()
