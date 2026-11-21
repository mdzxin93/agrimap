import json,tempfile,unittest
from pathlib import Path
from storage import FieldStore
class Tests(unittest.TestCase):
 def setUp(self):self.tmp=tempfile.TemporaryDirectory();self.s=FieldStore(Path(self.tmp.name)/"test.db")
 def tearDown(self):self.tmp.cleanup()
 def test_save(self):
  fid=self.s.add_field("North",1.25,"Rice","",[[0,0],[10,0],[10,10],[0,10]],[{"label":f"P{i+1}","x":x,"y":y} for i,(x,y) in enumerate([[0,0],[10,0],[10,10],[0,10]])]);f=self.s.list_fields()[0];self.assertEqual(f["id"],fid);self.assertEqual(len(f["points"]),4)
 def test_invalid(self):
  with self.assertRaises(ValueError):self.s.add_field("",1,"","",[[0,0],[1,0],[0,1]],[])
  with self.assertRaises(ValueError):self.s.add_field("Bad",0,"","",[[0,0],[1,0],[0,1]],[])
 def test_geojson(self):
  self.s.add_field("West",1,"Wheat","",[[0,0],[4,0],[4,4],[0,4]],[]);p=Path(self.tmp.name)/"fields.geojson";self.s.export_geojson(p);self.assertEqual(json.loads(p.read_text())["type"],"FeatureCollection");self.assertEqual(self.s.import_geojson(p),1);self.assertEqual(len(self.s.list_fields()),2)
if __name__=="__main__":unittest.main()