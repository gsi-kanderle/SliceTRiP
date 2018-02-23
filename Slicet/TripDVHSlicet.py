def onModuleSelected(modulename):
  global tabWidgetModules
  tabWidgetModules.addTab(getattr(slicer.modules, modulename.lower()).widgetRepresentation(), modulename)

import qt
import __main__
import argparse
import sys
import os

mainWidget = qt.QWidget()
vlayout = qt.QVBoxLayout()
mainWidget.setLayout(vlayout)

spliter = qt.QSplitter()
spliter.setOrientation(0)
spliter.setChildrenCollapsible(1)


hlayout = qt.QHBoxLayout()
frame = qt.QFrame()
vlayout.addLayout(hlayout)

#loadDataButton = qt.QPushButton("Load Data")
#hlayout.addWidget(loadDataButton)
#loadDataButton.connect('clicked()', slicer.util.openAddVolumeDialog)

vlayout.addWidget(spliter)

layoutWidget = slicer.qMRMLLayoutWidget()
layoutManager = slicer.qSlicerLayoutManager() 
layoutManager.setMRMLScene(slicer.mrmlScene) 
layoutManager.setScriptedDisplayableManagerDirectory(slicer.app.slicerHome + "/bin/Python/mrmlDisplayableManager") 
layoutWidget.setLayoutManager(layoutManager) 
slicer.app.setLayoutManager(layoutManager) 
layoutWidget.setLayout(slicer.vtkMRMLLayoutNode.SlicerLayoutFourUpQuantitativeView )
spliter.addWidget(layoutWidget)
#saveDataButton = qt.QPushButton("Save Data")
#hlayout.addWidget(saveDataButton)
#saveDataButton.connect('clicked()', slicer.util.openSaveDataDialog)
#tabWidget = qt.QTabWidget()
#vlayout.addWidget(tabWidget)
#LoadCTXLight
modules = ["TRiPDVH"]
for modulename in modules:
  #onModuleSelected(module)
  #tabWidget.addTab(getattr(slicer.modules, modulename.lower()).widgetRepresentation(), modulename)
  loadWidget = getattr(slicer.modules, modulename.lower()).widgetRepresentation()
  spliter.addWidget(loadWidget)
  #tabWidgetModules.addTab(loadWidget, "Binfo")
  #tabWidgetModules.addTab(slicer.modules.tripdvh.widgetRepresentation(), "loadctx")

mainWidget.show()

__main__.mainWidget = mainWidget # Keep track of the widget to avoid its premature destruction


if len(sys.argv) > 1 and not sys.argv[1] == "":

   parser = argparse.ArgumentParser()
   parser.add_argument('fileName', metavar='fileName', nargs='+',
                    help='dvh filename')
   parser.add_argument("-v","--selectContour", help="Which contour to display, default all")
   parser.add_argument("-p","--perscribedDose",nargs='?', const=100, type=float, help="Dose to scale")
   args = parser.parse_args()
   
   perscribedDose = 100
   if args.perscribedDose:
      perscribedDose = args.perscribedDose
   
   if args.fileName:
      for file in args.fileName:
         if os.path.isfile(file):
            loadWidget.self().loadgd(file,perscribedDose)
         
   for plan in loadWidget.self().patient.plans:
      for voi in plan.vois:
         if args.selectContour:
            if voi.name == args.selectContour.lower():
               voi.voiTableCheckBox.setChecked(True)
         else:
            voi.voiTableCheckBox.setChecked(True)
   
   import TRiPDVH
   logic = TRiPDVH.TRiPDVHLogic()
   logic.addChart(loadWidget.self().patient)