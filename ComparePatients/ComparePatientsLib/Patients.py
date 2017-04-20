import os, re
import numpy
import Voi


# This are patient python objects, which contain all data from comparison study of SBRT and carbon ions.
# Author: K. Anderle
#
# 07. May 2014


# Function that compares bestPlan to sbrt plan   
def compareToSbrt(patient,voiList=[],planPTV = False, normOn = False):
  #if patient.voiDifferences:
    #print patient.name + " already has voi Differences."
    #return True
  
  if planPTV:
    patient.loadPTVPlan()
    
  if not patient.bestPlan and not planPTV:
    patient.loadBestPlan()

  
  if not patient.bestPlan:
    print "No best plan"
    return False
  else:
    print patient.name + " has best plan: " + patient.bestPlan.fileName
  
  sbrtPlan = None
  sbrtPlan = patient.best3DPlan
  #sbrtPlan = patient.loadSBRTPlan()
  
      
  if not sbrtPlan:
    print "No sbrt plan"
    return False
  
  findIpsiLateralLung(sbrtPlan)
  
  if not voiList == []:
    for voi in voiList:
      voiSbrt = sbrtPlan.get_voi_by_name(voi)
      voiPlan = patient.bestPlan.get_voi_by_name(voi)
      
      if voiSbrt:
	#If there's no VOI in plan it has dose 0.
	if voiPlan:
	  v = Voi.Voi(voi)
	  #if voiSbrt.name.find('lung') > -1:
		  #print voiSbrt.name + "has d10 sbrt: " + str(voiSbrt.d10)
		  #print voiSbrt.name + "has d10 pt: " + str(voiPlan.d10)
		  
	  v.createVoiDifference(voiSbrt,voiPlan, normOn)
	  patient.voiDifferences.append(v)

	else:
	  patient.voiDifferences.append(voiSbrt)
  else:
    for voiSbrt in sbrtPlan.vois:
      voiPlan = patient.bestPlan.get_voi_by_name(voiSbrt.name)
      if voiPlan:
        v = Voi.Voi(voiSbrt.name)
        v.createVoiDifference(voiSbrt, voiPlan)
        patient.voiDifferences.append(v)
      else:
        print voiSbrt.name + " no instance in PT plan"
        
  return True
        
#Find out ipsi and contralateral lung, just by checking if the dose is higher than 20 Gy.
def findIpsiLateralLung(plan):
  voiLungL = plan.get_voi_by_name('lungl')
  voiLungR = plan.get_voi_by_name('lungr')
  if not voiLungL and not voiLungR:
    print "Cannot find lung voi"
    return
  if voiLungL.maxDose > 20:
    voiLungL.ipsiLateral = True
  elif voiLungR.maxDose > 20:
    voiLungR.ipsiLateral = True
  else:
    print "No lung has dose higher than 20 Gy"

  

#Goes through directory and reads all data into newPatient
def readPatientData(newPatient,planPTV=False, refPhase = 0):
  if not newPatient:
    print "Error, no newPatient!"
    
  print "BU"
  filePath = '/u/kanderle/AIXd/Data/FC/' + newPatient.name
  twoPlans = False #Flag for setting the best plan  
  
  if os.path.exists(filePath):
    filePathGD = filePath + '/GD/Old/'
    if not os.path.isfile(filePathGD + newPatient.name + '_sbrt.dvh.gd'):
      print "No file at " + filePathGD + newPatient.name + '_sbrt.dvh.gd'
      return 
    sbrtPlan = newPatient.loadSBRTPlan()
    if not sbrtPlan:
	    sbrtPlan = Plan()
	    sbrtPlan.patientFlag = newPatient.number
	    sbrtPlan.fileName = newPatient.name + '_sbrt.dvh.gd'
	    #Manual input, because it can't read it from fileName
	    sbrtPlan.optDose = 25
	    sbrtPlan.sbrt = True
	    sbrtPlan.targetPTV = True
	    newPatient.add_plan(sbrtPlan)
    
    
    sbrtPlan.readGDFile(filePathGD + newPatient.name + '_sbrt.dvh.gd')
    
    for fileName in os.listdir(filePathGD):
      skip = False
      filePrefix, fileExtension = os.path.splitext(fileName)
      for plan in newPatient.plans:
	if fileName == plan.fileName:
	  skip = True
      if skip:
	continue
      if fileExtension == '.gd':
        # Take only 4D doses into account
	if filePrefix.find('4D') > -1 or filePrefix.find('3D'):
	  newPlan = Plan()
	  newPlan.fileName = fileName
	  #Get info from filename
	  newPlan.readGDFileName(filePrefix)
	  #Add manual optDose = 25, because plan / dose(25) is set in all 4D calc (even if name says d26.5)
	  newPlan.optDose = 25
	  # Read dvh and add vois
	  newPlan.patientFlag = newPatient.number
	  newPlan.readGDFile(filePathGD + fileName,sbrtPlan)
	  newPatient.add_plan(newPlan)
	  if not planPTV and not newPlan.targetPTV and not twoPlans:
            if not newPatient.bestPlan:
	      newPatient.bestPlan = newPlan
            if not newPatient.best3DPlan:
              if filePrefix.find('ref' + str(refPhase)) > -1:
                newPatient.best3DPlan = newPlan
	    else:
	      newPatient.bestPlan = None
              newPatient.best3DPlan = None
	      twoPlans = True
        #if filePrefix.find('sbrt') > -1:
	  #if newPatient.number == 21:
	    #continue
	  #Find existing sbrt plan, otherwise create new
	  
      #if fileExtension == '.txt':
	##Patient 021 special case, we take only Left Target for now
	#if newPatient.number == 21:
	    #if filePrefix.find('_L') < 0:
	      #continue
	#if filePrefix.find('sbrt') > -1:
	  ##Find existing sbrt plan, otherwise create new
	  #sbrtPlan = newPatient.loadSBRTPlan()
	  #if not sbrtPlan:
	    #sbrtPlan = Plan()
	    #sbrtPlan.patientFlag = newPatient.number
	    #sbrtPlan.fileName = fileName
	    #newPatient.add_plan(sbrtPlan)
	  ##Read values and dvh 
	  #if filePrefix.find('dvh') > -1:
	    #sbrtPlan.readTxtDvhFile(filePathGD + fileName)
	  #else:
	    #sbrtPlan.readTxtFile(filePathGD + fileName)
	  

class Patient():
  def __init__(self,name):
    self.name = name
    self.number = -1
    self.info = ''
    self.numberOfTargets = 0
    self.vois = []
    self.plans = []
    self.voiDifferences = []
    self.slicerNodeID = ''
    self.slicerSubjectNodeID = ''
    self.bestPlan = None
    self.best3DPlan = None
    self.infoFilePath = '/u/kanderle/AIXd/Data/FC/' + name + '/' + name + '_info.txt'
    self.slicerTable = None
    self.segmentation = None
    self.this = "WhAT?"
    
  def get_voiDifferences_names(self):
        if not self.voiDifferences:
	  print "Voi difference not calculated."
	  return
        names = []
        for voi in self.voiDifferences:
            names.append(voi.name)
        return names
        
  def add_voi(self,voi):
    self.vois.append(voi)
    
  def get_voiDifference_by_name(self,name):
        if not self.voiDifferences:
	  print "Voi difference not calculated."
	  return
        for voi in self.voiDifferences:
            if voi.name.lower() == name.lower():
                return voi
            if voi.name.find(name) > -1:
	      return voi

        
  def get_plan_names(self):
        names = []
        for plan in self.plans:
            names.append(plan.name)
        return names
        
  
  def loadPTVPlan(self):
    self.loadBestPlan(True)
    if self.bestPlan:
      return
    for plan in self.plans:
      if not plan.sbrt and plan.targetPTV:
	self.bestPlan = plan
	return
    self.bestPlan = None
    
  def loadSBRTPlan(self):
    for plan in self.plans:
      if plan.sbrt:
	return plan
        #if self.name == 'Lung021':
	  ##if plan.fileName.find('_L') > -1 or plan.fileName.find('_R') > -1: 
	    ##continue
	  #if plan.fileName.find('_L') < 0:
	    #continue
        
    return None
  
  def loadBestPlan(self,PTV=False,refPhase = 0):
    filePath = self.infoFilePath
    fileName = ''
    if not os.path.isfile(filePath):
      print "No bestPlan file."
      return
    f = open(filePath,"r")
    content = f.read().split('\n')
    f.close()
    for column in content:
      if PTV:
        if column.find('BestPTVPlan') > -1:
          fileName = column.split()[1]      
      else:
        if column.find('BestPlan') > -1:
	  fileName = column.split()[1]
      
    if not fileName:
      return

    index = fileName.find('4D')
    newFileName = fileName[0:index] + '3D_ref' + str(refPhase) + fileName[index+2:]
    #if not os.path.isfile(newFileName):
      #print "Can't find file " + newFileName

    for plan in self.plans:
      if plan.fileName == fileName:
	self.bestPlan = plan
      if plan.fileName == newFileName:
        self.best3DPlan = plan
	
    if not self.bestPlan or not self.best3DPlan:
      print "Error, couldn't load best Plan."

 
    
  
  def saveBestPlan(self):
    if not self.bestPlan:
      print "No best Plan yet!"
      return
    filePath = self.infoFilePath
    if self.bestPlan.targetPTV:
      name = 'BestPTVPlan:'
    else:
      name = 'BestPlan:'
    if os.path.isfile(filePath):
      f = open(filePath,"r")
      content = str(f.read())
      f.close()
      if content.find(name) > -1:
	print "Already exist"
        return
    else:
      content = ""
    content += name + '\t' + self.bestPlan.fileName + '\n'
    
    f = open(filePath,"wb+")
    f.write(content)
    f.close() 
  
  def add_plan(self,plan):
    self.plans.append(plan)
    
  #def get_plan_by_name(self,name):
        #for plan in self.plans:
            #if plan.name.lower() == name.lower():
                #return plan
        #print("Plan doesn't exist")
  
  

        
class Plan():
  def __init__(self):
    self.fileName = ''
    self.sbrt = False
    self.couchAngle = []
    self.gantryAngle = []
    self.numberOfFields = 0
    self.dvh = None
    self.optDose = 0
    self.targetPTV = False
    self.binRemove = False
    self.bolus = 0
    self.oarSet = False
    self.oarMaxDoseFraction = 0
    self.oarWeigth = 0
    self.patientFlag = 0
    self.vois = []
    self.slicerNodeID = ''
    
    #self.voiTable = None
    self.voiTableCheckBox = []
    self.horizontalHeaders=['Show:',"Max(Gy)","D99%(Gy)","V95%(Gy)","D30(Gy)","per. Volume (Gy)","Volume(cc)"]
    
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
            if voi.name.find(name) > -1:
	      return voi


  def readTxtDvhFile(self,filePath):
    
    self.filePath = filePath
    self.sbrt = True
    
    fp = open(filePath,"r")
    content = fp.read().split('\n')
    fp.close()
    n=len(content)
    line = content[0]
    i = 0
    #Set a flag to know, when voi comes
    voiOn = True
    volumeOn = False
    v = None
    for column in line.split():
      
      if voiOn:
	v = self.get_voi_by_name(column)
	if not v:
	  v = Voi.Voi(column)
	  self.add_voi(v)
	  
	v.readTxtDvhFile(content,i)
	v.calculateDose()
	voiOn = False

      if volumeOn:
	if v:
	  volume = float(column)
	  #if abs(v.volume - volume) < 0.1:
	    #print "Volumes not matching for " + v.name
	
	volumeOn = False
      
      if column.find('of') > -1:
	volumeOn = True
	
      #Last thing before new voi
      if column.find('cc') > -1:
	voiOn = True
	i += 2
      
      
  def readTxtFile(self,filePath):
    self.filePath = filePath
    self.sbrt = True
    self.targetPTV = True
    fp = open(filePath,"r")
    content = fp.read().split('\n')
    fp.close()
    n=len(content)
    i=1
    for line in content:
      if not line:
	continue
      if line.split()[0] == 'Oar':
	continue
      v = self.get_voi_by_name(line.split()[0])
      if not v:
        v = Voi.Voi(line.split()[0], self.optDose)
        self.add_voi(v)
      v.readTxtFile(line)
      v.setOarConstraints()
      v.setDefaultVolumes(self.patientFlag)
        
  
  def readGDFileName(self,filePrefix): 
    
    self.sbrt = False

    #Find various parameters from file name
    find = filePrefix.find('f_')
    if find > 0:
      self.numberOfFields = int(filePrefix[find-1])
      
    find = filePrefix.find('_d')
    if find > -1:
      self.optDose = int(filePrefix[find+2:find+4])
      
    #find = filePrefix.find('_b')
    #if find > 0:
      #self.numberOfFields = int(filePrefix[find+2:find+4])
      
    if filePrefix.find('PTV') > -1:
      self.targetPTV = True
      
    #if filePrefix.find('binrem') > -1:
      #self.binRemove = True
      
    #find = filePrefix.find('oar')
    #if find > -1:
      #self.oarSet = True
      #filePrefixRest = filePrefix[find:]
      #find2 = filePrefixRest.find('_')
      #find3 = filePrefixRest.find('.dvh')
      #if find2 > -1:
	#self.oarMaxDoseFraction = float(filePrefixRest[3:find2-1])	
      #if find3 > -1:
	#if find2+1 == find3-1:
	  #self.oarWeigth = float(filePrefixRest[find2+1])
	#else:
	  #self.oarWeigth = float(filePrefixRest[find2+1:find3-1])
	  
  
  def readGDFile(self,filePath,sbrtPlan=None):
    self.filePath=filePath
    fp = open(filePath,"r")
    content = fp.read().split('\n')
    fp.close()
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
	  v = self.get_voi_by_name(line.split()[1])
	  if not v:
	    v = Voi.Voi(line.split()[1], self.optDose)
	    self.add_voi(v)
	  i = v.readGDFile(content,i)
	  v.setOarConstraints()
	  if sbrtPlan is not None:
	    sbrtVoi = sbrtPlan.get_voi_by_name(v.name)
	    if sbrtVoi:
	      v.rescaledVolume = sbrtVoi.volume
	    #else:
	      #print "Can't set volumes for " + v.name
	    v.setVolumes()
	  v.calculateDose()
	  
          #v.setSlicerOrigin(self.dimx,self.dimy,self.pixel_size)
      i += 1

  #TODO 
  def exportValuesAsText(self, filePath ):
    output_str = self.setOutputValues()
    f = open(filePath,"wb+")
    f.write(output_str)
    f.close()  
  
  def exportValuesOnClipboard(self):
    output_str = self.setOutputValues()

    
  def setOutputValues(self):
    dose = self.optDose
    output_str = 'Name\tMean Dose\tV10%\tV30%\tV99%\tV(onDose)\tMax Point Dose\tVolume (mm3) \n'
    voiOrder = ["heart","spinalcord","smallerairways","esophagus","trachea",
                "aorta","vesselslarge","airwayslarge","brachialplexus","carina",
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
  
  def setTable(self,table):
    from __main__ import qt
    if not table:
      print "No table."
      return
    
    
    table.setColumnCount(len(self.horizontalHeaders))
    table.setHorizontalHeaderLabels(self.horizontalHeaders)
    table.setEditTriggers(qt.QAbstractItemView.NoEditTriggers)

    table.setRowCount(len(self.vois))
    table.setVerticalHeaderLabels(self.get_voi_names())
        
    print self.fileName
    
    for i in range(0,len(self.vois)):
      checkBox = qt.QCheckBox()
      if checkBox:
        self.voiTableCheckBox.append(checkBox)
        table.setCellWidget(i,0,checkBox)
      voi = self.vois[i]
      doseValues = [str(voi.maxDose)+"/"+str(voi.maxPerscDose),str(voi.d99),str(voi.v95),str(voi.d30),
           str(voi.calcPerscDose)+"/"+str(voi.perscDose),str(voi.volume)+"/"+str(voi.rescaledVolume)]
      self.setVoiTable(table,voi,doseValues,i)
      #self.voiComboBox.addItem(voi)
    
    table.visible = True
    table.resizeColumnsToContents()

    
 
  def setVoiTable(self,table,voi,doseValues,n):
    voi.setDvhTableItems(self.horizontalHeaders)
    #doseValues = [str(voi.maxDose)+"/"+str(voi.maxPerscDose),str(voi.d99),str(voi.d10),str(voi.d30),
           #str(voi.calcPerscDose)+"/"+str(voi.perscDose),str(voi.volume)]
    for i in range(1,len(self.horizontalHeaders)):
      item = voi.dvhTableItems[i-1]
      table.setItem(n,i,item)
      if not len(doseValues) == len(voi.dvhTableItems):
	print "Not enough table items, check code."
      item.setText(doseValues[i-1])
      #if voi.overOarDose:
	#item.setBackground(qt.QColor().fromRgbF(1,0,0,1))

