import os, re
import numpy as np
import Voi


# This are patient python objects, which contain all data from comparison study of SBRT and carbon ions.
# Author: K. Anderle
#
# 07. May 2014


# Function that compares bestPlan to sbrt plan   
def compareToSbrt(patient,voiList=[],compareWith = "SBRT"):
  #if patient.voiDifferences:
    #print patient.name + " already has voi Differences."
    #return True
    
  normalize = False
  #if not patient.bestPlan:
  patient.loadBestPlan()

  
  if not patient.bestPlan:
    print "No best plan"
    return False
  else:
    print patient.name + " has best plan: " + patient.bestPlan.fileName
  
  sbrtPlan = None
  if compareWith == '3D':
    sbrtPlan = patient.best3DPlan
  elif compareWith == 'int':
    sbrtPlan = patient.bestIntPlan
  elif compareWith == 'SBRT':
    sbrtPlan = patient.loadSBRTPlan()
  elif compareWith == 'bio':
    sbrtPlan = patient.bestBioPlan
  else:
    print "Unkown command: " + compareWith
    return False
  
      
  if not sbrtPlan:
    print "No sbrt plan"
    return False

  print "Comparing to: " + sbrtPlan.fileName
  
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
		  
	  v.createVoiDifference(voiSbrt,voiPlan, normalize)
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

#Compares different motions
def compareDifferentMotions(patient,outputAllData,metric,compareWith):
  if not patient:
    print "Error, no patient."
    return ""
  
  if not patient.bestPlan or not patient.best3DPlan:
    patient.loadBestPlan()

  
  if not patient.bestPlan:
    print "No best plan"
    return ""
  else:
    print patient.name + " has best plan: " + patient.bestPlan.fileName
  
  if compareWith == 'int':
    numberOfPlans = 8
    if not patient.bestIntPlan:
      print "No interplay plan"
      return ""
    comparePlan = patient.bestIntPlan
  elif compareWith == '3D':
    comparePlan = patient.best3DPlan
    numberOfPlans = 1
    if comparePlan is None:
      print "No 3D Plan."
      return ""
    print "Motion comparing with: " + patient.best3DPlan.fileName
    
  elif compareWith == 'bio':
     comparePlan = patient.bestBioIntPlan
     numberOfPlans = 8
     
     if comparePlan is None:
       print "No Bio Plan."
       return ""
     print "Motion comparing with: " + patient.bestBioPlan.fileName
    
  sbrtPlan = patient.loadSBRTPlan()
  if not sbrtPlan:
    print "No SBRT plan."
    return ""
  
  voiList = []
  for plan in patient.plans:
    if plan.fileName.find('per') > -1:     
      #Find relevant CTVs
      for voi in plan.vois:
	if voi.name.find('ctv') > -1 or voi.name.find('gtv') > -1:
	  if (voi.name.find('_c-90') > -1 or voi.name.find('_c90') > -1 
	    or voi.name.find('_c0') > -1 or voi.name.find('residual') > -1
	    or voi.name.find('4d') > -1
	    or voi.name == 'ctvlsl' or voi.name == 'ctvmediastin' or voi.name.find('ctvliver') > -1
	    or voi.name == 'ctvpetvolumes' or voi.name == 'ctv1.1lungr'
	    or voi.name == 'ctv1suprarenal' or voi.name.find('lungs-ctv') > -1
	    or voi.name == 'ctv_lung4d' or voi.name == 'lungsr-ctv'):
	    continue
          voiList.append(voi.name)      
      break
  if patient.number == 1:
     voiList = ["ctv2.1irl","ctv2.2ill"]
  if patient.number == 13:
     voiList = ["ctv1.1lila","ctv1.2rsla","ctv1.4lsla","ctv1.5rslc","ctv1.6lslb"]
  
  valuesList = [95,99,105]
  planValues = np.zeros(( len(valuesList)+2, numberOfPlans*len(voiList) ))
  voiCount = 0
  #print voiList
  for voiName in voiList:
    
    for plan in patient.plans:
      
      if compareWith == '3D':
	if not comparePlan.fileName == plan.fileName:
	  continue
      
      wrongFile = False
      voiNumberLook = 0
      
      #Check for plans for multi targets
      if patient.number == 1:
         for voiNumber in range(1,3):
           if voiName.find('ctv2.' + str(voiNumber)) > -1:
             if plan.fileName.find('CTV' + str(voiNumber)) < 0:
               wrongFile = True
      if patient.number == 13 or patient.number == 20:
       for voiNumber in range(1,7):
           if voiName.find('.' + str(voiNumber)) > -1:
             voiNumberLook = voiNumber
             if plan.fileName.find('CTV' + str(voiNumber)) < 0:
               wrongFile = True
      if patient.number == 11:
	  if voiName == 'ctv1':
            voiNumberLook = 1
            if plan.fileName.find('CTV1') < 0:
               wrongFile = True
	  if voiName == 'ctv2':
            voiNumberLook = 2
            if plan.fileName.find('CTV2') < 0:
               wrongFile = True
	      
      if wrongFile:
	#print "Can't procede: " + plan.fileName
	continue
      #print "Finding values for: " + voiName + " with " + plan.fileName + " " + str(voiNumberLook)
      
      #if plan.fileName == comparePlan.fileName or plan.fileName == comparePlan.fileName.replace('PTV1','PTV' + str(voiNumberLook)):
	#number = 0
      #elif plan.fileName == patient.bestPlan.fileName and compareWith == 'int':
	#number = 4
      #elif plan.fileName == patient.bestBioPlan.fileName and compareWith == 'bio':
	#number = 4
      #elif plan.fileName == patient.bestBioPlan.fileName.replace('PTV1','PTV' + str(voiNumberLook)) and compareWith == 'bio':
         #number = 4
      #else:

	  
	#Find period and phases
	#Assign them right numbers if not 3D
      number = -1
      if not compareWith == '3D':
	  number = getDataFromFileName(plan.fileName)
	  if number < 0:
	    print "Can't assign number to: " + plan.fileName
	    continue

      voi = plan.get_voi_by_name(voiName)
      voiSbrt = sbrtPlan.get_voi_by_name(voiName)
      #voi = voiSbrt
      if not voi or not voiSbrt:
        print "Error: Can't find " + voiName + ' in ' + plan.fileName
        continue
      n = 0
      v24On = False  
      for value in valuesList:
        if compareWith == '3D' and number > 0:
	  continue
        
        planValues[n, number + numberOfPlans * voiCount] = voi.setValue(value)/24*100
        if n == 10:
	  planValues[n, number + numberOfPlans * voiCount] = 0
	  if voi.setValue(value) < 24:
	    planValues[n, number + numberOfPlans * voiCount] += 4
	    #print plan.fileName + " has " + str(voi.setValue(value))
	  
        #print plan.fileName + " " + str(voi.volume) + " " + voiName
        n += 1
        
        if not v24On:
	  if voi.name.find('ctv2') > -1:
	    planValues[3, number + numberOfPlans*voiCount] = voi.v7Gy	  
	  else:
	    planValues[3, number + numberOfPlans*voiCount] = voi.v24Gy
	    #planValues[3, number + numberOfPlans*voiCount] = voi.v99
	    planValues[4, number + numberOfPlans*voiCount] = voi.meanDose
	  v24On = True
    voiCount += 1
	
  output_str = ""
    
   
  #print planValues
  if outputAllData:
    for i in range(len(valuesList) + 1):
      if not i == 1:
	continue
      #output_str += "\n"
      if i == len(valuesList):
        output_str += "V24Gy" + "\t"
      else:
        output_str += "D" + str(valuesList[i]) + "\t"
      for j in range(voiCount):
        for k in range(8):
          output_str += str(planValues[i, k + 8*j]) + "\t"
        output_str += "\n"
        
      #output_str += "\n"
      
    #for voiName in voiList:
      #output_str += voiName + " "
    #output_str += "\n"
    return output_str
  else:
    if compareWith == 'int' or compareWith == 'bio':
      array = np.zeros(4*voiCount) #1. mean int, 2. std int, 3. mean rescan, 4. std rescan
      for j in range(voiCount):
        array[0+4*j] = np.mean(planValues[metric,(0+numberOfPlans*j):(4+numberOfPlans*j)])
        array[1+4*j] = np.std(planValues[metric,(0+numberOfPlans*j):(4+numberOfPlans*j)])
        array[2+4*j] = np.mean(planValues[metric,(4+numberOfPlans*j):(8+numberOfPlans*j)])
        array[3+4*j] = np.std(planValues[metric,(4+numberOfPlans*j):(8+numberOfPlans*j)])
    elif compareWith == '3D':
      array = np.zeros(voiCount)
      for j in range(voiCount):
        array[j] = planValues[metric,0+numberOfPlans*j]
      
    return array


#Compares different motions
def printDifferentMotions(patient):
  if not patient:
    print "Error, no patient."
    return ""
  

    
  sbrtPlan = patient.loadSBRTPlan()
  if not sbrtPlan:
    print "No SBRT plan."
    return ""
  
  voiList = []
  planNames = ["3D_ref0","3D_ref5","4D_int_per3600_ph0","4D_int_per3600_ph90","4D_int_per5000_ph0"
  ,"4D_int_per5000_ph90","4D_rescan_per3600_ph0","4D_rescan_per3600_ph90","4D_rescan_per5000_ph0"
  ,"4D_rescan_per5000_ph90","sbrt"]
  
  for plan in patient.plans:
    if plan.fileName.find('per') > -1:     
      #Find relevant CTVs
      for voi in plan.vois:
	if voi.name.find('ctv') > -1 or voi.name.find('gtv') > -1:
	  if (voi.name.find('_c-90') > -1 or voi.name.find('_c90') > -1 
	    or voi.name.find('_c0') > -1 or voi.name.find('residual') > -1
	    or voi.name.find('4d') > -1
	    or voi.name == 'ctvlsl' or voi.name == 'ctvmediastin' or voi.name.find('ctvliver') > -1
	    or voi.name == 'ctvpetvolumes' or voi.name == 'ctv1.1lungr'
	    or voi.name == 'ctv1suprarenal' or voi.name.find('lungs-ctv') > -1
	    or voi.name == 'ctv_lung4d' or voi.name == 'lungsr-ctv'):
	    continue
          voiList.append(voi.name)      
      break
  if patient.number == 1:
     voiList = ["ctv2.1irl","ctv2.2ill"]
  if patient.number == 13:
     voiList = ["ctv1.1lila","ctv1.2rsla","ctv1.4lsla","ctv1.5rslc","ctv1.6lslb"]
  if patient.number == 20:
     voiList = ["ctv1.1lil","ctv1.2lsl"]
  if patient.number == 11:
     voiList = ["ctv1", "ctv2"]
  if patient.number == 8:
     voiList = ["gtv_lung_tc"]
  if patient.number == 21:
     voiList = ["ctv1.2lungl"]
  
  valuesList = [99]
  planValues = np.zeros([len(voiList),11])
  voiCount = 0
  
  #print voiList
  for voiName in voiList:
   planNumber = 0
   for name in planNames:
    for plan in patient.plans:
      if plan.fileName.find(name) < 0:
         continue
      
      
      
      if name == "sbrt" and not plan.fileName == sbrtPlan.fileName:
         continue
      
      
      print "Working on " + plan.fileName
      wrongFile = False
      voiNumberLook = 0
      
      #Check for plans for multi targets
      if patient.number == 1:
         for voiNumber in range(1,3):
           if voiName.find('ctv2.' + str(voiNumber)) > -1:
             if plan.fileName.find('CTV' + str(voiNumber)) < 0:
               wrongFile = True
      if patient.number == 13 or patient.number == 20:
       for voiNumber in range(1,7):
           if voiName.find('.' + str(voiNumber)) > -1:
             voiNumberLook = voiNumber
             if plan.fileName.find('CTV' + str(voiNumber)) < 0:
               wrongFile = True
      if patient.number == 11:
	  if voiName == 'ctv1':
            voiNumberLook = 1
            if plan.fileName.find('CTV1') < 0:
               wrongFile = True
	  if voiName == 'ctv2':
            voiNumberLook = 2
            if plan.fileName.find('CTV2') < 0:
               wrongFile = True
	      
      if wrongFile and not name == "sbrt":
	#print "Can't procede: " + plan.fileName
	continue
      #print "Finding values for: " + voiName + " with " + plan.fileName + " " + str(voiNumberLook)
      
      #if plan.fileName == comparePlan.fileName or plan.fileName == comparePlan.fileName.replace('PTV1','PTV' + str(voiNumberLook)):
	#number = 0
      #elif plan.fileName == patient.bestPlan.fileName and compareWith == 'int':
	#number = 4
      #elif plan.fileName == patient.bestBioPlan.fileName and compareWith == 'bio':
	#number = 4
      #elif plan.fileName == patient.bestBioPlan.fileName.replace('PTV1','PTV' + str(voiNumberLook)) and compareWith == 'bio':
         #number = 4

      voi = plan.get_voi_by_name(voiName)
      voiSbrt = sbrtPlan.get_voi_by_name(voiName)
      if name == "sbrt":
         voi = voiSbrt
      #voi = voiSbrt
      if not voi or not voiSbrt:
        print "Error: Can't find " + voiName + ' in ' + plan.fileName
        continue
      n = 0

        
      planValues[voiCount, planNumber] = voi.setValue(99)/24*100
      if patient.number == 11 and voiName == "ctv2":
         planValues[voiCount, planNumber] = voi.setValue(99)/7*100
    planNumber += 1     
   voiCount += 1
  return planValues 
 
#Compares different motions
def compareDifferentMotionsMulti(patient, oarOn = False, margin = False, doseVolume = 0):
  if not patient:
    print "Error, no patient."
    return ""
    
  sbrtPlan = patient.loadSBRTPlan(margin)
  if not sbrtPlan:
    print "No SBRT plan."
    return None
  
  numberOfValues = 4 #V95, D95, D99, CN for CTV / Dmax and Dcalc for OAR
  CNDose = 0.95 #ratio of plan dose as ref dose in conformity number
  algoList = ["4DITV","sbrt"]
  periodeList = ["3600","5000"]
  phaseList = ["0","90"]
  filePath =  patient.name + "_multi_"
  output_str = ""
  
  alphabet = ["a","b","c","d","e"]
  planDose = patient.planDose
  values = np.zeros([4])
  if not oarOn:
     voiList = patient.ctvList
  else:
     voiList = patient.oarList

  array = np.zeros([len(voiList), numberOfValues, len(algoList), 4])
  nF = patient.nF
  
  marginStr = ""
  marginFileStr = ""
  if margin:
    marginStr = "Margin3mm"
    marginFileStr = "_Margin3mm"

  algoNumber = 0
  for algo in algoList:
   breathCount = 0
   for periode in periodeList:
      for phase in phaseList:
       plan = None
       voi = None
       bodyPlan = None
       targetIntegral = 0
       if algo == "sbrt":
          plan = sbrtPlan
          planName = plan.fileName
       else:
          planName = (filePath + algo + marginFileStr + "_" + nF +
                  "f_bio_4D_rescan20" +"_per" + str(periode) + "_ph" + str(phase) + ".dvh.gd")
          plan = patient.get_plan_by_name(planName)

       if plan is None:
         print "Can't find " + planName
         continue

       for i in range(numberOfValues):
          voiCount = 1
          for voiName in voiList:
             value = 0

             if voiName == "smallerairways" and (patient.number == 13 or patient.number == 22):
               voiCount += 1
               continue
             if voiName == "trachea" and (patient.number == 13):
                voiCount += 1
                continue
             voi = plan.get_voi_by_name(voiName.lower() + marginStr.lower())

             if not voi:
                 print "Error: Can't find " + voiName.lower() + marginStr.lower() + ' in ' + plan.fileName
                 continue
             if not oarOn:
                if i == 0:
                  value = voi.findV(0.95*planDose[voiCount-1])
                elif i == 1:
                  value = voi.d95/planDose[voiCount-1] * 100  
                elif i == 2:
                  value = voi.d99/planDose[voiCount-1] * 100
                elif i == 3:
                  if algo == "sbrt":
                     bodyPlan = patient.loadSBRTPlan()
                  else:
                     bodyPlanName = (filePath + algo + "_" + nF +
                        "f_bio_4D_rescan20" +"_per" + str(periode) + "_ph" + str(phase) + ".dvh.gd")
                     bodyPlan = patient.get_plan_by_name(bodyPlanName)
                  if bodyPlan is None:
                     print "Can't find " + planName
                     continue
                  bodyVoi = bodyPlan.get_voi_by_name("body")
                  if not bodyVoi:
                     print "Can't find body in " + bodyPlan.fileName
                     continue
                  
                  #bodyIntegral = np.sum(bodyVoi.y)*bodyVoi.voxVol / 100
                  #targetIntegral = np.sum(voi.y) * voi.voxVol / 100
                  #if bodyIntegral > 0:
                     #value = targetIntegral/bodyIntegral
                  # Conformity Number:
                  Vref = bodyVoi.findV(CNDose*planDose[voiCount-1])
                  
                  if Vref > 0.0:
                     #VTargetref = voi.findV(CNDose*planDose[voiCount-1])
                     #value = VTargetref * voi.volume / Vref / 100
                     value = Vref * bodyVoi.volume / voi.volume / 100
                     value = 1/value
                     #if patient.name == "Lung011":
                        #print voi.name + " at "+ algo +" with Plan: " + str(bodyVoi.y[128])+ " and Vref:" + str(Vref)
                  else:
                     print "Error in " + planName + " Vref: " + str(Vref) + " Volume: " + str(bodyVoi.volume)
                     value = 0
             else:
                if i == 0:
                   value = voi.maxDose
                elif i == 1:
                   value = voi.calcPerscDose
                elif i == 2 and doseVolume > 0:
                   if patient.number == 11 and voiName == "lungr":
                      value = voi.findV(4.8/2*9)
                   elif patient.number == 3 and voiName == "lungr":
                      value = voi.findV(4.4/2*9)
                   else:
                      value = voi.findV(doseVolume)
                else:
                   continue
                if value > 1 and i < 2 and voiCount < 7:
                      print str(patient.name) + " " + voiName + " at " + str(i) + " " + str(algoNumber) + " " + str(breathCount)

             array[voiCount - 1,i, algoNumber, breathCount] = value
             voiCount += 1
       breathCount += 1
   algoNumber += 1
    
  return array
  

def getDataFromFileName(fileName):
  interplay = False
  index = fileName.find('per')
  number = -1
  if index > -1:
    period = fileName[index+3:index+7]
    phase = fileName[index+10:index+11]
    if period == '3000':
      return -1
    if fileName.find('_int_') > -1:
      interplay = True
    if phase == '9':
      if period == '3600':
	if interplay:
	  number = 1
	else:
	  number = 5
      else:
	if interplay:
          number = 3
        else:
	  number = 7
    elif phase == '0':
      if period == '5000':
	if interplay:
          number = 2
        else:
	  number = 6
      else:
        if interplay:
           number = 0
        else:
           number = 4
    else:
      print "Unknown phase " + phase + " for " + fileName
      return -1
      
  return number


#Goes through directory and reads all data into newPatient
def readPatientData(newPatient, rescale = False):
  if not newPatient:
    print "Error, no newPatient!"
    return
    
  
  filePath = '/u/kanderle/AIXd/Data/FC/' + newPatient.name
  twoPlans = False #Flag for setting the best plan
  refPhase = newPatient.refPhase
  
  newPatient.setPatientData()
  
  special = False
  if newPatient.number == 11:
     special = True
  
  if os.path.exists(filePath):
    #filePathGD = filePath + '/Old_ab6/GD/'
    #Old case for First paper
    #if not newPatient.number in [1,3,11,13,20,21,22,23]:
      #filePathGD = filePath + '/Old_ab6/GD/'
    #else:
       #filePathGD = filePath + '/GD/'
    filePathGD = filePath + '/GD/'
    sbrtFilePath = filePath + '/Old4D/GD/' + newPatient.name + '_sbrt.dvh.gd'
    if not os.path.isfile(sbrtFilePath):
      print "No file at " + sbrtFilePath
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
    
    sbrtPlan.readGDFile(sbrtFilePath, None, newPatient.case, rescale, special)

    #print filePathGD
    filePathMarginSbrt = filePath + '/Old4D/GD/' + newPatient.name + '_sbrt_CTV.dvh.gd'
    marginPlan = newPatient.name + '_sbrt_CTV.dvh.gd'
    if os.path.isfile(filePathMarginSbrt):
      sbrtPlan = Plan()
      sbrtPlan.patientFlag = newPatient.number
      sbrtPlan.fileName = newPatient.name + '_sbrt_CTV.dvh.gd'
      #Manual input, because it can't read it from fileName
      sbrtPlan.optDose = 25
      sbrtPlan.sbrt = True
      sbrtPlan.margin = True
      sbrtPlan.targetPTV = True
      newPatient.add_plan(sbrtPlan)
      sbrtPlan.readGDFile(filePathMarginSbrt)
      #print sbrtPlan.fileName
      #print sbrtPlan.get_voi_by_name
    else:
      print "No file at " + filePathMarginSbrt
    
    for fileName in os.listdir(filePathGD):
      skip = False
      filePrefix, fileExtension = os.path.splitext(fileName)
      for plan in newPatient.plans:
	if fileName == plan.fileName:
	  skip = True
      if skip:
	continue
      if fileExtension == '.gd':
	  #print fileName
        # Take only 4D doses into account
	#if filePrefix.find('_4D.dvh') > -1 or filePrefix.find('4D_rescan') > -1:
	if filePrefix.find('4D') > -1 or filePrefix.find('3D') > -1:
          #print filePrefix
	  #if filePrefix.find('_PTV_') > -1:
            #continue
          newPlan = Plan()
	  newPlan.fileName = fileName
	  #Get info from filename
	  #newPlan.readGDFileName(filePrefix)
	  #Add manual optDose = 25, because plan / dose(25) is set in all 4D calc (even if name says d26.5)
	  newPlan.optDose = 25
	  if newPatient.number == 11 and not fileName.find('Margin') > -1:
             newPlan.optDose = 7
	  # Read dvh and add vois
	  newPlan.patientFlag = newPatient.number
	  newPlan.readGDFile(filePathGD + fileName,sbrtPlan, newPatient.case, rescale, special)
	  newPatient.add_plan(newPlan)
	  #print newPatient.get_plan_names()
	  if filePrefix.find('_int_') > -1:
              newPatient.bestIntPlan = newPlan
              #print "Intplan: " + filePrefix
              continue
          if filePrefix.find('_rescan_') > -1:
            newPatient.bestPlan = newPlan
            #print "Best plan: " +self.planDose[1] = 20 filePrefix
            continue
         
class Patient():
  def __init__(self,name, refPhase = 5):
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
    self.refPhase = refPhase
    self.best3DPlan = None
    self.bestIntPlan = None
    self.bestBioPlan = None
    self.bestBioIntPlan = None
    self.infoFilePath = '/u/kanderle/AIXd/Data/FC/' + name + '/' + name + '_info.txt'
    self.slicerTable = None
    self.CTVvalues = {} #D95,D99,D105,V24Gy
    self.segmentation = None
    self.ctvList = []
    self.oarList = []
    self.nF = 0
    self.planDose = np.array(np.ones(6))*24
    self.case = 1 #fractionaction regieme 1: 1x24 Gy, 2: 3x9Gy, 3: 5x7Gy
    
    
  def clear(self):
     for plan in self.plans:
        plan.clear()
     self.__init__(self.name)
  
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
	    #print plan.fileName
            names.append(plan.fileName)
        return names
        
  def setPatientData(self):
   oarList = []
   ctvList = []
   case = 1
   if self.number == 1:
     ctvList = ["ctv2.1irl", "ctv2.2ill"]
     nF = "4"
   elif self.number == 3:
     ctvList = ["ctv1-lsl-ct","ctv2-rsl1-ct","ctv3-lil-ct","ctv4-ril-ct","ctv5-rsl2-ct"]
     self.planDose[0] = 27
     self.planDose[2] = 27
     self.planDose[1] = 20
     self.planDose[3] = 22
     self.planDose[4] = 20
     oarList = ["SmallerAirways","Heart"]
     nF = "13"
     case = 2
   elif self.number == 11:
     ctvList = ["ctv1", "ctv2"]
     oarList = ["Esophagus", "Heart","Stomach"]
     nF = "5"
     self.planDose[1] = 7
     case = 3
   elif self.number == 13:
     ctvList = ["ctv1.1lila","ctv1.2rsla","ctv1.4lsla","ctv1.5rslc","ctv1.6lslb"]
     nF = "10"
   elif self.number == 20:
     ctvList = ["ctv1.1LIL","ctv1.2lsl"]
     nF = "6"
   elif self.number == 21:
     ctvList = ["ctv1.1lungr","ctv1.2lungl"]
     oarList = ["SmallerAirways", "Esophagus", "Heart"]
     self.planDose[0] = 27
     nF = "7"
     case = 2
   elif self.number == 22:
     ctvList = ["ctv2.1lulpos","ctv2.2lllant","ctv2.3lulheart","ctv2.4lulheart2"]
     oarList = ["Heart"]
     nF = "9"
   elif self.number == 23:
     ctvList = ["ctv1.1rll","ctv1.2lll"]
     oarList = ["AirwaysSmallR","SmallerAirways","Heart"]
     nF = "7"
   else:
     nF = ""
   
   self.nF = nF
   self.case = case
   self.oarList = oarList
   self.ctvList = ctvList
   

  def loadPTVPlan(self):
    self.loadBestPlan(True)
    if self.bestPlan:
      return
    for plan in self.plans:
      if not plan.sbrt and plan.targetPTV:
	self.bestPlan = plan
	return
    self.bestPlan = None
    
  def loadSBRTPlan(self,margin = False):
    for plan in self.plans:
      if plan.sbrt:
        if margin:
           if plan.margin:
             return plan
        else:
           return plan
        #if self.name == 'Lung021':
	  ##if plan.fileName.find('_L') > -1 or plan.fileName.find('_R') > -1: 
	    ##continue
	  #if plan.fileName.find('_L') < 0:
	    #continue
        
    return None
  
  def loadBestPlan(self,PTV=False):
    for plan in self.plans:
      if plan.filePath.find("rescan_per3600_ph0") > 1:
	 if plan.filePath.find("CTV") > 1:
	   continue
         self.bestPlan = plan
      if plan.filePath.find("3D_ref" + str(self.refPhase)) > -1:
	 self.best3DPlan = plan
	 #print "Best 3D Plan: " + plan.filePath
    return
    #multiPart = False

    
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
    indexR = fileName.find('_rescan5')
    #indexBio = fileName.find('tab6')
    newFileName = fileName[0:index] + '3D_ref' + str(self.refPhase) + fileName[index+2:]
    
    #if indexBio > -1:
      #indexBioMulti = fileName.find('_PTV')
      #if indexBioMulti > -1:
	#newFileNameBio = fileName[0:index+2] + '_tab6' + fileName[index+indexBioMulti] + +'1' + fileName[indexBioMulti+5:]
	#multiPart = True
      #else:
	#newFileNameBio = fileName[0:index+2] + '_tab6' + fileName[index+2:]
    
    
    if indexR > -1:
      newFileNameInt = fileName[0:index+2] + '_int' + fileName[index+2:indexR] + fileName[indexR+8:]
      newFileNameBio = fileName[0:index+2] + '_tab6' + fileName[index+2:indexR] + fileName[indexR+8:]
      newFileNameBioMulti = fileName[0:index+2] + '_tab6_PTV1' + fileName[index+2:indexR] + fileName[indexR+8:]
      
      newFileNameBioInt = fileName[0:index+2] + '_tab6_int' + fileName[index+2:indexR] + fileName[indexR+8:]
      newFileNameBioMultiInt = fileName[0:index+2] + '_tab6_PTV1_int' + fileName[index+2:indexR] + fileName[indexR+8:]
    else:
      newFileNameInt = fileName[0:index+2] + '_int' + fileName[index+2:]
      newFileNameBio = fileName[0:index+2] + '_tab6' + fileName[index+2:]
      newFileNameBioMulti = fileName[0:index+2] + '_tab6_PTV1' + fileName[index+2:]
      
      newFileNameBioInt = fileName[0:index+2] + '_tab6_int' + fileName[index+2:]
      newFileNameBioMultiInt = fileName[0:index+2] + '_tab6_int_PTV1' + fileName[index+2:]
    #if not os.path.isfile(newFileName):
      #print "Can't find file " + newFileName

    for plan in self.plans:
      if plan.fileName == fileName:
        print "Found best plan: " + fileName
	self.bestPlan = plan
      elif plan.fileName == newFileName:
        print "Found 3D best plan: " + newFileName
        self.best3DPlan = plan
        #self.bestPlan = plan
      elif plan.fileName == newFileNameInt:
        print "Found int best plan: " + newFileNameInt
        self.bestIntPlan = plan
        #self.bestPlan = plan
      elif plan.fileName == newFileNameBio:
         print "Found bio best plan: " + newFileNameBio
         self.bestBioPlan = plan
      elif plan.fileName == newFileNameBioMulti:
         print "Found bio best plan: " + newFileNameBioMulti
         self.bestBioPlan = plan
	 plan.multiPart = True
      elif plan.fileName == newFileNameBioInt:
         print "Found bio best plan: " + newFileNameBioInt
         self.bestBioIntPlan = plan
      elif plan.fileName == newFileNameBioMultiInt:
         print "Found bio int best plan: " + newFileNameBioMultiInt
         self.bestBioIntPlan = plan
	 plan.multiPart = True
      #else:
	#print "Nowhere " + plan.fileName + " vs " + newFileNameBioMulti
	
    if not self.bestPlan:
      print "Error, couldn't load best Plan. " + fileName
    if not self.best3DPlan:
      print "Error, couldn't load 3D best Plan. " + newFileName
    if not self.bestIntPlan:
      print "Error, couldn't load interplay best Plan. " + newFileNameInt
    if not self.bestBioPlan:
       print "Error, couldn't load bio best Plan. " + newFileNameBio + " or " + newFileNameBioMulti
    if not self.bestBioIntPlan:
       print "Error, couldn't load bio int best Plan. " + newFileNameBioInt + " or " + newFileNameBioMultiInt

 
    
  
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
    
  def get_plan_by_name(self,name):
        for plan in self.plans:
            if plan.fileName == name:
                return plan
        #print("Plan doesn't exist " + name)
        return None
  
  

        
class Plan():
  def __init__(self):
    self.name = "NewPlan"
    self.fileName = ''
    self.sbrt = False
    self.couchAngle = []
    self.gantryAngle = []
    self.numberOfFields = 0
    self.dvh = None
    self.optDose = 0
    self.targetPTV = False
    self.binRemove = False
    self.margin = False #Look at the CTV + margin
    self.bolus = 0
    self.oarSet = False
    self.oarMaxDoseFraction = 0
    self.oarWeigth = 0
    self.patientFlag = 0
    self.vois = []
    self.slicerNodeID = ''
    self.voiQtTable = None
    self.voiTableCheckBox = []
    self.horizontalHeaders=['Show:',"Max(Gy)","D99%(Gy)","per. Volume (Gy)","Volume(cc)"]
    self.multiPart = False #If there's multiple
    
  
  def clear(self):
     for voi in self.vois:
        voi.clear()
     self.__init__()
  
  def get_voi_names(self):
        names = []
        for voi in self.vois:
            names.append(voi.name)
        return names
        
  def add_voi(self,voi):
    self.vois.append(voi)
    
  def get_voi_by_name(self,name):
        for voi in self.vois:
            #Special case for smaller airways R in Lung023
            if name.lower() == "airwayssmallr":
               if voi.name.lower() == "smallerairways" and voi.rightSide:
                  return voi
                  
            if voi.name.lower() == name.lower():
              #Special case for smaller airways R in Lung023
              if voi.name.lower() == "smallerairways" and voi.rightSide:
                continue
              return voi

              ## DEBUG
        #for voi in self.vois:
            #if voi.name.find(name) > -1:
              #print "No voi's found, did you mean " + voi.name + " (" + name + ")" 
	      #return voi

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
	  
  
  def readGDFile(self,filePath,sbrtPlan=None, case = 1, rescale = False, special = False):
    self.filePath=filePath
    fp = open(filePath,"r")
    content = fp.read().split('\n')
    fp.close()
    n=len(content)
    #print filePath + str(case)
    i=1
    #print contet[len(content)-1]
    #print "Reading " + filePath
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
	  if special and ( v.name == "spinalcord" or v.name == "smallerairways"):
             caseTemp = 1
          else:
             caseTemp = case
	  v.setOarConstraints(caseTemp)
	  if sbrtPlan is not None:
	    sbrtVoi = sbrtPlan.get_voi_by_name(v.name)
	    if sbrtVoi:
              if sbrtVoi.name == v.name:
                 #print sbrtVoi.name + str(sbrtVoi.volume)
                 v.rescaledVolume = sbrtVoi.volume
              else:
                 print "Different names! " + sbrtVoi.name + " vs " + v.name
              #if sbrtVoi.name == "lungl":
              
	    #else:
	      #print "Can't set volumes for " + v.name
	    v.setVolumes()
	  v.calculateDose(rescale)
	  
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
  
  def setTable(self):
    from __main__ import qt
    table = self.voiQtTable
    if not table:
      print "No table."
      return
    table.setColumnCount(len(self.horizontalHeaders))
    table.setHorizontalHeaderLabels(self.horizontalHeaders)
    table.setEditTriggers(qt.QAbstractItemView.NoEditTriggers)

    table.setRowCount(len(self.vois))
    table.setVerticalHeaderLabels(self.get_voi_names())

    for i in range(0,len(self.vois)):
      checkBox = qt.QCheckBox()
      voi = self.vois[i]
      if checkBox:
        voi.voiTableCheckBox = checkBox
        table.setCellWidget(i,0,checkBox)
      
      #doseValues = [str(voi.maxDose)+"/"+str(voi.maxPerscDose),str(voi.d99),
           #str(voi.calcPerscDose)+"/"+str(voi.perscDose),str(voi.volume)]
      doseValues = [str(round(voi.maxDose,2)),str(round(voi.d99,2)),
           str(round(voi.calcPerscDose,2))+" ("+str(voi.perscVolume)+"cc)",str(round(voi.volume,2))]
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

