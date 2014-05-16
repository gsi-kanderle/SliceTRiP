import os
import unittest
from __main__ import vtk, qt, ctk, slicer
from ComparePatientsLib import Patients, Voi
reload(Patients)

#
# ComparePatients
#

class ComparePatients:
  def __init__(self, parent):
    parent.title = "Compare Patients" # TODO make this more human readable by adding spaces
    parent.categories = ["SliceTRiP"]
    parent.dependencies = []
    parent.contributors = ["Jean-Christophe Fillion-Robin (Kitware), Steve Pieper (Isomics)"] # replace with "Firstname Lastname (Org)"
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
    slicer.selfTests['ComparePatients'] = self.runTest

  def runTest(self):
    tester = ComparePatientsTest()
    tester.runTest()

#
# qComparePatientsWidget
#

class ComparePatientsWidget:
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
    self.reloadButton.name = "ComparePatients Reload"
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
    
    # Load all patients
    self.patientComboBox = qt.QComboBox()    
    self.patientComboBox.setToolTip( "Input file" )
    self.patientComboBox.enabled = True
    self.parametersFormLayout.addRow("Patient:", self.patientComboBox)
    
    
    patientNumber = 1
    filePath = '/u/kanderle/AIXd/Data/FC/Lung0'
    patientPath = ''
    #self.setPatientPathFromNumber(patientNumber,filePath,patientPath)
    #print patientPath
    #while os.path.exists(patientPath):
      #patientNumber += 1
      #self.setPatientPathFromNumber(patientNumber,filePath,patientPath)
    
    self.patientList = []
    for patientNumber in range(1,21+1):
      if patientNumber < 10:
        number = '0' + str(patientNumber)
      else:
        number = str(patientNumber)
      patientName = 'Lung0' + number
      self.patientComboBox.addItem(patientName)
      newPatient = Patients.Patient(patientName)
      newPatient.number = patientNumber
      self.patientList.append(newPatient)
    
    
      
    # Selection of plan
    self.planComboBox = qt.QComboBox()
    self.planComboBox.enabled = False
    self.parametersFormLayout.addRow("Select plan: ", self.planComboBox)
    
    # Metrics list (max Dose, mean Dose...)
    self.metricComboBox = qt.QComboBox()
    self.metricComboBox.enabled = False
    self.parametersFormLayout.addRow("Select metric to compare: ", self.metricComboBox)
    
    #
    # Show Plan Button
    #
    self.showPlan = qt.QPushButton("Show Plan")
    self.showPlan.toolTip = "Loads CT and plan to Slicer."
    self.showPlan.enabled = True
    self.parametersFormLayout.addRow(self.showPlan)
    
    #
    # Compare to SBRT Button
    #
    self.compareButton = qt.QPushButton("Compare to SBRT")
    self.compareButton.toolTip = "Calculates and visualizes plan to SBRT."
    self.compareButton.enabled = False
    self.parametersFormLayout.addRow(self.compareButton)
    
    #
    # Save Best Plan Button
    #
    self.saveBestPlan = qt.QPushButton("Save Best plan")
    self.saveBestPlan.toolTip = "Save best plan to disk (can read it later)."
    self.saveBestPlan.enabled =True
    self.parametersFormLayout.addRow(self.saveBestPlan)
    
    #
    # Save Best Plan Button
    #
    self.toClipboardButton = qt.QPushButton("Copy values to clipboard")
    self.toClipboardButton.toolTip = "Take difference from best plan and sbrt from desired metric."
    self.toClipboardButton.enabled =True
    self.parametersFormLayout.addRow(self.toClipboardButton)
    
    # Voi list
    self.voiComboBox = qt.QComboBox()
    self.voiComboBox.enabled = False
    self.parametersFormLayout.addRow("Select Voi: ", self.voiComboBox)
    
    #
    # Show Button
    #
    self.showButton = qt.QPushButton("Show VOI")
    self.showButton.toolTip = "Run the algorithm."
    self.showButton.enabled = True
    self.parametersFormLayout.addRow(self.showButton)

    # connections
    self.showPlan.connect('clicked(bool)', self.onShowPlanButton)
    self.compareButton.connect('clicked(bool)', self.onCompareButton)
    self.saveBestPlan.connect('clicked(bool)', self.onSaveBestPlanButton)
    self.toClipboardButton.connect('clicked(bool)', self.onToClipboardButton)
    self.patientComboBox.connect('currentIndexChanged(int)', self.setPlanComboBox)
    self.showButton.connect('clicked(bool)', self.onShowVoiButton)

    # Add vertical spacer
    self.layout.addStretch(1)
    
    
    self.table = None
    self.binfo = None
  
  def cleanup(self):
    pass


  def onToClipboardButton(self):
    metric = self.metricComboBox.currentText
    #patient = self.getCurrentPatient()
    #selectedPlan = self.getCurrentPlan()
    logic = ComparePatientsLogic()
    logic.exportMetricToClipboard(self.patientList,metric,planPTV = True)
    
  def onCompareButton(self):
    metric = self.metricComboBox.currentText
    patient = self.getCurrentPatient()
    selectedPlan = self.getCurrentPlan()
    logic = ComparePatientsLogic()
    logic.visualizeComparison(patient,selectedPlan,metric)
    
    
  def onShowPlanButton(self):
    logic = ComparePatientsLogic()
    newPatient=self.getCurrentPatient()
    plan = self.getCurrentPlan()
    print("Loading patient plan for: " + plan.fileName)
    logic.loadPlan(newPatient, plan)

  def setPlanComboBox(self,patientNumber):
    self.planComboBox.clear()
    self.planComboBox.enabled = True
    self.compareButton.enabled = True
    newPatient = self.patientList[patientNumber]
    Patients.readPatientData(newPatient)
    for plan in newPatient.plans:
      self.planComboBox.addItem(plan.fileName)
    self.setMetricComboBox()
    self.setVoiComboBox()
    
    #metricList = ['maxDose','calcPerscDose','meanDose','volume']
    #logic = ComparePatientsLogic()
    #logic.setTable(self.parametersFormLayout,newPatient,metricList)


  def setVoiComboBox(self):
    import LoadCTXLib
    
    name = self.getCurrentPatient().name
    filePath = ('/u/kanderle/PatientData/FC/'+name+'/Contour/4D/ByTRiPTrafo/'+name+'_00.binfo')
    if not os.path.isfile(filePath):
      filePath  = ('/u/kanderle/PatientData/FC/'+name+'/Contour/4D/ByTRiPTrafo/'+name+'.binfo')
      if not os.path.isfile(filePath):
	print "No binfo file for: " + name
	return
    self.voiComboBox.clear() 
    binfo = LoadCTXLib.Binfo()
    binfo.readFile(filePath)   
    for voiName in binfo.get_voi_names():
      voi = binfo.get_voi_by_name(voiName)
      self.voiComboBox.addItem(voiName)
    self.binfo = binfo
    self.voiComboBox.enabled = True
    
  def onShowVoiButton(self):
    import LoadCTX
    
    binfo=self.binfo
    filePrefix, fileExtension = os.path.splitext(binfo.filePath)
    voi = binfo.get_voi_by_name(self.voiComboBox.currentText)
    if not voi:
      print "Error, voi not found."
      return
    filePath = filePrefix + voi.name + ".ctx"
    n=0 #motion state
    logic = LoadCTX.LoadCTXLogic()
    voi.slicerNodeID[n]=logic.loadCube(filePath,2,motionState=n,voi=voi)
  def onSaveBestPlanButton(self):
    reload(Patients)
    patient = self.getCurrentPatient()
    patient.bestPlan = self.getCurrentPlan()
    patient.saveBestPlan()
  
  def setMetricComboBox(self):
    metricList = ['maxDose','calcPerscDose','meanDose','volume','d10','d30']
    self.metricComboBox.enabled = True
    self.metricComboBox.clear()
    for string in metricList:
      self.metricComboBox.addItem(string)
  
  def getCurrentPatient(self):
    return self.patientList[self.patientComboBox.currentIndex]
    
  def getCurrentPlan(self):
    patient = self.getCurrentPatient()
    return patient.plans[self.planComboBox.currentIndex]
    
  def onReload(self,moduleName="ComparePatients"):
    """Generic reload method for any scripted module.
    ModuleWizard will subsitute correct default moduleName.
    """
    globals()[moduleName] = slicer.util.reloadScriptedModule(moduleName)

  def onReloadAndTest(self,moduleName="ComparePatients"):
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
# ComparePatientsLogic
#

class ComparePatientsLogic:
  """This class should implement all the actual
  computation done by your module.  The interface
  should be such that other python code can import
  this class and make use of the functionality without
  requiring an instance of the Widget
  """
  def __init__(self):
    pass

  
  def setTable(self,layout,patient,metricList):
    # Voi Table
    table = patient.slicerTable
    if table:
      table.clearContents()
    else:
      table= qt.QTableWidget()
      patient.slicerTable = table
      layout.addRow(table)
    #table.visible = False
    

    if not Patients.compareToSbrt(patient):
      return
      
    table.setColumnCount(len(metricList))
    table.setHorizontalHeaderLabels(metricList)
    table.setEditTriggers(qt.QAbstractItemView.NoEditTriggers)

    table.setRowCount(len(patient.voiDifferences))
    table.setVerticalHeaderLabels(patient.get_voiDifferences_names())
        
    n = 0
    for voi in patient.voiDifferences:
      for i in range(0,len(metricList)):
	item = qt.QTableWidgetItem()
	table.setItem(n,i,item)
	value = getattr(voi,metricList[i])
	item.setText("tisoc")
      n += 1
    
    table.visible = True
    table.resizeColumnsToContents()
    


  def setVoiTable(self,table,voi,n,metricList):    
    for i in range(0,len(metricList)):
      item = qt.QTableWidgetItem()
      print n
      print i
      table.setItem(n,i,item)
      value = getattr(voi,metricList[i])
      print value
      item.setText()
      if value > 0:
	item.setBackground(qt.QColor().fromRgbF(0,1,0,1))
      else:
	item.setBackground(qt.QColor().fromRgbF(1,0,0,1))
  
  
  
  def exportMetricToClipboard(self,patientList,metric,planPTV=False):
    voiOrder = ["heart","spinalcord","smallerairways","esophagus","trachea",
                "aorta","vesselslarge","airwayslarge","brachialplexus","carina",
                "ivc","largebronchus","svc","liver","lungl","lungr"]
    
    output_str = 'Difference in ' + metric + '\n'
    output_str += 'Patient name\t'
    for voi in voiOrder:
      output_str += voi + '\t'
    planPTV=False
    norm = True
    output_str += '\n'
    maxLungDose = 0
    #Flag for following ipsilateral lungl
    firstLung = False
    voiIpsiLateral = None
    voiContraLateral = None
    for i in range(0,len(patientList)):
      newPatient = patientList[i]
      Patients.readPatientData(newPatient)
      if Patients.compareToSbrt(newPatient,voiOrder,planPTV):
	output_str += newPatient.name + '\t'
	for voiName in voiOrder:
	  voi = newPatient.get_voiDifference_by_name(voiName)
	  if voi:
	    #Normalization factor
	    if norm:
	      if metric == 'maxDose':
		normFactor = voi.maxPerscDose
	      elif metric == 'calcDose':
		normFactor = voi.perscDose
	      else:
		normFactor = 1	      
	    if normFactor == 0:
	      output_str += '\t'
	      continue

	    if voiName.find('lung') > -1:
	      if voiName == 'lungl':
	        if not voi.ipsiLateral:
	          voiContraLateral = voi
	          firstLung = True
	        else:
		  voiIpsiLateral = voi
	      elif voiName == 'lungr':
	        if firstLung:
		  if voi.ipsiLateral:
		    voiIpsiLateral = voi
		  else:
		    print "No ipsi-lateral lung"
		    output_str += '-1\t-1\t'
		else:
		  voiContraLateral = voi
	      if voiIpsiLateral and voiContraLateral:
	        output_str += str(getattr(voiIpsiLateral,metric)/normFactor) +'\t'
	        output_str += str(getattr(voiContraLateral,metric)/normFactor) +'\t'
	        voiIpsiLateral = None
	        voiContraLateral = None
	        firstLung = False
	    else:
	      output_str += str(getattr(voi,metric)/normFactor) +'\t'
	  else:
	    output_str += '\t'
	output_str += '\n'
      else:
	print "Not enough data."

    clipboard = qt.QApplication.clipboard()
    clipboard.setText(output_str,qt.QClipboard.Selection)
    clipboard.setText(output_str,qt.QClipboard.Clipboard)
    
  def visualizeComparison(self,patient,ptPlan,metric):
    
    ln = slicer.util.getNode(pattern='vtkMRMLLayoutNode*')
    ln.SetViewArrangement(25)
    cvn = slicer.util.getNode(pattern='vtkMRMLChartViewNode*')
    cn = slicer.mrmlScene.AddNode(slicer.vtkMRMLChartNode())
    n = 0
    
    if Patients.compareToSbrt(patient):
      #dn = slicer.mrmlScene.AddNode(slicer.vtkMRMLDoubleArrayNode())
      #array = dn.GetArray()
      ##array.SetNumberOfTuples(len(patient.voiDifferences))
      #array.SetNumberOfTuples(3)
      for voi in patient.voiDifferences:
	dn = slicer.mrmlScene.AddNode(slicer.vtkMRMLDoubleArrayNode())
        array = dn.GetArray()
        #array.SetNumberOfTuples(len(patient.voiDifferences))
        array.SetNumberOfTuples(3)
        metricValue = getattr(voi,metric)
        array.SetComponent(n,0,n+1)
        array.SetComponent(n,1,metricValue)
        #array.SetComponent(n, 2, 0)
        n += 1
        cn.AddArray(voi.name,dn.GetID())
        if n>5:
	  break
    
    
    cn.SetProperty('default', 'title', 'Difference for: ' + metric)
    cn.SetProperty('default', 'xAxisLabel', 'structure')
    #cn.SetProperty('default', 'xAxisType', 'categorical')
    cn.SetProperty('default', 'yAxisLabel', 'Dose Difference [Gy]')
    cn.SetProperty('default', 'type', 'Bar')
    cn.SetProperty('Volumes', 'lookupTable', slicer.util.getNode('GenericAnatomyColors').GetID() )
    cvn.SetChartNodeID(cn.GetID())
    print "Finished!"
    
  
  def loadPlan(self,patient,plan):
    import LoadCTX
    loadLogic = LoadCTX.LoadCTXLogic()
    filePathCT = ('/u/kanderle/AIXd/Data/FC/' + patient.name + '/CTX/'+patient.name+'_00.ctx')
    filePathPlan = ('/u/kanderle/AIXd/Data/FC/' + patient.name + '/Dose/' + plan.fileName[0:-7] + '_bio.dos')
    if not os.path.exists(filePathCT):
      print "No CT at: " + filePathCT
      return
    if not os.path.exists(filePathPlan):
      filePathPlan = ('/u/kanderle/AIXd/Data/FC/' + patient.name + '/Dose/' + plan.fileName[0:-7] + '_resample.dos')
      if not os.path.exists(filePathPlan):
        print "No plan at: " + filePathPlan
        return
    #TODO: Check if slicerNodeID already exist and then load it.
    patient.slicerNodeID = loadLogic.loadCube(filePathCT,0)
    plan.slicerNodeID = loadLogic.loadCube(filePathPlan,1,optDose = 24)
    
    


class ComparePatientsTest(unittest.TestCase):
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
    self.test_ComparePatients1()

  def test_ComparePatients1(self):
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
    logic = ComparePatientsLogic()
    self.assertTrue( logic.hasImageData(volumeNode) )
    self.delayDisplay('Test passed!')
