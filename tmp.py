 #
    # Reference Phase CT selector
    #
    self.selectNode = slicer.qMRMLNodeComboBox()
    self.selectNode.nodeTypes = ( ("vtkMRMLScalarVolumeNode"), "" )
    self.selectNode.addAttribute( "vtkMRMLScalarVolumeNode", "LabelMap", 0 )
    self.selectNode.selectNodeUponCreation = True
    self.selectNode.addEnabled = False
    self.selectNode.removeEnabled = False
    self.selectNode.noneEnabled = False
    self.selectNode.showHidden = False
    self.selectNode.showChildNodeTypes = False
    self.selectNode.setMRMLScene( slicer.mrmlScene )
    self.selectNode.setToolTip( "Select volume to be exported as ctx." )
    parametersFormLayout.addRow("Select volume: ", self.selectNode)


# Table
    self.hedTable = qt.QTableWidget()
    
    self.hedTable.setColumnCount(1)
      
    parametersFormLayout.addRow(self.hedTable)
    verticalHeaders=["Patient Name: ","Data type: ","Byte Number: ","Byte Order: ","Pixel dimension"\
    "Slice dimension","Number of slice","X dim:","Y dim: ","Z dim: ","Binfo: ","Modality: "]
    self.hedTable.setRowCount(len(verticalHeaders))
    horizontalHeaders=['Value']
    self.hedTable.setHorizontalHeaderLabels(horizontalHeaders)
    self.hedTable.setVerticalHeaderLabels(verticalHeaders)
    
    self.hedTable.visible = False
    
    #Set Data type
    self.dataType = qt.QComboWidget()
    self.dataType.addItem("integer")
    self.dataType.addItem("float")
    self.dataType.addItem("double")
    
    self.hedTable.addCellWidget(1,0,self.dataType)
    
    #Set Byte Number:
    self.byteNumber = qt.QComboWidget()
    self.byteNumber.addItem("4")
    self.dataType.addItem("2")
    
    self.hedTable.addCellWidget(2,0,self.byteNumber)
    
    #Set Byte Order
    self.byteOrder = qt.QComboWidget()
    self.byteOrder.addItem("aix")
    self.byteOrder.addItem("vms")
    
    self.hedTable.addCellWidget(3,0,self.byteOrder)
    
    #Set binfo
    self.binfoCheckBox = qt.QCheckBox()
    
    self.hedTable.addCellWidget(10,0,self.binfoCheckBox)
    
    #Set Modality
    self.modality = qt.QComboWidget()
    self.modality.addItem("CT")
    self.modality.addItem("Dose")
    
    self.hedTable.addCellWidget(11,0,self.modality)

    

    self.dvhTableItems = []
    for i in range(0,len(verticalHeaders)):
      item = qt.QTableWidgetItem()
      self.dvhTableItems.append(item)
      self.dvhTable.setItem(i,0,item)
      
    self.selectNode.connect("currentNodeChanged(vtkMRMLNode*)", self.tableVisible)
    
    pyTripCubetmp = pytrip.CtxCube()
    self.pyTripCube = pyTripCubetmp
    
    def tableVisible(self):
      self.hedTable.visible = self.selectNode.currentNode()
      
    
    def onApplyButton(self):
      
      if self.modality.currentText == "CT":
	pyTripCube = pytrip.CtxCube()
      elif self.modality.currentText == "Dose:"
        pyTripCube = pytrip.DosCube()
        
      pyTripCube.
    logic = TRiPDVHLogic()
    
    self.dvh = logic.addChart(self.dvh,self.voiComboBox.currentText)
    
    print("Displaying:" + self.voiComboBox.currentText)
    
    
    def setPyTRiPCube(self,node):
      
    

