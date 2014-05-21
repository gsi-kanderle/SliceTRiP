from __main__ import slicer


def addSeriesInHierarchy(patient,plan):
    tags = {}
    tags['seriesInstanceUID'] = "0020,000E"
    tags['seriesDescription'] = "0008,103E"
    tags['seriesModality'] = "0008,0060"
    tags['studyInstanceUID'] = "0020,000D"
    tags['studyDescription'] = "0008,1030"
    tags['studyDate'] = "0008,0020"
    tags['studyTime'] = "0008,0030"
    tags['patientID'] = "0010,0020"
    tags['patientName'] = "0010,0010"
    tags['patientSex'] = "0010,0040"
    tags['patientBirthDate'] = "0010,0030"

    from vtkSlicerSubjectHierarchyModuleMRML import vtkMRMLSubjectHierarchyNode
    from vtkSlicerSubjectHierarchyModuleLogic import vtkSlicerSubjectHierarchyModuleLogic
    try:
      vtkMRMLSubjectHierarchyNode
      vtkSlicerSubjectHierarchyModuleLogic
    except AttributeError:
      import sys
      sys.stderr.write('Unable to create SubjectHierarchy nodes: SubjectHierarchy module not found!')
      return

    seriesInstanceUid = '1.0.' + str(patient.number)
    
    if patient.slicerSubjectNodeID == '':
      #Create Node
      subjectNode = vtkMRMLSubjectHierarchyNode()
      subjectNode.SetName(patient.name)
      subjectNode.SetLevel('Subject')
      subjectNode.SetAttribute('DicomRtImport.DoseUnitName','GY')
      subjectNode.SetAttribute('DicomRtImport.DoseUnitValue','2.4e-5')
      subjectNode.AddUID('DICOM',seriesInstanceUid)
      slicer.mrmlScene.AddNode(subjectNode)
      patient.slicerSubjectNodeID = subjectNode.GetID()
      
    
    
    
    ctNode = vtkMRMLSubjectHierarchyNode()
    ctNode.SetParentNodeID(patient.slicerSubjectNodeID)
    ctNode.SetAssociatedNodeID(patient.slicerNodeID)
    ctNode.SetName(patient.name)
    ctNode.SetLevel('Series')
    ctNode.SetAttribute('DICOMHierarchy.SeriesModality','CT')
    ctNode.SetAttribute('DICOMHierarchy.StudyDate','1.1.2014')
    ctNode.SetAttribute('DICOMHierarchy.StudyTime','10:14')
    ctNode.SetAttribute('DICOMHierarchy.PatientSex','M')
    ctNode.SetAttribute('DICOMHierarchy.PatientBirthDate','1.1.1900')
    ctNode.SetOwnerPluginName('Volumes')
    slicer.mrmlScene.AddNode(ctNode)
    
    doseNode = vtkMRMLSubjectHierarchyNode()
    doseNode.SetParentNodeID(patient.slicerSubjectNodeID)
    doseNode.SetAssociatedNodeID(plan.slicerNodeID)
    doseNode.SetLevel('Series')
    doseNode.SetName(plan.fileName)
    doseNode.AddUID('DICOM',seriesInstanceUid)
    doseNode.SetAttribute('DICOMHierarchy.SeriesModality','RTDOSE')
    #doseNode.SetAttribute('DICOMHierarchy.StudyDate','1.1.2014')
    #doseNode.SetAttribute('DICOMHierarchy.StudyTime','10:14')
    #doseNode.SetAttribute('DICOMHierarchy.PatientSex','M')
    #doseNode.SetAttribute('DICOMHierarchy.PatientBirthDate','1.1.1900')
    doseNode.SetOwnerPluginName('Volumes')
    slicer.mrmlScene.AddNode(doseNode)
    
    contourSetsNode = vtkMRMLSubjectHierarchyNode()
    contourSetsNode.SetParentNodeID(ctNode.GetID())
    contourSetsNode.SetName(patient.name + '_ContourSet')
    contourSetsNode.SetLevel('Series')
    contourSetsNode.SetOwnerPluginName('ContourSets')
    #contourSetsNode.OwnerPluginAutoSearchOn
    contourSetsNode.SetAttribute('DICOMHierarchy.SeriesModality','RTSTRUCT')
    contourSetsNode.SetAttribute('DicomRtImport.RoiReferencedSeriesUid',seriesInstanceUid)
    contourSetsNode.SetAttribute('DicomRtImport.ContourHiearchy','1')
    slicer.mrmlScene.AddNode(contourSetsNode)
    
    heartVoi = slicer.util.getNode('Heart*')
    if heartVoi:
      print "Let's put: " + heartVoi.GetName() + " in it."
      contourSH = vtkMRMLSubjectHierarchyNode()
      contourSH.SetParentNodeID(contourSetsNode.GetID())
      contourSH.SetName(heartVoi.GetName())
      contourSH.SetLevel('Subseries')
      contourSH.SetOwnerPluginName('Contours')
      #contourSH.SetAttribute('DICOMHierarchy.SeriesModality','RTSTRUCT')
      contourSH.SetAttribute('DicomRtImport.RoiReferencedSeriesUid',seriesInstanceUid)
      #contourSH.SetAttribute('DicomRtImport.ContourHiearchy','1')
      contourSH.SetAttribute('DicomRtImport.StructureName',heartVoi.GetName())
      slicer.mrmlScene.AddNode(contourSH)
    
    #volumeNode = slicer.util.getNode(volumeNodeID)
    ##firstFile = loadable.files[0]

    ##seriesInstanceUid = slicer.dicomDatabase.fileValue(firstFile,tags['seriesInstanceUID'])
    #seriesInstanceUid = '1.2.3.4.5.6.7'
    #ctNode = vtkMRMLSubjectHierarchyNode.GetSubjectHierarchyNodeByUID(slicer.mrmlScene, 'DICOM', seriesInstanceUid)
    #ctNodeCreated = False
    #if ctNode == None:
      #ctNode = vtkMRMLSubjectHierarchyNode()
      #ctNodeCreated = True
    #elif ctNode.GetAttribute('DICOMHierarchy.SeriesModality') != None:
      #import sys
      #sys.stderr.write('Volume with the same UID has been already loaded!')
      #return

    ##seriesDescription = slicer.dicomDatabase.fileValue(firstFile,tags['seriesDescription'])
    #seriesDescription = 'Test'
    #if seriesDescription == '':
      #seriesDescription = 'No description'
    #seriesDescription = seriesDescription + '_SubjectHierarchy'
    #ctNode.SetName(seriesDescription)
    #ctNode.SetAssociatedNodeID(volumeNode.GetID())
    #ctNode.SetLevel('Series')
    #ctNode.AddUID('DICOM',seriesInstanceUid)
    ##RTIMAGE = Radiotherapy Image
    ##RTDOSE = Radiotherapy Dose
    ##RTSTRUCT = Radiotherapy Structure Set
    ##RTPLAN = Radiotherapy Plan 
    #ctNode.SetAttribute('DICOMHierarchy.SeriesModality','CT')
    #ctNode.SetAttribute('DICOMHierarchy.StudyDate','1.1.2014')
    #ctNode.SetAttribute('DICOMHierarchy.StudyTime','10:14')
    #ctNode.SetAttribute('DICOMHierarchy.PatientSex','M')
    #ctNode.SetAttribute('DICOMHierarchy.PatientBirthDate','1.1.1900')

    #if ctNodeCreated:
      ## Add to the scene after setting level, UID and attributes so that the plugins have all the information to claim it
      #slicer.mrmlScene.AddNode(ctNode)

    ##patientId = slicer.dicomDatabase.fileValue(firstFile,tags['patientID'])
    #patientId = 'Test'
    #patientNode = vtkMRMLSubjectHierarchyNode.GetSubjectHierarchyNodeByUID(slicer.mrmlScene, 'DICOM', patientId)
    #studyInstanceUid = seriesInstanceUid
    #studyNode = vtkMRMLSubjectHierarchyNode.GetSubjectHierarchyNodeByUID(slicer.mrmlScene, 'DICOM', studyInstanceUid)
    #vtkSlicerSubjectHierarchyModuleLogic.InsertDicomSeriesInHierarchy(slicer.mrmlScene, patientId, studyInstanceUid, seriesInstanceUid)

    #if patientNode == None:
      #patientNode = vtkMRMLSubjectHierarchyNode.GetSubjectHierarchyNodeByUID(slicer.mrmlScene, 'DICOM', patientId)
      #if patientNode != None:
        #patientName = 'KingKong'
        #if patientName == '':
          #patientName = 'No name'
        #patientName = patientName.encode('UTF-8', 'ignore')
        #patientNode.SetName(patientName + '_SubjectHierarchy')

    #if studyNode == None:
      #studyNode = vtkMRMLSubjectHierarchyNode.GetSubjectHierarchyNodeByUID(slicer.mrmlScene, 'DICOM', studyInstanceUid)
      #if studyNode != None:
        #studyDescription = 'StudyDescription'
        #if studyDescription == '':
          #studyDescription = 'No description'
        #studyDescription = studyDescription.encode('UTF-8', 'ignore')
        #studyNode.SetName(studyDescription + '_SubjectHierarchy')