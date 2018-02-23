#!/bin/bash

#Linux bash script to load slicet for trip files

# 2017 Kristjan Anderle
#
#--additional-module-path ${additionalModule2} --no-main-window
str="$*"
additionalModule1="/u/kanderle/Software/Slicer/SliceTRiP/LoadCTXLight"
additionalModule2="/u/motion/Software/Slicer/Modules/SliceTRiP/TRiPDVH"
additionalModule3="/u/kanderle/Software/Slicer/SliceTRiP/DataProbeLight"
#additionalModule=(/u/kanderle/Software/Slicer/SliceTRiP/LoadCTXLight /u/kanderle/Software/Slicer/SliceTRiP/TRiPDVH)
modulesToIgnore="DICOMPatcher,ACPCTransform,AddManyMarkupsFiducialTest,\
AddScalarVolumes,Annotations,AtlasTests,VectorToScalarVolume,\
VBRAINSDemonWarp,CLIEventTest,SubjectHierarchyGenericSelfTest,\
BRAINSFitRigidRegistrationCrashIssue4139,BRAINSStripRotation,\
BRAINSTransformConvert,BSplineToDeformationField,CastScalarVolume,\
Charting,CheckerBoardFilter,ColorsScalarBarSelfTest,ComparePatients,\
CompareVolumes,CreateDICOMSeries,CropVolume,CropVolumeSelfTest,\
CurvatureAnisotropicDiffusion,DICOM,DICOMDiffusionVolumePlugin,\
DICOMScalarVolumePlugin,DICOMSlicerDataBundlePlugin,DWIConvert,\
Editor,EMSegmentCommandLine,EMSegment,EMSegmentQuick,Endoscopy,\
ExecutionModelTour,ExpertAutomatedRegistration,ExtractSkeleton,\
FiducialLayoutSwitchBug1914,FiducialRegistration,GaussianBlurImageFilter,\
GrayscaleGrindPeakImageFilter,GrayscaleModelMaker,HistogramMatching,\
ImageLabelCombine,IslandRemoval,LabelMapSmoothing,LabelStatistics,\
LandmarkRegistration,Markups,MarkupsWidgetsSelfTest,MarkupsInCompareViewersSelfTest,\
MarkupsInViewsSelfTest,MaskScalarVolume,MedianImageFilter,\
MergeModels,ModelMaker,ModelToLabelMap,MultiplyScalarVolumes,\
MultiVolumeImporter,MultiVolumeExplorer,MultiVolumeImporterPlugin,\
N4ITKBiasFieldCorrection,OtsuThresholdImageFilter,PerformMetricTest,\
PETStandardUptakeValueComputation,ProbeVolumeWithModel,ReadRegistrationNodeKA,\
Reformat,RegistrationHierarchy,ResampleDTIVolume,ResampleScalarVectorDWIVolume,\
ResampleScalarVolume,RobustStatisticsSegmenter,RSNA2012ProstateDemo,\
RSNAQuantTutorial,SampleData,RSNAVisTutorial,SimpleFilters,SimpleRegionGrowingSegmentation\
,SubtractScalarVolumes,SurfaceToolbox,Tables,TablesSelfTest,ThresholdScalarVolume,\
EMSegmentTransformToNewFormat,BRAINSResize,BRAINSResample,BRAINSROIAuto,\
BRAINSLabelStats,BRAINSFit,BRAINSDemonWarp,BRAINSDWICleanup,Transforms,\
TwoCLIsInARowTest,TwoCLIsInParallelTest,GrayscaleFillHoleImageFilter,\
GradientAnisotropicDiffusion,AddStorableDataAfterSceneViewTest,\
ExtensionWizard,DMRIInstall,JRC2013Vis,Models,OpenIGTLinkIF,\
OrientScalarVolume,PerformanceTests,ScenePerformance,\
sceneImport2428,SegmentEditor,SelfTests,SliceLinkLogic,\
Slicer4Minute,slicerCloseCrashBug2590,SlicerMRBMultipleSaveRestoreLoopTest,\
SlicerOrientationSelectorTest,SubjectHierarchyCorePluginsSelfTest,\
SlicerMRBMultipleSaveRestoreTest,ThresholdThreadingTest,ViewControllers,\
ViewControllersSliceInterpolationBug1926,,DataStore,SlicerMRBSaveRestoreCheckPathsTest,\
VolumeRendering,VolumeRenderingSceneClose,VotingBinaryHoleFillingImageFilter,\
BatchProcessing,BatchProcessing,Beams,DicomRtImportExport,DicomSroExport,\
DicomSroImport,DoseAccumulation,DoseComparison,DoseVolumeHistogram,DvhComparison,\
ExternalBeamPlanning,Isodose,LeakFinder,PinnacleDvfReader,PlanarImage,PlastimatchPy,\
PlmBspline,PlmCommon,PlmLandwarp,PlmMismatchError,PlmRegister,PlmSynth,PlmThreshbox,\
PlmVectorFieldAnalysis,SegmentComparison,SegmentMorphology,SlicerRtCommon,SuperBuild,\
Testing,VffFileReader,\
BatchStructureSetConversion,IGRTWorkflow_SelfTest,\
RegistrationQuality,JacobianFilter,AbsoluteDifference"

/u/motion/Software/Slicer/Slicer-Stable/Slicer --no-main-window --additional-module-path ${additionalModule2} \
--modules-to-ignore ${modulesToIgnore} \
--python-script /u/motion/Software/Slicer/Modules/SliceTRiP/Slicet/TripDVHSlicet.py -- ${str}

exit 1
