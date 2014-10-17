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
    This is an example of scripted loadable module bundled in an extension.
    """
    parent.acknowledgementText = """
    This file was originally developed by Jean-Christophe Fillion-Robin, Kitware Inc. and Steve Pieper, Isomics, Inc.  and was partially funded by NIH grant 3P41RR013218-12S1.
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
    
    
    parametersCollapsibleButton = ctk.ctkCollapsibleButton()
    parametersCollapsibleButton.text = "Parameters"
    self.layout.addWidget(parametersCollapsibleButton)

    # Layout within the dummy collapsible button
    parametersFormLayout = qt.QFormLayout(parametersCollapsibleButton)
    #Load File
    #
    # Load CTX File Button
    #
    self.loadButton = qt.QPushButton("Load TRiP Volume")
    self.loadButton.toolTip = "Load TRiP File (*.ctx,*.dos,*.binfo)."
    self.loadButton.enabled = True
    
    parametersFormLayout.addRow(self.loadButton)
    
    #TODO: Daj opcijo, da se izbere doza in potem se zravn checkbox, zato da zberes, al ti normira na to al ne.
    # Optimized dose:
    #self.optDose = qt.QDoubleSpinBox()     
    #self.optDose.setToolTip( "Optimized dose value." )
    #self.optDose.setValue(25)
    #self.optDose.setRange(0, 100)
    #self.optDose.enabled = True
    #parametersFormLayout.addRow("Dose:", self.optDose)
   
    
    # Input dose value
    # TO DO: add check box to choose between substract origin or change origin
    self.optDoseBox = qt.QDoubleSpinBox()     
    self.optDoseBox.setToolTip( "The optimization value for dose." )
    self.optDoseBox.setValue(25)
    self.optDoseBox.setRange(0, 1000)
    parametersFormLayout.addRow("Dose optimization Value", self.optDoseBox)
    
    
    # Binfo
    self.binfoListFile = qt.QComboBox()    
    self.binfoListFile.setToolTip( "Input file" )
    self.binfoListFile.enabled = False
    parametersFormLayout.addRow("Binfo:", self.binfoListFile)
    

    #self.fileName.getOpenFileName(self, tr("Open File"),"",tr("Files (*.*)"));
    
    # Voi list
    self.voiComboBox = qt.QComboBox()
    self.voiComboBox.enabled = False
    parametersFormLayout.addRow("Select Voi: ", self.voiComboBox)
    
    # Motion state list
    self.motionStateComboBox = qt.QComboBox()
    self.motionStateComboBox.enabled = False
    parametersFormLayout.addRow("Select Motion State: ", self.motionStateComboBox)
    #motionStates=11
    #for i in range(0,motionStates+1):
      #self.motionStateComboBox.addItem(str(i))
    


    #
    # Show Button
    #
    self.showButton = qt.QPushButton("Show")
    self.showButton.toolTip = "Run the algorithm."
    self.showButton.enabled = True
    parametersFormLayout.addRow(self.showButton)
    
    #
    # Show Button
    #
    self.setOriginButton = qt.QPushButton("Set Origins to zero")
    self.setOriginButton.toolTip = "Set origins to zero."
    self.setOriginButton.enabled = True
    parametersFormLayout.addRow(self.setOriginButton)
    
    #
    # Select SBRT dose
    #
    self.selectSBRTDose = slicer.qMRMLNodeComboBox()
    self.selectSBRTDose.nodeTypes = ( ("vtkMRMLScalarVolumeNode"),"" )
    #self.selectSBRTDose.addAttribute( "vtkMRMLScalarVolumeNode", "LabelMap", 0 )
    #self.selectSBRTDose.selectSBRTDoseUponCreation = True
    self.selectSBRTDose.addEnabled = False
    self.selectSBRTDose.removeEnabled = False
    self.selectSBRTDose.noneEnabled = True
    self.selectSBRTDose.showHidden = False
    self.selectSBRTDose.showChildNodeTypes = False
    self.selectSBRTDose.setMRMLScene( slicer.mrmlScene )
    self.selectSBRTDose.setToolTip( "Select SBRT dose volume." )
    parametersFormLayout.addRow("SBRT dose: ", self.selectSBRTDose)
    
    #
    # Select PT dose
    #
    self.selectPTDose = slicer.qMRMLNodeComboBox()
    self.selectPTDose.nodeTypes = ( ("vtkMRMLScalarVolumeNode"),"" )
    #self.selectPTDose.addAttribute( "vtkMRMLScalarVolumeNode", "LabelMap", 0 )
    #self.selectPTDose.selectPTDoseUponCreation = True
    self.selectPTDose.addEnabled = False
    self.selectPTDose.removeEnabled = False
    self.selectPTDose.noneEnabled = True
    self.selectPTDose.showHidden = False
    self.selectPTDose.showChildNodeTypes = False
    self.selectPTDose.setMRMLScene( slicer.mrmlScene )
    self.selectPTDose.setToolTip( "Select PT dose volume." )
    parametersFormLayout.addRow("PT dose: ", self.selectPTDose)
    
    #
    # Recalculate button
    #
    self.setDoseButton = qt.QPushButton("Set Dose.")
    self.setDoseButton.toolTip = "Takes two doses into account and calculates their difference."
    self.setDoseButton.enabled = True
    parametersFormLayout.addRow(self.setDoseButton)

    # connections
    self.showButton.connect('clicked(bool)', self.onShowButton)
    self.setOriginButton.connect('clicked(bool)', self.onSetOriginButton)
    self.loadButton.connect('clicked(bool)', self.onLoadButton)
    self.voiComboBox.connect('currentIndexChanged(QString)', self.setMotionStatesFromComboBox)
    self.binfoListFile.connect('currentIndexChanged(int)', self.setBinfoFile)
    self.setDoseButton.connect('clicked(bool)', self.onSetDoseButton)


    # Add vertical spacer
    self.layout.addStretch(1)
    
    # Binfo file:
    #binfo=Binfo()
    self.binfoList = []
    self.ctx = None
    self.dos = None
    self.cbt = None
    

  def cleanup(self):
    pass

  #Load TRiP cube in slicer.   
  #fileInfo is for different filetypes: 0 CTX, 1 Dose, 2 binfo, 3 cbt
  def onLoadButton(self): 
    logic = LoadCTXLogic()  
    loadFileName = qt.QFileDialog()
    filePathList=loadFileName.getOpenFileNames()
    for filePath in filePathList:
      filePrefix, fileExtension = os.path.splitext(filePath)
      #Check for different extensions
      if fileExtension == ".ctx":
	reload(LoadCTXLib)
	fileInfo = 0
	#if not self.ctx:
	self.ctx = logic.loadCube(filePath,fileInfo,showOn = True)
	#LoadCTXLib.addSeriesInHierarchy(self.ctx)
      elif fileExtension == ".dos":
	fileInfo = 1
	#if filePrefix.find('phys')>-1:
	  #optDoseValue = 1000
	#else:
	  #optDoseValue = self.optDoseBox.value
	#print optDoseValue
	optDoseValue = self.optDoseBox.value
	#print optDoseValue
	#return
	#print filePrefix.find('phys')
	#optDose = 25
	self.dos = logic.loadCube(filePath,fileInfo,optDose = optDoseValue,showOn = True)
      elif fileExtension == ".cbt":
	fileInfo = 3
	self.cbt = logic.loadCube(filePath,fileInfo,showOn = True)
      #Binfo is special case.  
      elif fileExtension == ".binfo":
	self.voiComboBox.clear()
	self.motionStateComboBox.clear() 
	binfo = LoadCTXLib.Binfo()
	binfo.readFile(filePath)
	self.binfoList.append( binfo )
	self.binfoListFile.addItem( binfo.name )
	#self.setBinfoFile(-1)
	#self.binfoListFile.setCurrentIndex(-1)
	self.binfoListFile.enabled = True
		
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

  
  #Load voi from binfo file
  def onShowButton(self):
    binfo=self.binfoList[self.binfoListFile.currentIndex]
    filePrefix, fileExtension = os.path.splitext(binfo.filePath)
    voi = binfo.get_voi_by_name(self.voiComboBox.currentText)
    if not voi:
      print "Error, voi not found."
      return
    filePath = filePrefix + voi.name + ".ctx"
    logic = LoadCTXLogic()
    n=self.motionStateComboBox.currentIndex
    voi.slicerNodeID[n]=logic.loadCube(filePath,2,motionState=n,voi=voi,ctx=self.ctx)
      #self.confirmBox(("Loaded file: "+filePath))

  def onSetDoseButton(self):
    logic = LoadCTXLogic()
    
    sbrtNode = self.selectSBRTDose.currentNode()
    ptNode = self.selectPTDose.currentNode()
    
    if not ptNode or not sbrtNode:
      print "No SBRT and/or PT dose!."
      return
      
    logic.setDoses(sbrtNode,ptNode)
    
  def onSetOriginButton(self):
    nodes = slicer.util.getNodes('vtkMRMLScalarVolumeNode*')
    for currentNode in nodes:
      nodes[currentNode].GetName()
      nodes[currentNode].SetOrigin((0,0,0))
    print "Done!"
    return

    
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

  def loadCube(self,filePath,fileInfo,motionState=0,voi=None, ctx=None, optDose = 25, showOn = True):
    
    
    #Check if Slicer already has display node for voi.
    #TODO: Do the same for all types
    if voi is not None:
      if voi.slicerNodeID[motionState] is not None:
	slicerVolume = slicer.util.getNode(voi.slicerNodeID[motionState])
	if slicerVolume is not None:
	  selectionNode = slicer.app.applicationLogic().GetSelectionNode()
          selectionNode.SetReferenceActiveVolumeID(slicerVolume.GetID())
          slicer.app.applicationLogic().PropagateVolumeSelection(0)
          return True
        else:
	  voi.slicerNodeID[motionState]=None
    
    #ul[1][1][1]
#array([-0.04854982, -0.04737258, -0.00031896], dtype=float32)
    
    
    if not filePath or not os.path.isfile(filePath):
      print "No file!" + filePath
      return False
    #Find out cube type
          
    fileName, fileExtension = os.path.splitext(filePath)
    

    pbar = self.progressBar(("Loading file: "+filePath))
    pbar.setValue(10)
    pbar.show()
    
    #Read cube using PyTRiP
    if fileInfo==0 or fileInfo==2:
      pyTRiPCube=LoadCTXLib.ctx.CtxCube()
      pyTRiPCube.read(filePath)
    elif fileInfo==1:
      pyTRiPCube=LoadCTXLib.ctx.CtxCube()
      pyTRiPCube.read(filePath)
    #Prepare three cubes for reading cbt files
    elif fileInfo==3:
      fileNamePrefix = fileName[0:len(fileName)-2]
      pyTRiPCube = LoadCTXLib.ctx.CtxCube() #cube x is without index for setting dimension and name
      pyTRiPCube_y = LoadCTXLib.ctx.CtxCube()
      pyTRiPCube_z = LoadCTXLib.ctx.CtxCube()
      pyTRiPCube.read(fileNamePrefix+"_x"+fileExtension)
      pyTRiPCube_y.read(fileNamePrefix+"_y"+fileExtension)
      pyTRiPCube_z.read(fileNamePrefix+"_z"+fileExtension)
    else:
      print "Unknown extension type" + str(fileExtension)
      pbar.close()
      return False
    
    
    
    ##Set Dimensions
    #dim=(pyTRiPCube.dimx,pyTRiPCube.dimy,pyTRiPCube.dimz)
    
    if fileInfo is not 3:
      TRiPCube=pyTRiPCube.cube
    else:
      # Build a 3D array containing, each point containing vector value (x, y and z direction)
      TRiPCube = np.empty(pyTRiPCube.cube.shape + (3,),np.float32)
      # Vector field components in cbt are divided with voxel spacing due to historical reasons. 
      TRiPCube[:,:,:,0] = np.array(pyTRiPCube.cube)*pyTRiPCube.pixel_size
      TRiPCube[:,:,:,1] = np.array(pyTRiPCube_y.cube)*pyTRiPCube.pixel_size
      TRiPCube[:,:,:,2] = np.array(pyTRiPCube_z.cube)*pyTRiPCube.slice_distance
    
    if fileInfo==1:
      doseMax=int(TRiPCube.max())
      if doseMax > optDose*2 and filePath.find('phys') > -1:
	optDose = 1000
      
    pbar.setValue(20)

    #Read the transfer bit in binfo file
    if fileInfo==2:
      if voi is not None:
        print "Motion state " + str(motionState) + " on bit: " + str(voi.motionStateBit[motionState])
        TRiPCube=(TRiPCube>>voi.motionStateBit[motionState]) & 1
      else:
	print "Looking at reference State"
	TRiPCube=TRiPCube & 1
      #if voi is not None:
	#TRiPCube = voi.voiNumber * np.array(TRiPCube)
	  
    pbar.setValue(50) 
      
    ##Convert numpy array to vtk data  
    importer=LoadCTXLib.vtkImageImportFromArray()
    if fileInfo is not 3:
      importer.SetArray(TRiPCube)
      slicerVolume = slicer.vtkMRMLScalarVolumeNode()
    else:
      importer.SetArray(TRiPCube,numComponents=3)
      slicerVolume = slicer.vtkMRMLVectorVolumeNode()
    
    #Set vtkImageData to Slicer Volume & set all atributes    
    slicer.mrmlScene.AddNode( slicerVolume )
    #imageData = importer.GetOutput()
    
    #Set origin for vois in binfo files
    #if fileInfo == 2:
      #if voi:
        #imageData.SetOrigin(voi.getSlicerOrigin())
        #slicerVolume = self.convertLabelMapToClosedSurfaceModel(imageData = imageData)
      #else:
    slicerVolume.SetAndObserveImageData(importer.GetOutput())
    slicerVolume.SetSpacing(pyTRiPCube.pixel_size,pyTRiPCube.pixel_size,pyTRiPCube.slice_distance)
        #Set ijttoras matrix
    matrix = vtk.vtkMatrix4x4()
    matrix.DeepCopy((-1,0,0,0,0,-1,0,0,0,0,1,0,0,0,0,1))
    slicerVolume.SetIJKToRASDirectionMatrix(matrix)
    
    
    #slicerVolume.SetSpacing(pyTRiPCube.pixel_size,pyTRiPCube.pixel_size,pyTRiPCube.slice_distance)
    
    

    pbar.setValue(70)
      #slicerVolume.SetLabelMap(1)

      #displayNode = slicerVolume.GetDisplayNode()
      #if displayNode:
        #colorNode = displayNode.GetColorNode()
        #if colorNode:
          #labelValue = colorNode.GetColorName(labelIndex)
      #return "%s (%d)" % (labelValue, labelIndex)
          
    #Check if name exist
    if fileInfo == 2:
      slicerName = pyTRiPCube.patient_name+"_"+str(motionState)
    elif fileInfo == 3:
      slicerName = os.path.basename( fileNamePrefix )
    else:
      slicerName= os.path.basename( fileName )
    n=0    
    slicerName = slicer.mrmlScene.GenerateUniqueName(slicerName)         
    slicerVolume.SetName(slicerName)
    
    if fileInfo == 2:
      slicerVolume.SetOrigin(voi.getSlicerOrigin())
      if voi:
	index = voi.voiNumber
      else:
	index = 0
      slicerVolume = self.convertLabelMapToClosedSurfaceModel(slicerVolume,index = index)
      #pbar.close()
      #return
      #slicerVolume.SetLabelMap(1)
      
    else:
      origin = [round(pyTRiPCube.xoffset*pyTRiPCube.pixel_size,1),
		round(pyTRiPCube.yoffset*pyTRiPCube.pixel_size,1),
		pyTRiPCube.zoffset]
      slicerVolume.SetOrigin(origin)
      
      
    storageNode = slicerVolume.CreateDefaultStorageNode()
    slicerVolume.SetAndObserveStorageNodeID(storageNode.GetID())

    if not slicerVolume.GetDisplayNodeID():
      displayNode = None
      if fileInfo == 0 or fileInfo == 1:# or fileInfo == 2:
        displayNode = slicer.vtkMRMLScalarVolumeDisplayNode()
        displayNode.SetAndObserveColorNodeID("vtkMRMLColorTableNodeGrey")
      if fileInfo == 3:
        displayNode = slicer.vtkMRMLVectorVolumeDisplayNode()
        displayNode.SetAndObserveColorNodeID("vtkMRMLColorTableNodeGrey")
      if displayNode:
        slicer.mrmlScene.AddNode(displayNode)
        slicerVolume.SetAndObserveDisplayNodeID(displayNode.GetID())
        
    
    if showOn and not fileInfo == 2:
      # make the output volume appear in all the slice views
      if fileInfo>0:
        background=True
      else:
        background=False
    
      self.setSliceDisplay(slicerVolume,background)
        
      ##Set dose values to float for normalization and calculations
      #if pyTRiPCube.data_type=='integer' and fileInfo == 1:
        #cliNode = self.changeScalarVolumeType(slicerVolume)

      pbar.setValue(100)
            
      #Set color of dose volume
      if fileInfo==1:
        #TODO: Display doseMax on display
        slicerVolumeDisplay=slicerVolume.GetScalarVolumeDisplayNode()
        if slicerVolumeDisplay:
          slicerVolumeDisplay.AutoWindowLevelOff()
          slicerVolumeDisplay.AutoThresholdOff()
	  #slicerVolumeDisplay.SetThreshold(doseMax*0.1,doseMax*1.1)
	  #TODO: Tole se ne dela?
	  colorNode = slicer.util.getNode('GSIStandard')
	  if not colorNode:
	    colorNode = self.CreateDefaultGSIColorTable()	    
          slicerVolumeDisplay.SetAndObserveColorNodeID(colorNode.GetID())
          slicerVolumeDisplay.SetWindowLevelMinMax(0,round(optDose*1.05))
          slicerVolumeDisplay.SetThreshold(1,1200)
          slicerVolumeDisplay.ApplyThresholdOn()
        else:
	  print "No display node for:"+slicerVolume.GetName()
	  
      if fileInfo == 2:
	#Create subject Hierarchy
        ##Copied from SlicerSubjectHierarchyContourSetsPlugin
        ##from vtkSlicerSubjectHierarchyModuleMRML import vtkMRMLSubjectHierarchyNode
        #from vtkSlicerContoursModuleLogic import vtkSlicerContoursModuleLogic
        #try:
          #vtkMRMLSubjectHierarchyNode
          #vtkSlicerContoursModuleLogic
        #except AttributeError:
          #import sys
          #sys.stderr.write('Unable to load vtkMRMLSubjectHierarchyNode and vtkSlicerContoursModuleLogic')
          #return
        subjectNode = vtkMRMLSubjectHierarchyNode()
        subjectNode.SetName('Patient_SubjectHierarchy')
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
	color = [0.5,0.5,0.5,1]
	colorNode = slicer.vtkMRMLColorTableNode()
	slicer.mrmlScene.AddNode(colorNode)
	
	colorNode.SetName('NewContourSet_ColorTable')
	colorNode.SetAttribute('Category','SlicerRT')
	colorNode.SetTypeToUser()
	colorNode.HideFromEditorsOff()
	colorNode.SetNumberOfColors(2)
	colorNode.GetLookupTable().SetTableRange(0,1)
	
	#color[0:2] = contourNode.GetDisplayNode().GetColor()
	colorNode.AddColor('Background',0.0, 0.0, 0.0, 0.0)
	colorNode.AddColor('Invalid',0.5,0.5,0.5,0.5)
	
	contourSet.SetNodeReferenceID('contourSetColorTableRef', colorNode.GetID() )
	
	if not colorNode:
	  print "No color node for" + slicerVolume.GetName()
	  
	numberOfColors = colorNode.GetNumberOfColors()
	colorNode.SetNumberOfColors(numberOfColors+1);
	
	#lookupTable = vtk.vtkLookupTable()
	#colorNode.SetLookupTable( lookupTable )
        colorNode.GetLookupTable().SetTableRange(0, numberOfColors);
        colorNode.SetColor(numberOfColors, pyTRiPCube.patient_name, color[0], color[1], color[2], color[3]);


	
	
    pbar.close()
    print "Done!"
    return slicerVolume.GetID()

  def setDoses(self, sbrtNode, ptNode):
    
    sbrtArray = slicer.util.array(sbrtNode.GetID())
    ptArray = slicer.util.array(ptNode.GetID())
    
    if not sbrtArray.shape == ptArray.shape:
      print "Array dimensions not the same!"
      print str(sbrtArray.shape) + " vs " + str(ptArray.shape)
      return
    
    newArray = np.zeros(sbrtArray.shape)
    dim = sbrtArray.shape
    

    
    #Iterate through array to determain low values, which are removed from display.
    #Lengthy process
    print "Going through array."
    newArray = sbrtArray - ptArray
    for z in range(0,dim[0]):
      print "Slice: " + str(z) +"/" + str(dim[0])
      for y in range(0,dim[1]):
        for x in range(0,dim[2]):
	  if abs(sbrtArray[z][y][x]) < 0.01: #and abs(ptArray[z][y][x]) < 0.1:
	    newArray[z][y][x] = - 500
	  else:
	    newArray[z][y][x] = sbrtArray[z][y][x] - ptArray[z][y][x]
    
    importer=LoadCTXLib.vtkImageImportFromArray()
    importer.SetArray(newArray)
    slicerVolume = slicer.vtkMRMLScalarVolumeNode()

    slicerVolume.Copy(sbrtNode)
    
    slicer.mrmlScene.AddNode( slicerVolume )
    slicerVolume.SetAndObserveImageData(importer.GetOutput())
    
    slicerName = 'DoseDifference'
    slicerName = slicer.mrmlScene.GenerateUniqueName(slicerName)         
    slicerVolume.SetName(slicerName)
    
    displayNode = slicer.vtkMRMLScalarVolumeDisplayNode()
    slicer.mrmlScene.AddNode(displayNode)
    slicerVolume.SetAndObserveDisplayNodeID(displayNode.GetID())

    displayNode.AutoWindowLevelOff()
    displayNode.AutoThresholdOff()
    displayNode.SetLevel(0)
    displayNode.SetWindow(30)
    displayNode.SetThreshold(-24,24)
    displayNode.ApplyThresholdOn()
    
    colorNode = slicer.util.getNode('ColdToHotRainbow')
    if not colorNode:
      print "Error, no ColdToHotRainbow node"
      return
      #colorNode = self.CreateDefaultHotAndColdColorTable()
    #else:
      #self.CorrectColorNode(colorNode)
    displayNode.SetAndObserveColorNodeID(colorNode.GetID())
    
    
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
    translator.SetInput(imageData)
      
    # Translate the extent by 1 pixel
    translator.SetExtentTranslation(1, 1, 1);
    # Args are: -padx*xspacing, -pady*yspacing, -padz*zspacing but padding and spacing are both 1
    translator.SetOriginTranslation(-1.0, -1.0, -1.0);
    padder.SetInput(translator.GetOutput());
    padder.SetConstant(0);
    translator.Update();
    extent = imageData.GetWholeExtent()
    #Now set the output extent to the new size, padded by 2 on the positive side
    padder.SetOutputWholeExtent(extent[0], extent[1] + 2,
        extent[2], extent[3] + 2,
        extent[4], extent[5] + 2)
    
    marchingCubes = vtk.vtkMarchingCubes() 
    marchingCubes.SetInput(padder.GetOutput())
    marchingCubes.SetNumberOfContours(1)
    marchingCubes.SetValue(1,1)
    marchingCubes.ComputeGradientsOff()
    marchingCubes.ComputeNormalsOff()
    marchingCubes.ComputeScalarsOff()
    marchingCubes.Update()
    if marchingCubes.GetOutput().GetNumberOfPolys() < 0:
      print "Can't create Model."
      return None
      
    ##Decimate feature is disabled for now - the resulting contours are too small.
    #decimate = vtk.vtkDecimatePro()
    #decimate.SetInput(marchingCubes.GetOutput())
    #decimate.SetFeatureAngle(60)
    #decimate.SplittingOff()
    #decimate.PreserveTopologyOn()
    #decimate.SetMaximumError(0.5)
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
    transformFilter.SetInput(marchingCubes.GetOutput())
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
 
 
 
 #Set image in foreground / background
  def setSliceDisplay(self,node,background=False):
      selectionNode = slicer.app.applicationLogic().GetSelectionNode()
      rcn=slicer.util.getNode("vtkMRMLSliceCompositeNodeRed")
      ycn=slicer.util.getNode("vtkMRMLSliceCompositeNodeYellow")
      gcn=slicer.util.getNode("vtkMRMLSliceCompositeNodeGreen")
        
      ##Link Slice Controls
      rcn.SetLinkedControl(1);
      ycn.SetLinkedControl(1);
      gcn.SetLinkedControl(1);
      rcn.SetForegroundOpacity(0.5);
	
      if background:
	selectionNode.SetReferenceSecondaryVolumeID(node.GetID())
      else:
        selectionNode.SetReferenceActiveVolumeID(node.GetID())        
      
      slicer.app.applicationLogic().PropagateVolumeSelection(0)     
      layoutManager = slicer.app.layoutManager()
      redWidget = layoutManager.sliceWidget('Red')
      redWidget.sliceController().fitSliceToBackground()
      
  #Change type of scalar volume
  def changeScalarVolumeType(self,volumeNode,volumeScalarType = ''):
    parameters = {}
    parameters["InputVolume"] = volumeNode.GetID()
    parameters["OutputVolume"] = volumeNode.GetID()
    parameters["Type"] = volumeScalarType
    castScalarVolume = slicer.modules.castscalarvolume
    return (slicer.cli.run(castScalarVolume, None, parameters,wait_for_completion=True))
      
      
  def progressBar(self,message):

    progressBar = qt.QProgressDialog(slicer.util.mainWindow())
    progressBar.setModal(True)
    progressBar.setMinimumDuration(150)
    progressBar.setLabelText(message)
    qt.QApplication.processEvents()
    #progressBarLayout = qt.QVBoxLayout()
    #progressBar.setLayout(progressBarLayout)
    #label = qt.QLabel(message,progressBar)
    #progressBarLayout.addWidget(label)
    return progressBar
    
  def CreateDefaultHotAndColdColorTable(self):
    colorTableNode = slicer.vtkMRMLColorTableNode()    
    nodeName = "HotAndCold"
    colorTableNode.SetName(nodeName);
    colorTableNode.SetTypeToUser();
    colorTableNode.SetAttribute("Category", "User Generated");
    colorTableNode.HideFromEditorsOn();
    colorTableNode.SetNumberOfColors(256);
    colorTableNode.GetLookupTable().SetTableRange(0,255);
    for i in range(0,256):
      if i<125:
	green = i/124.
        colorTableNode.AddColor(str(i), 0, green, 1, 1)
      elif i<131:
        colorTableNode.AddColor(str(i), 1, 1, 1, 1)
      else:
	blue = 1-i/131.
	colorTableNode.AddColor(str(i), 1, 0, blue, 1)

    slicer.mrmlScene.AddNode( colorTableNode )
    return colorTableNode
  
  def CorrectColorNode(self,colorNode):
    for i in range(0,256):
	if i<125:
	  green = 1-i/124.
          colorNode.SetColor(i, 0, green, 1, 1)
        elif i<131:
          colorNode.SetColor(i, 0, 0, 0, 1)
        else:
	  green = (i-131)/124.
	  colorNode.SetColor(i, 1, green , 0, 1)
	
  def CreateDefaultGSIColorTable(self):
    colorTableNode = slicer.vtkMRMLColorTableNode()    
    nodeName = "GSIStandard"
    colorTableNode.SetName(nodeName);
    colorTableNode.SetTypeToUser();
    colorTableNode.SetAttribute("Category", "User Generated");
    colorTableNode.HideFromEditorsOn();
    colorTableNode.SetNumberOfColors(256);
    colorTableNode.GetLookupTable().SetTableRange(0,255)
    for i in range(0,256):
      if i<48:
        colorTableNode.AddColor(str(i), 0.06, 0, 1, 0.2)
      elif i<97:
	colorTableNode.AddColor(str(i), 0, 0.94, 1, 0.2)
      elif i<145:
        colorTableNode.AddColor(str(i), 0.02, 0.5, 0, 0.2)
      elif i<194:
        colorTableNode.AddColor(str(i), 0.02, 1, 0, 0.2)
      elif i<230:
        colorTableNode.AddColor(str(i), 1, 1, 0, 0.2)
      elif i<255:
        colorTableNode.AddColor(str(i), 1, 0, 0, 0.2)
      else:
	colorTableNode.AddColor(str(i), 1, 0, 1, 1)
    #for i in range(0,256):
      #if i<49:
        #colorTableNode.AddColor(str(i), 0.06, 0, 1, 0.2);
      #elif i<98:
	#colorTableNode.AddColor(str(i), 0, 0.94, 1, 0.2);
      #elif i<147:
        #colorTableNode.AddColor(str(i), 0.02, 0.5, 0, 0.2);
      #elif i<195:
        #colorTableNode.AddColor(str(i), 0.02, 1, 0, 0.2);
      #elif i<243:
        #colorTableNode.AddColor(str(i), 1, 1, 0, 0.2);
      #elif i<255:
        #colorTableNode.AddColor(str(i), 1, 0, 0, 0.2);
      #else:
	#colorTableNode.AddColor(str(i), 1, 0, 1, 1);

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
    
