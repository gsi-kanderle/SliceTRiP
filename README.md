SliceTRiP
=========

Author: Kristjan Anderle, GSI
Darmstadt, 2014

SliceTRiP is a scripted module for Slicer 3D that allows loading of TRiP98 specific files to Slicer3D.

1. LoadCTX is a module for loading TRiP98 files in Slicer. It supports .ctx, .dos, .cbt and .binfo. 
For the right color code of .dos files, you must insert the optimization value in Gy. If there was no optimization value, then you have to insert 1000, because the dose cube is in permil.

2. SaveTRiP is a module for saving Slicer files in TRiP98 file format. It can save files as .ctx, .dos and .cbt. One can select also the byte orded and various other parameters. Module can also save contours as .binfo but the feature is not yet fully implemented.

3. TRiPDVH is a module for displaying DVH that are stored in .gd files. It also compares it to some constratints.

4. CreateMovie is a module for saving screenshots. It's similar to scripted module template used in Slicer.

