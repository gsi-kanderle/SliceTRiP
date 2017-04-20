# -*- coding: iso-8859-1 -*-
import os
import unittest
from __main__ import vtk, qt, ctk, slicer
from ComparePatientsLib import Patients, Voi
import numpy as np
import time
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
    self.parametersFormLayout = qt.QGridLayout(parametersCollapsibleButton)
    
    # Load all patients
    self.patientComboBox = qt.QComboBox()    
    self.patientComboBox.setToolTip( "Select Patient." )
    self.patientComboBox.enabled = True
    #self.parametersFormLayout.addWidget("Patient:", self.patientComboBox)
    self.parametersFormLayout.addWidget(self.patientComboBox, 0 ,0)
    
    
    patientNumber = 1
    filePath = '/u/kanderle/AIXd/Data/FC/Lung0'
    patientPath = ''
    #self.setPatientPathFromNumber(patientNumber,filePath,patientPath)
    #print patientPath
    #while os.path.exists(patientPath):
      #patientNumber += 1
      #self.setPatientPathFromNumber(patientNumber,filePath,patientPath)
    
    self.patientList = []
    for patientNumber in range(1,23+1):
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
    #self.parametersFormLayout.addWidget("Select plan: ", self.planComboBox)
    self.parametersFormLayout.addWidget(self.planComboBox, 1 , 0)
    
    
    # Metrics list (max Dose, mean Dose...)
    self.metricComboBox = qt.QComboBox()
    self.metricComboBox.enabled = False
    #self.parametersFormLayout.addWidget("Select metric to compare: ", self.metricComboBox)
    self.parametersFormLayout.addWidget(self.metricComboBox, 0 , 1)
    
    # Voi list
    self.voiComboBox = qt.QComboBox()
    self.voiComboBox.enabled = False
    #self.parametersFormLayout.addWidget("Select Voi: ", self.voiComboBox)
    self.parametersFormLayout.addWidget(self.voiComboBox, 1, 1)
    
    #
    # Show Button
    #
    self.showButton = qt.QPushButton("Show VOI")
    self.showButton.toolTip = "Run the algorithm."
    self.showButton.enabled = True
    self.parametersFormLayout.addWidget(self.showButton, 2, 1)
    
    #
    # Show Plan Button
    #
    self.showPlan = qt.QPushButton("Show Plan")
    self.showPlan.toolTip = "Loads CT and plan to Slicer."
    self.showPlan.enabled = True
    self.parametersFormLayout.addWidget(self.showPlan,2,0)
    
    #
    # Compare to SBRT Button
    #
    self.compareButton = qt.QPushButton("Show VOI Data")
    self.compareButton.toolTip = "Calculates and visualizes plan to SBRT."
    self.compareButton.enabled = False
    self.parametersFormLayout.addWidget(self.compareButton,3,0)
    
    #
    # Export DVH
    #
    self.exportDVHButton = qt.QPushButton("Copy DVH to Clipboard")
    self.exportDVHButton.enabled = True
    self.parametersFormLayout.addWidget(self.exportDVHButton, 4 ,1)
    
    
    #
    # Save Best Plan Button
    #
    self.saveBestPlan = qt.QPushButton("Save Best plan")
    self.saveBestPlan.toolTip = "Save best plan to disk (can read it later)."
    self.saveBestPlan.enabled =True
    self.parametersFormLayout.addWidget(self.saveBestPlan,4,0)
    
    #
    # Save Best Plan Button
    #
    self.plotDVHButton = qt.QPushButton("Plot!")
    self.plotDVHButton.toolTip = "Plot dvh."
    self.plotDVHButton.enabled =True
    self.parametersFormLayout.addWidget(self.plotDVHButton,3,1)
    
    # Plan PTV
    self.PTVFrom = qt.QFormLayout()
    self.PTVCheckBox = qt.QCheckBox()     
    self.PTVCheckBox.setToolTip( "Look at the plans for PTV" )
    self.PTVCheckBox.setCheckState(0)
    self.PTVFrom.addRow("PTV plan:", self.PTVCheckBox)
    self.parametersFormLayout.addLayout(self.PTVFrom, 5, 0)
    
    # Plan PTV
    self.normalizeForm = qt.QFormLayout()
    self.normalizeCheckBox = qt.QCheckBox()     
    self.normalizeCheckBox.setToolTip( "Normalize dose" )
    self.normalizeCheckBox.setCheckState(0)
    #self.parametersFormLayout.addWidget("Normalize:", self.normalizeCheckBox)
    self.normalizeForm.addRow("Normalize:",self.normalizeCheckBox)
    self.parametersFormLayout.addLayout(self.normalizeForm, 5, 1)
    #
    # Copy to Clipboard Button
    #
    self.toClipboardButton = qt.QPushButton("Copy values to clipboard")
    self.toClipboardButton.toolTip = "Take difference from best plan and sbrt from desired metric."
    self.toClipboardButton.enabled =True
    self.parametersFormLayout.addWidget(self.toClipboardButton, 6, 0)
    
    #
    # Load voi for distance
    #
    self.loadVOIforDistanceButton = qt.QPushButton("Mark target VOI")
    self.loadVOIforDistanceButton.toolTip = "Load VOI and prepare it for calculation of distance."
    self.loadVOIforDistanceButton.enabled =True
    self.parametersFormLayout.addWidget(self.loadVOIforDistanceButton, 7, 0)
    
    #
    # Compute distances
    #
    self.computeDistancesButton = qt.QPushButton("Compute distances")
    self.computeDistancesButton.toolTip = "Compute distances between target and BODY contour."
    self.computeDistancesButton.enabled =True
    self.parametersFormLayout.addWidget(self.computeDistancesButton, 7, 1)
    
    # Target
    self.targetForm = qt.QFormLayout()
    self.targetLineEdit = qt.QLineEdit()     
    self.targetLineEdit.setToolTip( "Target VOI" )
    self.targetLineEdit.enabled = False
    self.targetForm.addRow("TargetID:", self.targetLineEdit)
    self.parametersFormLayout.addLayout(self.targetForm, 8, 0)
    
    # Body
    self.bodyForm = qt.QFormLayout()
    self.bodyLineEdit = qt.QLineEdit()     
    self.bodyLineEdit.setToolTip( "Body VOI" )
    self.bodyLineEdit.enabled = False
    self.bodyForm.addRow("BodyID:", self.bodyLineEdit)
    self.parametersFormLayout.addLayout(self.bodyForm, 8, 1)


    #Voi table
    self.voiTable= qt.QTableWidget()
    self.parametersFormLayout.addWidget(self.voiTable, 9, 0, 9, 2)
    self.voiTable.visible = False

    # connections
    self.showPlan.connect('clicked(bool)', self.onShowPlanButton)
    self.compareButton.connect('clicked(bool)', self.onCompareButton)
    self.saveBestPlan.connect('clicked(bool)', self.onSaveBestPlanButton)
    self.plotDVHButton.connect('clicked(bool)', self.onShowDVHButton)
    self.toClipboardButton.connect('clicked(bool)', self.onToClipboardButton)
    self.patientComboBox.connect('currentIndexChanged(int)', self.setPlanComboBox)
    self.showButton.connect('clicked(bool)', self.onShowVoiButton)
    self.exportDVHButton.connect('clicked(bool)', self.onExportDVHButton)
    self.loadVOIforDistanceButton.connect('clicked(bool)', self.onLoadVOIforDistanceButton)
    self.computeDistancesButton.connect('clicked(bool)', self.onComputeDistancesButton)

    # Add vertical spacer
    self.layout.addStretch(1)
    

    self.binfo = None
    self.targetVoi = None
    
    #First run
    self.setPlanComboBox(0)
  
  def cleanup(self):
    pass


  def onToClipboardButton(self):
    metric = self.metricComboBox.currentText
    #patient = self.getCurrentPatient()
    #selectedPlan = self.getCurrentPlan()
    logic = ComparePatientsLogic()
    if self.PTVCheckBox.checkState() == 0:
      planPTV = False
    else:
      planPTV = True
      
    if self.normalizeCheckBox.checkState() == 0:
      normalize = False
    else:
      normalize = True
    logic.exportMetricToClipboard(self.patientList,metric,planPTV,normalize)
    
  def onCompareButton(self):
    self.voiTable.clearContents()
    metric = self.metricComboBox.currentText
    patient = self.getCurrentPatient()
    selectedPlan = self.getCurrentPlan()
    selectedPlan.setTable(self.voiTable)

    #logic = ComparePatientsLogic()
    #logic.visualizeComparison(patient,selectedPlan,metric)
    
    
  def onShowPlanButton(self):
    logic = ComparePatientsLogic()
    newPatient=self.getCurrentPatient()
    plan = self.getCurrentPlan()
    print("Loading patient plan for: " + plan.fileName)
    logic.loadPlan(newPatient, plan)

  def onShowDVHButton(self):
    plan = self.getCurrentPlan()
    #Selected list goes linearly through all checkboxes
    selectedList = []
    for i in range(0,len(plan.voiTableCheckBox)):
      if plan.voiTableCheckBox[i].checkState() == 0:
	selectedList.append(False)
      else:
	selectedList.append(True)
    logic = ComparePatientsLogic()   
    logic.addChart(plan,selectedList)
  

  
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
    #self.patientNumber = patientNumber
    
    #metricList = ['maxDose','calcPerscDose','meanDose','volume']
    #logic = ComparePatientsLogic()
    #logic.setTable(self.parametersFormLayout,newPatient,metricList)


  def onLoadVOIforDistanceButton(self):
    self.onShowVoiButton()
    voi = self.binfo.get_voi_by_name(self.voiComboBox.currentText)
    self.targetLineEdit.text = voi.slicerNodeID[0]
    self.targetVoi = voi
    
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
    
    
  def onExportDVHButton(self):
    plan = self.getCurrentPlan()
    #Selected list goes linearly through all checkboxes
    selectedList = []
    #TODO: Add logic for selecting VOI
    #for i in range(0,len(plan.voiTableCheckBox)):
      #if plan.voiTableCheckBox[i].checkState() == 0:
	#selectedList.append(False)
      #else:
	#selectedList.append(True)
    logic = ComparePatientsLogic()   
    logic.copyDVHToClipboard(plan)
    
  
  def onShowVoiButton(self):
    import LoadCTX    
    binfo=self.binfo
    filePrefix, fileExtension = os.path.splitext(binfo.filePath)
    voi = binfo.get_voi_by_name(self.voiComboBox.currentText)
    
    newPatient = self.getCurrentPatient()
    segmentationNode = newPatient.segmentation
    
    if not segmentationNode:
       segmentationNode = slicer.vtkMRMLSegmentationNode()
       segmentationNode.SetName(newPatient.name)
       displayNode = slicer.vtkMRMLSegmentationDisplayNode()
       slicer.mrmlScene.AddNode(displayNode)
       segmentationNode.SetAndObserveDisplayNodeID(displayNode.GetID())
       slicer.mrmlScene.AddNode(segmentationNode)
       
    if not voi:
      print "Error, voi not found."
      return
    filePath = filePrefix + voi.name + ".nrrd"
    n=0 #motion state
    logic = LoadCTX.LoadCTXLogic()
    voi.slicerNodeID[n]=logic.loadVoi(filePath,segmentationNode,motionState=n,voi=voi)
    
  def onSaveBestPlanButton(self):
    patient = self.getCurrentPatient()
    patient.bestPlan = self.getCurrentPlan()
    patient.saveBestPlan()
  
  def onComputeDistancesButton(self):
    logic = ComparePatientsLogic()
    logic.computeDistances(self.binfo,self.targetVoi)
  
  def setMetricComboBox(self):
    metricList = ['maxDose','calcPerscDose','meanDose','volume','d10','d30','v7Gy']
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

  def copyDVHToClipboard(self,plan):

    if not plan:
      print "Error, no plan loaded."
      return
    
    voiNames = plan.get_voi_names()
    output_str = "X (Gy)" + "\t"
    for voiName in voiNames:
      output_str += voiName + "\t"
    output_str += "\n"
    output_str += "\n"
    output_str += "\n"
    dimx = len(plan.vois[0].x)
    for i in range(0,dimx):
      if plan.vois[0].x[i] < 0.01:
        continue
      output_str += str(plan.vois[0].x[i]) +"\t"
      for voiName in voiNames:
	voi = plan.get_voi_by_name(voiName)
	if not voi:
	  print "Error, no " + voiName
	  return
        output_str += str(voi.y[i]) + "\t"
      output_str += "\n"
      
    clipboard = qt.QApplication.clipboard()
    clipboard.setText(output_str,qt.QClipboard.Selection)
    clipboard.setText(output_str,qt.QClipboard.Clipboard)

  def addChart(self,plan,selectedList):
    if not plan or not selectedList:
      print "Error, no plan loaded."
      return
    ln = slicer.util.getNode(pattern='vtkMRMLLayoutNode*')
    ln.SetViewArrangement(25)
    cvn = slicer.util.getNode(pattern='vtkMRMLChartViewNode*')
    cn = slicer.mrmlScene.AddNode(slicer.vtkMRMLChartNode())
    
    vois = plan.get_voi_names()
    for i in range(0,len(vois)):
      if selectedList[i]:
	voi = plan.get_voi_by_name(vois[i])
	if voi.doubleArrayNode is None:
	  voi.doubleArrayNode = slicer.mrmlScene.AddNode(slicer.vtkMRMLDoubleArrayNode())
	  array = voi.doubleArrayNode.GetArray()
	  array.SetNumberOfTuples(len(voi.x))
	  for n in range(0,len(voi.x)):
	    array.SetComponent(n, 0, voi.x[n])
	    array.SetComponent(n, 1, voi.y[n])
	    #array.SetComponent(n, 2, voi.err[n])
	      
	cn.AddArray(vois[i], voi.doubleArrayNode.GetID())
	  
    cn.SetProperty('default', 'xAxisLabel', 'Dose [Gy]')
    cn.SetProperty('default', 'yAxisLabel', 'Volume [%]')
    cvn.SetChartNodeID(cn.GetID())

    
  def exportMetricToClipboard(self,patientList,metric,planPTV, normOn):
    voiOrder = ["heart","spinalcord","smallerairways","esophagus","trachea",
                "aorta","vesselslarge","airwayslarge","brachialplexus","carina",
                "ivc","svc","liver","lungl","lungr","lungs-ptv"]

    #voiOrder = ["ctv","gtv"]
    #voiOrder = ["sundr"]
    #metric = "v24Gy"
    #File path for pps file:
    ppsFilePath = '/u/kanderle/AIXd/Data/FC/planpars/'
    output_str = ""
    output_str = 'Difference in ' + metric + '\n'
    output_str += 'Patient name\t'
    #Look for selected patient
    selectedPatients = []
    patientOn = True
    targets = []
    
    for voi in voiOrder:
      output_str += voi + '\t'
    #ctvOn = True
    output_str += '\n'
    maxLungDose = 0
    #Flag for following ipsilateral lungl
    firstLung = False
    voiIpsiLateral = None
    voiContraLateral = None
    for i in range(0,len(patientList)):
      newPatient = patientList[i]
      Patients.readPatientData(newPatient,planPTV)
      #if not newPatient.number == 7:
        #continue
      if newPatient.number == 17 or newPatient.number == 3:
	print "Skipping Lung0" + str(newPatient.number)
	continue
      patientOn = True
      argumentValueIpsi = None
      argumentValueContra = None
      #Find out target names from pps files
      ppsFile = ppsFilePath + newPatient.name + '.pps'
      #if os.path.isfile(ppsFile):
	#targets = self.readTargetsFromPps(ppsFile)
	
      #Create voi difference for each patient - difference between best plan and sbrt
      #print voiOrder
      if Patients.compareToSbrt(newPatient,voiOrder,planPTV,normOn):
	output_str += newPatient.name + '\t'
	for voiName in voiOrder:
	  voi = newPatient.get_voiDifference_by_name(voiName)
	  if voi:
	    #Skip if it's insignificant
	    argumentValue = getattr(voi,metric)
	    if argumentValue == -100 and not voiName.find('lung') > -1:
	      output_str += '\t'
	      continue
      
	    #Normalization factor
	    normFactor = 1
	    #Limit for significance
	    if normOn:
	      limit = 0.1 # %
	    else:
	      limit = 0.1 # Gy
	    if 0:
	      if metric == 'maxDose':
		normFactor = voi.maxPerscDose
		limit = 0.01 # %
	      elif metric == 'calcPerscDose':
		normFactor = voi.perscDose
		limit = 0.01 # %
	    
	    if normFactor == 0:
	      output_str += '\t'
	      continue
	    
	    if not argumentValue == -100:
	      argumentValue = argumentValue/normFactor
	      
	    #Skip if insignificant difference
	    if abs(argumentValue) < limit and not voiName.find('lung') > -1: 
	      output_str += '\t'
	      continue
	    
	    if voiName.find('lung') > -1 and voiName is not "lungs-ptv":
	      #print voiName + " " + str(round(argumentValue,2))
	      if voiName == 'lungl' or voiName == 'lungr':
	        if not voi.ipsiLateral:
	          argumentValueContra = argumentValue
	        else:
		  if argumentValueIpsi:
		    argumentValueContra = argumentValue
		  else:
		    argumentValueIpsi = argumentValue

	      if argumentValueIpsi is not None and argumentValueContra is not None:
		#if getattr(voiIpsiLateral,metric) < 0 or getattr(voiContraLateral,metric) < 0:
		  #patientOn = False
		if argumentValueIpsi == - 100:
		  output_str += '\t'
	        else:
	          output_str += str(round(argumentValueIpsi,2)) +'\t'
	        if argumentValueContra == - 100:
	          output_str += '\t'
	        else:
	          output_str += str(round(argumentValueContra,2)) +'\t'
	        argumentValueIpsi = None
	        argumentValueContra = None
	        firstLung = False
	     
	    else:
	      if argumentValue < -0.05:
		patientOn = False
	      output_str += str(round(argumentValue,2)) +'\t'
	  else:
	    output_str += '\t'
	if targets:
	  #Patients.compareToSbrt(newPatient,targets,planPTV)
	  metricD99 = 'v24Gy'
	  targetNames = []
	  planSBRT = newPatient.loadSBRTPlan()
	  planPT = newPatient.bestPlan
	  if not planPT:
	    newPatient.loadBestPlan()
	    planPT = newPatient.bestPlan
          
          if planSBRT is None and planPT is None:
	    print "Can't load SBRT and/or PT plans."
	    output_str += '\n'
	    continue
	  for targetStr in targets:
	    if targetStr:
	      #We're interested only in CTV targets
	      if targetStr.find('PTV') > -1 or targetStr.find('couch') > -1:
		continue
	      targetSBRT = planSBRT.get_voi_by_name(targetStr)
	      targetPT = planPT.get_voi_by_name(targetStr)
	      if targetSBRT and targetPT:
		print "Found target: " + targetStr
	        output_str += str(getattr(targetSBRT,metricD99)) +'\t'
	        output_str += str(getattr(targetPT,metricD99)) +'\t'
	        targetNames.append(targetStr)
	  for targetStr in targetNames:
	    output_str += targetStr + '\t'
	output_str += '\n'
	if patientOn:
	  selectedPatients.append(newPatient.name)
      else:
	print "Not enough data."
      
    print output_str
    print selectedPatients
    clipboard = qt.QApplication.clipboard()
    clipboard.setText(output_str,qt.QClipboard.Selection)
    clipboard.setText(output_str,qt.QClipboard.Clipboard)
    
  def exportMetricToClipboard2(self,patientList,metric,planPTV, normOn):
    voiOrder = ["heart","spinalcord","smallerairways","esophagus","trachea",
                "aorta","vesselslarge","airwayslarge","brachialplexus","carina",
                "ivc","svc","liver","lungl","lungr","lungs-ptv"]

    #voiOrder = ["ctv","gtv"]
    #voiOrder = ["sundr"]
    #metric = "v24Gy"
    #File path for pps file:
    ppsFilePath = '/u/kanderle/AIXd/Data/FC/planpars/'
    output_str = ""
    #output_str = 'Difference in ' + metric + '\n'
    #output_str += 'Patient name\t'
    #Look for selected patient
    selectedPatients = []
    
    for voi in voiOrder:
      output_str += voi + '\t' + voi + '\t'
      #output_str += voi + '\t'
    #ctvOn = True
    output_str += '\n'
    maxLungDose = 0
    #Flag for following ipsilateral lungl
    firstLung = False
    voiIpsiLateralSBRT = None
    voiContraLateralSBRT = None
    for i in range(0,len(patientList)):
      newPatient = patientList[i]
      #if newPatient.number is not 7:
	#continue
      Patients.readPatientData(newPatient,planPTV)
      if newPatient.number == 17 or newPatient.number == 3 or newPatient.number > 21:
	print "Skipping Lung0" + str(newPatient.number)
	continue
      #Find out target names from pps files
      ppsFile = ppsFilePath + newPatient.name + '.pps'
      if os.path.isfile(ppsFile):
	targets = self.readTargetsFromPps(ppsFile)
      #Create voi difference for each patient - difference between best plan and sbrt
      #print voiOrder
      planSBRT = newPatient.loadSBRTPlan()
      planPT = newPatient.bestPlan
      if not planPT:
	newPatient.loadBestPlan()
	planPT = newPatient.bestPlan
      if planSBRT is not None and planPT is not None:
	Patients.findIpsiLateralLung(planSBRT)
	output_str += newPatient.name + '\t'
	for voiName in voiOrder:
	  voiSBRT = planSBRT.get_voi_by_name(voiName)
	  voiPT = planPT.get_voi_by_name(voiName)
	  if voiSBRT and voiPT:
	    #Normalization factor
	    normFactor = 1
	    if normOn:
	      if metric == 'maxDose':
		normFactor = voiSBRT.maxPerscDose
	      elif metric == 'calcPerscDose':
		normFactor = voiSBRT.perscDose
	      else:
		normFactor = 1	      
	    if normFactor == 0:
	      output_str += '\t'
	      continue
	    if voiName.find('lung') > -1 and voiName is not "lungs-ptv":
	      if voiName == 'lungl':
	        if not voiSBRT.ipsiLateral:
	          voiContraLateralSBRT = voiSBRT
	          voiContraLateralPT = voiPT
	          firstLung = True
	        else:
		  voiIpsiLateralSBRT = voiSBRT
		  voiIpsiLateralPT = voiPT
	      elif voiName == 'lungr':
	        if firstLung:
		  if voiSBRT.ipsiLateral:
		    voiIpsiLateralSBRT = voiSBRT
		    voiIpsiLateralPT = voiPT
		  else:
		    print "No ipsi-lateral lung"
		    output_str += '-10\t-10\t-10\t-10\t'
		else:
		  voiContraLateralSBRT = voiSBRT
		  voiContraLateralPT = voiPT
	      if voiContraLateralSBRT and voiIpsiLateralSBRT:
		#output_str += str(round(getattr(voiIpsiLateralPT,metric)/getattr(voiIpsiLateralSBRT,metric),2)) +'\t'
		#output_str += str(round(getattr(voiContraLateralPT,metric)/getattr(voiContraLateralSBRT,metric),2)) +'\t'

	        output_str += str(round(getattr(voiIpsiLateralSBRT,metric)/normFactor,2)) +'\t'
	        output_str += str(round(getattr(voiIpsiLateralPT,metric)/normFactor,2)) +'\t'
	        #output_str += '\n'
	        output_str += str(round(getattr(voiContraLateralSBRT,metric)/normFactor,2)) +'\t'
	        output_str += str(round(getattr(voiContraLateralPT,metric)/normFactor,2)) +'\t'
	        voiIpsiLateralSBRT = None
	        voiContraLateralSBRT = None
	        firstLung = False
	    else:
	      #output_str += str(round(getattr(voiPT,metric)/getattr(voiSBRT,metric),2)) +'\t'
	      output_str += str(round(getattr(voiSBRT,metric)/normFactor,2)) +'\t'
	      output_str += str(round(getattr(voiPT,metric)/normFactor,2)) +'\t'
	    #output_str += '\n'
	  else:
	    #output_str += '\t'
	    output_str += '\t' + '\t'
	    #pass
	  output_str += '\n'
	#if targets:
	  #Patients.compareToSbrt(newPatient,targets,planPTV)
	  #metricD99 = 'v24Gy'
	  #targetNames = []
	  #for targetStr in targets:
	    #if targetStr:
	      ##We're interested only in CTV targets
	      #if targetStr.find('PTV') > -1 or targetStr.find('couch') > -1:
		#continue
	      #target = newPatient.get_voiDifference_by_name(targetStr)
	      #if target:
		#print "Found target: " + targetStr
	        #output_str += str(getattr(target,metricD99)) +'\t'
	        #targetNames.append(targetStr)
	  #for targetStr in targetNames:
	    #output_str += targetStr + '\t'
	output_str += '\n'
      else:
	print "Not enough data."
      
    print output_str
    clipboard = qt.QApplication.clipboard()
    clipboard.setText(output_str,qt.QClipboard.Selection)
    clipboard.setText(output_str,qt.QClipboard.Clipboard)
    
  #def computeDistancesInPatients(self,patientList)
  #newPatient = patientList[i]
  def computeDistances(self,binfo,targetVoi):
    #Setting up
    import LoadCTX
    logic = LoadCTX.LoadCTXLogic()
    output_str = ""
    #output_str = "OAR" + "\t" + "Min" + "\t" + "Max" + "\n"
    n=0 #motion state
    minmax = [0,0]
    parameters = {}
    modelToModelCLI= slicer.modules.modeltomodeldistance
    
    #Oar for measuring distance of target
    oars = ["spinalcord", "smallerairways", "esophagus"]

    #Create new model for output
    outputModel = slicer.vtkMRMLModelNode()
    slicer.mrmlScene.AddNode(outputModel)
       
    #Load targetVoi
    filePrefix, fileExtension = os.path.splitext(binfo.filePath)
    
    filePath = filePrefix + targetVoi.name + ".nrrd"
    targetVoi.slicerNodeID[n]=logic.loadVoi(filePath,motionState=n,voi=targetVoi,threeD = True)
    
    #Parameters for CLI module    
    parameters["vtkFile1"] = targetVoi.slicerNodeID[n]
    parameters["vtkOutput"] = outputModel.GetID()
    parameters["distanceType"] = "absolute_closest_point"
    
    for oar in oars:
      voi = binfo.get_voi_by_name(oar)
      if not voi:
        print "Error," + oar + " not found."
        continue
      filePath = filePrefix + voi.name + ".nrrd"
      voi.slicerNodeID[n]=logic.loadVoi(filePath,motionState=n,voi=voi,threeD = True)
      parameters["vtkFile2"] = voi.slicerNodeID[n]   
      
      cliNode = slicer.cli.run(modelToModelCLI, None, parameters,wait_for_completion=True)
      
      array = outputModel.GetPolyData().GetPointData().GetArray(0)
      array.GetRange(minmax)
      
      output_str += str(minmax[0]) + "\n" + str(minmax[1]) + "\n"
    
    print output_str
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
    #cn.SetProperty('Volumes', 'lookupTable', slicer.util.getNode('GenericAnatomyColors').GetID() )
    cvn.SetChartNodeID(cn.GetID())
    print "Finished!"
    
  
  def loadPlan(self,patient,plan):
    import LoadCTX
    import LoadCTXLib
    
    loadLogic = LoadCTX.LoadCTXLogic()
    volumesLogic = slicer.vtkSlicerVolumesLogic()
    volumesLogic.SetMRMLScene(slicer.mrmlScene)
    if patient.slicerNodeID == '':
      filePathCT = ('/u/kanderle/AIXd/Data/FC/' + patient.name + '/CTX/'+patient.name+'_00.nrrd')
      if not os.path.exists(filePathCT):
	print "No CT at: " + filePathCT
	return
	
      slicerVolumeName = os.path.splitext(os.path.basename(filePathCT))[0]
      success, volume = slicer.util.loadVolume(filePathCT, properties = {'name' : slicerVolumeName}, returnNode=True)
      if not success:
        print "Can't load ct " + os.path.basename(filePathCT)
	return 
      
      patient.slicerNodeID = volume.GetID()
    
    return
    if plan.slicerNodeID == '':
      filePathPlan = ('/u/kanderle/AIXd/Data/FC/' + patient.name + '/Dose/' + plan.fileName[0:-7] + '_bio.nrrd')
      if not os.path.exists(filePathPlan):
	filePathPlan = ('/u/kanderle/AIXd/Data/FC/' + patient.name + '/Dose/' + plan.fileName[0:-7] + '_resample.nrrd')
	if not os.path.exists(filePathPlan):
	  print "No plan at: " + filePathPlan
	  return
	  
      slicerVolumeName = os.path.splitext(os.path.basename(filePathPlan))[0]
      volume = volumesLogic.AddArchetypeVolume(filePathPlan,slicerVolumeName)
      if not volume:
        print "Can't load dose " + os.path.basename(filePathPlan)
	return 
      plan.slicerNodeID = volume.GetID()
    
    #LoadCTXLib.addSeriesInHierarchy(patient,plan)
    
  def readTargetsFromPps(self,filePath):
    fp = open(filePath,"r")
    content = fp.read().split('\n')
    fp.close()
    targetList = []
    for line in content:
      if not line:
	continue
      #if line.find('#') > -1:
	#continue
      targetList.append(line.split()[2])
    print targetList
    return targetList

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
