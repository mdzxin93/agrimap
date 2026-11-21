import json,sqlite3
from contextlib import contextmanager
from contextlib import contextmanager
from pathlib import Path
class FieldStore:
 def __init__(self,path):self.path=str(path);Path(self.path).parent.mkdir(parents=True,exist_ok=True);self.init_db()
 def connect(self):
  c=sqlite3.connect(self.path);c.row_factory=sqlite3.Row;c.execute("PRAGMA foreign_keys=ON");return c
 @contextmanager
 def db(self):
  c=self.connect()
  try:
   yield c
   c.commit()
  finally:c.close()
 @contextmanager
 def db(self):
  c=self.connect()
  try:
   yield c
   c.commit()
  finally:c.close()
 def init_db(self):
  with self.db() as c:
   c.execute("CREATE TABLE IF NOT EXISTS fields(id INTEGER PRIMARY KEY,name TEXT NOT NULL,area REAL NOT NULL,crop TEXT DEFAULT '',notes TEXT DEFAULT '',boundary TEXT NOT NULL,created_at TEXT DEFAULT CURRENT_TIMESTAMP)")
   c.execute("CREATE TABLE IF NOT EXISTS points(id INTEGER PRIMARY KEY,field_id INTEGER NOT NULL REFERENCES fields(id) ON DELETE CASCADE,label TEXT,x REAL,y REAL)")
 def add_field(self,name,area,crop,notes,boundary,points):
  if not name.strip():raise ValueError("Field name is required.")
  if float(area)<=0:raise ValueError("Area must be greater than zero.")
  if len(boundary)<3:raise ValueError("A boundary needs at least three vertices.")
  with self.db() as c:
   cur=c.execute("INSERT INTO fields(name,area,crop,notes,boundary) VALUES(?,?,?,?,?)",(name.strip(),float(area),crop.strip(),notes.strip(),json.dumps(boundary)));fid=cur.lastrowid
   c.executemany("INSERT INTO points(field_id,label,x,y) VALUES(?,?,?,?)",[(fid,p.get("label",f"P{i+1}"),float(p["x"]),float(p["y"])) for i,p in enumerate(points)]);return fid
 def list_fields(self):
  with self.db() as c:
   out=[]
   for row in c.execute("SELECT * FROM fields ORDER BY id DESC").fetchall():
    f=dict(row);f["boundary"]=json.loads(f.pop("boundary"));f["points"]=[dict(p) for p in c.execute("SELECT label,x,y FROM points WHERE field_id=? ORDER BY id",(f["id"],)).fetchall()];out.append(f)
   return out
 def delete_field(self,fid):
  with self.db() as c:c.execute("DELETE FROM fields WHERE id=?",(fid,))
 def export_geojson(self,path):
  feats=[]
  for f in self.list_fields():
   ring=f["boundary"][:]
   if ring[0]!=ring[-1]:ring.append(ring[0])
   feats.append({"type":"Feature","properties":{k:f[k] for k in ("id","name","area","crop","notes")},"geometry":{"type":"Polygon","coordinates":[ring]}})
  Path(path).write_text(json.dumps({"type":"FeatureCollection","features":feats},indent=2),encoding="utf-8")
 def import_geojson(self,path):
  data=json.loads(Path(path).read_text(encoding="utf-8"));n=0
  for f in data.get("features",[]):
   g=f.get("geometry") or {};p=f.get("properties") or {}
   if g.get("type")!="Polygon":continue
   ring=g.get("coordinates",[[]])[0]
   if len(ring)>1 and ring[0]==ring[-1]:ring=ring[:-1]
   if len(ring)<3:continue
   self.add_field(p.get("name","Imported field"),p.get("area",1),p.get("crop",""),p.get("notes",""),ring,[]);n+=1
  return n
