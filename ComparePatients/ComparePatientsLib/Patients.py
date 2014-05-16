import os, re
import numpy
import Voi


# This are patient python objects, which contain all data from comparison study of SBRT and carbon ions.
# Author: K. Anderle
#
# 07. May 2014


# Function that compares bestPlan to sbrt plan   
def compareToSbrt(patient,voiList=[]):
  if patient.voiDifferences:
    print patient.name + " already has voi Differences."
    return True
  
  if not patient.bestPlan:
    patient.loadBestPlan()
    if not patient.bestPlan:
      print "No best plan."
      return False
  
  sbrtPlan = None
  for plan in patient.plans:
    if plan.sbrt:
      sbrtPlan = plan
      
  if not sbrtPlan:
    print "No sbrt plan"
    return False
  
  findIpsiLateralLung(sbrtPlan)
  
  if not voiList == []:
    for voi in voiList:
      voiSbrt = sbrtPlan.get_voi_by_name(voi)
      voiPlan = patient.bestPlan.get_voi_by_name(voi)
      if voiPlan and voiSbrt:
	v = Voi.Voi(voi)
	v.createVoiDifference(voiSbrt,voiPlan)
	patient.voiDifferences.append(v)
      else:
	print "No voi: " + voi
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
def readPatientData(newPatient):
  if not newPatient:
    print "Error, no newPatient!"
    
  
  filePath = '/u/kanderle/AIXd/Data/FC/' + newPatient.name
    
  if os.path.exists(filePath):
    filePathGD = filePath + '/GD/'
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
	if filePrefix.find('4D') > -1:
	  newPlan = Plan()
	  newPlan.fileName = fileName
	  #Get info from filename
	  newPlan.readGDFileName(filePrefix)
	  # Read dvh and add vois
	  newPlan.patientFlag = newPatient.number
	  newPlan.readGDFile(filePathGD + fileName)
	  newPatient.add_plan(newPlan)
	  if not newPatient.bestPlan:
	    if not newPlan.targetPTV:
	      newPatient.bestPlan = newPlan
	  else:
	    if newPlan.targetPTV:
	      pass
	    else:
	      print "Find new best plan for: " + newPatient.name
	      newPatient.bestPlan = None
        if filePrefix.find('sbrt') > -1:
	  newPlan = Plan()
	  newPlan.patientFlag = newPatient.number
	  newPlan.fileName = fileName
	  newPlan.readGDFile(filePathGD + fileName)
	  newPlan.sbrt = True
	  newPlan.targetPTV = True
	  newPatient.add_plan(newPlan)
      if fileExtension == '.txt':
	if filePrefix.find('sbrt') > -1:
	  if filePrefix.find('dvh') > -1:
	    continue	    
	  newPlan = Plan()
	  newPlan.patientFlag = newPatient.number
	  newPlan.fileName = fileName
	  newPlan.readTxtFile(filePathGD + fileName)
	  newPatient.add_plan(newPlan)
	   

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
    self.bestPlan = None
    self.infoFilePath = '/u/kanderle/AIXd/Data/FC/' + name + '/' + name + '_info.txt'
    self.slicerTable = None
    
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
        
  
  def loadBestPlan(self):
    filePath = self.infoFilePath
    if not os.path.isfile(filePath):
      print "No bestPlan file."
      return
    f = open(filePath,"r")
    content = f.read().split('\n')
    f.close()
    for column in content:
      if column.find('BestPlan') > -1:
	print "Found plan"
	fileName = column.split()[1]
    
    for plan in self.plans:
      if plan.fileName == fileName:
	print "Found Best Plan."
	self.bestPlan = plan
	
    if not self.bestPlan:
      print "Error, couldn't load best Plan."
    
  
  def saveBestPlan(self):
    if not self.bestPlan:
      print "No best Plan yet!"
      return
    filePath = self.infoFilePath
    if os.path.isfile(filePath):
      f = open(filePath,"r")
      content = str(f.read())
      f.close()
      if content.find('BestPlan:') > -1:
	print "Already exist"
        return
    else:
      content = ""
    content += 'BestPlan:\t' + self.bestPlan.fileName
    
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
    self.slicerNodeID = []
    
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
        print("Voi doesn't exist")


  def readTxtDvhFile(self,filePath):
    
    self.filePath = filePath
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
	voiOn = False

      if volumeOn:
	if v:
	  volume = float(column)
	  if abs(v.volume - volume) < 0.1:
	    print "Volumes not matching for " + v.name
	
	volumeOn = False
      
      if column.find('of') > -1:
	volumeOn = True
	
      #Last thing before new voi
      if column.find('cc') > -1:
	voiOn = True
	i += 2
      
      
    
  def readGDFileName(self,filePrefix): 
    
    self.sbrt = False

    #Find various parameters from file name
    find = filePrefix.find('f_')
    if find > 0:
      self.numberOfFields = int(filePrefix[find-1])
      
    find = filePrefix.find('_d')
    if find > -1:
      self.optDose = int(filePrefix[find+2:find+4])
      
    find = filePrefix.find('_b')
    if find > 0:
      self.numberOfFields = int(filePrefix[find+2:find+4])
      
    if filePrefix.find('PTV') > -1:
      self.targetPTV = True
      
    if filePrefix.find('binrem') > -1:
      self.binRemove = True
      
    find = filePrefix.find('oar')
    if find > -1:
      self.oarSet = True
      filePrefixRest = filePrefix[find:]
      find2 = filePrefixRest.find('_')
      find3 = filePrefixRest.find('.dvh')
      if find2 > -1:
	self.oarMaxDoseFraction = float(filePrefixRest[3:find2-1])	
      if find3 > -1:
	if find2+1 == find3-1:
	  self.oarWeigth = float(filePrefixRest[find2+1])
	else:
	  self.oarWeigth = float(filePrefixRest[find2+1:find3-1])
	  
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
      v = Voi.Voi(line.split()[0], self.optDose)
      v.readTxtFile(line)
      v.setOarConstraints()
      v.setDefaultVolumes(self.patientFlag)
      self.add_voi(v)
  
  def readGDFile(self,filePath):
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
	  v = Voi.Voi(line.split()[1], self.optDose)
	  i = v.readGDFile(content,i)
	  v.setOarConstraints()
	  v.setVolumes(self.patientFlag)
	  v.calculateDose()
	  self.add_voi(v)
	  #print v.name
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
