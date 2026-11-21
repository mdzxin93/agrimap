from pathlib import Path
from storage import FieldStore
s=FieldStore(Path.home()/"AgriMap"/"agrimap.sqlite3")
if not s.list_fields():
 for i in range(10):
  x,y=(i%5)*15,(i//5)*15;b=[[x,y],[x+10,y+1],[x+9,y+10],[x-1,y+9]];pts=[{"label":f"P{n+1}","x":a,"y":z} for n,(a,z) in enumerate(b)];s.add_field(f"Synthetic plot {i+1:02d}",1,["Rice","Wheat","Maize","Vegetables"][i%4],"Synthetic sample; not a real drone survey.",b,pts)
 print("Created 10 synthetic one-acre plots with four reference points each.")
else:print("Existing data retained.")