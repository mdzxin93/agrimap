import sys
from pathlib import Path
from PySide6.QtCore import Qt,QPointF
from PySide6.QtGui import QColor,QBrush,QPen,QPolygonF
from PySide6.QtWidgets import QApplication,QMainWindow,QWidget,QHBoxLayout,QVBoxLayout,QLabel,QPushButton,QFrame,QGraphicsView,QGraphicsScene,QTableWidget,QTableWidgetItem,QHeaderView,QDialog,QFormLayout,QLineEdit,QDoubleSpinBox,QTextEdit,QComboBox,QMessageBox,QFileDialog,QAbstractItemView
from storage import FieldStore
DB=Path.home()/"AgriMap"/"agrimap.sqlite3"
class MapView(QGraphicsView):
 def __init__(self):
  super().__init__();self.scene=QGraphicsScene(self);self.setScene(self.scene);self.setMinimumHeight(300);self.setBackgroundBrush(QBrush(QColor("#101a14")));self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
 def plot(self,fields):
  self.scene.clear();pen=QPen(QColor("#263b2d"))
  for x in range(0,1000,40):self.scene.addLine(x,0,x,700,pen)
  for y in range(0,700,40):self.scene.addLine(0,y,1000,y,pen)
  colors=["#9acb70","#6eb6a0","#d0b76e","#7ea9cf","#c58caa"]
  for i,f in enumerate(fields):
   poly=QPolygonF([QPointF(p[0]*8+45,p[1]*8+65) for p in f["boundary"]]);col=QColor(colors[i%len(colors)]);self.scene.addPolygon(poly,QPen(col,2),QBrush(QColor(col.red(),col.green(),col.blue(),35)));label=self.scene.addText(f["name"]);label.setDefaultTextColor(QColor("#e7efe3"));label.setPos(poly.boundingRect().center())
   for p in f["points"]:self.scene.addEllipse(p["x"]*8+42,p["y"]*8+62,8,8,QPen(QColor("#efc86d")),QBrush(QColor("#efc86d")))
  self.scene.addRect(45,590,79,79,QPen(QColor("#efc86d"),2));t=self.scene.addText("33 x 33 ft reference");t.setDefaultTextColor(QColor("#efc86d"));t.setPos(140,615);self.fitInView(self.scene.itemsBoundingRect(),Qt.AspectRatioMode.KeepAspectRatio)
class AddField(QDialog):
 def __init__(self,parent=None):
  super().__init__(parent);self.setWindowTitle("Add field record");form=QFormLayout(self);self.name=QLineEdit("North field");self.area=QDoubleSpinBox();self.area.setRange(.01,100000);self.area.setValue(1);self.crop=QComboBox();self.crop.addItems(["Unassigned","Rice","Wheat","Maize","Vegetables","Other"]);self.notes=QTextEdit();self.notes.setMaximumHeight(70);form.addRow("Field name",self.name);form.addRow("Area",self.area);form.addRow("Crop",self.crop);form.addRow("Notes",self.notes);ok=QPushButton("Save field");ok.clicked.connect(self.accept);form.addRow(ok)
 def values(self):
  b=[[2,2],[12,2],[12,10],[2,10]];pts=[{"label":f"P{i+1}","x":x,"y":y} for i,(x,y) in enumerate(b)];crop="" if self.crop.currentText()=="Unassigned" else self.crop.currentText();return self.name.text(),self.area.value(),crop,self.notes.toPlainText(),b,pts
class Main(QMainWindow):
 def __init__(self):
  super().__init__();DB.parent.mkdir(parents=True,exist_ok=True);self.store=FieldStore(DB);self.setWindowTitle("AgriMap | Field Intelligence");self.resize(1260,800);self.setStyleSheet("QMainWindow,QWidget{background:#101712;color:#e7eee5;font-family:'Segoe UI'} QFrame#side{background:#173F2B;border-radius:12px} QPushButton{background:#24382a;border:1px solid #38513c;border-radius:7px;padding:9px;color:#e5eee0} QPushButton#primary{background:#a7cc78;color:#142318;font-weight:700} QLineEdit,QComboBox,QTextEdit{background:#17231b;border:1px solid #334739;border-radius:6px;padding:7px;color:#eaf1e6} QTableWidget{background:#141e17;alternate-background-color:#19251c;gridline-color:#293b2d} QHeaderView::section{background:#1b2b20;color:#a9c69e;padding:7px;border:0}")
  root=QWidget();layout=QHBoxLayout(root);side=QFrame();side.setObjectName("side");side.setFixedWidth(205);sv=QVBoxLayout(side);brand=QLabel("AgriMap");brand.setStyleSheet("font-size:24px;font-weight:700;padding:7px");sv.addWidget(brand);sv.addWidget(QLabel("FIELD INTELLIGENCE"))
  for name in ["Overview","Field boundaries","Reference points","Survey samples","Crop planning","Map layers","Settings"]:
   b=QPushButton(name);b.clicked.connect(lambda _,n=name:self.statusBar().showMessage(n+" workspace"));sv.addWidget(b)
  sv.addStretch();sv.addWidget(QLabel("SYNTHETIC DATA MODE"));content=QWidget();v=QVBoxLayout(content);top=QHBoxLayout();titles=QVBoxLayout();ey=QLabel("AGRICULTURAL GIS / DESKTOP PROTOTYPE");ey.setStyleSheet("color:#9aac9d;font-size:10px");h=QLabel("Field overview");h.setStyleSheet("font-size:29px;font-weight:700");titles.addWidget(ey);titles.addWidget(h);top.addLayout(titles);top.addStretch()
  for label,fn,primary in [("Import GeoJSON",self.import_geo,False),("Export GeoJSON",self.export_geo,False),("Add field",self.add,True)]:
   b=QPushButton(label);b.clicked.connect(fn)
   if primary:b.setObjectName("primary")
   top.addWidget(b)
  v.addLayout(top);cards=QHBoxLayout();self.metrics=[]
  for cap,val in [("FIELD RECORDS","00"),("TOTAL AREA","0.0 ac"),("REFERENCE POINTS","00"),("DATA SOURCE","SYNTHETIC")]:
   f=QFrame();f.setStyleSheet("QFrame{background:#19251c;border:1px solid #2b4030;border-radius:9px;padding:7px}");box=QVBoxLayout(f);a=QLabel(cap);a.setStyleSheet("color:#9aac9d;font-size:9px");b=QLabel(val);b.setStyleSheet("font-size:21px;font-weight:700;color:#c6e4a4");box.addWidget(a);box.addWidget(b);self.metrics.append(b);cards.addWidget(f)
  v.addLayout(cards);v.addWidget(QLabel("Survey map / local coordinate view"));self.map=MapView();v.addWidget(self.map,2);bar=QHBoxLayout();bar.addWidget(QLabel("Field register"));bar.addStretch();delete=QPushButton("Delete selected");delete.clicked.connect(self.delete);bar.addWidget(delete);v.addLayout(bar);self.table=QTableWidget(0,5);self.table.setHorizontalHeaderLabels(["ID","Field name","Area (ac)","Crop","Points"]);self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch);self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows);self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers);v.addWidget(self.table,1);layout.addWidget(side);layout.addWidget(content,1);self.setCentralWidget(root);self.refresh()
 def refresh(self):
  fs=self.store.list_fields();self.metrics[0].setText(str(len(fs)).zfill(2));self.metrics[1].setText(f"{sum(f['area'] for f in fs):.1f} ac");self.metrics[2].setText(str(sum(len(f['points']) for f in fs)).zfill(2));self.table.setRowCount(len(fs))
  for r,f in enumerate(fs):
   for c,x in enumerate([f["id"],f["name"],f"{f['area']:.2f}",f["crop"] or "—",len(f["points"])]):self.table.setItem(r,c,QTableWidgetItem(str(x)))
  self.map.plot(fs)
 def add(self):
  d=AddField(self)
  if d.exec()==QDialog.DialogCode.Accepted:
   try:self.store.add_field(*d.values());self.refresh()
   except Exception as e:QMessageBox.warning(self,"Invalid field",str(e))
 def delete(self):
  r=self.table.currentRow()
  if r<0:return QMessageBox.information(self,"Select a field","Choose a row first.")
  self.store.delete_field(int(self.table.item(r,0).text()));self.refresh()
 def export_geo(self):
  p,_=QFileDialog.getSaveFileName(self,"Export GeoJSON","agrimap-fields.geojson","GeoJSON (*.geojson)")
  if p:self.store.export_geojson(p);QMessageBox.information(self,"Export complete","Field boundaries exported.")
 def import_geo(self):
  p,_=QFileDialog.getOpenFileName(self,"Import GeoJSON","","GeoJSON (*.geojson *.json)")
  if p:
   try:n=self.store.import_geojson(p);self.refresh();QMessageBox.information(self,"Import complete",f"Imported {n} polygon(s).")
   except Exception as e:QMessageBox.warning(self,"Import failed",str(e))
def main():
 app=QApplication(sys.argv);w=Main();w.show();return app.exec()
if __name__=="__main__":raise SystemExit(main())