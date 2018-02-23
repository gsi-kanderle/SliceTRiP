import os, re
import numpy as np


class Voi():
  def __init__(self,name,optDose=1):
    #Check for different instances of the same name
    self.optDose = optDose
    self.x=np.zeros(400)
    self.y=np.zeros(400)
    self.err=np.zeros(400)
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
    self.d95=0
    self.d95105=0
    self.d99 = 0
    self.v24Gy = 0
    self.v105 = 0
    self.v7Gy = 0
    self.v5 = 0
    self.dvhTableItems = []
    self.perscDose = 0
    self.perscVolume = 1
    self.maxPerscDose = 0
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
    self.rightSide = False #special case for two different smaller airways in Lung023
    self.slicerNodeID=[]
    self.motionStateBit=[]
    self.motionStateDescription=[]
    self.voiTableCheckBox = None #Checkbox for dvh
    self.dn = None #Double array for chart
    
    self.setSlicerNodeID()
    
    self.setName(name)

  def clear(self):
     if self.dn is not None:
       from __main__ import slicer
       slicer.mrmlScene.RemoveNode(self.dn)
     self.__init__("NewVoi")
     
  
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
  def createVoiDifference(self,voi1,voi2, norm = False):

    self.volume = voi1.volume
    if not voi1.volume == voi2.volume:
      print "Volumes not the same for: " + self.name
    
    namesList = ['calcPerscDose','maxDose','meanDose','d10','d30','d99','v24Gy','v5']
    for name in namesList:
      difference = self.getDifferenceForMethodName(name,voi1,voi2, norm)
      setattr(self, name, difference)
    
    self.setOarConstraints(1)
    if voi1.ipsiLateral or voi2.ipsiLateral:
      self.ipsiLateral = True
    

  def getDifferenceForMethodName(self,name,voi1,voi2, norm):
    try:
      method1 = getattr(voi1,name)
      method2 = getattr(voi2,name)
    except AttributeError:
      print "Method: " + name + "cannot be found"
      return None

    #Normalization
    if norm:
      if method1 <= 0.1 and method2 <= 0.1:
        result = -100 #Arbitrary value to find insignificant results
      elif not method1 == 0:
        result = (1-method2/method1)
      elif method1 == 0 and method2 == 0:
        result = 0
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
    self.maxDose = float(line.split()[3])*self.optDose
    self.meanDose = float(line.split()[4])*self.optDose
    #self.stdev = float(line.split()[5])*self.optDose
    self.mdian = float(line.split()[6])*self.optDose
    self.volume = float(line.split()[7])/1000
    self.rescaledVolume = self.volume
    self.voxVol=float(line.split()[8])
    i += 2
    n=0
    while i < len(content)-1:
      line = content[i]
      if line == "":
         break
      if re.match("H:",line) is not None:
	i += 1
	continue
      elif re.match("c:",line) is not None:
        break
      else:
	if n>=380:
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
  
  def calculateDose(self, rescale = False):
    
    # If doses are to small, set everything to zero.
    if self.maxDose < 0.01*self.optDose:
	self.d10 = 0
	self.d30 = 0
	self.d99 = 0
	self.v24Gy = 0
	self.v7Gy = 0
	self.v5 = 0
	self.calcPerscDose = 0
        return
    self.d10 = self.setValue(10)
    #self.d10 = self.d10*dose
    self.d30 = self.setValue(30)
    self.d99 = self.setValue(99)
    self.d95 = self.setValue(95)
    
    #Find out volume, which gets 24 Gy. Important for CTV
    array = abs(self.x-24)
    index = np.argmin(array)
    self.v24Gy = round(self.y[index],2)
    
    #Find out volume, which gets 25.2 Gy (105%). Important for CTV
    array = abs(self.x-25.2)
    index = np.argmin(array)
    self.v105 = round(self.y[index],2)
    
    #Find out volume, which gets 23.76 Gy (99%). Important for CTV
    array = abs(self.x-23.76)
    index = np.argmin(array)
    self.v99 = round(self.y[index],2)
    
    #Find out volume, which gets 7 Gy. Important for Lungs
    array = abs(self.x-7)
    index = np.argmin(array)
    self.v7Gy = round(self.y[index],2)
    
    #Find out volume, which gets 5% (1.2 Gy). Important for heart
    array = abs(self.x-1.2)
    index = np.argmin(array)
    self.v5 = round(self.y[index],2)
    #if self.name == "heart":
      #print self.v5
    
    if not self.perscDose == 0 and not self.rescaledVolume == 0:
      percentage = self.perscVolume*1e2/self.rescaledVolume
      
      calcDose = self.setValue(percentage)
      if calcDose > self.perscDose:
	self.overOarDose = True
      self.calcPerscDose = calcDose
    maxDose = self.setValue(3.5/self.rescaledVolume)
    self.d30 = maxDose
    
    if rescale:
      if not self.maxPerscDose == 0:
        #print "Seting " + self.name +  str(self.maxDose) + " to " + str(self.maxPerscDose)
	self.maxDose /= self.maxPerscDose
      if not self.perscDose == 0:
	self.calcPerscDose /= self.perscDose
        
     
  def findV(self,value):
    array = abs(self.x-value)
    index = np.argmin(array)
    return round(self.y[index],2)
  
  def setValue(self,value,show = False):
    #special case, to disregard the no dose
    x=self.x
    y=self.y
    if y[1] == 0:
      return 0
    array = abs(y-value)
    
    if value > 1:
       #Reverse order to avoid confusion with the first elements
       index = np.argmin(array[::-1])
       index = len(array) - index - 1
    else:
       #except for small values
       index = np.argmin(array)

    if index:
      #special case, if index == 0
      if index == 0:
         return 0
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
    
  def setOarConstraints(self, case = 1):
    
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
      return False
    
    perscVolume=[0.35,15,5,10,0.5,
             10,4,1500,1500,1500,
             700,3,10,4,4,
             4,10,10,0.5,10,
             0.5]
    if case == 1:
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
    elif case == 2:
      norm = 27
      perscDose = [18,24,17.7,16.5,18.9,
		   39,15,norm,norm,norm,
		   norm, 1, 39, 15, 15,
		   15, 39,39,18.9,39,
		   18.9]
      maxPerscDose = [21.9, 30.0, 25.2, 22.2, 23.1,
		      45, 30.0, norm, norm, norm,
		      norm, 1.0, 45.0, 30.0, 30.0,
		      30.0, 45.0, 45.0, 23.1, 45.0,
		      23.1]
      
    elif case == 3:
      norm = 7.5
      perscDose = [23.0, 32.0, 19.5, 18.0, 21.0,
		   47.0, 16.5, norm, norm, norm,
		   norm, 1.0, 47.0, 16.5, 16.5,
		   16.5, 47.0, 47.0, 21.0, 47.0,
		   21.0  ]
      maxPerscDose = [30.0, 38.0, 35.0, 32.0, 33.0,
		      53.0, 40.0, norm, norm, norm,
		      norm, 1.0, 53.0, 40.0, 40.0,
		      40.0, 53.0, 53.0, 33.0, 50.0,
		      33.0]
      #We are looking at single fraction plan
      perscDose = np.array(perscDose) / 5
      maxPerscDose = np.array(maxPerscDose) / 5
    else:
      print "Unknown Case " + str(case)
      return True
		      
    self.perscDose = perscDose[index]
    self.perscVolume = perscVolume[index]
    self.maxPerscDose = maxPerscDose[index]
    
    if not self.maxPerscDose == 0 and self.maxDose > self.maxPerscDose:
      self.overOarDose = True
    
    # Some VOI volumes differ in 4D CT and Planning CT (i.e. if it has less slices). So this flag is used for comparing VOI volumes.
    # First you specified for which patient you want to check, then you input all volumes.
    #If you don't know it, or don't need it, just input 0.
    
    
  def readVolumes(self,patientFlag):
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
      
  def setVolumes(self):
    if self.name.find('ctv') > -1 or self.name.find('itv') > -1 or self.name.find('ptv') > -1:
      return
    if not self.rescaledVolume == 0:
      if abs(self.volume-self.rescaledVolume)/self.rescaledVolume > 0.1:
	self.y = np.array(self.y)*self.volume/self.rescaledVolume
	self.meanDose *= self.volume/self.rescaledVolume


  def setName(self,name):
    #self.name = name
    #return
    if name.find('PA') > -1 or name.find('Pulmonary') > -1:
      name = 'vesselslarge'
    #if name.find('.'):
      #name = name.replace(".","")
    name = name.lower()
    #if name.find("smallerairways") > -1: #or name.find("airwayssmall") > -1:
	#name = "smallerairways"
    if name.find("smallerairways1") > -1 or name.find("airwayssmalll") > - 1:
       name = "smallerairways"
       self.rightSide = False
    if name.find("airwayssmallr") > -1:
        name = "smallerairways"
        self.rightSide = True
    if name.find("spinalcord") > -1:
      name = "spinalcord"
    if name.find("largebronchus") > -1:
      name = "airwayslarge"
    if name.find("traquea") > -1 or name.find("trtachea") > -1 or name.find("trachea1") > -1:
      name = "trachea"
    if name.find("lungtotal-ptv1") > -1 or name.find("lungsptv") > -1:
      name = "lungs-ptv"
    
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
    
  def setSlicerDoubleArray(self): 
    if self.dn is not None:
      return
    from __main__ import slicer
    self.dn = slicer.mrmlScene.AddNode(slicer.vtkMRMLDoubleArrayNode())
    array = self.dn.GetArray()
    #Trim zeroes
    x = np.trim_zeros(self.x,'b')
    array.SetNumberOfTuples(len(x))
    for i in range(len(x)):
       array.SetComponent(i, 0, x[i])
       array.SetComponent(i, 1, self.y[i])
       array.SetComponent(i, 2, self.err[i])
