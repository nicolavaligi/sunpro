import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from datetime import datetime, timezone

spec=importlib.util.spec_from_file_location('weekly',Path(__file__).resolve().parents[1]/'scripts/weekly_research.py')
weekly=importlib.util.module_from_spec(spec)
spec.loader.exec_module(weekly)


def element(identifier=1,delta=0):
    return {'type':'way','id':identifier,'tags':{'landuse':'farmland'},'geometry':[
        {'lon':x,'lat':y} for x,y in [(10,45),(10.01+delta,45),(10.01+delta,45.01),(10,45.01),(10,45)]]}


class ResearchTest(unittest.TestCase):
    def test_geometry_and_threshold(self):
        feature=weekly.candidate(element(),'Lombardia','now')
        self.assertGreater(feature['properties']['area_ha'],2)
        self.assertTrue(weekly.shape(feature['geometry']).contains(weekly.Point(feature['properties']['point'])))
        self.assertEqual(feature['properties']['status'],'DA_VERIFICARE')
        small=element();small['geometry']=[{'lon':10+x/10000,'lat':45+y/10000} for x,y in [(0,0),(1,0),(1,1),(0,1),(0,0)]]
        self.assertIsNone(weekly.candidate(small,'Lombardia','now'))
        invalid=element();invalid['geometry'].pop()
        self.assertIsNone(weekly.candidate(invalid,'Lombardia','now'))

    def test_diff_outage_and_recovery(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            def fetch(code):return [element()] if code=='IT-25' else []
            first=weekly.run(root,fetch,datetime(2026,10,31,tzinfo=timezone.utc))
            self.assertEqual(first['new_ids'],['osm-way-1'])
            second=weekly.run(root,fetch)
            self.assertEqual(second['new_ids'],[])
            def outage(code):raise RuntimeError('network unavailable')
            failed=weekly.run(root,outage)
            self.assertEqual(failed['status'],'errore')
            self.assertEqual(failed['total_candidates'],1)
            self.assertEqual(failed['no_longer_matching_ids'],[])
            changed=weekly.run(root,lambda code:[element(delta=.001)] if code=='IT-25' else [])
            self.assertEqual(changed['changed_ids'],['osm-way-1'])
            gone=weekly.run(root,lambda code:[])
            self.assertEqual(gone['no_longer_matching_ids'],['osm-way-1'])
            self.assertTrue((root/'weekly/report.html').exists())

    def test_incomplete_source_not_empty_success(self):
        self.assertIn('around.roads:300',weekly.query_region('IT-25'))
        with tempfile.TemporaryDirectory() as directory:
            def partial(code):
                if code=='IT-25':raise RuntimeError('timeout')
                return []
            report=weekly.run(Path(directory),partial)
            self.assertEqual(report['status'],'parziale')
            self.assertIn('Lombardia',report['regions_failed'])

if __name__=='__main__': unittest.main()
