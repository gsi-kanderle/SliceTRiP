import os, re
import unittest
from __main__ import vtk, qt, ctk, slicer
import numpy as np
import time

import LoadCTXLib

#import binfo

#
# LoadCTX
#

class LoadCTX:
  def __init__(self, parent):
    parent.title = "Load TRiP Volume" # TODO make this more human readable by adding spaces
    parent.categories = ["SliceTRiP"]
    parent.dependencies = []
    parent.contributors = ["Kristjan Anderle (GSI)"] # replace with "Firstname Lastname (Org)"
    parent.helpText = """
    This is a module for loading binfo files and setting colormap to GSI Standard for Dose.
    """
    parent.acknowledgementText = """
    This was developed for better representation of binfo files..
""" # replace with organization, grant and thanks.
    #parent.icon = qt.QIcon(':Icons/XLarge/SlicerDownloadMRHead.png')
    self.parent = parent
    #reload(binfo)

    # Add this test to the SelfTest module's list for discovery when the module
    # is created.  Since this module may be discovered before SelfTests itself,
    # create the list if it doesn't already exist.
    try:
      slicer.selfTests
    except AttributeError:
      slicer.selfTests = {}
    slicer.selfTests['LoadCTX'] = self.runTest

  def runTest(self):
    tester = LoadCTXTest()
    tester.runTest()

#
# qLoadCTXWidget
#

class LoadCTXWidget:
  def __init__(self, parent = None):
    if not parent:
      self.parent = slicer.qMRMLWidget()
      self.parent.setLayout(qt.QVBoxLayout())
      self.parent.setMRMLScene(slicer.mrmlScene)
    else:
      self.parent = parent
    self.layout = self.parent.layout()
    if not parent:
      self.setup()
      self.parent.show()

  def setup(self):
    # Instantiate and connect widgets ...

    #
    # Reload and Test area
    #
    reloadCollapsibleButton = ctk.ctkCollapsibleButton()
    reloadCollapsibleButton.text = "Reload && Test"
    self.layout.addWidget(reloadCollapsibleButton)
    reloadFormLayout = qt.QFormLayout(reloadCollapsibleButton)

    # reload button
    # (use this during development, but remove it when delivering
    #  your module to users)
    self.reloadCTXButton = qt.QPushButton("Reload")
    self.reloadCTXButton.toolTip = "Reload this module."
    self.reloadCTXButton.name = "LoadCTX Reload"
    reloadFormLayout.addWidget(self.reloadCTXButton)
    self.reloadCTXButton.connect('clicked()', self.onReload)

    # reload and test button
    # (use this during development, but remove it when delivering
    #  your module to users)
    self.reloadAndTestButton = qt.QPushButton("Reload and Test")
    self.reloadAndTestButton.toolTip = "Reload this module and then run the self tests."
    reloadFormLayout.addWidget(self.reloadAndTestButton)
    self.reloadAndTestButton.connect('clicked()', self.onReloadAndTest)

    #
    # Parameters Area
    #
    
    
    binfoCollapsibleButton = ctk.ctkCollapsibleButton()
    binfoCollapsibleButton.text = "LoadBinfo"
    self.layout.addWidget(binfoCollapsibleButton)

    # Layout within the dummy collapsible button
    binfoFormLayout = qt.QFormLayout(binfoCollapsibleButton)
    #Load File
    #
    # Load CTX File Button
    #
    self.loadButton = qt.QPushButton("Load Binfo File")
    self.loadButton.toolTip = "Load binfo file."
    self.loadButton.enabled = True
    
    binfoFormLayout.addRow(self.loadButton)
    
    #TODO: Daj opcijo, da se izbere doza in potem se zravn checkbox, zato da zberes, al ti normira na to al ne.
    # Optimized dose:
    #self.optDose = qt.QDoubleSpinBox()     
    #self.optDose.setToolTip( "Optimized dose value." )
    #self.optDose.setValue(25)
    #self.optDose.setRange(0, 100)
    #self.optDose.enabled = True
    #binfoFormLayout.addRow("Dose:", self.optDose)
   
   
    # Binfo
    self.binfoListFile = qt.QComboBox()    
    self.binfoListFile.setToolTip( "Input file" )
    self.binfoListFile.enabled = False
    binfoFormLayout.addRow("Binfo:", self.binfoListFile)
    

    #self.fileName.getOpenFileName(self, tr("Open File"),"",tr("Files (*.*)"));
    
    # Voi list
    self.voiComboBox = qt.QComboBox()
    self.voiComboBox.enabled = False
    binfoFormLayout.addRow("Select Voi: ", self.voiComboBox)
    
    # Motion state list
    self.motionStateComboBox = qt.QComboBox()
    self.motionStateComboBox.enabled = False
    binfoFormLayout.addRow("Select Motion State: ", self.motionStateComboBox)
    #
    # Show Button
    #
    self.buttonForm = qt.QGridLayout()
    
    self.show3DButton = qt.QPushButton("Load VOI")
    self.show3DButton.enabled = False
    self.buttonForm.addWidget(self.show3DButton,0,0)
    binfoFormLayout.addRow(self.buttonForm)
    
    
    #
    # Modify Volumes
    #
    doseCollapsibleButton = ctk.ctkCollapsibleButton()
    doseCollapsibleButton.text = "Modify Volume"
    self.layout.addWidget(doseCollapsibleButton)
    
    doseFormLayout = qt.QFormLayout(doseCollapsibleButton)
    #
    # Select dose volume
    #
    self.selectVolume = slicer.qMRMLNodeComboBox()
    self.selectVolume.nodeTypes = ( ("vtkMRMLScalarVolumeNode"),("vtkMRMLVectorVolumeNode"),"" )
    #self.selectVolume.addAttribute( "vtkMRMLScalarVolumeNode", "LabelMap", 0 )
    #self.selectVolume.selectVolumeUponCreation = True
    self.selectVolume.addEnabled = False
    self.selectVolume.removeEnabled = False
    self.selectVolume.noneEnabled = True
    self.selectVolume.showHidden = False
    self.selectVolume.showChildNodeTypes = False
    self.selectVolume.setMRMLScene( slicer.mrmlScene )
    self.selectVolume.setToolTip( "Select dose volume." )
    doseFormLayout.addRow("Volume: ", self.selectVolume)
    
    # Input dose value
    # TO DO: add check box to choose between substract origin or change origin
    self.optDoseLayout = qt.QGridLayout(binfoCollapsibleButton)
    
    self.optDoseForm = qt.QFormLayout()
    self.optDoseBox = qt.QDoubleSpinBox()     
    self.optDoseBox.setToolTip( "The optimization value for dose." )
    self.optDoseBox.setValue(24)
    self.optDoseBox.setRange(0, 1000)
    self.optDoseForm.addRow("Dose optimization Value", self.optDoseBox)
    
    self.pyhsDoseForm = qt.QFormLayout()
    self.pyhsDoseCheckBox = qt.QCheckBox()
    self.pyhsDoseCheckBox.setToolTip("Check if the dose volume is in permil")
    self.pyhsDoseForm.addRow("Pyhsical dose: ", self.pyhsDoseCheckBox)
    
    self.overDoseOffForm = qt.QFormLayout()
    self.overDoseOffCheckBox = qt.QCheckBox()
    self.overDoseOffCheckBox.setToolTip("Check if you don't want to display overodse.")
    self.overDoseOffForm.addRow("Overdose Off: ", self.overDoseOffCheckBox)
    
    self.optDoseLayout.addLayout(self.optDoseForm,0,0)
    self.optDoseLayout.addLayout(self.pyhsDoseForm,0,1)
    self.optDoseLayout.addLayout(self.overDoseOffForm,0,2)
    
    doseFormLayout.addRow(self.optDoseLayout)
    #
    # Set dose colormap
    #
    self.setDoseColorButton = qt.QPushButton("Set colormap for dose volume")
    self.setDoseColorButton.toolTip = "Creates default GSI Color table and sets it for input volume."
    self.setDoseColorButton.enabled = False
    self.optDoseLayout.addWidget(self.setDoseColorButton,1,0)
    
    #
    # Set dose colormap
    #
    self.setVectorFieldButton = qt.QPushButton("Set TRiP vector field")
    self.setVectorFieldButton.toolTip = "Multiplies vector field values with pixel spacing (historical reason in TRiP)."
    self.setVectorFieldButton.enabled = False
    self.optDoseLayout.addWidget(self.setVectorFieldButton,1,1)
    
    #
    # Origins to zero Button
    #
    self.setOriginButton = qt.QPushButton("Set Origins to zero")
    self.setOriginButton.toolTip = "Set origins to zero."
    self.setOriginButton.enabled = True
    self.optDoseLayout.addWidget(self.setOriginButton,2,0)
    
    
    #
    # Prepare plan cube
    #
    self.setPlanCubeButton = qt.QPushButton("Create trafo from VF")
    self.setPlanCubeButton.toolTip = "Prepares plan cube based on input dose cube and dose optimization value."
    self.setPlanCubeButton.enabled = False
    self.optDoseLayout.addWidget(self.setPlanCubeButton,2,1)
    
    #
    # Modify Volumes
    #
    doseDifferenceButton = ctk.ctkCollapsibleButton()
    doseDifferenceButton.text = "Dose difference"
    self.layout.addWidget(doseDifferenceButton)
    
    doseDifferenceLayout = qt.QFormLayout(doseDifferenceButton)
    #
    # Select SBRT dose
    #
    self.selectSBRTDose = slicer.qMRMLNodeComboBox()
    self.selectSBRTDose.nodeTypes = ( ("vtkMRMLScalarVolumeNode"),("vtkMRMLVectorVolumeNode"),("vtkMRMLLabelMapVolumeNode"),"" )
    #self.selectSBRTDose.addAttribute( "vtkMRMLScalarVolumeNode", "LabelMap", 1 )
    #self.selectSBRTDose.selectSBRTDoseUponCreation = True
    self.selectSBRTDose.addEnabled = False
    self.selectSBRTDose.removeEnabled = False
    self.selectSBRTDose.noneEnabled = True
    self.selectSBRTDose.showHidden = False
    self.selectSBRTDose.showChildNodeTypes = False
    self.selectSBRTDose.setMRMLScene( slicer.mrmlScene )
    self.selectSBRTDose.setToolTip( "Select SBRT dose volume." )
    doseDifferenceLayout.addRow("SBRT dose: ", self.selectSBRTDose)
    #
    # Select PT dose
    #
    self.selectPTDose = slicer.qMRMLNodeComboBox()
    self.selectPTDose.nodeTypes = ( ("vtkMRMLScalarVolumeNode"),("vtkMRMLVectorVolumeNode"),("vtkMRMLLabelMapVolumeNode"),"" )
    #self.selectPTDose.addAttribute( "vtkMRMLScalarVolumeNode", "LabelMap", 0 )
    #self.selectPTDose.selectPTDoseUponCreation = True
    self.selectPTDose.addEnabled = False
    self.selectPTDose.removeEnabled = False
    self.selectPTDose.noneEnabled = True
    self.selectPTDose.showHidden = False
    self.selectPTDose.showChildNodeTypes = False
    self.selectPTDose.setMRMLScene( slicer.mrmlScene )
    self.selectPTDose.setToolTip( "Select PT dose volume." )
    doseDifferenceLayout.addRow("PT dose: ", self.selectPTDose)
    #
    # Recalculate button
    #
    self.setDoseDifferenceButton = qt.QPushButton("Calculate dose difference")
    self.setDoseDifferenceButton.toolTip = "Takes two doses into account and calculates their difference."
    self.setDoseDifferenceButton.enabled = True
    doseDifferenceLayout.addRow(self.setDoseDifferenceButton)
    #
    # Recalculate button
    #
    self.setVOIUnionButton = qt.QPushButton("Create VOI Union")
    self.setVOIUnionButton.toolTip = "Takes two scalar volumes and makes or operation between them."
    self.setVOIUnionButton.enabled = True
    doseDifferenceLayout.addRow(self.setVOIUnionButton)
    #
    # Copy origin button
    #
    self.setCopyOriginButton = qt.QPushButton("Copy Origin")
    self.setCopyOriginButton.toolTip = "Takes origin from SBRT and copy it to PT."
    self.setCopyOriginButton.enabled = True
    doseDifferenceLayout.addRow(self.setCopyOriginButton)
    
    #
    # Add vector volumes Button
    #
    self.setAddVecorButton = qt.QPushButton("Add two vector volumes")
    self.setAddVecorButton.toolTip = "Set origins to zero."
    self.setAddVecorButton.enabled = True
    doseDifferenceLayout.addRow(self.setAddVecorButton)
    
    # connections
    self.show3DButton.connect('clicked(bool)', self.onShow3DButton)
    self.setOriginButton.connect('clicked(bool)', self.onSetOriginButton)
    self.setPlanCubeButton.connect('clicked(bool)', self.onSetPlanCubeButton)
    self.loadButton.connect('clicked(bool)', self.onLoadButton)
    self.voiComboBox.connect('currentIndexChanged(QString)', self.setMotionStatesFromComboBox)
    self.binfoListFile.connect('currentIndexChanged(int)', self.setBinfoFile)
    self.setDoseColorButton.connect('clicked(bool)', self.onSetDoseColorButton)
    self.setVectorFieldButton.connect('clicked(bool)', self.onSetVectorFieldButton)
    self.pyhsDoseCheckBox.connect('clicked(bool)',self.onChangePyhsDoseCheckBox)
    self.selectVolume.connect("currentNodeChanged(vtkMRMLNode*)", self.onSelect)
    self.setDoseDifferenceButton.connect('clicked(bool)', self.onSetDoseDifferenceButton)
    self.setVOIUnionButton.connect('clicked(bool)', self.onSetVOIUnionButton)
    self.setCopyOriginButton.connect('clicked(bool)', self.onSetCopyOriginButton)
    self.setAddVecorButton.connect('clicked(bool)', self.onSetAddVecorButton)

    # Add vertical spacer
    self.layout.addStretch(1)
    
    # Binfo file:
    #binfo=Binfo()
    self.binfoList = []
    self.segmentationList = []
    self.cbt = None
    

  def cleanup(self):
    pass

  def onSelect(self,node):
    if not node:
      return
    if node.IsA('vtkMRMLVectorVolumeNode'):
      self.setVectorFieldButton.enabled = True
      self.setDoseColorButton.enabled = False
      self.setPlanCubeButton.enabled = True
    elif node.IsA('vtkMRMLScalarVolumeNode'):
      self.setVectorFieldButton.enabled = False
      self.setDoseColorButton.enabled = True
      self.setPlanCubeButton.enabled = False
      
  #Load Binfo in Slicer
  def onLoadButton(self): 
    logic = LoadCTXLogic()  
    loadFileName = qt.QFileDialog()
    #loadFileName.setFileMode(loadFileName.AnyFile)
    #loadFileName.setFilter("Text files (*.txt)")
    #loadFileName.setNameFilter("Images (*.png *.xpm *.jpg)");
    filePathList=loadFileName.getOpenFileNames(caption = "Helo")
    for filePath in filePathList:
      filePrefix, fileExtension = os.path.splitext(filePath)
      if fileExtension == ".binfo":
	self.voiComboBox.clear()
	self.motionStateComboBox.clear() 
	binfo = LoadCTXLib.Binfo()
	binfo.readFile(filePath)
	self.binfoList.append( binfo )
	self.binfoListFile.addItem( binfo.name )
	#self.setBinfoFile(-1)
	#self.binfoListFile.setCurrentIndex(-1)
	self.binfoListFile.enabled = True
	
	#Create segmentation node for this binfo
	segmentationNode = slicer.vtkMRMLSegmentationNode()
	segmentationNode.SetName(os.path.basename(filePrefix))
	slicer.mrmlScene.AddNode(segmentationNode)
	self.segmentationList.append(segmentationNode)
	
	displayNode = slicer.vtkMRMLSegmentationDisplayNode()
	slicer.mrmlScene.AddNode(displayNode)
	segmentationNode.SetAndObserveDisplayNodeID(displayNode.GetID())
	
	storageNode = slicer.vtkMRMLSegmentationStorageNode()
	slicer.mrmlScene.AddNode(storageNode)
        segmentationNode.SetAndObserveStorageNodeID(storageNode.GetID())
		
	#for voiName in binfo.get_voi_names():
	  #voi = binfo.get_voi_by_name(voiName)
	  #self.voiComboBox.addItem(voiName)
	  #self.setMotionStates(voi)
	  
	#self.voiComboBox.enabled = True
	#self.motionStateComboBox.enabled = True
		
      else:
	if not filePath == '':
	  qt.QMessageBox.critical(
	    slicer.util.mainWindow(),
	    'Load TRiP Cube', 'Unknown file type: ' + fileExtension)
      

  def setBinfoFile(self, binfoNumber):
    self.voiComboBox.clear()
    self.motionStateComboBox.clear()
    binfo = self.binfoList[binfoNumber]
    
    #self.binfoListFile.setCurrentIndex[binfoNumber]
    for voiName in binfo.get_voi_names():
      voi = binfo.get_voi_by_name(voiName)
      self.voiComboBox.addItem(voiName)
      self.setMotionStates(voi)
	  
    self.voiComboBox.enabled = True
    self.motionStateComboBox.enabled = True
    self.show3DButton.enabled = True
  
  def setMotionStatesFromComboBox(self,voiName):
    binfo = self.binfoList[self.binfoListFile.currentIndex]
    voi = binfo.get_voi_by_name(voiName)
    self.setMotionStates(voi)
  
  
  #Find out motion states from binfo file
  def setMotionStates(self,voi): 
    if voi is not None:
      self.motionStateComboBox.clear()
      motionStates=voi.N_of_motion_states
      for i in range(0,motionStates):
        self.motionStateComboBox.addItem(voi.motionStateDescription[i])
    else:
      print "Error, no voi."

 
  def onShow3DButton(self):
    binfo=self.binfoList[self.binfoListFile.currentIndex]
    segmentationNode = self.segmentationList[self.binfoListFile.currentIndex]
    filePrefix, fileExtension = os.path.splitext(binfo.filePath)
    voi = binfo.get_voi_by_name(self.voiComboBox.currentText)
    if not voi:
      print "Error, voi not found."
      return
    filePath = filePrefix + voi.name + ".nrrd"
    logic = LoadCTXLogic()
    n=self.motionStateComboBox.currentIndex
    voi.slicerNodeID[n]=logic.loadVoi(filePath,segmentationNode, motionState=n,voi=voi)

  def onSetVectorFieldButton(self):
    logic = LoadCTXLogic()
    vectorNode = self.selectVolume.currentNode()
    if not vectorNode:
      print "No vector field."
      return
    logic.setVectorField(vectorNode)
    
  def onSetDoseColorButton(self):
    logic = LoadCTXLogic()
    doseNode = self.selectVolume.currentNode()
    optDoseValue = self.optDoseBox.value
    if not doseNode:
      print "No SBRT and/or PT dose!"
      return
    
    if self.overDoseOffCheckBox.checkState() == 0:
      overDoseOff = False
    else:
      overDoseOff = True
    
    logic.setDose(doseNode,optDoseValue, overDoseOff)
    
  def onSetOriginButton(self):
    nodes = slicer.util.getNodes('vtkMRMLScalarVolumeNode*')
    for currentNode in nodes:
      nodes[currentNode].GetName()
      nodes[currentNode].SetOrigin((0,0,0))
    print "Done!"
    return

  def onSetPlanCubeButton(self):
    logic = LoadCTXLogic()
    doseNode = self.selectVolume.currentNode()
    #optDoseValue = self.optDoseBox.value
    logic.setPlanCube(doseNode)
    
  def onChangePyhsDoseCheckBox(self):
    if self.pyhsDoseCheckBox.checkState() == 0:
      self.optDoseBox.setValue(25)
      self.optDoseBox.enabled = True
    else:
      self.optDoseBox.setValue(1000)
      self.optDoseBox.enabled = False
  
  def onSetDoseDifferenceButton(self):
    logic = LoadCTXLogic()
    sbrtNode = self.selectSBRTDose.currentNode()
    ptNode = self.selectPTDose.currentNode()
    if not sbrtNode:
      print "No SBRT and/or PT dose!."
      return
    logic.makeDoseDifference(sbrtNode,ptNode)
  
  def onSetVOIUnionButton(self):
    logic = LoadCTXLogic()
    voi1Node = self.selectSBRTDose.currentNode()
    #voi2Node = self.selectPTDose.currentNode()
    #if not voi1Node or not voi2Node:
      #print "Input two vois!."
      #return
    logic.makeVOIUnioun(voi1Node)
    
  def onSetCopyOriginButton(self):
    sbrtNode = self.selectSBRTDose.currentNode()
    ptNode = self.selectPTDose.currentNode()
    if not ptNode or not sbrtNode:
      print "No SBRT and/or PT dose!."
      return
    ptNode.SetOrigin(sbrtNode.GetOrigin())
    
  def onSetAddVecorButton(self):
    logic = LoadCTXLogic()
    vector1 = self.selectSBRTDose.currentNode()
    vector2 = self.selectPTDose.currentNode()
    if not vector1 or not vector2:
      print "No SBRT and/or PT dose!."
      return
    logic.addVectors(vector1, vector2)
  

  def onReload(self,moduleName="LoadCTX"):
    """Generic reload method for any scripted module.
    ModuleWizard will subsitute correct default moduleName.
    """
    globals()[moduleName] = slicer.util.reloadScriptedModule(moduleName)

  def onReloadAndTest(self,moduleName="LoadCTX"):
    try:
      self.onReload()
      evalString = 'globals()["%s"].%sTest()' % (moduleName, moduleName)
      tester = eval(evalString)
      tester.runTest()
    except Exception, e:
      import traceback
      traceback.print_exc()
      qt.QMessageBox.warning(slicer.util.mainWindow(), 
          "Reload and Test", 'Exception!\n\n' + str(e) + "\n\nSee Python Console for Stack Trace")
          


#
# LoadCTXLogic
#

class LoadCTXLogic:
  """This class should implement all the actual 
  computation done by your module.  The interface 
  should be such that other python code can import
  this class and make use of the functionality without
  requiring an instance of the Widget
  """
  def __init__(self):
    pass

  
  def loadVoi(self,filePath,segmentationNode,motionState=0,voi=None):
    
    if not segmentationNode:
       print "No segmentation node"
       return
       
    
    segLogic = slicer.modules.segmentations.logic()
    segLogic.SetMRMLScene(slicer.mrmlScene)
    voi.slicerNodeID[motionState]=None
    
    print "Logic set"
	  
    if not filePath or not os.path.isfile(filePath):
      print "No file!" + filePath
      return None
      
    volumesLogic = slicer.vtkSlicerVolumesLogic()
    volumesLogic.SetMRMLScene(slicer.mrmlScene)
    slicerVolumeName = os.path.splitext(os.path.basename(filePath))[0] + "_" + str(motionState)
    slicerVolume = volumesLogic.AddArchetypeVolume(filePath,slicerVolumeName,1) 
    
    print "File loaded"
    #success, midV = slicer.util.loadVolume(os.path.basename(filePath), 
                                           #properties = {'name' : "Helo", 'labelmap' : True}, returnNode = True)
    slicerVolume.SetOrigin(voi.getSlicerOrigin())
    if not slicerVolume:
      print "Can't load volume " + os.path.basename(filePath)
      return None
    
    colorNode = slicer.util.getNode("vtkMRMLColorTableNodeFileGenericAnatomyColors.txt")
    
    colorIndex = colorNode.GetColorIndexByName(voi.name.lower())
    
    color = [1,0,0,1]
    
    if colorIndex > -1:
       colorNode.GetColor(colorIndex,color)
    
    displayNode = slicer.vtkMRMLLabelMapVolumeDisplayNode()
    displayNode.SetAndObserveColorNodeID(colorNode.GetID())
    displayNode.SetColor(color[0:3])
    slicer.mrmlScene.AddNode(displayNode)
    slicerVolume.SetAndObserveDisplayNodeID(displayNode.GetID())


    try:
       array = slicer.util.array(slicerVolume.GetID())
    except AttributeError:
      import sys
      sys.stderr.write('Cannot get array.')
      
    array[:] = ( array[:] >> voi.motionStateBit[motionState] ) & 1
    

    #if not segLogic.ImportLabelmapToSegmentationNode(slicerVolume,segmentationNode):
       #print "Can't import " + slicerVolume.GetName()
       #slicer.mrmlScene.RemoveNode(slicerVolume)
       

       
    #Color?
    
    #if threeD:
      #if voi:
	#index = voi.voiNumber
      #else:
	#index = 0
      #slicerVolume = self.convertLabelMapToClosedSurfaceModel(slicerVolume, index)
    #else:
      #displayNode = slicer.vtkMRMLScalarVolumeDisplayNode()
      #displayNode.SetAndObserveColorNodeID("vtkMRMLColorTableNodeGrey")
      #slicer.mrmlScene.AddNode(displayNode)
      #slicerVolume.SetAndObserveDisplayNodeID(displayNode.GetID())
      ##slicerVolume.SetLabelMap(1)
    
                  	  
    if 0:
	#This Logic need some work
	#Create subject Hierarchy
        ##Copied from SlicerSubjectHierarchyContourSetsPlugin
        from vtkSlicerSubjectHierarchyModuleMRML import vtkMRMLSubjectHierarchyNode
        from vtkSlicerContoursModuleLogic import vtkSlicerContoursModuleLogic
        try:
          vtkMRMLSubjectHierarchyNode
          vtkSlicerContoursModuleLogic
        except AttributeError:
          import sys
          sys.stderr.write('Unable to load vtkMRMLSubjectHierarchyNode and vtkSlicerContoursModuleLogic')
          return
        subjectNode = vtkMRMLSubjectHierarchyNode()
        subjectNode.SetName(patientName + '_SubjectHierarchy')
        subjectNode.SetLevel('Subject')
        contourSet = slicer.util.getNode('NewContourSet_SubjectHierarchy')
        if not contourSet:
          slicer.mrmlScene.AddNode(subjectNode)
          study = subjectNode.CreateSubjectHierarchyNode(slicer.mrmlScene,subjectNode,'Study','Contour')
          contourSet = study.CreateSubjectHierarchyNode(slicer.mrmlScene,study,'Series','NewContourSet')
          contourSet.SetAttribute('DicomRtImport.ContourHierarchy','1')
      
        contourNodeHierarchy = contourSet.CreateSubjectHierarchyNode(slicer.mrmlScene,contourSet,'Subseries',pyTRiPCube.patient_name)
        
        #cliNode = self.changeScalarVolumeType(slicerVolume,volumeScalarType = 'UnsignedChar')
        contourNode = vtkSlicerContoursModuleLogic.CreateContourFromRepresentation(slicerVolume)
        if not contourNode:
	  print "Can't create Contour node from " + slicerVolume.GetNode()
	  return
	  
	contourNodeHierarchy.SetAttribute('StructureName',pyTRiPCube.patient_name)
	contourNodeHierarchy.SetAssociatedNodeID(contourNode.GetID())
	
	#Set color
	color = [0,0,0]
	#CreateColors
        colorNode = slicer.util.getNode('vtkMRMLColorTableNodeLabels')
        #color = [0,0,0]
        colorNode.GetScalarsToColors().GetColor(index, color)
        print color
        color.append(1)
        
	
	colorNode = slicer.vtkMRMLColorTableNode()
	slicer.mrmlScene.AddNode(colorNode)
	
	colorNode.SetName('NewContourSet_ColorTable')
	colorNode.SetAttribute('Category','SlicerRT')
	colorNode.SetTypeToUser()
	colorNode.HideFromEditorsOff()
	colorNode.SetNumberOfColors(2)
	colorNode.GetLookupTable().SetTableRange(0,1)
	
	#color[0:2] = slicerVolume.GetDisplayNode().GetColor()
	colorNode.AddColor('Background',0.0, 0.0, 0.0, 0.0)
	colorNode.AddColor('Invalid',0.5,0.5,0.5,1)
	
	contourSet.SetNodeReferenceID('contourSetColorTableRef', colorNode.GetID() )
	
	if not colorNode:
	  print "No color node for" + slicerVolume.GetName()
	  
	numberOfColors = colorNode.GetNumberOfColors()
	colorNode.SetNumberOfColors(numberOfColors+1);
	
	#lookupTable = vtk.vtkLookupTable()
	#colorNode.SetLookupTable( lookupTable )
        colorNode.GetLookupTable().SetTableRange(0, numberOfColors)
        colorNode.SetColor(numberOfColors, pyTRiPCube.patient_name, color[0], color[1], color[2], color[3])
        contourNode.GetDisplayNode().SetColor(color[0:3])
        slicer.mrmlScene.RemoveNode(slicerVolume)

    print "Done!"
    return slicerVolume.GetID()

  def setVectorField(self, vectorNode):
    spacing = vectorNode.GetSpacing()
    
    vectorArray = slicer.util.array(vectorNode.GetID())
    
    for i in range(0,3):
      vectorArray[:,:,:,i] = vectorArray[:,:,:,i] * spacing[i] /2
    vectorNode.GetImageData().Modified()
    print "Finshed!"
    
  
  def addVectors(self, vector1, vector2, name="SumVF"):
    
    vectorArray1 = slicer.util.array(vector1.GetID())
    vectorArray2 = slicer.util.array(vector2.GetID())
    
    if len(vectorArray1) == 0 or len(vectorArray2) == 0:
       print "No vectors!"
       return
    

    newImageData = vtk.vtkImageData()
    newImageData.DeepCopy(vector1.GetImageData())
    
    matrix = vtk.vtkMatrix4x4()
    vector1.GetIJKToRASDirectionMatrix(matrix)
    
    newVector = slicer.vtkMRMLVectorVolumeNode()
    newVector.SetAndObserveImageData(newImageData)
    slicer.mrmlScene.AddNode( newVector )
    
    newVector.SetIJKToRASDirectionMatrix(matrix)
    newVector.SetOrigin(vector1.GetOrigin())
    newVector.SetSpacing(vector1.GetSpacing())
    
    slicerName = name
    slicerName = slicer.mrmlScene.GenerateUniqueName(slicerName)         
    newVector.SetName(slicerName)
    
    displayNode = slicer.vtkMRMLVectorVolumeDisplayNode()
    slicer.mrmlScene.AddNode(displayNode)
    newVector.SetAndObserveDisplayNodeID(displayNode.GetID())
    
    newVectorArray = slicer.util.array(newVector.GetID())
    print "Adding " + vector1.GetName() + " and " + vector2.GetName()
    newArray = np.add(vectorArray1, vectorArray2)
    newVectorArray[:] = newArray[:]
    newVector.GetImageData().Modified()
    print "Finished!"
  
  def setDose(self, doseNode, optDose, overDoseOff = False):
    #Set attribute
    doseNode.SetAttribute('DicomRtImport.DoseVolume','1')
    
    #Set Origins
    #doseNode.SetOrigin([300,214,19.5])

    #Set display
    slicerVolumeDisplay=doseNode.GetScalarVolumeDisplayNode()
    if slicerVolumeDisplay:
      slicerVolumeDisplay.AutoWindowLevelOff()
      slicerVolumeDisplay.AutoThresholdOff()
      if overDoseOff:
         colorNode = slicer.util.getNode('GSIStandard_NoOverDose')
      else:
         colorNode = slicer.util.getNode('GSIStandard_OverDose')
         
      if not colorNode:
        colorNode = self.CreateDefaultGSIColorTable(overDoseOff)	    
      slicerVolumeDisplay.SetAndObserveColorNodeID(colorNode.GetID())
      #slicerVolumeDisplay.SetWindowLevelMinMax(0,round(optDose))
      slicerVolumeDisplay.SetWindowLevelMinMax(0,1.08*optDose)
      slicerVolumeDisplay.SetThreshold(0.2,1200)
      slicerVolumeDisplay.ApplyThresholdOn()
    else:
      print "No display node for:"+doseNode.GetName()
      return
  
  def setPlanCube(self, doseNode):
     
     #Najprej pomnoz vektor, pol pa novga nared.
    doseArray = slicer.util.array(doseNode.GetID())
    for i in range(0,3):
       doseArray[:,:,:,i] /= doseNode.GetSpacing()[i]
       
    doseNode.GetImageData().Modified()
    planCube = slicer.vtkMRMLScalarVolumeNode()
    slicer.mrmlScene.AddNode( planCube )
    storageNode = planCube.CreateDefaultStorageNode()
    slicer.mrmlScene.AddNode(storageNode)
    planCube.SetAndObserveStorageNodeID(storageNode.GetID())
    
    imageData = vtk.vtkImageData()

    for i in range(0,3):
      
       if i == 0:
          slicerName = 'Lung022_00_01_x'
       elif i == 1:
          slicerName = 'Lung022_00_01_y'
       elif i == 2:
          slicerName = 'Lung022_00_01_z'
          
         
       planCube.SetName(slicerName)
       extract = vtk.vtkImageExtractComponents()
       extract.SetComponents(i)
       extract.SetInputData(doseNode.GetImageData())
       extract.Modified()
       extract.Update()
       imageData.DeepCopy(extract.GetOutput())
       
       ijkToRAS = vtk.vtkMatrix4x4()
       doseNode.GetIJKToRASMatrix(ijkToRAS)
       planCube.SetIJKToRASMatrix(ijkToRAS)
       planCube.SetAndObserveImageData(imageData)

       if not slicer.util.saveNode(planCube,
       '/u/kanderle/FC/Lung022/Registration/MidV/'+ planCube.GetName() +
       ".nhdr"):
          print "Can't save " + planCube.GetName()
          
    doseArray[:,:,:,i] *= doseNode.GetSpacing()[i]
    doseNode.GetImageData().Modified()
    print "Plan Cube created."
    
  def makeDoseDifference(self,sbrtNode,ptNode):
     
    slope = 0.928
    intercept = 33
    
    #Revert slope and intercept
    intercept = -intercept/slope
    slope = 1/slope
    
    HUlimit = -90
    
    CTlimit = HUlimit*slope + intercept
    print slope
    print intercept
    sbrtArray = slicer.util.array(sbrtNode.GetID())
    
    dim = sbrtArray.shape

    print "Going through array."
    for z in range(0,dim[0]):
      print "Slice: " + str(z) +"/" + str(dim[0])
      for y in range(0,dim[1]):
        for x in range(0,dim[2]):
          if sbrtArray[z][y][x] > CTlimit: #and abs(ptArray[z][y][x]) < 0.1:
            sbrtArray[z][y][x] = round(sbrtArray[z][y][x] * slope + intercept,0)

    
    #sbrtArray = slicer.util.array(sbrtNode.GetID())
    #ptArray = slicer.util.array(ptNode.GetID())
    #if not sbrtArray.shape == ptArray.shape:
      #print "Array dimensions not the same!"
      #print str(sbrtArray.shape) + " vs " + str(ptArray.shape)
      #return
    ##Iterate through array to determain low values, which are removed from display.
    ##Lengthy process
    #newArray = np.zeros(sbrtArray.shape)
    #dim = sbrtArray.shape
    
    #print "Going through array."
    #newArray = sbrtArray - ptArray
    #for z in range(0,dim[0]):
      #print "Slice: " + str(z) +"/" + str(dim[0])
      #for y in range(0,dim[1]):
        #for x in range(0,dim[2]):
	  #if abs(sbrtArray[z][y][x]) < 0.01: #and abs(ptArray[z][y][x]) < 0.1:
	    #newArray[z][y][x] = - 500
	  #else:
	    #newArray[z][y][x] = sbrtArray[z][y][x] - ptArray[z][y][x]
    
    #importer=LoadCTXLib.vtkImageImportFromArray()
    #importer.SetArray(newArray)
    #slicerVolume = slicer.vtkMRMLScalarVolumeNode()

    #slicerVolume.Copy(sbrtNode)
    
    #slicer.mrmlScene.AddNode( slicerVolume )
    #slicerVolume.SetAndObserveImageData(importer.GetOutput())
    
    #slicerName = 'DoseDifference'
    #slicerName = slicer.mrmlScene.GenerateUniqueName(slicerName)         
    #slicerVolume.SetName(slicerName)
    
    #displayNode = slicer.vtkMRMLScalarVolumeDisplayNode()
    #slicer.mrmlScene.AddNode(displayNode)
    #slicerVolume.SetAndObserveDisplayNodeID(displayNode.GetID())

    #displayNode.AutoWindowLevelOff()
    #displayNode.AutoThresholdOff()
    #displayNode.SetLevel(0)
    #displayNode.SetWindow(30)
    #displayNode.SetThreshold(-24,24)
    #displayNode.ApplyThresholdOn()
    
    #colorNode = slicer.util.getNode('ColdToHotRainbow')
    #if not colorNode:
      #print "Error, no ColdToHotRainbow node"
      #return
      ##colorNode = self.CreateDefaultHotAndColdColorTable()
    ##else:
      ##self.CorrectColorNode(colorNode)
    #displayNode.SetAndObserveColorNodeID(colorNode.GetID())
    
    
    print "Finshed!"
    
  def makeVOIUnioun(self,jacNode1):
    #Cast to int
    parameters = {}
    parameters["InputVolume"] = jacNode1.GetID()
    parameters["OutputVolume"] = jacNode1.GetID()
    parameters["Type"] = "Int"
    castVolume= slicer.modules.castscalarvolume
    slicer.cli.run(castVolume, None, parameters, wait_for_completion=True)
    
    ##Now byte swap
    #array = slicer.util.array(jacNode1.GetID())
    #array[:] = array[:].byteswap()
    
    jacNode1.SetName("Pat00Target")
    
    print "Finished"
    
    return
    
    #voi1Array = slicer.util.array(voi1Node.GetID())
    #voi2Array = slicer.util.array(voi2Node.GetID())
    #if not voi1Array.shape == voi2Array.shape:
      #print "Array dimensions not the same!"
      #print str(voi1Array.shape) + " vs " + str(voi2Array.shape)
      #return
    ##Iterate through array to determain low values, which are removed from display.
    ##Lengthy process
    #newArray = np.zeros(voi1Array.shape)
    #dim = voi1Array.shape
    
    #print "Going through array."
    ##newArray = voi1Array + voi2Array
    #for z in range(0,dim[0]):
      #print "Slice: " + str(z) +"/" + str(dim[0])
      #for y in range(0,dim[1]):
        #for x in range(0,dim[2]):
	  #if voi1Array[z][y][x] == 1 and voi2Array[z][y][x] == 1: #and abs(voi2Array[z][y][x]) < 0.1:
	    #newArray[z][y][x] = 1

    
    #importer=LoadCTXLib.vtkImageImportFromArray()
    #importer.SetArray(newArray)
    slicerVolume = slicer.vtkMRMLScalarVolumeNode()

    slicerVolume.Copy(voi1Node)
    
    slicer.mrmlScene.AddNode( slicerVolume )
    #slicerVolume.SetAndObserveImageData(importer.GetOutput())
    
    slicerName = 'VoiCS'
    slicerName = slicer.mrmlScene.GenerateUniqueName(slicerName)         
    slicerVolume.SetName(slicerName)
    
    displayNode = slicer.vtkMRMLScalarVolumeDisplayNode()
    slicer.mrmlScene.AddNode(displayNode)
    slicerVolume.SetAndObserveDisplayNodeID(displayNode.GetID())
    
    slicerArray = slicer.util.array(slicerVolume.GetID())
    slicerArray[:] = newArray[:]
    
    slicerVolume.GetImageData().Modified()
      
    print "Finshed!"
  #This code is translated from SlicerRT module Contours.
  def convertLabelMapToClosedSurfaceModel(self, labelMapNode, index=0):
    if labelMapNode is None:
      print "No input labelMap or image Data"
      return
    else:
      imageData = labelMapNode.GetImageData()
  
    #Padding labelmap with 1 pixel around the image, shifting origin
    padder = vtk.vtkImageConstantPad()
    translator = vtk.vtkImageChangeInformation()
    translator.SetInputData(imageData)
      
    # Translate the extent by 1 pixel
    translator.SetExtentTranslation(1, 1, 1)
    # Args are: -padx*xspacing, -pady*yspacing, -padz*zspacing but padding and spacing are both 1
    translator.SetOriginTranslation(-1.0, -1.0, -1.0)
    padder.SetInputConnection(translator.GetOutputPort())
    padder.SetConstant(0);
    translator.Update();
    extent = imageData.GetExtent()
    #Now set the output extent to the new size, padded by 2 on the positive side
    padder.SetOutputWholeExtent(extent[0], extent[1] + 2,
        extent[2], extent[3] + 2,
        extent[4], extent[5] + 2)
    
    marchingCubes = vtk.vtkMarchingCubes() 
    marchingCubes.SetInputConnection(padder.GetOutputPort())
    marchingCubes.SetNumberOfContours(1)
    marchingCubes.SetValue(1,1)
    marchingCubes.ComputeGradientsOff()
    marchingCubes.ComputeNormalsOff()
    marchingCubes.ComputeScalarsOff()
    marchingCubes.Update()
    if marchingCubes.GetOutput().GetNumberOfPolys() < 0:
      print "Can't create Model."
      return None
      
    
    #triangle = vtk.vtkTriangleFilter()
    #triangle.SetInputData(marchingCubes.GetOutput())
    #triangle.Update()
    
    ###Decimate feature is disabled for now - the resulting contours are too small.
    #decimate = vtk.vtkDecimatePro()
    #decimate.SetInputData(triangle.GetOutput())
    #decimate.SetFeatureAngle(60)
    #decimate.SplittingOff()
    #decimate.PreserveTopologyOn()
    #decimate.SetMaximumError(0.1)
    #decimate.SetTargetReduction(1)
    #decimate.Update()
    
    #Get & Set transformation - get model to Label Map coordinates
    matrix = vtk.vtkMatrix4x4()
    labelMapNode.GetRASToIJKMatrix(matrix)
    transformation = vtk.vtkGeneralTransform()
    transformation.Identity()
    transformation.Concatenate(matrix)
    transformation.Inverse()
    
    transformFilter = vtk.vtkTransformPolyDataFilter()
    transformFilter.SetInputConnection(marchingCubes.GetOutputPort())
    transformFilter.SetTransform(transformation)
    transformFilter.Update()

    #Create Display Node
    contourDisplayNode = slicer.vtkMRMLModelDisplayNode()
    slicer.mrmlScene.AddNode(contourDisplayNode)
    contourDisplayNode.SliceIntersectionVisibilityOn()
    contourDisplayNode.VisibilityOn()
    contourDisplayNode.SetBackfaceCulling(0)
    contourDisplayNode.SetSliceIntersectionThickness(3)
    
    #CreateColors
    colorNode = slicer.util.getNode('vtkMRMLColorTableNodeLabels')
    color = [0,0,0]
    colorNode.GetScalarsToColors().GetColor(index, color)
    contourDisplayNode.SetColor(color)
    
    #Create Node
    contourNode = slicer.vtkMRMLModelNode()
    slicer.mrmlScene.AddNode(contourNode)
    contourNode.SetName(labelMapNode.GetName())
    contourNode.SetAndObserveDisplayNodeID(contourDisplayNode.GetID())
    contourNode.SetAndObservePolyData(transformFilter.GetOutput())

    slicer.mrmlScene.RemoveNode(labelMapNode)
    
    return contourNode
 
 
	
  def CreateDefaultGSIColorTable(self, overDoseOff):
    colorTableNode = slicer.vtkMRMLColorTableNode()
    if overDoseOff:
       nodeName = "GSIStandard_NoOverDose"
    else:
       nodeName = "GSIStandard_OverDose"
    colorTableNode.SetName(nodeName);
    colorTableNode.SetTypeToUser();
    colorTableNode.SetAttribute("Category", "User Generated");
    colorTableNode.HideFromEditorsOn();
    colorTableNode.SetNumberOfColors(256);
    colorTableNode.GetLookupTable().SetTableRange(0,255)
    darkBlue = 47.0
    lightBlue = 95.0
    darkGreen = 142.0
    lightGreen = 189.0
    yellow = 225.0
    red = 248.0
    
    if overDoseOff:
       for i in range(0,256):
         if i>=0 and i<darkBlue:
           colorTableNode.AddColor(str(i), 0, 0 + i/darkBlue, 1, 0.2)
         elif i>=darkBlue and i<lightBlue:
           colorTableNode.AddColor(str(i), 0, 1-0.5*(i-darkBlue)/(lightBlue-darkBlue), 1 - (i-darkBlue)/(lightBlue-darkBlue), 0.2)
         elif i>=lightBlue and i<darkGreen:
           colorTableNode.AddColor(str(i), 0, 0.5 + 0.5*(i-lightBlue)/(darkGreen-lightBlue), 0, 0.2)
         elif i>=darkGreen and i<lightGreen:
           colorTableNode.AddColor(str(i), 0 + (i-darkGreen)/(lightGreen-darkGreen), 1, 0, 0.2)
         elif i>=lightGreen and i<236:
           colorTableNode.AddColor(str(i), 1, 1, 0, 0.2)
         else:
           colorTableNode.AddColor(str(i), 1, 0, 0, 0.2)
    else:
      for i in range(0,256):
         if i>=0 and i<darkBlue:
           colorTableNode.AddColor(str(i), 0, 0 + i/darkBlue, 1, 0.2)
         elif i>=darkBlue and i<lightBlue:
           colorTableNode.AddColor(str(i), 0, 1-0.5*(i-darkBlue)/(lightBlue-darkBlue), 1 - (i-darkBlue)/(lightBlue-darkBlue), 0.2)
         elif i>=lightBlue and i<darkGreen:
           colorTableNode.AddColor(str(i), 0, 0.5 + 0.5*(i-lightBlue)/(darkGreen-lightBlue), 0, 0.2)
         elif i>=darkGreen and i<lightGreen:
           colorTableNode.AddColor(str(i), 0 + (i-darkGreen)/(lightGreen-darkGreen), 1, 0, 0.2)
         elif i>=lightGreen and i<yellow:
           colorTableNode.AddColor(str(i), 1, 1, 0, 0.2)
         elif i<=red:
           colorTableNode.AddColor(str(i), 1, 0, 0, 0.2)
         else:
           colorTableNode.AddColor(str(i), 1, 0, 1, 0.2)
   
    slicer.mrmlScene.AddNode( colorTableNode )
    return colorTableNode
  
  
class LoadCTXTest(unittest.TestCase):
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
    self.test_LoadCTX1()

  def test_LoadCTX1(self):
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
    #filePath='/u/kanderle/examples/Py/Lung014_00LungL.ctx'
    filePath='/u/kanderle/examples/Py/ns_00_Pat122wk0_05.binfo'
    logic = LoadCTXLogic()
    binfo = LoadCTXLib.Binfo()
    binfo.readFile(filePath)
    #vois = binfo.get_voi_names
    voi = binfo.get_voi_by_name('CTV_T50')
    filePath2 = '/u/kanderle/examples/Py/ns_00_Pat122wk0_05CTV_T50.ctx'
    logic.loadCube(filePath2,2,0,voi)
    
    
    self.delayDisplay('Test passed!')
    
