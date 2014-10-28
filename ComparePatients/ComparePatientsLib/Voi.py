import os, re
import numpy as np


class Voi():
  def __init__(self,name,optDose=1):
    #Check for different instances of the same name
    self.setName(name)    
    self.optDose = optDose
    self.x=np.zeros(129)
    self.y=np.zeros(129)
    self.err=np.zeros(129)
    # All dose values must be in Gy
    self.minDose = 0
    self.maxDose = 0
    self.meanDose = 0
    self.stdev = 0
    self.mdian = 0
    self.volume = 0 # in cc
    self.rescaledVolume = 0 # if different in PT
    self.voxVol=0
    self.d10=0
    self.d30=0
    self.d95105=0
    self.d99 = 0
    self.v24Gy = 0
    self.dvhTableItems = []
    self.perscDose = 0
    self.perscVolume = 1
    self.maxPerscDose = 0
    self.rescaledVolume = 0
    self.calcPerscDose = 0
    self.overOarDose = False
    self.ipsiLateral = False
    self.doubleArrayNode = None #Slicer double array node
    #Display settings
    self.N_of_motion_states=1 #Default
    self.offsetx=0
    self.offsety=0
    self.offsetz=0
    self.voi_type=''
    self.voiNumber=0
    self.slicerNodeID=[]
    self.motionStateBit=[]
    self.motionStateDescription=[]
    
    self.setSlicerNodeID()

  def readTxtDvhFile(self, content, i):
    n = len(content)
    self.x = np.zeros(n-1)
    self.y = np.zeros(n-1)
    row = 1
    while row < n:
      line = content[row]
      if line:
	
	self.x[row] = float(line.split()[i])
	self.y[row] = float(line.split()[i+1])
      row += 1
    
  #Function for creating difference between two voi values
  def createVoiDifference(self,voi1,voi2):
    if not voi1.volume == voi2.volume:
      print "Volumes not the same for: " + self.name
    self.volume = voi1.volume
    
    namesList = ['calcPerscDose','maxDose','meanDose','d10','d30','d99','v24Gy']
    for name in namesList:
      difference = self.getDifferenceForMethodName(name,voi1,voi2)
      setattr(self, name, difference)
    
    self.setOarConstraints()
    if voi1.ipsiLateral or voi2.ipsiLateral:
      self.ipsiLateral = True
    

  def getDifferenceForMethodName(self,name,voi1,voi2):
    try:
      method1 = getattr(voi1,name)
      method2 = getattr(voi2,name)
    except AttributeError:
      print "Method: " + name + "cannot be found"
      return None

    #Normalization
    if 0:
      if not method1 == 0:
        result = (1-method2/method1)
      elif method1 == 0 and method2 == 0:
        result = 1
      else:
        result = -1
    else:
      if method1 <= 0.1 and method2 <= 0.1:
        result = -100 #Arbitrary value to find insignificant results
      else:
        result = method1 - method2
    return result
    
    
  def readTxtFile(self,line):
    self.volume = round(float(line.split()[1]),2)
    self.meanDose = round(float(line.split()[2]),2)
    self.minDose = round(float(line.split()[3]),2)
    self.maxDose = round(float(line.split()[4]),2)
    if not line.split()[5] == "":
      if self.name.find('ctv') > -1:
	self.d99 = round(float(line.split()[5]),2)
      else:
        self.calcPerscDose = round(float(line.split()[5]),2)
    if len(line.split()) > 7:
      if not line.split()[6] == "":
	self.d10 = round(float(line.split()[6]),2)
      if not line.split()[7] == "":
	self.d30 = round(float(line.split()[7]),2)
  
  def readGDFile(self,content,i):
    line = content[i]
    
    if line is '':
      return i
      
    #self.name = string.join(line.split()[1:],' ')
    self.minDose = float(line.split()[2])*self.optDose
    self.maxDose = round(float(line.split()[3]),2)*self.optDose
    self.meanDose = float(line.split()[4])*self.optDose
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
    
    # If doses are to small, set everything to zero.
    if self.maxDose < 0.01*self.optDose:
	self.d10 = 0
	self.d30 = 0
	self.d99 = 0
	self.v24Gy = 0
	self.calcPerscDose = 0
        return
    self.d10 = self.setValue(10)
    #self.d10 = self.d10*dose
    self.d30 = self.setValue(30)
    self.d95105 = self.setValue(95) - self.setValue(105)
    self.d99 = self.setValue(99)
    
    #Find out volume, which gets 24 Gy. Important for CTV
    array = abs(self.x-24)
    index = np.argmin(array)
    self.v24Gy = round(self.y[index],2)
    
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
      #If difference between value and y is more than 1%, do linear interpolation,
      #if index is not the last element in array
      if abs(y[index] - value) > 1 and index < len(x)-1:
	#Switch x and y and find if left or right value
	if y[index] - value > 0:
	  interp_y = [ x[index+1], x[index] ]
	  interp_x = [ y[index+1], y[index] ]
	else:
	  #Special case in index-1 = 0
	  if index-1 == 0:
	    interp_x = [ y[index], self.maxDose ]
	  else:
	    interp_x = [ y[index], y[index-1] ]  
	  interp_y = [ x[index], x[index-1] ]
	result = np.interp(value, interp_x, interp_y)
      else:
        result = x[index]
      return round(result,2)
    else:
      return 0
      
    
  def setDefaultVolumes(self,patientFlag):
    if patientFlag == 0:
      print "Wrong patient number!"
      
    if patientFlag < 10:
      number = '0' + str(patientFlag)
    else:
      number = str(patientFlag)
    filePath = '/u/kanderle/AIXd/Data/FC/Lung0' + number + '/Contour/voiVolumes.txt'
    if os.path.isfile(filePath):
      f = open(filePath,"r")
      content = str(f.read())
      f.close()
      if content.find(self.name) > -1:
        return
    else:
      content = ""

    content += self.name + "\t" + str(self.volume) +"\n"
    f = open(filePath,"wb+")
    f.write(content)
    f.close() 
    
  def setOarConstraints(self):
    
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
     #For lungs and liver max dose is "24 Gy" for normalization purposes only          
    norm = 24
    maxPerscDose=[14,22,15.4,12.4,13.3,
              37,20.2,norm,norm,norm,
              norm,17.5,37,20.2,20.2,
              20.2,37,37,13.3,37,
              13.3]
    self.perscDose = perscDose[index]
    self.perscVolume = perscVolume[index]
    self.maxPerscDose = maxPerscDose[index]
    
    if not self.maxPerscDose == 0 and self.maxDose > self.maxPerscDose:
      self.overOarDose = True
    
    # Some VOI volumes differ in 4D CT and Planning CT (i.e. if it has less slices). So this flag is used for comparing VOI volumes.
    # First you specified for which patient you want to check, then you input all volumes.
    #If you don't know it, or don't need it, just input 0.
    
    
  def setVolumes(self,patientFlag):
    #Skip target volumes
    if self.name.find('ctv') > -1 or self.name.find('itv') > -1 or self.name.find('ptv') > -1:
      return
    rescaledVolume = 0
    if patientFlag == 0:
      print "Wrong patient number!"
      
    if patientFlag < 10:
      number = '0' + str(patientFlag)
    else:
      number = str(patientFlag)
    filePath = '/u/kanderle/AIXd/Data/FC/Lung0' + number + '/Contour/voiVolumes.txt'
    if os.path.isfile(filePath):
      f = open(filePath,"r")
      content = f.read().split('\n')
      f.close()
      for line in content:
	if not line:
	  continue
	if line.split()[0] == self.name.lower():
	  rescaledVolume = float(line.split()[1])
      
    if not rescaledVolume == 0:
      if abs(self.volume-rescaledVolume)/rescaledVolume > 0.1:
	self.y = np.array(self.y)*self.volume/rescaledVolume
	self.rescaledVolume = rescaledVolume

      
  def setName(self,name):
    #self.name = name
    #return
    if name.find('PA') > -1 or name.find('Pulmonary') > -1:
      name = 'vesselslarge'
    #if name.find('.'):
      #name = name.replace(".","")
    name = name.lower()
    if name.find("smallerairways") > -1 or name.find("airwayssmall") > -1:
	name = "smallerairways"
    if name.find("spinalcord") > -1:
      name = "spinalcord"
    if name.find("largebronchus") > -1:
      name = "airwayslarge"
    self.name = name
    
  def setDvhTableItems(self,horizontalHeaders):
    from __main__ import qt
    
    self.dvhTableItems=[]
    for i in range(0,len(horizontalHeaders)-1):
      item = qt.QTableWidgetItem()
      self.dvhTableItems.append(item)
    self.calculateDose()
    
  #Display functions
  def read_binfo(self,content,i):
    line = content[i]
    #self.name = string.join(line.split()[1:],' ')
    if line.split()[3]=='0':
      self.voi_type='OAR'
    else:
      self.voi_type='Target'
      
    #Residual is sometimes added as NanQ.
    if line.split()[5] == 'NaNQ':
       i += 1
    else:
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