import os

def convert(file):
    prefix, suffix = dosmth(file)
    if not suffix == ".hed":
        print file + "Is not a header file"
        return
    
    CHECKWRIGHTS
    nrrdParameters = {'type':'','space':'left-posterior-superior',
                       'sizes':'','space directions':''
                       'kinds':'domain domain domain',
                       'endian':'','encoding':'raw',
                       'space origin':''
                       'data file':''}
    
    hedParameters = {'data_type':'','num_bytes':'','byte_order':'',
                     'patient_name':'','slice_dimension':'',
                     'pixel_size':'','slice_distance':'',
                     'slice_number':'',
                     'xoffset':'','yoffset':'','zoffset':'',
                     'dimx':'','dimy':'','dimz':''}
    
    fp = open(file,"r")
    content = fp.read().split('\n')
    fp.close()
    
    #Go through hed file and write all parameters
    for line in content:
        bFound = False
        if not line or line.find('version') > -1:
            continue
        for key, value in hedParameters.iteritems():
            if line.find(key) > -1:
                hedParameters[key] = line.split(' ')[1]
                bFound = True
                break
        if not bFound:
            print line " is not recognized"
     
            
    #Let's fill nrrdParameters
    if hedParameters[data_type] == 'short':
        if hedParameters[num_bytes] == '4':
            nrrdParameters['type'] = 'int'
        else:
            nrrdParameters['type'] = 'int'
    elif hedParameters[data_type] == 'float':
        if hedParameters[num_bytes] == '8':
            nrrdParameters['type'] = 'double'
        else:
            nrrdParameters['type'] = 'float'
            
    if hedParameters['byte_order'] == 'vms':
        nrrdParameters['endian'] = 'little'
    elif hedParameters['byte_order'] == 'aix':
        nrrdParameters['endian'] = 'big'
    else:
        print "Unknown endian type: " + hedParameters['byte_order']
        return
    
    nrrdSize = hedParameters['dimx'] + ' ' hedParameters['dimy'] + ' ' hedParameters['dimz']
    nrrdParameters['sizes'] = nrrdSize
    
    nrrdDirections = '(' + hedParameters['pixel_size'] + ',0,0) '
    nrrdDirections += '(0' +hedParameters['pixel_size'] + ',0) '
    nrrdDirections +=  '(0,0,' + hedParameters['slice_distance'] + ')'
    nrrdParameters['space directions'] = nrrdDirections
    
    nrrdOrigin = '(' + hedParameters['xoffset']
    nrrdOrigin += ',' + hedParameters['yoffset']
    nrrdOrigin += ',' + hedParameters['zoffset'] + ')'
    nrrdParameters['space origin'] = nrrdOrigin
    
    if suffix == '.gz' or suffix == '.zip':
        nrrdParameters['encoding'] = 'gzip'
    
    #Special case if we have vector field
    nrrdFile = ""
    if file.find('cbt'):
        dim = ['x','y','z']
        for d in dim:
            index = file.find('_'+dim)
            if index > -1:
                vectorFileName = file[0:index]
                break
        if index = -1:
            print "Can't find vector filename: " + file
            return
        for d in dim:
            if suffix == '.gz' or suffix == '.gzip':
                vectorSuffix = suffix
            else:
                vectorSuffix = ''
                
            nrrdFile += +'\n' + vectorFileName + '_' + d + '.cbt' + vectorSuffix
    else:
        nrrdFile = file
     
    nrrdParameters['data file'] = nrrdFile
    
    outputFile = self.writeNrrd(nrrdParameters)
    
def writeNrrd(self, nrrdParameters):
    outputFile = "NRRD0004\n"
    for key, value in nrrdParameters.iteritems():
        outputFile += key + ':' + value + '\n'
        if value == '':
            return ""
    return outputFile
