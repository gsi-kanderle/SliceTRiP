import os
import unittest
from __main__ import vtk, qt, ctk, slicer

import LoadCTXLib

import numpy as np

#import SaveTRiPLib

#
# SaveTRiP
#

class SaveTRiP:
  def __init__(self, parent):
    parent.title = "Save TRiP Cube" # TODO make this more human readable by adding spaces
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

    # Add this test to the SelfTest module's list for discovery when the module
    # is created.  Since this module may be discovered before SelfTests itself,
    # create the list if it doesn't already exist.
    try:
      slicer.selfTests
    except AttributeError:
      slicer.selfTests = {}
    slicer.selfTests['SaveTRiP'] = self.runTest

  def runTest(self):
    tester = SaveTRiPTest()
    tester.runTest()

#
# qSaveTRiPWidget
#

class SaveTRiPWidget:
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
    self.reloadButton = qt.QPushButton("Reload")
    self.reloadButton.toolTip = "Reload this module."
    self.reloadButton.name = "SaveTRiP Reload"
    reloadFormLayout.addWidget(self.reloadButton)
    self.reloadButton.connect('clicked()', self.onReload)

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

    #
    # Select Scalar Volume
    #
    self.selectNode = slicer.qMRMLNodeComboBox()
    self.selectNode.nodeTypes = ( ("vtkMRMLScalarVolumeNode"),("vtkMRMLVectorVolumeNode"),"" )
    #self.selectNode.addAttribute( "vtkMRMLScalarVolumeNode", "LabelMap", 0 )
    self.selectNode.selectNodeUponCreation = True
    self.selectNode.addEnabled = False
    self.selectNode.removeEnabled = False
    self.selectNode.noneEnabled = True
    self.selectNode.showHidden = False
    self.selectNode.showChildNodeTypes = False
    self.selectNode.setMRMLScene( slicer.mrmlScene )
    self.selectNode.setToolTip( "Select volume to be exported as ctx." )
    parametersFormLayout.addRow("Select volume: ", self.selectNode)
    
        #
    # Select Subject Hierarchy
    #
    self.contourNode = slicer.qMRMLNodeComboBox()
    self.contourNode.nodeTypes = ( ("vtkMRMLSubjectHierarchyNode"),"" )
    #self.contourNode.addAttribute( "vtkMRMLScalarVolumeNode", "LabelMap", 0 )
    self.contourNode.selectNodeUponCreation = True
    self.contourNode.addEnabled = False
    self.contourNode.removeEnabled = False
    self.contourNode.noneEnabled = True
    self.contourNode.showHidden = False
    self.contourNode.showChildNodeTypes = False
    self.contourNode.setMRMLScene( slicer.mrmlScene )
    self.contourNode.enabled = False
    self.contourNode.setToolTip( "Select subject hierarchy to be exported as binFile." )
    parametersFormLayout.addRow("Select hirerachy: ", self.contourNode)
    
    #
    # Show and select data from node in table:
    #
    
    self.table = qt.QTableWidget()
    self.table = qt.QTableWidget()   
    self.table.setColumnCount(1)     
    verticalHeaders=["Patient Name: ","Data type: ","Byte Number: ","Byte Order: ","Pixel size",\
    "Slice distance","X dim:","Y dim: ","Z dim: ","Bin file: ","Cube Type: "]
    self.table.setRowCount(len(verticalHeaders))
    horizontalHeaders=['Value']
    self.table.setHorizontalHeaderLabels(horizontalHeaders)
    self.table.setVerticalHeaderLabels(verticalHeaders)
    parametersFormLayout.addRow(self.table)
    self.table.visible = False
       
    self.tableParameters = None
        
    #
    # Apply Button
    #
    self.exportButton = qt.QPushButton("Export")
    self.exportButton.toolTip = "Run the algorithm."
    self.exportButton.enabled = False
    parametersFormLayout.addRow(self.exportButton)
    
    #
    # Refresh Table Button
    #
    self.refreshTableButton = qt.QPushButton("Refresh Table")
    self.refreshTableButton.toolTip = "Refresh Table."
    self.refreshTableButton.enabled = True
    parametersFormLayout.addRow(self.refreshTableButton)

    # connections
    self.exportButton.connect('clicked(bool)', self.onExportButton)
    self.refreshTableButton.connect('clicked(bool)', self.readData)
    self.selectNode.connect("currentNodeChanged(vtkMRMLNode*)", self.readData)

    # Add vertical spacer
    self.layout.addStretch(1)
    
    self.pytripCube = None
    
    self.extension = ".ctx"

  def cleanup(self):
    pass

  # Read all data from selected node
  def readData(self):
    node = self.selectNode.currentNode()
    saveCubeLogic = SaveTRiPLogic()
    if node:
      self.pytripCube = None
      self.table.clearContents()
      self.pytripCube = saveCubeLogic.getPyTRiPCubeFromNode(node)
      self.setTable()
      self.table.visible = self.selectNode.currentNode()
      self.contourNode.enabled = True
      self.exportButton.enabled = True
      if node.IsA('vtkMRMLVectorVolumeNode'):
	self.tableParameters.cubeType.setCurrentIndex(2)

      
  # Export node into TRiP cube.
  def onExportButton(self):
    #logic = SaveTRiPLogic()
    saveCubeLogic = SaveTRiPLogic()
    loadFileName = qt.QFileDialog()    
    filePath=loadFileName.getExistingDirectory( )
    if filePath is not '':
      self.setParameters()
      node = self.selectNode.currentNode()
      subjectNode = self.contourNode.currentNode()
      if subjectNode:
	saveCubeLogic.writeBinfile(filePath,self.pytripCube,subjectNode,node)
      else:
        saveCubeLogic.writeTRiPdata(filePath,self.pytripCube,extension=self.extension,nodeID = node.GetID())
      
  # Set parameters from table in widget to pytrip cube before exporting
  def setParameters(self):
    tP = self.tableParameters    
    self.pytripCube.patient_name = str(tP.patientName.text().replace(" ","_")) #remove spaces from string
    #self.pytripCube.pixel_size = tP.pixelSize.text
    #self.pytripCube.slice_distance = tP.sliceDistance.text
    #self.pytripCube.dimx = tP.xdim.text
    #self.pytripCube.dimy = tP.ydim.text
    #self.pytripCube.dimz = tP.zdim.text
    self.pytripCube.data_type = tP.dataType.currentText
    self.pytripCube.num_bytes = tP.byteNumber.currentText
    if tP.cubeType.currentText == "CT":
	self.extension = ".ctx"
    elif tP.cubeType.currentText == "Dose":
	self.extension = ".dos"
    elif tP.cubeType.currentText == "Cbt":
	self.extension = ".cbt"
    if self.pytripCube.byte_order == tP.byteOrder.currentText:
	print "No byte swaping."
    else:
	print "Swap bytes to "+ tP.byteOrder.currentText
	self.pytripCube.byte_order = tP.byteOrder.currentText
	self.pytripCube.cube.byteswap()
    
  
  # Create table with parameters obtained from node
  def setTable(self):
    self.tableParameters = None
    tP = TableParameters(self.table)    
    tP.patientName.setText(self.pytripCube.patient_name)  
    self.setComboBoxIndex(tP.dataType,self.pytripCube.data_type)
    self.setComboBoxIndex(tP.byteNumber,self.pytripCube.num_bytes)
    tP.pixelSize.setText(self.pytripCube.pixel_size)
    tP.sliceDistance.setText(self.pytripCube.slice_distance)
    tP.xdim.setText(self.pytripCube.dimx)
    tP.ydim.setText(self.pytripCube.dimy)
    tP.zdim.setText(self.pytripCube.dimz)
    self.tableParameters = tP

  # Looks for string in combobox and set's it to the string's value.
  def setComboBoxIndex(self,combobox, string):
    if combobox.findText(string)<0:
      print "Cannot find string: " + str(string )
      return   
    combobox.setCurrentIndex(combobox.findText(str(string)))
	  
  def onReload(self,moduleName="SaveTRiP"):
    """Generic reload method for any scripted module.
    ModuleWizard will subsitute correct default moduleName.
    """
    globals()[moduleName] = slicer.util.reloadScriptedModule(moduleName)

  def onReloadAndTest(self,moduleName="SaveTRiP"):
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
# SaveTRiPLogic
#

class SaveTRiPLogic:
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

  def getPyTRiPCubeFromNode(self,node):
    # Set pytrip cube
    if node is None:
      print "Error, no input node"
      return None
    
    #if not node.IsA('vtkMRMLVectorVolumeNode') or node.IsA('vtkMRMLScalarVolumeNode'):
      #raise "Can export only Scalar and Vector Volumes"
      
    cube = LoadCTXLib.cube.Cube()
    array = slicer.util.array(node.GetID())
    # Get dimensions and spacing and set it into header
    dim = node.GetImageData().GetDimensions()
    spacing = node.GetSpacing()
    origin = node.GetOrigin()
    
    cube.create_empty_cube(0,dim[0],dim[1],dim[2],spacing[0],spacing[2])

    cube.patient_name = node.GetName()
    cube.xoffset = origin[0]
    cube.yoffset = origin[1]
    cube.zoffset = origin[2]
    cube.slice_pos = []
    cube.z_table = False 
        
    #TODO: Make a 3D cube in pytrip
    
    if node.IsA('vtkMRMLVectorVolumeNode'):
      cube.cube[:] = array[:,:,:,0]#[:,::-1,::-1,0]
    else:
      if node.GetLabelMap():
	print "Converting label map to int32.."
	array = array.astype(np.int32)
	maximum = array.max()
	if not maximum == 0:
	  cube.cube = np.array(array)/maximum
	else:
	#TODO: Tuki mors en error dat, al pa voi vn fuknt.
	  print "Maximum value is 0"
      else:
        cube.cube[:] = array[:]#[:,::-1,::-1]
        
    #Reduce float64 to float32 (we don't need dobule precision)
    if array.dtype == np.float32 or array.dtype == np.float64:
      cube.set_data_type(np.float)
      cube.pydata_type=np.float32
    else:
      if array.dtype == np.int32:
	cube.set_data_type(np.int32)
        cube.pydata_type=np.int32
      else:
        cube.set_data_type(array.dtype)
        cube.pydata_type=array.dtype      
    return cube

  #Function for writing pytrip cube or slicer node into file. Filepath is a path to directory.
  def writeTRiPdata(self, filePath, pytripCube=None, extension='.ctx', nodeID = None, binfoName='',aix = False, resample = []):
    
    if nodeID is not None:
      node = slicer.util.getNode( nodeID )
      print "Node to write:" + node.GetID()
    else:
      node = None
      
    if pytripCube is None and node is not None:
      
      print "Converting slicer node into pytrip cube " + str(node.GetID())
      #Getting vector field from transform node
      if node.IsA('vtkMRMLGridTransformNode') or node.IsA('vtkMRMLBSplineTransformNode'):
	print "Converting Transform Node to Vector Field"
	trans = node.GetTransformFromParent()#.GetConcatenatedTransform(0)
	#trans.Inverse()
	#trans.Update()
	im = trans.GetDisplacementGrid()
	if im is None:
	  print "Can't get image data. " + str(im)
	  return
	  
	vectorVolume = slicer.vtkMRMLVectorVolumeNode()
	slicer.mrmlScene.AddNode( vectorVolume )
	vectorVolume.SetAndObserveImageData( im )
	vectorVolume.SetName( node.GetName() )
	vectorVolume.SetSpacing( im.GetSpacing() )
	
	#vectorVolume.SetOrigin( im.GetOrigin() )
	
	#Get Right Direction For Vector Volume
	#matrix = vtk.vtkMatrix4x4()
	matrix = trans.GetGridDirectionMatrix()
        #matrix.DeepCopy((-1,0,0,0,0,-1,0,0,0,0,1,0,0,0,0,1))
        vectorVolume.SetIJKToRASDirectionMatrix(matrix)
        

        
        if not resample == []:
	  newVectorVolume = self.resampleVectorVolume(vectorVolume,resample)
	  slicer.mrmlScene.RemoveNode(vectorVolume)
	  vectorVolume = newVectorVolume
        
	node = vectorVolume

      pytripCube = self.getPyTRiPCubeFromNode(node)

      if aix:
	pytripCube.byte_order = 'aix'
	pytripCube.cube.byteswap()
      else:
	pytripCube.byte_order = 'vms'

    if pytripCube is None:
      if node is None:
        print "Input slicer node or pytrip Cube!"
        return
      else:
	print "Cannot create/find pytripCube"
	return

    if not filePath[-1] == '/':
      filePath += '/'
    fName = str(filePath)+binfoName+ pytripCube.patient_name
    if node is not None:
      if node.IsA('vtkMRMLVectorVolumeNode'):
        if not extension == '.cbt':
	  print "Error, vector volume can be exported only as .cbt (no: "+extension+" )"
	  return
        array = slicer.util.array(node.GetID())
        
        #Change precision from double to float
        if array.dtype == np.float64:
	  array = array.astype(np.float32)

        if pytripCube.byte_order == 'aix':
	  print "Changing array to aix byte order."
	  array.byteswap()
	pName = pytripCube.patient_name
        for i in range(0,3):
	  # Vector field components in cbt are divided with voxel spacing due to historical reasons.
	  if i == 2:
	      pytripCube.cube = np.array(array[:,:,:,i])/pytripCube.slice_distance
	  else:
	    if nodeID.find('GridTransform') > -1:
	      print "Changing sign"
	      pytripCube.cube = -np.array(array[:,:,:,i])/pytripCube.pixel_size
	    else:
	      pytripCube.cube = np.array(array[:,:,:,i])/pytripCube.pixel_size
	    
	  #if i == 2:
	    #print "Converting vector components."
	    #pytripCube.cube = np.array(array[:,:,:,i]/pytripCube.slice_distance
	  #elif i < 2:
	    #pytripCube.cube = np.array(array[:,:,:,i]/pytripCube.pixel_size
	  #pytripCube.cube = array
	  if i==0:
	    fNameNew = fName + "_x"
	    pytripCube.patient_name = pName + "_x"
	  elif i==1:
	    fNameNew = fName + "_y"
	    pytripCube.patient_name = pName + "_y"
	  elif i==2:
	    fNameNew = fName + "_z"
	    pytripCube.patient_name = pName + "_z"
	  print("Saving: "+fNameNew)
	  pytripCube.write_trip_data(fNameNew+extension)
          pytripCube.write_trip_header(fNameNew+".hed")
        if nodeID.find('GridTransform') > -1:
          slicer.mrmlScene.RemoveNode(vectorVolume)
      elif node.IsA('vtkMRMLScalarVolumeNode'):
	pytripCube.write_trip_data(fName+extension)
        pytripCube.write_trip_header(fName+".hed")
    else:
      if extension == '.cbt':
	print "Error, input is not vector volume for exporting cbt."
	return
      pytripCube.write_trip_data(fName+extension)
      pytripCube.write_trip_header(fName+".hed")
      
    print("Saved: "+fName+extension)
  
  
  
  def resampleVectorVolume(self,vectorVolume,resample):
      if not vectorVolume or not vectorVolume.IsA('vtkMRMLVectorVolumeNode'):
        print "No vector volume for resampling."
        return
      
      if resample == []:
	print "No resample values."
	return
	
      if not len(resample) == 3:
        print "Too many values for resampling."
        return
      
      oldVectorVolume = vectorVolume
      
      #Create new vector volume
      newVectorVolume = slicer.vtkMRMLVectorVolumeNode()
      newVectorVolume.SetName(oldVectorVolume.GetName())
      slicer.mrmlScene.AddNode(newVectorVolume)
      
      newStorageNode = newVectorVolume.CreateDefaultStorageNode()
      newVectorVolume.SetAndObserveStorageNodeID(newStorageNode.GetID())
      
      #Create strings for resampling
      spacing = ''
      size = ''
      for i in range(0,len(resample)):
        spacing += str(oldVectorVolume.GetSpacing()[i]*resample[i])
        #extent = oldVectorVolume.GetImageData().GetExtent[2*i+1]
        extent = oldVectorVolume.GetImageData().GetExtent()[2*i+1]+1
        size += str(extent/resample[i])
        if i < 2:
	  spacing += ','
	  size += ','

      print "Resampling " + oldVectorVolume.GetName() + " to new pixel size " + size 
      
      #Set parameters
      parameters = {} 
      parameters["inputVolume"] = oldVectorVolume.GetID()
      parameters["outputVolume"] = newVectorVolume.GetID()
      parameters["referenceVolume"] = ''
      parameters["outputImageSpacing"] = spacing
      parameters["outputImageSize"] = size
      
      #Do resampling
      resampleScalarVolume = slicer.modules.resamplescalarvectordwivolume
      clNode = slicer.cli.run(resampleScalarVolume, None, parameters, wait_for_completion=True)
      
      #Remove old vector node and set new:
      return newVectorVolume
  
  # Looks at the subject hierarchy node and loops through all child nodes
  def writeBinfile(self,filePath,pytripCube,node,referenceNode):
    
    # First we create binfo class and fill it with values
    binfo = Binfo(pytripCube)
    
    # Loop through nodes.
    node.GetAssociatedChildrenNodes(binfo.vtkCollection)
    childContourNodes = binfo.vtkCollection
    childContourNodes.InitTraversal()
    refExtent = referenceNode.GetImageData().GetExtent()
    if childContourNodes.GetNumberOfItems < 1:
      print "Error, Selected Subject Hiearchy doesn't have any child contour nodes."   
    for i in range(0,childContourNodes.GetNumberOfItems()):
      contourNode = childContourNodes.GetItemAsObject(i)
      #Rename contours.
      index = contourNode.GetName().find("_Contour")
      contourName = contourNode.GetName()[0:index]
      contourName = contourName.replace(" ","_")
      
      voi = Voi(contourName)
      binfo.add_voi(voi)
      
      #Change voi to labelmap, which is Scalar Volume and we can export it as ctx.
      print "Changing " + contourNode.GetName() + " to labelmap. " + str(i+1) + "/" + str(childContourNodes.GetNumberOfItems())
      if contourNode.GetIndexedLabelmapVolumeNodeId() is None:
        contourNode.SetAndObserveRasterizationReferenceVolumeNodeId(referenceNode.GetID())
        contourNode.SetRasterizationOversamplingFactor(1.0)
        labelmapNode = contourNode.GetIndexedLabelmapVolumeNode()
        contourExtent = labelmapNode.GetImageData().GetExtent()
      #Somtimes conversion to labelmap adds pading, we need same extents. Code copied from SlicerRT.
        if not contourExtent == refExtent:
	  print "Extents not the same for: " + contourNode.GetName()
	  self.resampleInputVolumeNodetoReferenceVolumeNode(labelmapNode, referenceNode, labelmapNode)	  
      else:
	labelmapNode = contourNode.GetIndexedLabelmapVolumeNode()

  
      #Crop labelmap if necessary
      outputVolume = None
      if slicer.util.getNode('R'):
	print "Cropping " + labelmapNode.GetName()
        volumesLogic = slicer.modules.volumes.logic()
        cropVolumeLogic = slicer.modules.cropvolume.logic()
        outputVolume = volumesLogic.CloneVolume( slicer.mrmlScene, labelmapNode, labelmapNode.GetName() + '-subvolume' )
        ROInode = slicer.util.getNode('R')
        cropVolumeLogic.CropVoxelBased(ROInode,labelmapNode,outputVolume)
        labelmapNode = outputVolume

      # Create pytrip cube and save it
      pytripContourCube = self.getPyTRiPCubeFromNode(labelmapNode)
      
      #Change byte order
      pytripContourCube.byte_order = 'aix'
      pytripContourCube.cube.byteswap()
      pytripContourCube.patient_name = contourName
      #pytripContourCube.patient_name = binfo.name + contourName
      self.writeTRiPdata(filePath, pytripContourCube, binfoName = binfo.name)
      
      #Remove croped labelmap if exist:
      if outputVolume:
	slicer.mrmlScene.RemoveNode(outputVolume)
      
    
    #Create and save binfo file.
    binfoFilePath = filePath +"/" + binfo.name + ".binfo"
    binfo.writeBinfile(binfoFilePath)  
  
   #
   # This function is copied from SlicerRT
   #
  def resampleInputVolumeNodetoReferenceVolumeNode(self, inputVolumeNode, referenceVolumeNode, outputVolumeNode):
    if not inputVolumeNode or not referenceVolumeNode or not outputVolumeNode:
      print "Volumes not initialized."
      return
    inputVolumeIJK2RASMatrix = vtk.vtkMatrix4x4()
    inputVolumeNode.GetIJKToRASMatrix(inputVolumeIJK2RASMatrix)
    referenceVolumeRAS2IJKMatrix = vtk.vtkMatrix4x4()
    referenceVolumeNode.GetRASToIJKMatrix(referenceVolumeRAS2IJKMatrix)
    dimensions = referenceVolumeNode.GetImageData().GetDimensions()

    outputVolumeResliceTransform = vtk.vtkTransform()
    outputVolumeResliceTransform.Identity()
    outputVolumeResliceTransform.PostMultiply()
    outputVolumeResliceTransform.SetMatrix(inputVolumeIJK2RASMatrix)

    if inputVolumeNode.GetTransformNodeID() is not None:
      inputVolumeNodeTransformNode = slicer.util.getNode(inputVolumeNode.GetTransformNodeID())
      inputVolumeRAS2RASMatrix = vtk.vtkMatrix4x4()
      if inputVolumeNodeTransformNode is not None:
        inputVolumeNodeTransformNode.GetMatrixTransformToWorld(inputVolumeRAS2RASMatrix)
        outputVolumeResliceTransform.Concatenate(inputVolumeRAS2RASMatrix)
      
    outputVolumeResliceTransform.Concatenate(referenceVolumeRAS2IJKMatrix)
    outputVolumeResliceTransform.Inverse()

    resliceFilter = vtk.vtkImageReslice()
    resliceFilter.SetInput(inputVolumeNode.GetImageData())
    resliceFilter.SetOutputOrigin(0, 0, 0)
    resliceFilter.SetOutputSpacing(1, 1, 1)
    resliceFilter.SetOutputExtent(0, dimensions[0]-1, 0, dimensions[1]-1, 0, dimensions[2]-1)
    resliceFilter.SetResliceTransform(outputVolumeResliceTransform)
    resliceFilter.Update()

    outputVolumeNode.CopyOrientation(referenceVolumeNode)
    outputVolumeNode.SetAndObserveImageData(resliceFilter.GetOutput())
    return
  
  def run(self):
    """
    Run the actual algorithm
    """

    self.delayDisplay('Running the aglorithm')

    self.enableScreenshots = enableScreenshots
    self.screenshotScaleFactor = screenshotScaleFactor

    self.takeScreenshot('SaveTRiP-Start','Start',-1)

    return True


class SaveTRiPTest(unittest.TestCase):
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
    self.test_SaveTRiP1()

  def test_SaveTRiP1(self):
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
    logic = SaveTRiPLogic()
    self.assertTrue( logic.hasImageData(volumeNode) )
    self.delayDisplay('Test passed!')

    
class Binfo():
  def __init__(self,pytripCube):
    self.name = pytripCube.patient_name
    self.pixel_size = pytripCube.pixel_size
    self.slice_distance = pytripCube.slice_distance
    self.dimx = pytripCube.dimx
    self.dimy = pytripCube.dimy
    self.dimz = pytripCube.dimz
    self.vois=[]
    self.vtkCollection = vtk.vtkCollection()    
    self.filePath=''
    
  def readFile(self,filePath):
    self.filePath=filePath
    fp = open(filePath,"r")
    content = fp.read().split('\n')
    fp.close()
    i = 0
    n = len(content)
    voiCount = 1
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
      
  def writeBinfile(self,filePath):
    output_str = "# binvoi infofile\n"
    output_str += "## Format:\n"
    output_str += "## lines preceeded by # are comments\n"
    output_str += "## \"patient\" <patient_name>\n"
    output_str += "## \"geometry\" <voxel_size_x> <voxel_size_y> <voxel_size_z> <dim_x> <dim_y> <dim_z>\n"
    output_str += "## \"binvoi\" <volume_name> <tissue_type> <lVdxType> <ulFlag> <subcube_positionvector> <updatewdwfrombit>\n"
    output_str += "## \"descriptor\" <volume_name> bit <bitnumber> <bitusage> <bitstates> <bitname> <bitdesc>\n"
    output_str += "patient " + self.name + "\n"
    output_str += ("geometry " + str(self.pixel_size) +" "+ str(self.pixel_size)+" " 
               + str(self.slice_distance)+" " + str(self.dimx)+" " + str(self.dimy)+" " + str(self.dimz) + "\n")
    for i in range(0,self.vtkCollection.GetNumberOfItems()):
      voi = self.vois[i]
      output_str += "binvoi " + voi.name + " " + voi.name +" 0 272 0 0 0 0\n"
      output_str += "descriptor " + voi.name + " bit 0 1 0 \"DEFAULT\" \"3D reference state\"\n"
    
    output_str += "# eof"
    f = open(filePath,"wb+")
    f.write(output_str)
    f.close()
  
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
    self.labelmapNode = None
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

    
    
    
class TableParameters:
  def __init__(self,table):
    #Set Data type
    self.dataType = qt.QComboBox()
    self.dataType.addItem("integer")
    self.dataType.addItem("float")
    self.dataType.addItem("double")
    
    table.setCellWidget(1,0,self.dataType)
    
    #Set Byte Number:
    self.byteNumber = qt.QComboBox()
    self.byteNumber.addItem("4")
    self.byteNumber.addItem("1")
    self.byteNumber.addItem("2")
    self.byteNumber.addItem("8")
    
    table.setCellWidget(2,0,self.byteNumber)
    
    #Set Byte Order
    self.byteOrder = qt.QComboBox()
    self.byteOrder.addItem("vms")
    self.byteOrder.addItem("aix")
    
    
    table.setCellWidget(3,0,self.byteOrder)
    
    #Set binfo
    self.binFile = qt.QCheckBox()
    
    table.setCellWidget(9,0,self.binFile)
    
    #Set Modality
    self.cubeType = qt.QComboBox()
    self.cubeType.addItem("CT")
    self.cubeType.addItem("Dose")
    self.cubeType.addItem("Cbt")
    
    table.setCellWidget(10,0,self.cubeType)
    
    #Patient name
    self.patientName = qt.QTableWidgetItem("Lung001")
    table.setItem(0,0,self.patientName)
    
    self.pixelSize = qt.QTableWidgetItem()
    table.setItem(4,0,self.pixelSize)
    
    self.sliceDistance = qt.QTableWidgetItem()
    table.setItem(5,0,self.sliceDistance)
    
    self.xdim = qt.QTableWidgetItem()
    table.setItem(6,0,self.xdim)
    
    self.ydim = qt.QTableWidgetItem()
    table.setItem(7,0,self.ydim)
    
    self.zdim = qt.QTableWidgetItem()
    table.setItem(8,0,self.zdim)
