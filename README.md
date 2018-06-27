[![Docker Pulls](https://img.shields.io/docker/pulls/flywheel/hcp-icafix.svg)](https://hub.docker.com/r/flywheel/hcp-icafix/)
[![Docker Stars](https://img.shields.io/docker/stars/flywheel/hcp-icafix.svg)](https://hub.docker.com/r/flywheel/hcp-icafix/)
# flywheel/hcp-icafix
[Flywheel Gear](https://github.com/flywheel-io/gears/tree/master/spec) that runs [ICA-FIX denoising](https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/FIX) on functional data preprocessed according to the [Human Connectome Project](http://www.humanconnectome.org) Minimal Preprocessing Pipeline (MPP).  This is based on scripts from the v4.0-alpha release of the ICAFIX, PostFix, and RestingStateStats pipelines. For more info on the pipelines, see [HCP Pipelines](https://github.com/Washington-University/Pipelines). For more info on FSL FIX, including available classifiers, see [FSL FIX User Guide](https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/FIX/UserGuide).

## Important notes
* ICA-FIX works best when applied to time series with many volumes. Original HCP rfMRI scans were 15 minutes TR=720ms each (1200 volumes). If data was collected in shorter scans within the same session, it's recommended to concatenate these before running ICA. For this gear, you can provide multiple FuncZip inputs and the pipeline will handle the concatenation and split the outputs once it completes.
* If providing multiple FuncZip inputs, **make sure each HCP-Func gear was run with a unique fMRIName!** Otherwise, scans will be overwritten!

## Required inputs
1. FuncZip output from HCP-Func gear for at least one functional run.
2. StructZip output from the HCP-Struct gear (containing <code>T1w/</code>, <code>T2w/</code>, and <code>MNINonLinear/</code> folders).

## Configuration options
1. FIXClassifier: Name of FIX training file to use for classification. 'Standard', 'HCP_hp2000' (default), 'HCP7T_hp2000', 'WhII_MB6', 'WhII_Standard', 'UKBiobank'. See [FSL FIX User Guide: Trained-weights files](https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/FIX/UserGuide#Trained-weights_files) for details.
2. HighPassFilter: Cutoff of temporal highpass full-width (2*sigma) in seconds (default=2000). This should match the filter cutoff used during classifier training.
3. RegName: Surface registration to use during CIFTI resampling: either 'FS' (freesurfer) or 'MSMSulc'. ('Empty'=gear uses RegName from HCP-Structural)

## Outputs
* <code>\<subject\>\_\<fMRIName\>\_hcpicafix.zip</code>: Zipped output directory.
* <code>\<subject\>\_\<fMRIName\>\_RestingStateStats.zip</code>: Zipped RestingStateStats directory containing
  * <code>\<fMRIName\>\_Atlas\_stats.dscalar.nii</code>: spatial maps of SNR, CNR, etc...
  * <code>\<fMRIName\>\_Atlas\_stats.txt</code>: whole-brain summary of SNR, CNR, etc...
  * <code>RestingStateStats/*.png</code>: gray-plot images depicting impact of ICAFIX and other denoising strategies on time series and global signal.
* <code>\<subject\>\_\<fMRIName\>\_ICA_Classification_Scene.zip</code>: Zip containing wb_view .scene files to load into the [Connectome Workbench Viewer - wb_view](https://www.humanconnectome.org/software/connectome-workbench) to inspect ICA components and their classification.  After unzipping, view with <code>wb\_view \<subject\>/MNINonLinear/Results/\<fMRIName\>/\<fMRIName\>/\<fMRIName\>\_hp\<HP\>.ica/\*.scene</code>
* Note: When providing multiple FuncZip inputs, the outputs will be named <code>\<subject\>\_ICAFIX\_multi\_\<fMRIName1\>\_\<fMRIName2\>...</code>
* Logs (details to come...)

## Optional inputs
1. FuncZip2, FuncZip3, etc... HCP-Functional output zips from additional scans.
2. CustomClassifier: Supply your own .RData file containing training weights.
