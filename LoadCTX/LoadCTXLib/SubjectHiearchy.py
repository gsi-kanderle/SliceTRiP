from __main__ import slicer


def addSeriesInHierarchy(volumeNode):
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

    #firstFile = loadable.files[0]

    #seriesInstanceUid = slicer.dicomDatabase.fileValue(firstFile,tags['seriesInstanceUID'])
    seriesInstanceUid = '1.2.3.4.5.6.7'
    seriesNode = vtkMRMLSubjectHierarchyNode.GetSubjectHierarchyNodeByUID(slicer.mrmlScene, 'DICOM', seriesInstanceUid)
    seriesNodeCreated = False
    if seriesNode == None:
      seriesNode = vtkMRMLSubjectHierarchyNode()
      seriesNodeCreated = True
    elif seriesNode.GetAttribute('DICOMHierarchy.SeriesModality') != None:
      import sys
      sys.stderr.write('Volume with the same UID has been already loaded!')
      return

    #seriesDescription = slicer.dicomDatabase.fileValue(firstFile,tags['seriesDescription'])
    seriesDescription = 'Test'
    if seriesDescription == '':
      seriesDescription = 'No description'
    seriesDescription = seriesDescription + '_SubjectHierarchy'
    seriesNode.SetName(seriesDescription)
    seriesNode.SetAssociatedNodeID(volumeNode.GetID())
    seriesNode.SetLevel('Series')
    seriesNode.AddUID('DICOM',seriesInstanceUid)
    #RTIMAGE = Radiotherapy Image
    #RTDOSE = Radiotherapy Dose
    #RTSTRUCT = Radiotherapy Structure Set
    #RTPLAN = Radiotherapy Plan 
    seriesNode.SetAttribute('DICOMHierarchy.SeriesModality','CT')
    seriesNode.SetAttribute('DICOMHierarchy.StudyDate','1.1.2014')
    seriesNode.SetAttribute('DICOMHierarchy.StudyTime','10:14')
    seriesNode.SetAttribute('DICOMHierarchy.PatientSex','M')
    seriesNode.SetAttribute('DICOMHierarchy.PatientBirthDate','1.1.1900')

    if seriesNodeCreated:
      # Add to the scene after setting level, UID and attributes so that the plugins have all the information to claim it
      slicer.mrmlScene.AddNode(seriesNode)

    #patientId = slicer.dicomDatabase.fileValue(firstFile,tags['patientID'])
    patientId = 'Test'
    patientNode = vtkMRMLSubjectHierarchyNode.GetSubjectHierarchyNodeByUID(slicer.mrmlScene, 'DICOM', patientId)
    studyInstanceUid = seriesInstanceUID
    studyNode = vtkMRMLSubjectHierarchyNode.GetSubjectHierarchyNodeByUID(slicer.mrmlScene, 'DICOM', studyInstanceUid)
    vtkSlicerSubjectHierarchyModuleLogic.InsertDicomSeriesInHierarchy(slicer.mrmlScene, patientId, studyInstanceUid, seriesInstanceUid)

    if patientNode == None:
      patientNode = vtkMRMLSubjectHierarchyNode.GetSubjectHierarchyNodeByUID(slicer.mrmlScene, 'DICOM', patientId)
      if patientNode != None:
        patientName = 'KingKong'
        if patientName == '':
          patientName = 'No name'
        patientName = patientName.encode('UTF-8', 'ignore')
        patientNode.SetName(patientName + '_SubjectHierarchy')

    if studyNode == None:
      studyNode = vtkMRMLSubjectHierarchyNode.GetSubjectHierarchyNodeByUID(slicer.mrmlScene, 'DICOM', studyInstanceUid)
      if studyNode != None:
        studyDescription = 'StudyDescription'
        if studyDescription == '':
          studyDescription = 'No description'
        studyDescription = studyDescription.encode('UTF-8', 'ignore')
        studyNode.SetName(studyDescription + '_SubjectHierarchy')