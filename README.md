SliceTRiP
=========

Author: Kristjan Anderle, GSI
Darmstadt, 2014

SliceTRiP is a scripted module for Slicer 3D that allows loading of TRiP98 specific files to Slicer3D.

1. LoadCTX is a module for loading TRiP98 binfo files in Slicer. Additionally it can set standart GSI colormap and set vector field to right values - TRiP vector fields components are divided by spacing.

2. SaveTRiP is a module for saving Slicer files in TRiP98 file format. It can save files as .ctx, .dos and .cbt. One can select also the byte orded and various other parameters. Module can also save contours as .binfo but the feature is not yet fully implemented.

3. TRiPDVH is a module for displaying DVH that are stored in .gd files. It also compares it to some constratints.

4. CreateMovie is a module for saving screenshots. It's similar to scripted module template used in Slicer. It can be used to create 360 degrees pictures of 3D module in Slicer.

