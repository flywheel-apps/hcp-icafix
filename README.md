# flywheel/hcp-icafix
[Flywheel Gear](https://github.com/flywheel-io/gears/tree/master/spec) that runs [ICA-FIX denoising](https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/FIX) on functional data preprocessed according to the [Human Connectome Project](http://www.humanconnectome.org) Minimal Preprocessing Pipeline (MPP).  This is based on scripts from the v4.0-alpha pipelines, as well as generating some helpful QC images. For more info on the pipelines, see [HCP Pipelines](https://github.com/Washington-University/Pipelines).  For more info on ICA-FIX, including available classifiers, see [FSL FIX User Guide](https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/FIX/UserGuide).

## Important notes
* ICA-FIX works best when applied to time series with many volumes. Original HCP rfMRI scans were 15 minutes TR=720ms each (1200 volumes). If data was collected in shorter scans within the same session, it's recommended to concatenate these before running ICA. For this gear, you can provide multiple FuncZip inputs and the pipeline will handle the concatenation and split the outputs once it completes. 
* If providing multiple FuncZip inputs, **make sure each HCP-Func gear was run with a unique fMRIName!** Otherwise, scans will be overwritten!

## Required inputs
1. FuncZip output from HCP-Func gear for at least one functional run
2. StructZip output from the HCP-Struct gear (containing <code>T1w/</code>, <code>T2w/</code>, and <code>MNINonLinear/</code> folders)