def onModuleSelected(modulename):
  global tabWidgetModules
  tabWidgetModules.addTab(getattr(slicer.modules, modulename.lower()).widgetRepresentation(), modulename)

def onSagittalButton():
   global layoutWidget
   layoutWidget.setLayout(slicer.vtkMRMLLayoutNode.SlicerLayoutOneUpYellowSliceView)
   
def onAxialButton():
   global layoutWidget
   layoutWidget.setLayout(slicer.vtkMRMLLayoutNode.SlicerLayoutOneUpRedSliceView)
   
def onCoronalButton():
   global layoutWidget
   layoutWidget.setLayout(slicer.vtkMRMLLayoutNode.SlicerLayoutOneUpGreenSliceView)

   
  
import qt
import __main__
import argparse
import sys

mainWidget = qt.QWidget()
vlayout = qt.QVBoxLayout()
mainWidget.setLayout(vlayout)

tabWidgetViews = qt.QTabWidget()
vlayout.addWidget(tabWidgetViews)

layoutWidget = slicer.qMRMLLayoutWidget()
layoutManager = slicer.qSlicerLayoutManager() 
layoutManager.setMRMLScene(slicer.mrmlScene) 
layoutManager.setScriptedDisplayableManagerDirectory(slicer.app.slicerHome + "/bin/Python/mrmlDisplayableManager") 
layoutWidget.setLayoutManager(layoutManager) 
slicer.app.setLayoutManager(layoutManager) 
#layoutWidget.setLayout(slicer.vtkMRMLLayoutNode.SlicerLayoutFourUpView) 
#layoutWidget.setMRMLScene(slicer.mrmlScene)
layoutWidget.setLayout(slicer.vtkMRMLLayoutNode.SlicerLayoutOneUpRedSliceView)
vlayout.addTab(layoutWidget,"Sagittal")

#layoutManagerGreen = slicer.qMRMLLayoutWidget()
#layoutManagerGreen.setMRMLScene(slicer.mrmlScene)
#layoutManagerGreen.setLayout(slicer.vtkMRMLLayoutNode.SlicerLayoutOneUpGreenSliceView)
#tabWidgetViews.addTab(layoutManagerGreen,"green")

#layoutManagerYellow = slicer.qMRMLLayoutWidget()
#layoutManagerYellow.setMRMLScene(slicer.mrmlScene)
#layoutManagerYellow.setLayout(slicer.vtkMRMLLayoutNode.SlicerLayoutOneUpYellowSliceView)
#tabWidgetViews.addTab(layoutManagerYellow,"yellow")

hlayout = qt.QHBoxLayout()
vlayout.addLayout(hlayout)

loadDataButton = qt.QPushButton("Load Data")
hlayout.addWidget(loadDataButton)
loadDataButton.connect('clicked()', slicer.util.openAddVolumeDialog)

axialButton = qt.QPushButton("Axial")
hlayout.addWidget(axialButton)
axialButton.connect('clicked()', onAxialButton)

sagittalButton = qt.QPushButton("Sagittal")
hlayout.addWidget(sagittalButton)
sagittalButton.connect('clicked()', onSagittalButton)

coronalButton = qt.QPushButton("Coronal")
hlayout.addWidget(coronalButton)
coronalButton.connect('clicked()', onCoronalButton)
#saveDataButton = qt.QPushButton("Save Data")
#hlayout.addWidget(saveDataButton)
#saveDataButton.connect('clicked()', slicer.util.openSaveDataDialog)

#moduleSelector = slicer.qSlicerModuleSelectorToolBar()
#moduleSelector.setModuleManager(slicer.app.moduleManager())
#hlayout.addWidget(moduleSelector)
#moduleSelector.connect('moduleSelected(QString)', onModuleSelected)

#tabWidgetModules = qt.QTabWidget()
#vlayout.addWidget(tabWidgetModules)

modules = ["LoadCTX"]
for module in modules:
  #onModuleSelected(module)
  loadCTXWidget = slicer.modules.loadctxlight.widgetRepresentation()
  vlayout.addWidget(loadCTXWidget)
  #tabWidgetModules.addTab(loadCTXWidget, "Binfo")
  #tabWidgetModules.addTab(slicer.modules.tripdvh.widgetRepresentation(), "loadctx")

mainWidget.show()

__main__.mainWidget = mainWidget # Keep track of the widget to avoid its premature destruction


if len(sys.argv) > 1 and not sys.argv[1] == "":

   parser = argparse.ArgumentParser()
   parser.add_argument("-c","--loadCT", help="load CT file")
   parser.add_argument("-d","--loadDose", help="load Dose file")
   parser.add_argument("-v","--loadContour", help="load Binfo file")
   parser.add_argument("-p","--perscribedDose",nargs='?', const=1000, type=float, help="Dose to scale")
   args = parser.parse_args()
   doseNode = None
   if args.loadDose:
      success, doseNode = slicer.util.loadVolume(args.loadDose,properties = {}, returnNode = True)
      if not success:
         print "Can't load " + args.loadDose
      else:
         import LoadCTX
         logic = LoadCTX.LoadCTXLogic()
         logic.setDose(doseNode,args.perscribedDose, True)
         
   if args.loadCT:
      success = slicer.util.loadVolume(args.loadCT)
      if not success:
         print "Can't load " + args.loadCT
      else:
         if doseNode:
            slicer.app.applicationLogic().PropagateVolumeSelection(1)
            r = slicer.util.getNode('vtkMRMLSliceCompositeNodeRed')
            g = slicer.util.getNode('vtkMRMLSliceCompositeNodeGreen')
            y = slicer.util.getNode('vtkMRMLSliceCompositeNodeYellow')
            r.SetLinkedControl(1)
            r.SetForegroundVolumeID(doseNode.GetID())
            g.SetForegroundVolumeID(doseNode.GetID())
            y.SetForegroundVolumeID(doseNode.GetID())
            r.SetForegroundOpacity(0.5)
            #r.SetDoPropagateVolumeSelection(1)
            #g.SetDoPropagateVolumeSelection(1)
            #y.SetDoPropagateVolumeSelection(1)
            #slicer.app.applicationLogic().PropagateVolumeSelection(1)
   if args.loadContour:
      loadCTXWidget.self().loadBinfo(args.loadContour)
   #slicer.app.applicationLogic().PropagateVolumeSelection(0)