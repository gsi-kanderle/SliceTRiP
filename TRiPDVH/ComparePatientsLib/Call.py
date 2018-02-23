# -*- coding: iso-8859-1 -*-
import os
import unittest
import sys
import CopyData

arguments = sys.argv

if sys.argv[1] == '0':
  if sys.argv[2] == '3D0':
    d = CopyData.Data(0)
  else:
    d = CopyData.Data()
    
  if sys.argv[2] == '3D0' or sys.argv[2] == '3D5':
    compareWith = '3D'
  elif sys.argv[2] == 'SBRT' or sys.argv[2] == 'int':
    compareWith = sys.argv[2]
  else:
    print "Unknown argument " + sys.argv[2]
  
  for i in range(0,6):
    d.comparePatients(i, compareWith)

elif sys.argv[1] == '1':
  if sys.argv[3] == '1':
    d = CopyData.Data(0)
  else:
    d = CopyData.Data()

  if sys.argv[3] == '0':
    d.compareMotion(True,int(sys.argv[2]),'int')
  elif sys.argv[3] == '1' or sys.argv[3] == '2':
    d.compareMotion(False,int(sys.argv[2]),'3D')
  elif sys.argv[3] == '3':
    d.compareMotion(False,int(sys.argv[2]),'rescan')
  elif sys.argv[3] == '4':
    d.compareMotion(False,int(sys.argv[2]),'bio')
  else:
    print "Unknown argument " + sys.argv[3]
   

elif sys.argv[1] == '2':
  d = CopyData.Data()
  metric = [0,2]
  for i in range(len(metric)):
    d.exportMetricToClipboard2(metric[i])
    
elif sys.argv[1] == '3':
  d = CopyData.Data()
  metric = [0,2]
  for i in range(len(metric)):
    d.exportMetricToClipboard3(metric[i]) 
    
else:
  print "Unknown argument"
  

