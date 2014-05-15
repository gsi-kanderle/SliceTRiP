import os
from __main__ import vtk, qt, ctk, slicer
import numpy as np
#Copyright: http://code.google.com/p/volumetric-defacing/source/browse/defacing/vtkImageImportFromArray.py?r=66b053cb1a157c1a8bb14ba85397ab1c9845deb8&spec=svn90f4995ded9ec2974e255f667c0b8817ce23f9ad
"""
vtkImageImportFromArray: a NumPy front-end to vtkImageImport

Load a python array into a vtk image.
To use this class, you must have NumPy installed (http://numpy.scipy.org/)

Methods:

  GetOutput() -- connect to VTK image pipeline
  SetArray()  -- set the array to load in
 
Convert python 'Int' to vtk.VTK_UNSIGNED_SHORT:
(python doesn't support unsigned short, so this might be necessary)

  SetConvertIntToUnsignedShort(yesno)
  ConvertIntToUnsignedShortOn()
  ConvertIntToUnsignedShortOff()

Methods from vtkImageImport:
(if you don't set these, sensible defaults will be used)

  SetDataExtent()
  SetDataSpacing()
  SetDataOrigin()
"""

class vtkImageImportFromArray:
    def __init__(self):
        self.__import = vtk.vtkImageImport()
        self.__ConvertIntToUnsignedShort = False
        self.__Array = None

    # type dictionary: note that python doesn't support
    # unsigned integers properly!
    __typeDict = {'b':vtk.VTK_CHAR,             # int8
                  'B':vtk.VTK_UNSIGNED_CHAR,    # uint8
                  'h':vtk.VTK_SHORT,            # int16
                  'H':vtk.VTK_UNSIGNED_SHORT,   # uint16
                  'i':vtk.VTK_INT,              # int32
                  'I':vtk.VTK_UNSIGNED_INT,     # uint32
                  'l':vtk.VTK_LONG,             # int64
                  'L':vtk.VTK_UNSIGNED_LONG,    # uint64
                  'f':vtk.VTK_FLOAT,            # float32
                  'd':vtk.VTK_DOUBLE,           # float64
                  }

    # convert 'Int32' to 'unsigned short'
    def SetConvertIntToUnsignedShort(self, yesno):
        self.__ConvertIntToUnsignedShort = yesno

    def GetConvertIntToUnsignedShort(self):
        return self.__ConvertIntToUnsignedShort
   
    def ConvertIntToUnsignedShortOn(self):
        self.__ConvertIntToUnsignedShort = True

    def ConvertIntToUnsignedShortOff(self):
        self.__ConvertIntToUnsignedShort = False

    # get the output
    def GetOutputPort(self):
        return self.__import.GetOutputPort()

    # get the output
    def GetOutput(self):
        return self.__import.GetOutput()

    # import an array
    def SetArray(self, imArray, numComponents = 1):
        self.__Array = imArray
        imString = imArray.tostring()
        dim = imArray.shape

        if (len(dim) == 4):
            numComponents = dim[3]
            dim = (dim[0], dim[1], dim[2])


        typecode = imArray.dtype.char
       
        ar_type = self.__typeDict[typecode]

        if (typecode == 'F' or typecode == 'D'):
            numComponents = numComponents * 2

        if (self.__ConvertIntToUnsignedShort and typecode == 'i'):
            imString = imArray.astype(Numeric.Int16).tostring()
            ar_type = vtk.VTK_UNSIGNED_SHORT
        else:
            imString = imArray.tostring()
           
        self.__import.CopyImportVoidPointer(imString, len(imString))
        self.__import.SetDataScalarType(ar_type)
        self.__import.SetNumberOfScalarComponents(numComponents)
        extent = self.__import.GetDataExtent()
        self.__import.SetDataExtent(extent[0], extent[0] + dim[2] - 1,
                                    extent[2], extent[2] + dim[1] - 1,
                                    extent[4], extent[4] + dim[0] - 1)
        self.__import.SetWholeExtent(extent[0], extent[0] + dim[2] - 1,
                                     extent[2], extent[2] + dim[1] - 1,
                                     extent[4], extent[4] + dim[0] - 1)

    def GetArray(self):
        return self.__Array
       
    # a whole bunch of methods copied from vtkImageImport
    def SetDataExtent(self, extent):
        self.__import.SetDataExtent(extent)

    def GetDataExtent(self):
        return self.__import.GetDataExtent()
   
    def SetDataSpacing(self, spacing):
        self.__import.SetDataSpacing(spacing)

    def GetDataSpacing(self):
        return self.__import.GetDataSpacing()
   
    def SetDataOrigin(self, origin):
        self.__import.SetDataOrigin(origin)

    def GetDataOrigin(self):
        return self.__import.GetDataOrigin()

