import os, re
import unittest
from __main__ import vtk, qt, ctk, slicer
import numpy as np
import pytrip
import time

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
   
    
    
    # File Name
    self.fileName = qt.QLineEdit()     
    self.fileName.setToolTip( "Input file" )
    self.fileName.text = ''
    parametersFormLayout.addRow("Loaded file:", self.fileName)

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

    # connections
    self.showButton.connect('clicked(bool)', self.onShowButton)
    self.loadButton.connect('clicked(bool)', self.onLoadButton)
    self.voiComboBox.connect('currentIndexChanged(QString)', self.setMotionStates)


    # Add vertical spacer
    self.layout.addStretch(1)
    
    # Binfo file:
    #binfo=Binfo()
    self.binfo = []
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
    filePath=loadFileName.getOpenFileName()
    filePrefix, fileExtension = os.path.splitext(filePath)
    #Check for different extensions
    if fileExtension == ".ctx":
      fileInfo = 0
      self.ctx = logic.loadCube(filePath,fileInfo)
    elif fileExtension == ".dos":
      fileInfo = 1
      self.dos = logic.loadCube(filePath,fileInfo)
    elif fileExtension == ".cbt":
      fileInfo = 3
      self.cbt = logic.loadCube(filePath,fileInfo)
    #Binfo is special case.  
    elif fileExtension == ".binfo":
      self.binfo = []
      self.voiComboBox.clear()
      self.motionStateComboBox.clear()
      self.fileName.text=filePath   
      binfo = Binfo()
      binfo.readFile(filePath)
      self.binfo = binfo
      
      for voi in binfo.get_voi_names():
        self.voiComboBox.addItem(voi)
        self.setMotionStates(voi)
        
      self.voiComboBox.enabled = True
      self.motionStateComboBox.enabled = True   
    else:
      if not filePath == '':
        qt.QMessageBox.critical(
          slicer.util.mainWindow(),
          'Load TRiP Cube', 'Unknown file type: ' + fileExtension)
      return
      

  #Find out motion states from binfo file
  def setMotionStates(self,voiName):
    voi=self.binfo.get_voi_by_name(voiName)
    if voi is not None:
      self.motionStateComboBox.clear()
      motionStates=voi.N_of_motion_states
      for i in range(0,motionStates):
        self.motionStateComboBox.addItem(voi.motionStateDescription[i])
    else:
      print "Error, can't find voi."

  
  #Load voi from binfo file
  def onShowButton(self):
    binfo=self.binfo
    filePrefix, fileExtension = os.path.splitext(binfo.filePath)
    voi = binfo.get_voi_by_name(self.voiComboBox.currentText)
    if not voi:
      print "Error, voi not found."
      return
    filePath = filePrefix + voi.name + ".ctx"
    logic = LoadCTXLogic()
    n=self.motionStateComboBox.currentIndex
    voi.slicerNodeID[n]=logic.loadCube(filePath,2,motionState=n,voi=voi,ctx=self.ctx)
    self.fileName.text=filePath
      #self.confirmBox(("Loaded file: "+filePath))

      
  #def confirmBox(self,message):
    #self.confirmBox = qt.QMessageBox()
    #self.label = qt.QLabel(message,self.confirmBox)
    #self.infoLayout = qt.QVBoxLayout()
    #self.infoLayout.addWidget(self.label)
    #self.confirmBox.show()
    
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

  def hasImageData(self,volumeNode):
    """This is a dummy logic method that 
    returns true if the passed in volume
    node has valid image data
    """
    if not volumeNode:
      print('no volume node')
      return False
    if volumeNode.GetImageData() == None:
      print('no image data')
      return False
    return True

  def delayDisplay(self,message,msec=1000):
    #
    # logic version of delay display
    #
    print(message)
    self.info = qt.QDialog()
    self.infoLayout = qt.QVBoxLayout()
    self.info.setLayout(self.infoLayout)
    self.label = qt.QLabel(message,self.info)
    self.infoLayout.addWidget(self.label)
    qt.QTimer.singleShot(msec, self.info.close)
    self.info.exec_()

  
  def run(self,inputVolume,outputVolume,enableScreenshots=0,screenshotScaleFactor=1):
    """
    Run the actual algorithm
    """

    self.delayDisplay('Running the aglorithm')

    return True
  
        
  def loadCube(self,filePath,fileInfo,motionState=0,voi=None, ctx=None, optDose = 25):
    
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
    
    #pbar = self.progressBar(("Loading file: "+filePath))
    #pbar.setValue(10)
    #pbar.show()
    
    if not filePath:
      print "No file!"
      return False
    #Find out cube type
          
    fileName, fileExtension = os.path.splitext(filePath)
    
    #Read cube using PyTRiP
    if fileInfo==0 or fileInfo==2:
      pyTRiPCube=pytrip.CtxCube()
      pyTRiPCube.read(filePath)
    elif fileInfo==1:
      pyTRiPCube=pytrip.DosCube()
      pyTRiPCube.read(filePath)
    #Prepare three cubes for reading cbt files
    elif fileInfo==3:
      fileNamePrefix = fileName[0:len(fileName)-2]
      pyTRiPCube = pytrip.CtxCube() #cube x is without index for setting dimension and name
      pyTRiPCube_y = pytrip.CtxCube()
      pyTRiPCube_z = pytrip.CtxCube()
      pyTRiPCube.read(fileNamePrefix+"_x"+fileExtension)
      pyTRiPCube_y.read(fileNamePrefix+"_y"+fileExtension)
      pyTRiPCube_z.read(fileNamePrefix+"_z"+fileExtension)
    else:
      print "Unknown extension type" + str(fileExtension)
      return False
    
    
    
    #Set Dimensions
    dim=(pyTRiPCube.dimx,pyTRiPCube.dimy,pyTRiPCube.dimz)
    
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
      
    #pbar.setValue(20)

    #Read the transfer bit in binfo file
    if fileInfo==2:
      print "Motion state " + str(motionState) + " on bit: " + str(len(voi.motionStateBit))
      TRiPCube=(TRiPCube>>voi.motionStateBit[motionState]) & 1
      #if voi is not None:
	#TRiPCube = voi.voiNumber * np.array(TRiPCube)
	  
    #pbar.setValue(50)
    #Set cube to int
    #if not pyTRiPCube.data_type=='integer':
      #print "Converting data type to int"
      #TRiPCube=np.uint16(np.array(TRiPCube)*1000)
      ##TRiPCube=np.uint16(TRiPCube)
    ##if pyTRiPCube.num+bytes = 2
    #else:
      #TRiPCube=np.uint16(TRiPCube)
 
    ##Convert numpy array to vtk data
    #importer=vtk.vtkImageImport()
    #importer.CopyImportVoidPointer(TRiPCube,TRiPCube.nbytes)
    #importer.SetDataExtent(0,dim[0]-1,0,dim[1]-1,0,dim[2]-1)
    #importer.SetWholeExtent(0,dim[0]-1,0,dim[1]-1,0,dim[2]-1)
    #if fileInfo is not 3:
      #importer.SetNumberOfScalarComponents(1)
      #slicerVolume = slicer.vtkMRMLScalarVolumeNode()
    #else:
      #importer.SetNumberOfScalarComponents(3)
      #slicerVolume = slicer.vtkMRMLVectorVolumeNode()
      
    ##Convert numpy array to vtk data  
    importer=vtkImageImportFromArray()
    if fileInfo is not 3:
      importer.SetArray(TRiPCube)
      slicerVolume = slicer.vtkMRMLScalarVolumeNode()
    else:
      importer.SetArray(TRiPCube,numComponents=3)
      slicerVolume = slicer.vtkMRMLVectorVolumeNode()
    
    
    #TODO: Should I also add a visualization node?
    #Set vtkImageData to Slicer Volume & set all atributes    
    slicer.mrmlScene.AddNode( slicerVolume )
    imageData = importer.GetOutput()
    imageData.SetSpacing(pyTRiPCube.pixel_size,pyTRiPCube.pixel_size,pyTRiPCube.slice_distance)
    #Set origin for vois in binfo files
    if fileInfo == 2:
      if voi:
        imageData.SetOrigin(voi.getSlicerOrigin())
        slicerVolume = self.convertLabelMapToClosedSurfaceModel(imageData = imageData)
      else:
        slicerVolume.SetAndObserveImageData(imageData)   
    #slicerVolume.SetSpacing(pyTRiPCube.pixel_size,pyTRiPCube.pixel_size,pyTRiPCube.slice_distance)
    
    #Set ijttoras matrix
    
    #TODO: A lahko to naredis za imageData?
    matrix = vtk.vtkMatrix4x4()
    matrix.DeepCopy((-1,0,0,0,0,-1,0,0,0,0,1,0,0,0,0,1))
    slicerVolume.SetIJKToRASDirectionMatrix(matrix)

    #pbar.setValue(70)
	#newOrigin=voi.getSlicerOrigin()
	#newOrigin[0]=newOrigin[0]-dim[0]*pyTRiPCube.pixel_size
	#newOrigin[1]=newOrigin[1]-dim[1]*pyTRiPCube.pixel_size
	
    #if fileInfo == 2:
      #cliNode = self.changeScalarVolumeType(slicerVolume,volumeScalarType = 'UnsignedChar')
      #n=0
      #while not (cliNode.GetStatusString()=="Completing" or cliNode.GetStatusString()=="Completed" or cliNode.GetStatusString()=='Completed with errors'):
	#print("Wait!"+str(n))
	#print cliNode.GetStatusString()	      
        #time.sleep(5)
        #n+=1
        #if n>100:
	  #return False
          #break
    if fileInfo == 2
      slicerVolume.SetLabelMap(1)
      self.converLabelMapToClosedSurfaceModel(imageData = imageData)
      #displayNode = slicerVolume.GetDisplayNode()
      #if displayNode:
        #colorNode = displayNode.GetColorNode()
        #if colorNode:
          #labelValue = colorNode.GetColorName(labelIndex)
      #return "%s (%d)" % (labelValue, labelIndex)
      
  #This code is partially copied from SlicerRT module Contours.
  def convertLabelMapToClosedSurfaceModel(self, labelMapNode=None, imageData=None):
    if labelMapNode is None and imageData is None:
      print "No input labelMap or image Data"
      return
    if imageData is None:
      imageData = labelMapNode.GetImageData()
    
    marchingCubes = vtk.vtkMarchingCubes() 
    marchingCubes.SetInput(imageData)
    marchingCubes.SetNumberOfContours(1)
    marchingCubes.SetValue(1,1)
    marchingCubes.ComputeGradientsOff()
    marchingCubes.ComputeNormalsOff()
    marchingCubes.ComputeScalarsOff()
    marchingCubes.Update()
    if marchingCubes.GetOutput().GetNumberOfPolys() < 0:
      print "Can't create Model."
      return None
    decimate = vtk.vtkDecimatePro()
    decimate.SetInput(marchingCubes.GetOutput())
    decimate.SetFeatureAngle(60)
    decimate.SplittingOff()
    decimate.PreserveTopologyOn()
    decimate.SetMaximumError(1)
    decimate.SetTargetReduction(1)
    decimate.Update
    
  
    
    #Check if name exist
    if fileInfo == 2:
      slicerName = pyTRiPCube.patient_name+"_"+str(motionState)
    elif fileInfo == 3:
      slicerName = os.path.basename( fileNamePrefix )
    else:
      slicerName=pyTRiPCube.patient_name
    n=0    
    slicerName = slicer.mrmlScene.GenerateUniqueName(slicerName)         
    slicerVolume.SetName(slicerName)
    
      
   # make the output volume appear in all the slice views
    if fileInfo>0:
      background=True
    else:
      background=False
     
    self.setSliceDisplay(slicerVolume,background)
        
         
    #Set dose values to float for normalization and calculations
    if pyTRiPCube.data_type=='integer' and fileInfo == 1:
      cliNode = self.changeScalarVolumeType(slicerVolume)
      n=0
      while not (cliNode.GetStatusString()=="Completing" or cliNode.GetStatusString()=="Completed" or cliNode.GetStatusString()=='Completed with errors'):
	print("Wait!"+str(n))
	print cliNode.GetStatusString()	      
        time.sleep(5)
        n+=1
        if n>100:
	  return False
          break
    volumeArray = slicer.util.array(slicerVolume.GetID())
    if fileInfo is 1:
      print "Normalizing dose volume" + str(optDose)
      volumeArray[:] = volumeArray[:]*100/optDose


    
    slicerVolume.GetImageData().Modified()
    #pbar.setValue(100)
            
    #Set color of dose volume
    if fileInfo>0:
      #TODO: Display doseMax on display
      slicerVolumeDisplay=slicerVolume.GetScalarVolumeDisplayNode()
      if slicerVolumeDisplay:
        slicerVolumeDisplay.AutoWindowLevelOff()
        slicerVolumeDisplay.AutoThresholdOff()
        if fileInfo==2:
	  slicerVolumeDisplay.SetThreshold(voi.voiNumber+0.05,voi.voiNumber+0.1)
	  slicerVolumeDisplay.SetAndObserveColorNodeID("vtkMRMLColorTableNodeRandom")
	  slicerVolumeDisplay.SetLevel(voi.voiNumber)
          slicerVolumeDisplay.SetWindow(0.2)
	elif fileInfo==1:
	  #slicerVolumeDisplay.SetThreshold(doseMax*0.1,doseMax*1.1)
	  #TODO: Tole se ne dela?
	  colorNode = slicer.util.getNode('GSI*')
	  if not colorNode:
	    colorNode = self.CreateDefaultGSIColorTable()	    
          slicerVolumeDisplay.SetWindowLevelMinMax(0,110)
          slicerVolumeDisplay.SetAndObserveColorNodeID(colorNode.GetID())
          slicerVolumeDisplay.SetThreshold(1,600)
        slicerVolumeDisplay.ApplyThresholdOn()
      else:
	print "No display node for:"+slicerVolume.GetName()

    #pbar.close()
    return slicerVolume.GetID()
    
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
  def changeScalarVolumeType(self,volumeNode,volumeScalarType = 'Float'):
    parameters = {}
    parameters["InputVolume"] = volumeNode.GetID()
    parameters["OutputVolume"] = volumeNode.GetID()
    parameters["Type"] = volumeScalarType
    castScalarVolume = slicer.modules.castscalarvolume
    return (slicer.cli.run(castScalarVolume, None, parameters))
      
      
  def progressBar(self,message):  
    progressBar = qt.QProgressBar()
    progressBarLayout = qt.QVBoxLayout()
    progressBar.setLayout(progressBarLayout)
    label = qt.QLabel(message,progressBar)
    progressBarLayout.addWidget(label)
    return progressBar
    
  def CreateDefaultGSIColorTable(self):
    colorTableNode = slicer.vtkMRMLColorTableNode()    
    nodeName = "GSI Standard"
    colorTableNode.SetName(nodeName);
    colorTableNode.SetTypeToUser();
    colorTableNode.SetAttribute("Category", "User Generated");
    colorTableNode.HideFromEditorsOn();
    colorTableNode.SetNumberOfColors(256);
    colorTableNode.GetLookupTable().SetTableRange(0,255);
    for i in range(0,256):
      if i<47:
        colorTableNode.AddColor(str(i), 0.06, 0, 1, 0.2);
      elif i<92:
	colorTableNode.AddColor(str(i), 0, 0.94, 1, 0.2);
      elif i<139:
        colorTableNode.AddColor(str(i), 0.02, 0.5, 0, 0.2);
      elif i<185:
        colorTableNode.AddColor(str(i), 0.02, 1, 0, 0.2);
      elif i<220:
        colorTableNode.AddColor(str(i), 1, 1, 0, 0.2);
      elif i<243:
        colorTableNode.AddColor(str(i), 1, 0, 0, 0.2);
      else:
	colorTableNode.AddColor(str(i), 1, 0, 1, 1);

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
    binfo = Binfo()
    binfo.readFile(filePath)
    #vois = binfo.get_voi_names
    voi = binfo.get_voi_by_name('CTV_T50')
    filePath2 = '/u/kanderle/examples/Py/ns_00_Pat122wk0_05CTV_T50.ctx'
    logic.loadCube(filePath2,2,0,voi)
    
    
    self.delayDisplay('Test passed!')
    
class Binfo():
  def __init__(self):
    self.name=''
    self.pixel_size=0
    self.slice_distance=0
    self.dimx=0
    self.dimy=0
    self.dimz=0
    self.vois=[]
    
    self.filePath=''
    
  def readFile(self,filePath):
    self.filePath=filePath
    fp = open(filePath,"r")
    content = fp.read().split('\n')
    fp.close()
    i = 0
    n = len(content)
    voiCount = 1;
    header_full = False
    while(i < n):
      line = content[i]
      if not header_full:
	if re.match("patient",line) is not None:
          self.name = line.split()[1]
        if re.match("geometry",line) is not None:
	  self.pixel_size= float(line.split()[1])
	  self.slice_distance = float(line.split()[3])
          self.dimx = int(line.split()[4])
          self.dimy = int(line.split()[5])
          self.dimz = int(line.split()[6])
      if re.match("binvoi",line) is not None:
        v = Voi(line.split()[1])
        i = v.read_binfo(content,i)
        v.voiNumber = voiCount
        voiCount += 1
        v.setSlicerNodeID()
        #v.setSlicerOrigin(self.dimx,self.dimy,self.pixel_size)
        self.add_voi(v)
        header_full = True
      i += 1
  
  def get_voi_names(self):
        names = []
        for voi in self.vois:
            names.append(voi.name)
        return names
        
  def add_voi(self,voi):
        self.vois.append(voi)
  
  def get_voi_by_name(self,name):
        for voi in self.vois:
            if voi.name.lower() == name.lower():
                return voi
        raise InputError("Voi doesn't exist")
    
class Voi:
  def __init__(self,name):
    self.name=name
    self.N_of_motion_states=0
    self.offsetx=0
    self.offsety=0
    self.offsetz=0
    self.voi_type=''
    self.voiNumber=0
    self.slicerNodeID=[]
    self.motionStateBit=[]
    self.motionStateDescription=[]
    #self.slicerOriginx=0
    #self.slicerOriginy=0
    #self.slicerOriginz=0
    
  def read_binfo(self,content,i):
    line = content[i]
    #self.name = string.join(line.split()[1:],' ')
    if line.split()[3]=='0':
      self.voi_type='OAR'
    else:
      self.voi_type='Target'
    self.offsetx=float(line.split()[5])
    self.offsety=float(line.split()[6])
    self.offsetz=float(line.split()[7])
    i += 1
    while i < len(content):
      line = content[i]
      if re.match("descriptor",line) is not None:
	self.N_of_motion_states += 1
	self.motionStateBit.append(int(line.split()[3]))
	self.motionStateDescription.append(line.split("\"")[3])
      elif re.match("binvoi",line) is not None:
        break
      elif re.match("eof",line) is not None:
        i=len(content)
        break
      i += 1
    return i-1
    
  def setSlicerNodeID(self):
    self.slicerNodeID = [None]*(self.N_of_motion_states+1)
  
  
  #def setSlicerOrigin(self,CTdimx,CTdimy,pixel_size):
    #slicerOffsetX = CTdimx*pixel_size-self.offsetx
    #slicerOffSetY = CTdimy*pixel_size-self.offsety    
    #self.slicerOriginx = slicerOffsetX
    #self.slicerOriginy = slicerOffSetY
    #self.slicerOriginz = self.offsetz
    
  def getSlicerOrigin(self):
    slicerOrigin = [- self.offsetx, - self.offsety,self.offsetz]
    return slicerOrigin
    

#Copyright: http://code.google.com/p/volumetric-defacing/source/browse/defacing/vtkImageImportFromArray.py?r=66b053cb1a157c1a8bb14ba85397ab1c9845deb8&spec=svn90f4995ded9ec2974e255f667c0b8817ce23f9ad
"""
vtkImageImportFromArray: a NumPy front-end to vtkImageImport

Load a python array into a vtk image.
To use this class, you must have NumPy installed (http://numpy.scipy.org/)

Methods:

  GetOutput() -- connect to VTK image pipeline
  SetArray()  -- set the array to load in
 
Convert python 'Int' to vtk.VTK_UNSIGNED_SHORT:
(python doesn't support unsigned short, so this might be necessary)

  SetConvertIntToUnsignedShort(yesno)
  ConvertIntToUnsignedShortOn()
  ConvertIntToUnsignedShortOff()

Methods from vtkImageImport:
(if you don't set these, sensible defaults will be used)

  SetDataExtent()
  SetDataSpacing()
  SetDataOrigin()
"""

class vtkImageImportFromArray:
    def __init__(self):
        self.__import = vtk.vtkImageImport()
        self.__ConvertIntToUnsignedShort = False
        self.__Array = None

    # type dictionary: note that python doesn't support
    # unsigned integers properly!
    __typeDict = {'b':vtk.VTK_CHAR,             # int8
                  'B':vtk.VTK_UNSIGNED_CHAR,    # uint8
                  'h':vtk.VTK_SHORT,            # int16
                  'H':vtk.VTK_UNSIGNED_SHORT,   # uint16
                  'i':vtk.VTK_INT,              # int32
                  'I':vtk.VTK_UNSIGNED_INT,     # uint32
                  'l':vtk.VTK_LONG,             # int64
                  'L':vtk.VTK_UNSIGNED_LONG,    # uint64
                  'f':vtk.VTK_FLOAT,            # float32
                  'd':vtk.VTK_DOUBLE,           # float64
                  }

    # convert 'Int32' to 'unsigned short'
    def SetConvertIntToUnsignedShort(self, yesno):
        self.__ConvertIntToUnsignedShort = yesno

    def GetConvertIntToUnsignedShort(self):
        return self.__ConvertIntToUnsignedShort
   
    def ConvertIntToUnsignedShortOn(self):
        self.__ConvertIntToUnsignedShort = True

    def ConvertIntToUnsignedShortOff(self):
        self.__ConvertIntToUnsignedShort = False

    # get the output
    def GetOutputPort(self):
        return self.__import.GetOutputPort()

    # get the output
    def GetOutput(self):
        return self.__import.GetOutput()

    # import an array
    def SetArray(self, imArray, numComponents = 1):
        self.__Array = imArray
        imString = imArray.tostring()
        dim = imArray.shape

        if (len(dim) == 4):
            numComponents = dim[3]
            dim = (dim[0], dim[1], dim[2])


        typecode = imArray.dtype.char
       
        ar_type = self.__typeDict[typecode]

        if (typecode == 'F' or typecode == 'D'):
            numComponents = numComponents * 2

        if (self.__ConvertIntToUnsignedShort and typecode == 'i'):
            imString = imArray.astype(Numeric.Int16).tostring()
            ar_type = vtk.VTK_UNSIGNED_SHORT
        else:
            imString = imArray.tostring()
           
        self.__import.CopyImportVoidPointer(imString, len(imString))
        self.__import.SetDataScalarType(ar_type)
        self.__import.SetNumberOfScalarComponents(numComponents)
        extent = self.__import.GetDataExtent()
        self.__import.SetDataExtent(extent[0], extent[0] + dim[2] - 1,
                                    extent[2], extent[2] + dim[1] - 1,
                                    extent[4], extent[4] + dim[0] - 1)
        self.__import.SetWholeExtent(extent[0], extent[0] + dim[2] - 1,
                                     extent[2], extent[2] + dim[1] - 1,
                                     extent[4], extent[4] + dim[0] - 1)

    def GetArray(self):
        return self.__Array
       
    # a whole bunch of methods copied from vtkImageImport
    def SetDataExtent(self, extent):
        self.__import.SetDataExtent(extent)

    def GetDataExtent(self):
        return self.__import.GetDataExtent()
   
    def SetDataSpacing(self, spacing):
        self.__import.SetDataSpacing(spacing)

    def GetDataSpacing(self):
        return self.__import.GetDataSpacing()
   
    def SetDataOrigin(self, origin):
        self.__import.SetDataOrigin(origin)

    def GetDataOrigin(self):
        return self.__import.GetDataOrigin()

