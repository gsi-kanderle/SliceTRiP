import os, re
import unittest
from __main__ import vtk, qt, ctk, slicer
import numpy as np

#
# TRiPDVH
#

class TRiPDVH:
  def __init__(self, parent):
    parent.title = "TRiP DVH" # TODO make this more human readable by adding spaces
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
    slicer.selfTests['TRiPDVH'] = self.runTest

  def runTest(self):
    tester = TRiPDVHTest()
    tester.runTest()

#
# qTRiPDVHWidget
#

class TRiPDVHWidget:
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
    self.reloadButton.name = "TRiPDVH Reload"
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
    self.parametersFormLayout = qt.QFormLayout(parametersCollapsibleButton)
    
    #
    # Load gd Button
    #
    self.loadGdButton = qt.QPushButton("Load gd file")
    self.loadGdButton.toolTip = "Load gd File."
    self.loadGdButton.enabled = True
    self.parametersFormLayout.addRow(self.loadGdButton)
    
   #
    # Patient Name
    #
    self.dvhName = qt.QLineEdit()     
    self.dvhName.setToolTip( "Filepath of gd file." )
    self.dvhName.text = ''
    self.parametersFormLayout.addRow('DVH Filepath:', self.dvhName)
    
    # Input optimized Dose:
    self.inputDose = qt.QDoubleSpinBox()     
    self.inputDose.setToolTip( "Optimization dose." )
    self.inputDose.setValue(25)
    self.inputDose.setRange(0, 1020)
    self.parametersFormLayout.addRow("Dose (Gy):", self.inputDose)
    
    ## Voi list
    #self.voiComboBox = qt.QComboBox()
    #self.parametersFormLayout.addRow("Select Voi: ", self.voiComboBox)
    

    #
    # Apply Button
    #
    self.applyButton = qt.QPushButton("Show DVH")
    self.applyButton.toolTip = "Run the algorithm."
    self.applyButton.enabled = False
    self.parametersFormLayout.addRow(self.applyButton)
    
   #
    # Recalculate with different Dose
    #
    self.recalcButton = qt.QPushButton("Recalculate dose values")
    self.recalcButton.toolTip = "Recalculate all the dose values with different input."
    self.recalcButton.enabled = True
    self.parametersFormLayout.addRow(self.recalcButton)
    
    #
    # Export values
    #
    self.exportButton = qt.QPushButton("Export Values")
    self.exportButton.toolTip = "Export all values."
    self.exportButton.visible = False 
    self.parametersFormLayout.addRow(self.exportButton)
    
    #
    # Copy values
    #
    self.copyButton = qt.QPushButton("Copy Values")
    self.copyButton.toolTip = "Copy values on clipboard."
    self.copyButton.enabled = True
    self.parametersFormLayout.addRow(self.copyButton)
    
    
     ## Voi Table
    #self.voiTable= qt.QTableWidget()
    #self.parametersFormLayout.addRow(self.voiTable)
    #self.voiTable.visible = False
    
    #self.horizontalHeaders=['Show:',"Max(Gy)","D99%(Gy)","D10%(Gy)","D30(Gy)","per. Volume (Gy)","Volume(cc)"]
    #self.voiTable.setColumnCount(len(self.horizontalHeaders))
    #self.voiTable.setHorizontalHeaderLabels(self.horizontalHeaders)
    
    #self.voiTable.setEditTriggers(qt.QAbstractItemView.NoEditTriggers)
    
    # Voi Table checkbox list:
    self.voiTableCheckBox = []
   




    # Add vertical spacer
    self.layout.addStretch(1)
    
    # DVH
    self.dvh = []
    
     # connections
    self.applyButton.connect('clicked(bool)', self.onApplyButton)
    self.loadGdButton.connect('clicked(bool)', self.onLoadGdButton)
    self.recalcButton.connect('clicked(bool)', self.onRecalcButton)
    self.exportButton.connect('clicked(bool)', self.onExportButton)
    self.copyButton.connect('clicked(bool)', self.onCopyButton)
    #self.voiComboBox.connect('currentIndexChanged(QString)', self.setDvhTable)
    

  def cleanup(self):
    pass


  def onLoadGdButton(self):
    #self.dvhTable.visible = False
    
    #Comment this if you want more tables:
    if self.dvh:
      self.parametersFormLayout.removeWidget(self.dvh[0].voiTable)
    self.dvh = []
    
    loadFileName = qt.QFileDialog()
    filePath=loadFileName.getOpenFileName()
    filePrefix, fileExtension = os.path.splitext(filePath)
    if filePath == '':
      return
    if not fileExtension == '.gd':
      print "Wrong extension"
      return
    
    self.readDoseFromFilename(filePrefix)
    patientFlag = self.readPatientFlagFromFilename(filePrefix)
    #self.dvh = None
    #self.voiTableCheckBox = []
    #self.voiTable.clear()
    #optDose = 25
    optDose = self.inputDose.value
    dvh = DVH(optDose=optDose,patientFlag=patientFlag)
    dvh.readFile(filePath)
    #TODO: Dodaj error, ce je neuspesn
    dvh.setTable(self.parametersFormLayout)
    self.applyButton.enabled=True
    self.dvh.append( dvh )
    self.dvhName.text = dvh.filePath

  def onApplyButton(self):
    
    #Selected list goes linearly through all checkboxes
    selectedList = []
    for j in range(0,len(self.dvh)):
      length = len(self.dvh[j].voiTableCheckBox)
      for i in range(0,length):
        if self.dvh[j].voiTableCheckBox[i].checkState() == 0:
	  selectedList.append(False)
        else:
	  selectedList.append(True)
	    
    logic = TRiPDVHLogic()    
    logic.addChart(self.dvh,selectedList)
    print("Displaying")

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
	
  
  #Read Patient Name From filename 
  def readPatientFlagFromFilename(self,fileName):
    index = fileName.find('Lung0')
    if index > -1:
      patientFlag = fileName[index+5:index+7]
      return int(patientFlag)
    else:
      return 0
      
      #if fileNameRest.find('_') > -1:
        #dose = float(fileNameRest[0:fileNameRest.find('_')])
        ##dose = float(dose)
        #self.inputDose.setValue(round(dose,1))
  
  #Read Dose from file name 
  def readDoseFromFilename(self,fileName):
    index = fileName.find('_d')
    if index > -1:
      fileNameRest = fileName[index+2:-1]
      if fileNameRest.find('_') > -1:
	try:
          dose = float(fileNameRest[0:fileNameRest.find('_')])
          #dose = float(dose)
          self.inputDose.setValue(round(dose,1))
        except ValueError:
          print "Not a float"

  def onReload(self,moduleName="TRiPDVH"):
    """Generic reload method for any scripted module.
    ModuleWizard will subsitute correct default moduleName.
    """
    #globals()[moduleName] = slicer.util.reloadScriptedModule(moduleName)
    
    import imp, sys, os, slicer

    widgetName = moduleName + "Widget"

    # reload the source code
    # - set source file path
    # - load the module to the global space
    filePath = eval('slicer.modules.%s.path' % moduleName.lower())
    p = os.path.dirname(filePath)
    if not sys.path.__contains__(p):
      sys.path.insert(0,p)
    fp = open(filePath, "r")
    globals()[moduleName] = imp.load_module(
        moduleName, fp, filePath, ('.py', 'r', imp.PY_SOURCE))
    fp.close()

    # rebuild the widget
    # - find and hide the existing widget
    # - create a new widget in the existing parent
    parent = slicer.util.findChildren(name='%s Reload' % moduleName)[0].parent().parent()
    for child in parent.children():
      try:
        child.hide()
      except AttributeError:
        pass
    # Remove spacer items
    item = parent.layout().itemAt(0)
    while item:
      parent.layout().removeItem(item)
      item = parent.layout().itemAt(0)

    # delete the old widget instance
    if hasattr(globals()['slicer'].modules, widgetName):
      getattr(globals()['slicer'].modules, widgetName).cleanup()

    # create new widget inside existing parent
    globals()[widgetName.lower()] = eval(
        'globals()["%s"].%s(parent)' % (moduleName, widgetName))
    globals()[widgetName.lower()].setup()
    setattr(globals()['slicer'].modules, widgetName, globals()[widgetName.lower()])
    
    
  def onReloadAndTest(self,moduleName="TRiPDVH"):
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

  def addChart(self,dvhs,selectedList):
    ln = slicer.util.getNode(pattern='vtkMRMLLayoutNode*')
    ln.SetViewArrangement(25)
    cvn = slicer.util.getNode(pattern='vtkMRMLChartViewNode*')
    cn = slicer.mrmlScene.AddNode(slicer.vtkMRMLChartNode())
    
    n = 0
    for j in range(0,len(dvhs)):
      vois = dvhs[j].get_voi_names()
      for i in range(0,len(vois)):
        if selectedList[n]:
	  dn = dvhs[j].getSlicerDoubleArray(vois[i])
	  cn.AddArray(vois[i], dn.GetID())
	n += 1

    cn.SetProperty('default', 'xAxisLabel', 'Dose [Gy]')
    cn.SetProperty('default', 'yAxisLabel', 'Volume [%]')
    cn.SetProperty('default', 'title', os.path.basename(dvhs[-1].filePath))
    cvn.SetChartNodeID(cn.GetID())
    return


class DVH():
  def __init__(self,optDose=1,patientFlag=0):
    self.name=''
    self.optDose = optDose
    self.patientFlag = patientFlag
    self.vois=[]
    self.filePath=''
    self.voiTable = None
    self.voiTableCheckBox = []
    self.horizontalHeaders=['Show:',"Max(Gy)","D99%(Gy)","D10%(Gy)","D30(Gy)","per. Volume (Gy)","Volume(cc)"]
  
  def readFile(self,filePath):
    #print "Lets do it"
    self.filePath=filePath
    fp = open(filePath,"r")
    content = fp.read().split('\n')
    fp.close()
    self.name=content[0]
    n=len(content)
    i=1
    #print contet[len(content)-1]
    while(i < n):
      line = content[i]
      #print "This is our line: " + str(i)
      
      if re.match("c:",line) is not None:
	if re.match("VOI",line.split()[1]) is not None:
	  i += 1
	  continue
	else:
	  v = Voi(line.split()[1], self.optDose)
	  i = v.readFile(content,i)
	  v.setOarConstraints(patientFlag = self.patientFlag)
	  self.add_voi(v)
	  #print v.name
          #v.setSlicerOrigin(self.dimx,self.dimy,self.pixel_size)
      i += 1

  def setTable(self,layout):
    # Voi Table
    table = self.voiTable
    if table:
      table.clearContents()
    else:
      table= qt.QTableWidget()
      layout.addRow(table)
    #table.visible = False
    
    table.setColumnCount(len(self.horizontalHeaders))
    table.setHorizontalHeaderLabels(self.horizontalHeaders)
    table.setEditTriggers(qt.QAbstractItemView.NoEditTriggers)

    table.setRowCount(len(self.vois))
    table.setVerticalHeaderLabels(self.get_voi_names())
        
    for i in range(0,len(self.vois)):
      checkBox = qt.QCheckBox()
      checkBox.setCheckState(0)
      self.voiTableCheckBox.append(checkBox)
      table.setCellWidget(i,0,checkBox)
      self.setVoiTable(table,self.vois[i],i)
      #self.voiComboBox.addItem(voi)
    
    table.visible = True
    table.resizeColumnsToContents()
    self.voiTable = table
    
 
  def setVoiTable(self,table,voi,n):    
    #voi=self.dvh.get_voi_by_name(voiName)          
    #dose=self.inputDose.value
    dose = self.optDose
    #if voi.dvhTableItems == []:
    voi.setDvhTableItems(self.horizontalHeaders) 
    a = [str(voi.maximumDose)+"/"+str(voi.maxDose),str(voi.d99),str(voi.d10),str(voi.d30),
           str(voi.calcPerscDose)+"/"+str(voi.perscDose),str(voi.volume)]
    for i in range(1,len(self.horizontalHeaders)):
      item = voi.dvhTableItems[i-1]
      table.setItem(n,i,item)
      if not len(a) == len(voi.dvhTableItems):
	print "Not enough table items, check code."
      item.setText(a[i-1])
      if voi.overOarDose:
	item.setBackground(qt.QColor().fromRgbF(1,0,0,1))
	
    

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
      
  def exportValuesAsText(self, filePath ):
    output_str = self.setOutputValues()
    f = open(filePath,"wb+")
    f.write(output_str)
    f.close()  
  
  def exportValuesOnClipboard(self):
    output_str = self.setOutputValues()
    clipboard = qt.QApplication.clipboard()
    clipboard.setText(output_str,qt.QClipboard.Selection)
    clipboard.setText(output_str,qt.QClipboard.Clipboard)
    
  def setOutputValues(self):
    dose = self.optDose
    output_str = 'Name\tMean Dose\tV10%\tV30%\tV99%\tV(onDose)\tMax Point Dose\tVolume (mm3) \n'
    voiOrder = ["heart","spinalcord","smallerairways","esophagus","trachea",
                "aorta","vesselslarge","airwayslarge","bracialplexus","carina",
                "ivc","largebronchus","svc","liver","lungl","lungr"]

    for nameit in voiOrder:
      for voi in self.vois:
	if voi.name.lower() == nameit:
	  if nameit.find("lung") > -1:
	    output_str += (voi.name+'\t'+str(voi.mean)+'\t'+str(voi.d10)+'\t'+str(voi.d30)+'\t'+str(voi.d99)
		      +'\t'+str(voi.calcPerscDose)+'\t'+str(voi.maximumDose)+'\t'+str(voi.volume) + ' \n')
	  #output_str += (voi.name+'\t'+str(voi.mean)+'\t'+str(voi.d10)+'\t'+str(voi.d30)+'\t'+str(voi.d99)
		      #+'\t'+str(voi.calcPerscDose)+'\t'+str(voi.maximumDose)+'\t'+str(voi.volume) + ' \n')
	  else:
	    output_str += (voi.name+'\t'+'\t'+str(voi.calcPerscDose)+'\t'+str(voi.maximumDose)+'\t'+str(voi.volume) + ' \n')

      #output_str += (nameit+'\n')
    return output_str
  
  def getSlicerDoubleArray(self,name):
    
    voi=self.get_voi_by_name(name)
    
    if voi.dn is not None:
      return voi.dn
      
    voi.dn = slicer.mrmlScene.AddNode(slicer.vtkMRMLDoubleArrayNode())
    
    if voi.array is None:
      voi.array = voi.dn.GetArray()
      voi.array.SetNumberOfTuples(len(voi.x))
      for i in range(0,len(voi.x)):
        voi.array.SetComponent(i, 0, voi.x[i])
        voi.array.SetComponent(i, 1, voi.y[i])
        voi.array.SetComponent(i, 2, voi.err[i])
        
    return voi.dn
      
class Voi():
  def __init__(self,name,optDose=1):
    self.name=name    
    self.optDose = optDose
    self.dn=None
    self.array=None
    self.x=np.zeros(129)
    self.y=np.zeros(129)
    self.err=np.zeros(129)
    self.minimum = 0
    self.maximumDose = 0
    self.mean = 0
    self.stdev = 0
    self.mdian = 0
    self.volume = 0
    self.voxVol=0
    self.d10=0
    self.d30=0
    self.d95105=0
    self.d99 = 0
    self.dvhTableItems = []
    self.perscDose = 0
    self.perscVolume = 1
    self.maxDose = 0
    self.rescaledVolume = 0
    self.calcPerscDose = 0
    self.overOarDose = False
   
  def readFile(self,content,i):
    line = content[i]
    
    if line is '':
      return i
      
    #self.name = string.join(line.split()[1:],' ')
    self.minimum = float(line.split()[2])*self.optDose
    self.maximumDose = round(float(line.split()[3]),2)*self.optDose
    self.mean = float(line.split()[4])*self.optDose
    if not line.split()[5] == 'NaNQ':
      self.stdev = float(line.split()[5])*self.optDose
    self.mdian = float(line.split()[6])*self.optDose
    self.volume = round(float(line.split()[7])/1000,2)
    self.voxVol=float(line.split()[8])
    i += 2
    n=0
    while i < len(content):
      line = content[i]
      if re.match("H:",line) is not None:
	i += 1
	continue
      elif re.match("c:",line) is not None:
        break
      else:
	if n>=129:
	  break	  
	self.x[n]=float(line.split()[0])
	self.y[n]=float(line.split()[1])
	self.err[n]=float(line.split()[1])
	n += 1
        #self.array.SetComponent(n, 0, float(line.split()[0]))
        #self.array.SetComponent(n, 1, float(line.split()[1]))
        #self.array.SetComponent(n, 2, float(line.split()[2]))
        #n += 1
        #if n>128:
	  #self.array.SetNumberOfTuples(n)
      i += 1
      
    self.x = np.array(self.x)*self.optDose/100
    return i-1
  
  def calculateDose(self):
    
    # If doses are to small, ignore.
    if self.maximumDose < 1e-3:
      return
      
    self.d10 = self.setValue(10)
    #self.d10 = self.d10*dose
    self.d30 = self.setValue(30)
    self.d95105 = self.setValue(95) - self.setValue(105)
    self.d99 = self.setValue(99)
    
    if not self.perscDose == 0:
      percantage = self.perscVolume*1e2/self.volume
      calcDose = self.setValue(percantage)
      if calcDose > self.perscDose:
	self.overOarDose = True
      self.calcPerscDose = calcDose    
        
     
  def setValue(self,value):
    x=self.x
    y=self.y
    array = abs(y-value)
    index = np.argmin(array)
    if index:
      result = x[index]
      return round(result,2)
    else:
      return 0
      
  def setDvhTableItems(self,horizontalHeaders):
    self.dvhTableItems=[]
    for i in range(0,len(horizontalHeaders)-1):
      item = qt.QTableWidgetItem()
      self.dvhTableItems.append(item)
    self.calculateDose()
    
  def setOarConstraints(self,patientFlag=None):
    
    # Function oarset makes a oar cell with specific oar names, volumes and doses.
    # Make sure, that position of the oar name coresponds to volumes, maxdose and perscdose
    
    names=["spinalcord","heart","esophagus","stomach","smallerairways",
           "aorta","largebronchus","lungs","lungl","lungr",
           "liver","brachialplexus","vesselslarge","trachea","airwayslarge",
           "carina","ivc","svc","airwayssmall","pulmonaryvessel",
           "smallairways"]
    if self.name.lower() in names:
      index = names.index(self.name.lower())
    else:
      print "No percription dose found for oar: " + self.name
      return
           
    perscVolume=[0.35,15,5,10,0.5,
             10,4,1500,1500,1500,
             700,3,10,4,4,
             4,10,10,0.5,10,
             0.5]
    perscDose=[10,16,11.9,11.2,12.4,
               31,10.5,7,7,7,
               9.1,14,31,10.5,10.5,
               10.5,31,31,12.4,31,
               12.4]
    maxDose=[14,22,15.4,12.4,13.3,
              37,20.2,0,0,0,
              0,17.5,37,20.2,20.2,
              20.2,37,37,13.3,37,
              13.3]
    self.perscDose = perscDose[index]
    self.perscVolume = perscVolume[index]
    self.maxDose = maxDose[index]
    
    if not self.maxDose == 0 and self.maximumDose > self.maxDose:
      self.overOarDose = True
      print "Maximum dose too high: " + names[index]
    
    # Some VOI volumes differ in 4D CT and Planning CT (i.e. if it has less slices). So this flag is used for comparing VOI volumes.
    # First you specified for which patient you want to check, then you input all volumes.
    #If you don't know it, or don't need it, just input 0.
    
    if patientFlag:
      patientOarVolumes=np.zeros(len(names))
      if patientFlag==2:
        patientOarVolumes=[54,878,58,0,1.8,210,0,0,1362,1438,805]
      elif patientFlag==4:
	patientOarVolumes=[40.7,337.7,66.4,0,2.21,300.0,0,2828.1,1266,1552,1208,0,140,0,8.8,0]
      elif patientFlag==5:
	patientOarVolumes=[60,499,35,0,0.8,185,0,0,792,1071,0]
      elif patientFlag==6:
	patientOarVolumes=[26.4,686,35.3,0,5,209,0,0,2479,2654,0,0,0,42,22,5.5,0]
      elif patientFlag==12:
	patientOarVolumes=[27.3,551.8,40.8,0,1.56,283.1,0,0,1781,1456,0,124.5,0,40.2,0,0,0]
      elif patientFlag==15:
	patientOarVolumes=[24.5,0,41.2,0,0,64.6,0,0,1968,1812,0,3,0,37.1,0]
      elif patientFlag==16:
	patientOarVolumes=[36.6,386,35.6,0,0,276,0,2113,895,1211,0,0,198,22.2,11.2,0]
      
      if index < len(patientOarVolumes):
	rescaledVolume = patientOarVolumes[index]
      else:
	rescaledVolume = 0
	
      #if not rescaledVolume == 0:
	#if abs(self.volume-rescaledVolume)/rescaledVolume > 0.1:
	  #self.y = np.array(self.y)*self.volume/rescaledVolume
	  #self.volume = rescaledVolume
	  #print "setting volume for: " + names[index]
	  
      
   
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
