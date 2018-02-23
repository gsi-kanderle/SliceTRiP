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
# LoadCTXLight
#

class LoadCTXLight(ScriptedLoadableModule):
  """Uses ScriptedLoadableModule base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "Load TRiP Volume Light" # TODO make this more human readable by adding spaces
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
# LoadCTXLightWidget
#

class LoadCTXLightWidget(ScriptedLoadableModuleWidget):
  """Uses ScriptedLoadableModuleWidget base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def setup(self):
    ScriptedLoadableModuleWidget.setup(self)

    # Instantiate and connect widgets ...

    #
    # Parameters Area
    #
    self.frame = qt.QFrame(self.parent)
    self.frame.setLayout(qt.QHBoxLayout())
    self.parent.layout().addWidget(self.frame)
    
    #binfoCollapsibleButton = ctk.ctkCollapsibleButton()
    #binfoCollapsibleButton.text = "LoadBinfo"
    #self.layout.addWidget(binfoCollapsibleButton)

    # Layout within the dummy collapsible button
    #binfoFormLayout = qt.QFormLayout(binfoCollapsibleButton)
    #Load File
    #
    # Load CTX File Button
    #
    self.loadButton = qt.QPushButton("Load Binfo File:")
    self.loadButton.toolTip = "Load binfo file."
    self.loadButton.enabled = True
    self.frame.layout().addWidget(self.loadButton)
    
    # Binfo
    self.selectSegmentation = slicer.qMRMLNodeComboBox()
    self.selectSegmentation.nodeTypes = ( ("vtkMRMLSegmentationNode"),"" )
    #self.selectSegmentation.addAttribute( "vtkMRMLScalarVolumeNode", "LabelMap", 0 )
    self.selectSegmentation.selectNodeUponCreation = True
    self.selectSegmentation.addEnabled = False
    self.selectSegmentation.removeEnabled = True
    self.selectSegmentation.noneEnabled = True
    self.selectSegmentation.showHidden = False
    self.selectSegmentation.showChildNodeTypes = False
    self.selectSegmentation.setMRMLScene( slicer.mrmlScene )
    self.selectSegmentation.setToolTip( "Select segmentation." )
    self.frame.layout().addWidget(self.selectSegmentation)
    #binfoFormLayout.addRow("Volume: ", self.selectVolume)
    #self.binfoListFile = qt.QComboBox()    
    #self.binfoListFile.setToolTip( "Input file" )
    #self.binfoListFile.enabled = False
    #self.frame.layout().addWidget(self.binfoListFile)
    #binfoFormLayout.addRow("Binfo:", self.binfoListFile)
    

    #self.fileName.getOpenFileName(self, tr("Open File"),"",tr("Files (*.*)"));
    
    # Voi list
    self.voiComboBox = qt.QComboBox()
    self.voiComboBox.enabled = False
    self.frame.layout().addWidget(self.voiComboBox)
    #binfoFormLayout.addRow("Select Voi: ", self.voiComboBox)
    
    # Motion state list
    self.motionStateComboBox = qt.QComboBox()
    self.motionStateComboBox.enabled = False
    self.frame.layout().addWidget(self.motionStateComboBox)
    #binfoFormLayout.addRow("Select Motion State: ", self.motionStateComboBox)
    
    self.frame2 = qt.QFrame(self.parent)
    self.frame2.setLayout(qt.QHBoxLayout())
    self.parent.layout().addWidget(self.frame2)
    #
    # Show Button
    #
    self.buttonForm = qt.QGridLayout()
    
    self.show3DButton = qt.QPushButton("Load VOI")
    self.show3DButton.enabled = False
    #self.buttonForm.addWidget(self.show3DButton,0,0)
    self.frame2.layout().addWidget(self.show3DButton)
    
    self.calculateMotionButton = qt.QPushButton("Calculate Motion")
    self.calculateMotionButton.enabled = False
    #self.buttonForm.addWidget(self.calculateMotionButton,0,1)
    self.frame2.layout().addWidget(self.calculateMotionButton)
    #binfoFormLayout.addRow(self.buttonForm)
    #
    # Select dose volume
    #
    self.frame3 = qt.QFrame(self.parent)
    self.frame3.setLayout(qt.QHBoxLayout())
    self.parent.layout().addWidget(self.frame3)
    
    self.selectVolume = slicer.qMRMLNodeComboBox()
    self.selectVolume.nodeTypes = ( ("vtkMRMLScalarVolumeNode"),("vtkMRMLVectorVolumeNode"),"" )
    #self.selectVolume.addAttribute( "vtkMRMLScalarVolumeNode", "LabelMap", 0 )
    self.selectVolume.selectNodeUponCreation = True
    self.selectVolume.addEnabled = False
    self.selectVolume.removeEnabled = True
    self.selectVolume.noneEnabled = True
    self.selectVolume.showHidden = False
    self.selectVolume.showChildNodeTypes = False
    self.selectVolume.setMRMLScene( slicer.mrmlScene )
    self.selectVolume.setToolTip( "Select dose volume." )
    self.frame3.layout().addWidget(self.selectVolume)
    #binfoFormLayout.addRow("Volume: ", self.selectVolume)
    
    self.setDoseColorButton = qt.QPushButton("Set dose color")
    self.setDoseColorButton.toolTip = "Creates default GSI Color table and sets it for input volume."
    self.setDoseColorButton.enabled = True
    self.frame3.layout().addWidget(self.setDoseColorButton)
    

    self.interpolateLabel = qt.QLabel("Interpolate:")
    self.frame3.layout().addWidget(self.interpolateLabel)
    
    self.setInterpolateCheckbox = qt.QCheckBox()
    self.setInterpolateCheckbox.toolTip = "Sets volume interpolation on/off."
    self.setInterpolateCheckbox.enabled = True
    self.frame3.layout().addWidget(self.setInterpolateCheckbox)
    
    self.frame4 = qt.QFrame(self.parent)
    self.frame4.setLayout(qt.QHBoxLayout())
    self.parent.layout().addWidget(self.frame4)
    
    # Input dose value
    # TO DO: add check box to choose between substract origin or change origin
    
    self.doseBoxLabel = qt.QLabel("Dose optimization Value: ", self.frame4)
    self.frame4.layout().addWidget(self.doseBoxLabel)
    #self.doseBoxLabel.setToolTip( "Select the grayscale volume (background grayscale scalar volume node) for statistics calculations")
    #self.grayscaleSelectorFrame.layout().addWidget(self.doseBoxLabel)
    
    self.optDoseBox = qt.QDoubleSpinBox()     
    self.optDoseBox.setToolTip( "The optimization value for dose." )
    self.optDoseBox.setValue(24)
    self.optDoseBox.setRange(0, 1000)
    self.frame4.layout().addWidget(self.optDoseBox)
    #self.optDoseForm.addRow("Dose optimization Value", self.optDoseBox)
    
    self.physDoseLabel = qt.QLabel("Dose in permil:", self.frame4)
    self.optDoseBox.setToolTip( "Check this if doses are evaluated in permil (if you get strange colors, this is probably te case)." )
    self.frame4.layout().addWidget(self.physDoseLabel)
    
    self.pyhsDoseForm = qt.QFormLayout()
    self.pyhsDoseCheckBox = qt.QCheckBox()
    self.pyhsDoseCheckBox.setToolTip("Check if the dose volume is in permil")
    self.frame4.layout().addWidget(self.pyhsDoseCheckBox)
    #self.pyhsDoseForm.addRow("Pyhsical dose: ", self.pyhsDoseCheckBox)
    
    self.overDoseLabel = qt.QLabel("Overdose Off:", self.frame4)
    self.frame4.layout().addWidget(self.overDoseLabel)
    
    self.overDoseOffForm = qt.QFormLayout()
    self.overDoseOffCheckBox = qt.QCheckBox()
    self.overDoseOffCheckBox.setToolTip("Check if you don't want to display overodse.")
    self.frame4.layout().addWidget(self.overDoseOffCheckBox)
    #self.overDoseOffForm.addRow("Overdose Off: ", self.overDoseOffCheckBox)
    
    
    self.frame5 = qt.QFrame(self.parent)
    self.frame5.setLayout(qt.QHBoxLayout())
    self.parent.layout().addWidget(self.frame5)
    #
    # Set dose colormap
    #
    self.setVectorFieldButton = qt.QPushButton("Set TRiP vector field")
    self.setVectorFieldButton.toolTip = "Multiplies vector field values with pixel spacing (historical reason in TRiP)."
    self.setVectorFieldButton.enabled = False
    self.frame5.layout().addWidget(self.setVectorFieldButton)
    
    self.frame6 = qt.QFrame(self.parent)
    self.frame6.setLayout(qt.QHBoxLayout())
    self.parent.layout().addWidget(self.frame6)
    
    self.saveScreenshotButton = qt.QPushButton("Save Screenshot")
    self.saveScreenshotButton.toolTip = "Saves screenshot."
    self.saveScreenshotButton.enabled = True
    self.frame6.layout().addWidget(self.saveScreenshotButton)
    

    
    # connections
    self.show3DButton.connect('clicked(bool)', self.onShow3DButton)
    self.calculateMotionButton.connect('clicked(bool)', self.onCalculateMotionButton)
    self.loadButton.connect('clicked(bool)', self.onLoadButton)
    self.voiComboBox.connect('currentIndexChanged(QString)', self.setMotionStatesFromComboBox)
    self.selectSegmentation.connect("currentNodeChanged(vtkMRMLNode*)", self.setBinfoFile)
    self.setDoseColorButton.connect('clicked(bool)', self.onSetDoseColorButton)
    self.setInterpolateCheckbox.connect('clicked(bool)', self.onSetInterpolateCheckbox)
    self.pyhsDoseCheckBox.connect('clicked(bool)',self.onChangePyhsDoseCheckBox)
    self.selectVolume.connect("currentNodeChanged(vtkMRMLNode*)", self.onSelect)
    self.setVectorFieldButton.connect('clicked(bool)', self.onSetVectorFieldButton)
    self.saveScreenshotButton.connect('clicked(bool)', self.onSaveScreenShotButton)

    # Add vertical spacer
    self.layout.addStretch(1)
    
    # Binfo file:
    #binfo=Binfo()
    self.binfoList = []

  def cleanup(self):
    pass

  def onSelect(self,node):
    if node is None:
      self.setVectorFieldButton.enabled = False
      self.setDoseColorButton.enabled = False
      return
    elif node.IsA('vtkMRMLVectorVolumeNode'):
       self.setVectorFieldButton.enabled = True
       self.setDoseColorButton.enabled = False
    elif node.IsA('vtkMRMLScalarVolumeNode'):
      self.setDoseColorButton.enabled = True
      self.setVectorFieldButton.enabled = False
      displayNode = node.GetDisplayNode()
      if displayNode.GetInterpolate() == 0:
         self.setInterpolateCheckbox.setCheckState(0)
      else:
         self.setInterpolateCheckbox.setCheckState(2)
    
       
      
  #Load Binfo in Slicer
  def loadBinfo(self,filePath):
     filePrefix, fileExtension = os.path.splitext(filePath)
     if not fileExtension == ".binfo":
        print "Error, file not a binfo file: " + filePath
     self.voiComboBox.clear()
     self.motionStateComboBox.clear() 
     binfo = LoadCTXLib.Binfo()
     binfo.readFile(filePath)
     self.binfoList.append(binfo)
     
     #

     #Create segmentation node for this binfo
     segmentationNode = slicer.vtkMRMLSegmentationNode()
     name = slicer.mrmlScene.GenerateUniqueName(os.path.basename(filePrefix))
     segmentationNode.SetName(name)
     slicer.mrmlScene.AddNode(segmentationNode)
     
     binfo.segmentationNode = segmentationNode
     self.selectSegmentation.setCurrentNode(segmentationNode)
     self.setBinfoFile(segmentationNode)
     
     displayNode = slicer.vtkMRMLSegmentationDisplayNode()
     slicer.mrmlScene.AddNode(displayNode)
     segmentationNode.SetAndObserveDisplayNodeID(displayNode.GetID())
     
     displayNode.SetAllSegmentsVisibility2DFill(False)
     displayNode.SetSliceIntersectionThickness(3)
     
     storageNode = slicer.vtkMRMLSegmentationStorageNode()
     slicer.mrmlScene.AddNode(storageNode)
     segmentationNode.SetAndObserveStorageNodeID(storageNode.GetID())
     
  def onLoadButton(self): 
    loadFileName = qt.QFileDialog()
    filePathList=loadFileName.getOpenFileNames(None,"Select Binfo File","","Binfo (*.binfo)")
    for filePath in filePathList:
      self.loadBinfo(filePath)


  def setBinfoFile(self, segmentationNode):
    self.voiComboBox.clear()
    self.motionStateComboBox.clear()
    if segmentationNode == None:
       return
       
    binfo = self.findBinfoForSegmentation(segmentationNode)
    if binfo == None:
       print "Can't find binfo for " + segmentationNode.GetName()
       return

    #self.binfoListFile.setCurrentIndex[binfoNumber]
    voiNames = binfo.get_voi_names()
    if voiNames == []:
       print "No names in " + binfo.name
    else:
       for voiName in voiNames:
         voi = binfo.get_voi_by_name(voiName)
         self.voiComboBox.addItem(voiName)
         self.setMotionStates(voi)
          
    self.voiComboBox.enabled = True
    self.motionStateComboBox.enabled = True
    self.show3DButton.enabled = True

  
  def setMotionStatesFromComboBox(self,voiName):
    segmentationNode = self.selectSegmentation.currentNode()
    if segmentationNode == None:
       return
    binfo = self.findBinfoForSegmentation(segmentationNode)
    if binfo == None:
       print "Can't get binfo for " + segmentationNode.GetName()
    voi = binfo.get_voi_by_name(voiName)
    self.setMotionStates(voi)
  
  
  #Find out motion states from binfo file
  def setMotionStates(self,voi): 
    if voi is None:
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
    segmentationNode = self.selectSegmentation.currentNode()
    binfo = self.findBinfoForSegmentation(segmentationNode)
    
    if binfo == None:
       print "Can't get binfo for " + segmentationNode.GetName()
       
    filePrefix, fileExtension = os.path.splitext(binfo.filePath)
    voi = binfo.get_voi_by_name(self.voiComboBox.currentText)
    if not voi:
      print "Error, voi not found."
      return
    filePath = filePrefix + voi.name + ".nrrd"
    logic = LoadCTXLightLogic()
    n=self.motionStateComboBox.currentIndex
    voi.slicerNodeID[n]=logic.loadVoi(filePath,segmentationNode, motionState=n,voi=voi)

  def onCalculateMotionButton(self):
     segmentationNode = self.selectSegmentation.currentNode()
     binfo = self.findBinfoForSegmentation(segmentationNode)
    
     if binfo == None:
       print "Can't get binfo for " + segmentationNode.GetName()
     voi = binfo.get_voi_by_name(self.voiComboBox.currentText)
     logic = LoadCTXLightLogic()
     logic.calculateMotion(voi, binfo, segmentationNode, axisOfMotion = False, showPlot = True)
 
    
  def onSetDoseColorButton(self):
    logic = LoadCTXLightLogic()
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
    
  def onSetInterpolateCheckbox(self):
     doseNode = self.selectVolume.currentNode()
     doseDisplayNode = doseNode.GetDisplayNode()
     if self.setInterpolateCheckbox.checkState() == 0:
        doseDisplayNode.InterpolateOff()
     else:
        doseDisplayNode.InterpolateOn()
  
  def onChangePyhsDoseCheckBox(self):
    if self.pyhsDoseCheckBox.checkState() == 0:
      self.optDoseBox.setValue(25)
      self.optDoseBox.enabled = True
    else:
      self.optDoseBox.setValue(1000)
      self.optDoseBox.enabled = False

  def onSetVectorFieldButton(self):
    logic = LoadCTXLightLogic()
    vectorNode = self.selectVolume.currentNode()
    if not vectorNode:
      print "No vector field."
      return
    logic.setVectorField(vectorNode)
  
  
  def onSaveScreenShotButton(self):
     filePath = qt.QFileDialog().getSaveFileName(None,"Save Screenshot","","png (*.png)")
     filePrefix, fileExtension = os.path.splitext(filePath)
     if not fileExtension == ".png":
        filePath = filePrefix + ".png"

     name =  os.path.basename(filePrefix)
     
     logic = LoadCTXLightLogic()
     logic.saveScreenshot(name,filePath,"Screenshot")
     print "Screenshot saved to " + filePath
     
  def findBinfoForSegmentation(self, segmentationNode):
    if segmentationNode == None:
       print "No segmentation"
       return None
    for binfo in self.binfoList:
       if binfo.segmentationNode.GetID() == segmentationNode.GetID():
          return binfo
    return None

#
# LoadCTXLightLogic
#

class LoadCTXLightLogic:
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
    
    binaryLabelmapReprName = vtkSegmentationCore.vtkSegmentationConverter.GetSegmentationBinaryLabelmapRepresentationName()
    segLogic = slicer.modules.segmentations.logic()
    segLogic.SetMRMLScene(slicer.mrmlScene)
    voi.slicerNodeID[motionState]=None
    
    if not filePath or not os.path.isfile(filePath):
      #Try to execute hed2nrrd.sh
      filePrefix, fileExtension = os.path.splitext(filePath)
      hed2nrrd = "/u/motion/share/bin/hed2nrrd.sh"
      dirName = os.path.dirname(os.path.realpath(filePath) )
      if os.path.isfile(hed2nrrd):
         #If you have write access, nrrd file is created
         if os.access(dirName, os.W_OK):
            os.system(hed2nrrd + " " + dirName)
         else:
            print "No write access to " + dirName +"\n Either create .nrrd files or get write permission."
            
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
       colorIndex = colorNode.GetColorIndexByName("region 11")
       
    if not colorNode.GetColor(colorIndex,color):
       print "Can't set color for " + voi.name.lower()
       color = [0,0,0,1]

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
    
    return slicerVolume.GetID()

  
  def calculateMotion(self, voi, binfo, segmentationNode, axisOfMotion = False, showPlot = True):
    # logging.info('Processing started')

    origins = np.zeros([3, voi.N_of_motion_states-1])
    relOrigins = np.zeros([4, voi.N_of_motion_states-1])
    minmaxAmplitudes = [[-1e3, -1e3, -1e3], [1e3, 1e3, 1e3]]
    amplitudes = [0, 0, 0]

    refPhase = 5
    exportTrafo = False

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
    # Plot
    if showPlot:
      self.plotMotion(relOrigins, voi.name)

    #Export origins to trafo for tracking
    if exportTrafo:
      dirPath = "/u/kanderle/AIXd/Data/CNAO/Liver/CenterOfMass_Demons/"
      for i in range(0,voi.N_of_motion_states-1):
         fileName = "Liver_COM_D_0" + str(i) + "_0" + str(refPhase) +".aff"
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
         
         fileName = "Liver_COM_D_0" + str(refPhase) +"_0" + str(i) + ".aff"
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
       
  def getCenterOfMass(self,contour):
      comFilter = vtk.vtkCenterOfMass()
      comFilter.SetInputData(contour)
      comFilter.SetUseScalarsAsWeights(False)
      comFilter.Update()
      return comFilter.GetCenter()
  
  def plotMotion(self, relOrigins, contourName):
    ln = slicer.util.getNode(pattern='vtkMRMLLayoutNode*')
    ln.SetViewArrangement(ln.SlicerLayoutOneUpQuantitativeView )

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
      slicerVolumeDisplay.SetThreshold(0.005*optDose,1200)
      slicerVolumeDisplay.ApplyThresholdOn()
    else:
      print "No display node for:"+doseNode.GetName()
      return
  
  def setVectorField(self, vectorNode):
    spacing = vectorNode.GetSpacing()
    
    vectorArray = slicer.util.array(vectorNode.GetID())
    
    for i in range(0,3):
      vectorArray[:,:,:,i] = vectorArray[:,:,:,i] * spacing[i]
    vectorNode.GetImageData().Modified()
    print "Finshed!"
 
        
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


class LoadCTXLightTest(ScriptedLoadableModuleTest):
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
    self.test_LoadCTXLight1()

  def test_LoadCTXLight1(self):
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
    logic = LoadCTXLightLogic()
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

#class LoadCTXLightSlicelet(Slicelet):
  #""" Creates the interface when module is run as a stand alone gui app.
  #"""

  #def __init__(self):
    #super(LoadCTXLightSlicelet,self).__init__(LoadCTXLightWidget)


#if __name__ == "__main__":
  ## TODO: need a way to access and parse command line arguments
  ## TODO: ideally command line args should handle --xml

  #import sys
  #print( sys.argv )

#slicelet = LoadCTXLightSlicelet()
