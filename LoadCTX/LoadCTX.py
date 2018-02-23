import os, re
import unittest
import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
import logging
import numpy as np
import LoadCTXLib
reload(LoadCTXLib)
import vtkSegmentationCorePython as vtkSegmentationCore
#
# LoadCTX
#

class LoadCTX(ScriptedLoadableModule):
  """Uses ScriptedLoadableModule base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "Load TRiP Volume" # TODO make this more human readable by adding spaces
    self.parent.categories = ["SliceTRiP"]
    self.parent.dependencies = []
    self.parent.contributors = ["Kristjan Anderle (GSI)"] # replace with "Firstname Lastname (Organization)"
    self.parent.helpText = """
This is a module for loading binfo files and setting colormap to GSI Standard for Dose.
"""
    self.parent.helpText += self.getDefaultModuleDocumentationLink()
    self.parent.acknowledgementText = """
This file was originally developed by Jean-Christophe Fillion-Robin, Kitware Inc.
and Steve Pieper, Isomics, Inc. and was partially funded by NIH grant 3P41RR013218-12S1.
""" # replace with organization, grant and thanks.

#
# LoadCTXWidget
#

class LoadCTXWidget(ScriptedLoadableModuleWidget):
  """Uses ScriptedLoadableModuleWidget base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def setup(self):
    ScriptedLoadableModuleWidget.setup(self)

    # Instantiate and connect widgets ...

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
    
    self.calculateMotionButton = qt.QPushButton("Calculate Motion")
    self.calculateMotionButton.enabled = False
    self.buttonForm.addWidget(self.calculateMotionButton,0,1)
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
    self.setAddVecorButton = qt.QPushButton("Random Script")
    self.setAddVecorButton.toolTip = "Set origins to zero."
    self.setAddVecorButton.enabled = True
    doseDifferenceLayout.addRow(self.setAddVecorButton)
    
    # connections
    self.show3DButton.connect('clicked(bool)', self.onShow3DButton)
    self.calculateMotionButton.connect('clicked(bool)', self.onCalculateMotionButton)
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
      
  def onLoadButton(self): 
    loadFileName = qt.QFileDialog()
    filePathList=loadFileName.getOpenFileNames(None,"Select Binfo File","","Binfo (*.binfo)")
    for filePath in filePathList:
      self.loadBinfo(filePath)
  
  #Load Binfo in Slicer
  def loadBinfo(self,filePath):
     filePrefix, fileExtension = os.path.splitext(filePath)
     if not fileExtension == ".binfo":
        print "Error, file not a binfo file: " + filePath
     self.voiComboBox.clear()
     self.motionStateComboBox.clear() 
     binfo = LoadCTXLib.Binfo()
     binfo.readFile(filePath)
     self.binfoList.append( binfo )
     self.binfoListFile.addItem( binfo.name )
     self.setBinfoFile(-1)
     self.binfoListFile.setCurrentIndex(self.binfoListFile.count - 1)
     self.binfoListFile.enabled = True
     
     #Create segmentation node for this binfo
     patName = os.path.basename(filePrefix)
     
     shNode = slicer.util.getNode('SubjectHierarchy')
     patID = shNode.GetItemChildWithName(shNode.GetSceneItemID(),patName)
     if patID < 1:
        patID = shNode.CreateSubjectItem(shNode.GetSceneItemID(), patName);
        
     folderID = shNode.GetItemChildWithName(patID, "Contour")
     if folderID < 1:
        folderID = shNode.CreateFolderItem(patID, "Contour");
        
     name = slicer.mrmlScene.GenerateUniqueName(patName)
     segmentationNode = slicer.vtkMRMLSegmentationNode()
     segmentationNode.SetName(name)
     slicer.mrmlScene.AddNode(segmentationNode)
     
     segmentationNodeID = shNode.GetItemByDataNode(segmentationNode)
     shNode.SetItemParent(segmentationNodeID, folderID)
        
     displayNode = slicer.vtkMRMLSegmentationDisplayNode()
     slicer.mrmlScene.AddNode(displayNode)
     segmentationNode.SetAndObserveDisplayNodeID(displayNode.GetID())
     
     displayNode.SetAllSegmentsVisibility2DFill(False)
     displayNode.SetSliceIntersectionThickness(3)
     
     storageNode = slicer.vtkMRMLSegmentationStorageNode()
     slicer.mrmlScene.AddNode(storageNode)
     segmentationNode.SetAndObserveStorageNodeID(storageNode.GetID())
     
     self.segmentationList.append(segmentationNode)
     
  def setBinfoFile(self, binfoNumber):
    self.voiComboBox.clear()
    self.motionStateComboBox.clear()
    binfo = self.binfoList[binfoNumber]
    
    #self.binfoListFile.setCurrentIndex[binfoNumber]
    voiNames = binfo.get_voi_names()
    if voiNames == []:
       print "No names in " + binfo.name
    else:
       for voiName in voiNames:
         voi = binfo.get_voi_by_name(voiName)
         if voi:
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
    if voi is None:
       print "No voi"
       return
    self.motionStateComboBox.clear()
    motionStates=voi.N_of_motion_states
    #We need at least 3 motion states - reference + two motion states
    if motionStates > 2:
       self.calculateMotionButton.enabled = True
    else:
       self.calculateMotionButton.enabled = False
    for i in range(0,motionStates):
      self.motionStateComboBox.addItem(voi.motionStateDescription[i])

 
  def onShow3DButton(self):
    binfo = self.binfoList[self.binfoListFile.currentIndex]
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

  def onCalculateMotionButton(self):
     binfo = self.binfoList[self.binfoListFile.currentIndex]
     segmentationNode = self.segmentationList[self.binfoListFile.currentIndex]
     voi = binfo.get_voi_by_name(self.voiComboBox.currentText)
     logic = LoadCTXLogic()
     logic.calculateMotion(voi, binfo, segmentationNode, axisOfMotion = False, showPlot = True)
  
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
    sbrtNode = self.selectSBRTDose.currentNode()
    logic = LoadCTXLogic()
    logic.addVectors(sbrtNode)
  

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
    
    
    if voi.slicerNodeID[motionState]:
       return voi.slicerNodeID[motionState]
    
    #binaryLabelmapReprName = vtkSegmentationCore.vtkSegmentationConverter.GetSegmentationBinaryLabelmapRepresentationName()
    segLogic = slicer.modules.segmentations.logic()
    segLogic.SetMRMLScene(slicer.mrmlScene)
    voi.slicerNodeID[motionState]=None
    if not filePath or not os.path.isfile(filePath):
      print "No file!" + filePath
      return None
      
    volumesLogic = slicer.vtkSlicerVolumesLogic()
    volumesLogic.SetMRMLScene(slicer.mrmlScene)
    slicerVolumeName = voi.name + "_" + str(motionState)
    slicerVolume = volumesLogic.AddArchetypeVolume(filePath,slicerVolumeName,1) 
    #success, midV = slicer.util.loadVolume(os.path.basename(filePath), 
                                           #properties = {'name' : "Helo", 'labelmap' : True}, returnNode = True)
    slicerVolume.SetOrigin(voi.getSlicerOrigin())
    if not slicerVolume:
      print "Can't load volume " + os.path.basename(filePath)
      return None
    
    colorNode = slicer.util.getNode("vtkMRMLColorTableNodeFileGenericAnatomyColors.txt")
    colorIndex = colorNode.GetColorIndexByName(voi.name.lower())
    color = [0,0,0,1]
    
    if colorIndex < 2:
       colorNode = slicer.util.getNode("vtkMRMLColorTableNodeLabels")
       colorIndex = colorNode.GetColorIndexByName("dylan")
       
    if not colorNode.GetColor(colorIndex,color):
       print "Can't set color for " + voi.name.lower()
       color = [0,0,0,1]
       #colorIndex = colorNode.GetColorIndexByName("region 11")
       
    #print colorIndex

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
    if colorIndex > -1:
       array[:] *= colorIndex
    slicerVolume.GetImageData().Modified()
    if not slicer.vtkSlicerSegmentationsModuleLogic.ImportLabelmapToSegmentationNode(slicerVolume,segmentationNode):
       print "Can't load volume in segmentation"
       return None
    else:
       print "Added " + slicerVolume.GetName() + " to " + segmentationNode.GetName()
    
    
    
    print "Done!"
    return slicerVolume.GetID()

  def setVectorField(self, vectorNode):
    spacing = vectorNode.GetSpacing()
    
    vectorArray = slicer.util.array(vectorNode.GetID())
    
    for i in range(0,3):
      vectorArray[:,:,:,i] = vectorArray[:,:,:,i] * spacing[i]
    vectorNode.GetImageData().Modified()
    print "Finshed!"
    
  
  def addVectors(self,node):
    
    nodeArray = slicer.util.array(node.GetID())
    
    maxDose = nodeArray.max()
    minDose = np.min(nodeArray[np.nonzero(nodeArray)])
    
    dim = nodeArray.shape
    
    nodeArray[:] = nodeArray[:]/maxDose
    
    #for z in range(0,dim[0]):
      #print "Slice: " + str(z) +"/" + str(dim[0])
      #for y in range(0,dim[1]):
        #for x in range(0,dim[2]):
          #if nodeArray[z][y][x] > 0.2*maxDose:
             #pass
            ##nodeArray[z][y][x] = np.log(nodeArray[z][y][x]/minDose)/np.log(maxDose/minDose)
          #else:
            #nodeArray[z][y][x] = -100
            
    node.GetImageData().Modified()
    print "Voila"
    return
    
    
    refPhase = 5
    numberOfPhases = 8
    filePath = "/u/kanderle/AIXd/Data/CNAO/Liver/ManualContour/"
    name = "liver_"
    ext = ".mha"
    phaseList = ["00","12","25","37","50","62","75","87"]
    
    phaseContourFile = filePath + name + phaseList[refPhase-1] + ext
    if not os.path.isfile(phaseContourFile):
         print "No file " + phaseContourFile
         return
    success, phaseNode = slicer.util.loadVolume(phaseContourFile, 
                                           properties = {'labelmap' : True}, returnNode = True)

    #Refphase first
    newNode = slicer.vtkMRMLScalarVolumeNode()
    newNode.SetName('Merged')
    
    newImageData = vtk.vtkImageData()
    newImageData.DeepCopy( phaseNode.GetImageData() )
    newNode.SetAndObserveImageData( newImageData )
    
    newNode.SetSpacing( phaseNode.GetSpacing() )
    newNode.SetOrigin( phaseNode.GetOrigin() )
    
    slicer.mrmlScene.AddNode( newNode )

    parameters = {}
    parameters["InputVolume"] = newNode.GetID()
    parameters["OutputVolume"] = newNode.GetID()
    parameters["Type"] = "Int"
    castVolume= slicer.modules.castscalarvolume
    slicer.cli.run(castVolume, None, parameters, wait_for_completion=True)
    
    newArray = slicer.util.array( newNode.GetID() )
    
    newNode.CreateDefaultDisplayNodes()
    storage = newNode.CreateDefaultStorageNode()
    slicer.mrmlScene.AddNode( storage )
    newNode.SetAndObserveStorageNodeID( storage.GetID() )
    
    if len(newArray) == 0:
      print "No new array for phase " + phase
      return
    
    for phase in range(1,len(phaseList)+1):

      phaseContourFile = filePath + name + phaseList[phase-1] + ext
      if not os.path.isfile(phaseContourFile):
         print "No file " + phaseContourFile
         return
      success, phaseNode = slicer.util.loadVolume(phaseContourFile, 
                                           properties = {'labelmap' : True}, returnNode = True)
      if not success:
         print "Can't load file " + phaseContourFile
         return
      
      arrayPhase = slicer.util.array(phaseNode.GetID())
      if len(arrayPhase) == 0:
         print "No array for phase " + phase
         return
      print "Adding bit: " + str(phase) + " ( " + str(1<<phase) + " )"
      newArray[:] |= ( arrayPhase[:] << phase )

    print "Finished"

  def calculateMotion(self, voi, binfo, segmentationNode, axisOfMotion = False, showPlot = True):
    # logging.info('Processing started')

    origins = np.zeros([3, voi.N_of_motion_states-1])
    relOrigins = np.zeros([4, voi.N_of_motion_states-1])
    minmaxAmplitudes = [[-1e3, -1e3, -1e3], [1e3, 1e3, 1e3]]
    amplitudes = [0, 0, 0]

    refPhase = 5
    exportTrafo = True

    #This is the relative difference between planning CT and reference position
    #Amplitudes are shifted for this value, so we can get an estimate, where is our planning CT in 4DCT

    planOrigins = [0,0,0]
    #print "planorigins: ", planOrigins

    # Propagation in 4D
    for i in range(1, voi.N_of_motion_states):

      if not voi.slicerNodeID[i]:
        filePrefix, fileExtension = os.path.splitext(binfo.filePath)
        filePath = filePrefix + voi.name + ".nrrd"
        voi.slicerNodeID[i] = self.loadVoi(filePath,segmentationNode, motionState=i,voi=voi)
     
    for i in range(1, voi.N_of_motion_states):
      #Create & propagate contour
      segmentation = segmentationNode.GetSegmentation()
      segmentation.CreateRepresentation('Closed surface')
      voiName = voi.name + "_" + str(i)
      contour = self.getContourFromVoi(voiName,segmentation)
      if contour is None:
        #print "Can't get contour  " + str(i) + "0 %"
        continue
      
      origins[:, i-1] = self.getCenterOfMass(contour)

    # Find axis of motion
    if axisOfMotion:
      matrix_W = self.findAxisOfMotion(origins)
      if matrix_W is None:
        print "Can't calculate axis of motion"
        return
      #This is turned off for the moment, because we can't add margins in arbitrary direction
      origins = np.dot(matrix_W.T, origins)
      patient.matrix = matrix_W

    #Find relative motion
    for i in range(0,voi.N_of_motion_states-1):
      relOrigins[0:3, i] = origins[:, refPhase] - origins[:, i] + relOrigins[0:3, refPhase]

    # Absolute motion & max & min motion
    #print relOrigins
    #print np.zeros([1, voi.N_of_motion_states-1])
    #relOrigins = np.vstack([relOrigins, np.zeros([1, voi.N_of_motion_states-1])])
    for j in range(0,voi.N_of_motion_states-1):
      amplitude = 0
      for i in range(0, 3):
        #Max
        if relOrigins[i, j] > minmaxAmplitudes[0][i]:
          minmaxAmplitudes[0][i] = relOrigins[i, j]
        #Min
        if relOrigins[i, j] < minmaxAmplitudes[1][i]:
          minmaxAmplitudes[1][i] = relOrigins[i, j]
        amplitude += relOrigins[i, j]*relOrigins[i, j]
      relOrigins[3, j] = np.sqrt(amplitude)

    #Find & save peak-to-peak amplitudes
    amplitudesTmp = [-1, -1, -1]
    for j in range(3):
      amplitudesTmp[j] = abs(minmaxAmplitudes[0][j] - minmaxAmplitudes[1][j])
      if amplitudesTmp[j] > amplitudes[j]:
        amplitudes[j] = amplitudesTmp[j]

    print amplitudes
    # Plot
    if showPlot:
      self.plotMotion(relOrigins, voi.name)

    print origins
    print relOrigins
    if exportTrafo:
      dirPath = "/u/kanderle/AIXd/Data/CNAO/Liver/CenterOfMass_Manual/"
      patName = "Liver"
      #dirPath = "/u/kanderle/AIXd/Data/FC/"+ patName+"/Registration/CenterOfMass/"
      for i in range(0,voi.N_of_motion_states-1):
         fileName = patName + "_0" + str(i) + "_0" + str(refPhase) +".aff"
         matrixMuster = "1 0 0 X\n0 1 0 Y \n0 0 1 Z \n0 0 0 1"
         matrixExport = matrixMuster.replace("X",str(relOrigins[0, i]))
         matrixExport = matrixExport.replace("Y",str(relOrigins[1, i]))
         matrixExport = matrixExport.replace("Z",str(-relOrigins[2, i]))
         #outputString = "FinalRegistrationMatrix = " + matrixExport
         outputString = matrixExport
         filePath = dirPath + fileName
         f = open(filePath,"wb+")
         f.write(outputString)
         f.close()
         
         fileName = patName + "_0" + str(refPhase) +"_0" + str(i) + ".aff"
         matrixMuster = "1 0 0 X\n0 1 0 Y \n0 0 1 Z \n0 0 0 1"
         matrixExport = matrixMuster.replace("X",str(-relOrigins[0, i]))
         matrixExport = matrixExport.replace("Y",str(-relOrigins[1, i]))
         matrixExport = matrixExport.replace("Z",str(relOrigins[2, i]))
         #outputString = "FinalRegistrationMatrix = " + matrixExport
         outputString = matrixExport
         filePath = dirPath + fileName
         f = open(filePath,"wb+")
         f.write(outputString)
         f.close()
    
    print "Calculated motion"
    return
    
  def getContourFromVoi(self,voiName,segmentation):
     segment = segmentation.GetSegment(voiName)
     if segment is None:
        print "Can't get " + voiName + " segment"
        return None
        
     return segment.GetRepresentation('Closed surface')
  
  def getCenterOfMass(self,contour):
      comFilter = vtk.vtkCenterOfMass()
      comFilter.SetInputData(contour)
      comFilter.SetUseScalarsAsWeights(False)
      comFilter.Update()
      return comFilter.GetCenter()
  
  def plotMotion(self, relOrigins, contourName):
    ln = slicer.util.getNode(pattern='vtkMRMLLayoutNode*')
    ln.SetViewArrangement(25)

    # Get the first ChartView node
    cvn = slicer.util.getNode(pattern='vtkMRMLChartViewNode*')

    # Create arrays of data
    dn = {}
    dim = relOrigins.shape
    for i in range(0, 4):
      dn[i] = slicer.mrmlScene.AddNode(slicer.vtkMRMLDoubleArrayNode())
      a = dn[i].GetArray()
      a.SetNumberOfTuples(dim[1])
      for j in range(0,dim[1]):
        a.SetComponent(j, 0, j)
        a.SetComponent(j, 1, relOrigins[i, j])
        a.SetComponent(j, 2, 0)

    # Create the ChartNode,
    cn = slicer.mrmlScene.AddNode(slicer.vtkMRMLChartNode())

    # Add data to the Chart
    cn.AddArray('L-R', dn[0].GetID())
    cn.AddArray('A-P', dn[1].GetID())
    cn.AddArray('I-S', dn[2].GetID())
    cn.AddArray('abs', dn[3].GetID())

    # Configure properties of the Chart
    cn.SetProperty('default', 'title','Relative ' + contourName + ' motion')
    cn.SetProperty('default', 'xAxisLabel', 'phase')
    cn.SetProperty('default', 'yAxisLabel', 'position [mm]')
    cn.SetProperty('default', 'showGrid', 'on')
    cn.SetProperty('default', 'xAxisPad', '1')
    cn.SetProperty('default', 'showMarkers', 'on')

    cn.SetProperty('L-R', 'color', '#0000ff')
    cn.SetProperty('A-P', 'color', '#00ff00')
    cn.SetProperty('I-S', 'color', '#ff0000')
    cn.SetProperty('abs', 'color', '#000000')

    # Set the chart to display
    cvn.SetChartNodeID(cn.GetID())

  def findAxisOfMotion(self, origins):
    #Following guide from: http://sebastianraschka.com/Articles/2014_pca_step_by_step.html

    #scale factor for better display:
    scale = 100

    #Calculate mean position
    meanVector = [0, 0 ,0]
    for i in range(3):
      meanVector[i] = np.mean(origins[i, :])


    #Computing covariance matrix
    convMatrix = np.cov([origins[0, :], origins[1, :], origins[2, :]])

    #Get eigenvectors
    eig_val, eig_vec = np.linalg.eig(convMatrix)

    # Make a list of (eigenvalue, eigenvector) tuples
    eig_pairs = [(np.abs(eig_val[i]), eig_vec[:,i]) for i in range(len(eig_val))]

    # Sort the (eigenvalue, eigenvector) tuples from high to low
    eig_pairs.sort()
    # eig_pairs.reverse()
    matrix_w = np.hstack((eig_pairs[0][1].reshape(3, 1),
                          eig_pairs[1][1].reshape(3, 1),
                          eig_pairs[2][1].reshape(3, 1)))
    print('Matrix W:\n', matrix_w)

    #Create linear transform for contour propagation

    vtkMatrix = vtk.vtkMatrix4x4()
    transform = slicer.vtkMRMLLinearTransformNode()
    slicer.mrmlScene.AddNode(transform)

    for i in range(3):
      for j in range(3):
        vtkMatrix.SetElement(j, i, matrix_w[i, j])

    transform.SetAndObserveMatrixTransformFromParent(vtkMatrix)

    #Plot eigenvectors from mean position
    fiducials = slicer.vtkMRMLMarkupsFiducialNode()
    displayNode = slicer.vtkMRMLMarkupsDisplayNode()
        # vtkNew<vtkMRMLMarkupsFiducialStorageNode> wFStorageNode;
    slicer.mrmlScene.AddNode(displayNode)
    slicer.mrmlScene.AddNode(fiducials)
    fiducials.SetAndObserveDisplayNodeID(displayNode.GetID())
    fiducials.AddFiducialFromArray(meanVector, "Mean Position")
    for i in range(len(eig_vec)):
      # fiducials.AddFiducialFromArray(meanVector + scale * eig_vec[i], " P " + str(i+1))
      #Plot ruler
      ruler = slicer.vtkMRMLAnnotationRulerNode()
      displayRuler = slicer.vtkMRMLAnnotationLineDisplayNode()
      displayRuler.SetLabelVisibility(0)
      displayRuler.SetMaxTicks(0)
      displayRuler.SetLineWidth(5)
      slicer.mrmlScene.AddNode(displayRuler)
      slicer.mrmlScene.AddNode(ruler)
      ruler.SetAndObserveDisplayNodeID(displayRuler.GetID())
      ruler.SetPosition1(meanVector)
      ruler.SetPosition2(meanVector + scale * eig_vec[i])

    return matrix_w  
  
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
      slicerVolumeDisplay.SetThreshold(0.01*optDose,1200)
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
    log = False
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
      if log:
        colorTableNode.SetNumberOfColors(1200);
        colorTableNode.GetLookupTable().SetTableRange(0,1199)
        for i in range(0,1200):
         lightBlue = 1.0
         darkGreen = 10.0
         lightGreen = 100.0
         yellow = 1000.0
         red = 1100.0
         if i>=0 and i<lightBlue:
              colorTableNode.AddColor(str(i), 0, 0 + i/lightBlue, 0.5, 0.2)
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

class LoadCTXTest(ScriptedLoadableModuleTest):
  """
  This is the test case for your scripted module.
  Uses ScriptedLoadableModuleTest base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

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
    tests should exercise the functionality of the logic with different inputs
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
        logging.info('Requesting download %s from %s...\n' % (name, url))
        urllib.urlretrieve(url, filePath)
      if loader:
        logging.info('Loading %s...' % (name,))
        loader(filePath)
    self.delayDisplay('Finished with download and loading')

    volumeNode = slicer.util.getNode(pattern="FA")
    logic = LoadCTXLogic()
    self.assertIsNotNone( logic.hasImageData(volumeNode) )
    self.delayDisplay('Test passed!')
    
#class Slicelet(object):
  #"""A slicer slicelet is a module widget that comes up in stand alone mode
  #implemented as a python class.
  #This class provides common wrapper functionality used by all slicer modlets.
  #"""
  ## TODO: put this in a SliceletLib
  ## TODO: parse command line arge


  #def __init__(self, widgetClass=None):
    #self.parent = qt.QFrame()
    #self.parent.setLayout( qt.QVBoxLayout() )

    ## TODO: should have way to pop up python interactor
    #self.buttons = qt.QFrame()
    #self.buttons.setLayout( qt.QHBoxLayout() )
    #self.parent.layout().addWidget(self.buttons)
    #self.addDataButton = qt.QPushButton("Add Data")
    #self.buttons.layout().addWidget(self.addDataButton)
    #self.addDataButton.connect("clicked()",slicer.app.ioManager().openAddDataDialog)
    #self.loadSceneButton = qt.QPushButton("Load Scene")
    #self.buttons.layout().addWidget(self.loadSceneButton)
    #self.loadSceneButton.connect("clicked()",slicer.app.ioManager().openLoadSceneDialog)

    #if widgetClass:
      #self.widget = widgetClass(self.parent)
      #self.widget.setup()
    #self.parent.show()

#class LoadCTXSlicelet(Slicelet):
  #""" Creates the interface when module is run as a stand alone gui app.
  #"""

  #def __init__(self):
    #super(LoadCTXSlicelet,self).__init__(LoadCTXWidget)


#if __name__ == "__main__":
  ## TODO: need a way to access and parse command line arguments
  ## TODO: ideally command line args should handle --xml

  #import sys
  #print( sys.argv )

#slicelet = LoadCTXSlicelet()
