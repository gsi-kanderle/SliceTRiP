import os, re
import unittest
from __main__ import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
import numpy as np
import ComparePatientsLib
reload(ComparePatientsLib)

#
# TRiPDVH
#

class TRiPDVH(ScriptedLoadableModule):
  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    parent.title = "TRiP DVH" # TODO make this more human readable by adding spaces
    parent.categories = ["SliceTRiP"]
    parent.dependencies = []
    parent.contributors = ["Kristjan Anderle (GSI)"] # replace with "Firstname Lastname (Org)"
    parent.helpText = """
    Module to display dvh gd files.
    """
    parent.acknowledgementText = """
   Developed by Kristjan Anderle.
""" # replace with organization, grant and thanks.

#
# qTRiPDVHWidget
#

class TRiPDVHWidget(ScriptedLoadableModuleWidget):
  def setup(self):
    ScriptedLoadableModuleWidget.setup(self)
    # Instantiate and connect widgets ...

    #
    # Parameters Area
    #
    parametersCollapsibleButton = ctk.ctkCollapsibleButton()
    parametersCollapsibleButton.text = "Parameters"
    self.layout.addWidget(parametersCollapsibleButton)

    # Layout within the dummy collapsible button
    self.parametersFormLayout = qt.QFormLayout(parametersCollapsibleButton)
    
    
    self.buttonForm = qt.QGridLayout()
    #
    # Load gd Button
    #
    self.loadGdButton = qt.QPushButton("Load gd file")
    self.loadGdButton.toolTip = "Load gd File."
    self.loadGdButton.enabled = True
    
    self.buttonForm.addWidget(self.loadGdButton,0,0)
    
    #
    # List of DVHs
    #
    # Binfo
    #self.dvhList = qt.QComboBox()    
    #self.dvhList.setToolTip( "List of loaded DVHs" )
    #self.dvhList.enabled = False
    #self.parametersFormLayout.addRow("DVH:", self.dvhList)
    
    

    
    # Input optimized Dose:
    
    self.grayInfo = qt.QLabel()
    self.grayInfo.setText("Scale to Gray:")
    self.buttonForm.addWidget(self.grayInfo,1,0)
    
    self.grayCheckbox = qt.QCheckBox()
    self.grayCheckbox.setToolTip("Uncheck if you want to display in percentage instead of Gray.")
    self.grayCheckbox.setChecked(False)
    self.buttonForm.addWidget(self.grayCheckbox,1,1)
    
    self.inputDose = qt.QDoubleSpinBox()     
    self.inputDose.setToolTip( "Optimization dose." )
    self.inputDose.setMaximum(1000)
    self.inputDose.setMinimum(0)
    self.inputDose.setValue(100)
    self.inputDose.setRange(0, 1020)
    self.inputDose.enabled = False
    self.buttonForm.addWidget(self.inputDose,1,2)
    
    
    
    self.parametersFormLayout.addRow(self.buttonForm)
    
    ## Voi list
    #self.voiComboBox = qt.QComboBox()
    #self.parametersFormLayout.addRow("Select Voi: ", self.voiComboBox)
    

    #
    # Apply Button
    #
    self.applyButton = qt.QPushButton("Show DVH")
    self.applyButton.toolTip = "Run the algorithm."
    self.applyButton.enabled = False
    self.buttonForm.addWidget(self.applyButton,0,1)
    
    self.clearButton = qt.QPushButton("Clear")
    self.clearButton.toolTip = "Clears all module."
    self.clearButton.enabled = True
    self.buttonForm.addWidget(self.clearButton,0,2)
    
   ##
    ## Recalculate with different Dose
    ##
    #self.recalcButton = qt.QPushButton("Recalculate dose values")
    #self.recalcButton.toolTip = "Recalculate all the dose values with different input."
    #self.recalcButton.visible = False
    #self.parametersFormLayout.addRow(self.recalcButton)
    
    ##
    ## Export values
    ##
    #self.exportButton = qt.QPushButton("Export Values")
    #self.exportButton.toolTip = "Export all values."
    #self.exportButton.visible = False 
    #self.parametersFormLayout.addRow(self.exportButton)
    
    ##
    ## Copy values
    ##
    #self.copyButton = qt.QPushButton("Copy Values")
    #self.copyButton.toolTip = "Copy values on clipboard."
    #self.copyButton.visible = False
    #self.parametersFormLayout.addRow(self.copyButton)
    
    self.parametersFormLayout.addRow(self.buttonForm)
    
    # Tab wiget
    self.tabWidget = qt.QTabWidget()
    self.parametersFormLayout.addRow(self.tabWidget)
    
    self.saveButton = qt.QPushButton("Save screenshot")
    self.saveButton.toolTip = "Saves current view as a screenshot."
    self.parametersFormLayout.addRow(self.saveButton)
    
    

    # Add vertical spacer
    self.layout.addStretch(1)
    
    # Patien struct to save all plans
    self.patient = ComparePatientsLib.Patient("NewPatient")
    
     # connections
    #self.dvhList.connect('currentIndexChanged(int)', self.setDvhList)
    self.applyButton.connect('clicked(bool)', self.onApplyButton)
    self.loadGdButton.connect('clicked(bool)', self.onLoadGdButton)
    self.clearButton.connect('clicked(bool)', self.onClear)
    #self.recalcButton.connect('clicked(bool)', self.onRecalcButton)
    #self.exportButton.connect('clicked(bool)', self.onExportButton)
    self.saveButton.connect('clicked(bool)', self.onSaveButton)
    self.grayCheckbox.connect('clicked(bool)',self.onChangeScale)
    #self.voiComboBox.connect('currentIndexChanged(QString)', self.setDvhTable)
    

  def cleanup(self):
    self.patient = None
    pass


  def onLoadGdButton(self):
    #self.dvhTable.visible = False
    loadFileName = qt.QFileDialog()
    filePathList=loadFileName.getOpenFileNames(None,"Select DVH gd File","","GD (*.gd)")
    optDose = self.inputDose.value
    for filePath in filePathList:
       self.loadgd(filePath, optDose)
    
  def loadgd(self, filePath, optDose = 1):    
    filePrefix, fileExtension = os.path.splitext(filePath)
    if filePath == '':
      return
    if not fileExtension == '.gd':
      print "Wrong extension"
      return
      
    newPlan = ComparePatientsLib.Plan()
    newPlan.name = os.path.basename(filePath)
    newPlan.optDose = optDose
    newPlan.readGDFile(filePath)
    self.patient.add_plan(newPlan)
    
    table= qt.QTableWidget()
    self.tabWidget.addTab(table,newPlan.name)
    self.tabWidget.setCurrentWidget(table)
    
    #self.parametersFormLayout.addRow(table)
    newPlan.voiQtTable = table
    newPlan.setTable()
    self.applyButton.enabled=True

    
  def onClear(self):
     self.tabWidget.clear()
     self.patient.clear()
     self.patient = ComparePatientsLib.Patient("NewPatient")
  
  def onApplyButton(self):
    logic = TRiPDVHLogic()    
    logic.addChart(self.patient)
    print("Displaying")

  def onChangeScale(self):
    if self.grayCheckbox.checkState() == 0:
      self.inputDose.setValue(100)
      self.inputDose.enabled = False
    else:
      self.inputDose.enabled = True
      self.inputDose.setValue(2)
  
  def onSaveButton(self):
     filePath = qt.QFileDialog().getSaveFileName(None,"Save Screenshot","","png (*.png)")
     filePrefix, fileExtension = os.path.splitext(filePath)
     if not fileExtension == ".png":
        filePath = filePrefix + ".png"

     name =  os.path.basename(filePrefix)
     
     logic = TRiPDVHLogic()
     logic.saveScreenshot(name,filePath,"DVH Screenshot")
     print "Screenshot saved to " + filePath
  
  def onRecalcButton(self):
    self.dvh[-1].optDose = self.inputDose.value
    #self.dvh[-1].voiTable.clearContents()
    self.dvh[-1].setTable(self.parametersFormLayout)
    
  def onExportButton(self):
    loadFileName = qt.QFileDialog()
    filePath = loadFileName.getSaveFileName()
    if filePath is not '':
      for dvh in self.dvh:
	dvh.exportValuesAsText( filePath )
	
  def onCopyButton(self):
    if len(self.dvh) > 1:
      print "Too many dvhs. Select only one."
      #for dvh in self.dvh:
	#dvh.exportValuesOnClipboard()
    else:
      self.dvh[0].exportValuesOnClipboard()
	

#
# TRiPDVHLogic
#

class TRiPDVHLogic:
  """This class should implement all the actual 
  computation done by your module.  The interface 
  should be such that other python code can import
  this class and make use of the functionality without
  requiring an instance of the Widget
  """
  def __init__(self):
    pass

  def addChart(self,patient):
    ln = slicer.util.getNode(pattern='vtkMRMLLayoutNode*')
    ln.SetViewArrangement(26)
    cvn = slicer.util.getNode(pattern='vtkMRMLChartViewNode*')
    cn = slicer.mrmlScene.AddNode(slicer.vtkMRMLChartNode())
    linePattern = ["solid","dashed","dotted","dashed-dotted"]
    planNumber = 0
    chartNames = []
    
    if patient.plans == []:
       print "No plans."
       return

    for plan in patient.plans:
      for voi in plan.vois:
        if voi.voiTableCheckBox.checkState() == 0:
           continue
        voi.setSlicerDoubleArray() #set double array for chart
        newName = voi.name
        n = 1
        nameBool = True
        while nameBool:
           nameBool = False
           for name in chartNames:
              if newName == name:
                 nameBool = True
                 newName = voi.name + "_" + str(n)
                 n += 1
                 break

	cn.AddArray(newName, voi.dn.GetID())
	cn.SetProperty(voi.name,'linePattern',linePattern[planNumber])
	chartNames.append(newName)
      planNumber += 1

    if plan.optDose == 100:
       cn.SetProperty('default', 'xAxisLabel', 'Dose [%]')
    else:
       cn.SetProperty('default', 'xAxisLabel', 'Dose [Gy]')
    cn.SetProperty('default', 'yAxisLabel', 'Volume [%]')
    cvn.SetChartNodeID(cn.GetID())
    return
    
  def saveScreenshot(self, name, filePath, description):
    type = slicer.qMRMLScreenShotDialog.FullLayout
    lm = slicer.app.layoutManager()
    widget = lm.viewport()
    # grab and convert to vtk image data
    qpixMap = qt.QPixmap().grabWidget(widget)
    qimage = qpixMap.toImage()
    imageData = vtk.vtkImageData()
    slicer.qMRMLUtils().qImageToVtkImageData(qimage,imageData)

    annotationLogic = slicer.modules.annotations.logic()
    annotationLogic.CreateSnapShot(name, description, type, 1, imageData)
    
    snapshotNode = slicer.util.getNode(name)
    
    if not snapshotNode:
       print "Can't get snapshotNode"
       return
    
    if not slicer.util.saveNode(snapshotNode, filePath):
       print "Can't save " + filePath
       return

class TRiPDVHTest(unittest.TestCase):
  """
  This is the test case for your scripted module.
  """

  def delayDisplay(self,message,msec=1000):
    """This utility method displays a small dialog and waits.
    This does two things: 1) it lets the event loop catch up
    to the state of the test so that rendering and widget updates
    have all taken place before the test continues and 2) it
    shows the user/developer/tester the state of the test
    so that we'll know when it breaks.
    """
    print(message)
    self.info = qt.QDialog()
    self.infoLayout = qt.QVBoxLayout()
    self.info.setLayout(self.infoLayout)
    self.label = qt.QLabel(message,self.info)
    self.infoLayout.addWidget(self.label)
    qt.QTimer.singleShot(msec, self.info.close)
    self.info.exec_()

  def setUp(self):
    """ Do whatever is needed to reset the state - typically a scene clear will be enough.
    """
    slicer.mrmlScene.Clear(0)

  def runTest(self):
    """Run as few or as many tests as needed here.
    """
    self.setUp()
    self.test_TRiPDVH1()

  def test_TRiPDVH1(self):
    """ Ideally you should have several levels of tests.  At the lowest level
    tests sould exercise the functionality of the logic with different inputs
    (both valid and invalid).  At higher levels your tests should emulate the
    way the user would interact with your code and confirm that it still works
    the way you intended.
    One of the most important features of the tests is that it should alert other
    developers when their changes will have an impact on the behavior of your
    module.  For example, if a developer removes a feature that you depend on,
    your test should break so they know that the feature is needed.
    """

    self.delayDisplay("Starting the test")
    #
    # first, get some data
    #
    import urllib
    downloads = (
        ('http://slicer.kitware.com/midas3/download?items=5767', 'FA.nrrd', slicer.util.loadVolume),
        )

    for url,name,loader in downloads:
      filePath = slicer.app.temporaryPath + '/' + name
      if not os.path.exists(filePath) or os.stat(filePath).st_size == 0:
        print('Requesting download %s from %s...\n' % (name, url))
        urllib.urlretrieve(url, filePath)
      if loader:
        print('Loading %s...\n' % (name,))
        loader(filePath)
    self.delayDisplay('Finished with download and loading\n')

    volumeNode = slicer.util.getNode(pattern="FA")
    logic = TRiPDVHLogic()
    self.assertTrue( logic.hasImageData(volumeNode) )
    self.delayDisplay('Test passed!')
