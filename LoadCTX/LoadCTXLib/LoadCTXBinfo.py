import os, re

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
        print("Voi doesn't exist")
    
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
    
