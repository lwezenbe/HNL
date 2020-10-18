from HNL.Tools.mergeFiles import merge
import os
import glob
from HNL.Tools.helpers import makePathTimeStamped

#
# Argument parser and logging
#
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('bkgr',     action='store',      default=None,   help='Select bkgr')
argParser.add_argument('--onlyReco',     action='store_true',      default=False,   help='only have reco efficiency')
argParser.add_argument('--wp',     action='store',      default='tight',   help='only have reco efficiency')
args = argParser.parse_args()


from HNL.Samples.sampleManager import SampleManager
sample_manager = SampleManager(args.year, 'noskim', 'compareTauIdList_'+str(args.year))
jobs = []
for sample_name in sample_manager.sample_names:
    sample = sample_manager.getSample(sample_name)
    for njob in xrange(sample.split_jobs):
        jobs += [(sample.name, str(njob))]

#Merges subfiles if needed
input_file_path = os.getcwd()+'/data/compareTauID/includeReco/'
if args.onlyReco:
    input_file_path += 'onlyReco/'

merge_files = glob.glob(input_file_path + '*')
for mf in merge_files:
    if "Results" in mf: merge_files.pop(merge_files.index(mf))
    if not args.onlyReco and 'onlyReco' in mf: merge_files.pop(merge_files.index(mf))
script = os.path.expandvars(os.path.join('$CMSSW', 'src', 'HNL', 'ObjectSelection', 'compareTauID.py')
merge(merge_files, script, jobs, ('sample', 'subJob'))

list_of_bkgr_eff = {}
list_of_signal_eff = {}
list_of_bkgr_pt = {}
list_of_signal_pt = {}

inputfiles_eff = glob.glob(input_file_path + '*/*root')
samples = {f.split('/')[-2] for f in inputfiles_eff}
from HNL.Tools.efficiency import Efficiency
from HNL.Tools.helpers import getObjFromFile
for sample in samples:
    eff = Efficiency('efficiency_pt', None, None, input_file_path + sample+'/efficiency.root', subdirs = ['deeptauVSjets-none-none-'+args.wp, 'efficiency_pt'])
    if 'HNL' in sample:
        list_of_signal_eff[sample] = eff.getEfficiency() 
        list_of_signal_pt[sample] = getObjFromFile(os.path.expandvars('$CMSSW_BASE/src/HNL/Test/data/plotTau/gen/' + sample + '/variables.root'), 'pt/'+sample+'-pt')
        list_of_signal_pt[sample].Scale(1./list_of_signal_pt[sample].GetSumOfWeights())
    else:
        list_of_bkgr_eff[sample] = eff.getEfficiency()
        list_of_bkgr_pt[sample] = getObjFromFile(os.path.expandvars('$CMSSW_BASE/src/HNL/Test/data/plotTau/gen/' + sample + '/variables.root'), 'pt/'+sample+'-pt')
        list_of_bkgr_pt[sample].Scale(1./list_of_bkgr_pt[sample].GetSumOfWeights())

from HNL.Plotting.plot import Plot

output_dir = os.getcwd()+'/data/Results/compareTauID/includeReco/'
if args.onlyReco:     output_dir += 'onlyReco/'
output_dir = makePathTimeStamped(output_dir)

for sample in list_of_signal_eff.keys():
    legend_names = ['efficiency in '+sample, 'efficiency in '+args.bkgr, 'tau distribution in '+sample, 'tau distribution in '+args.bkgr]
    p = Plot([list_of_signal_eff[sample], list_of_bkgr_eff[args.bkgr]], legend_names, sample, bkgr_hist = [list_of_signal_pt[sample], list_of_bkgr_pt[args.bkgr]]) 
    final_dir = output_dir
    if not args.onlyReco:
        final_dir += '/'+args.wp+'/'
    p.drawHist(output_dir = final_dir, draw_option = 'EP',  bkgr_draw_option = 'EHist')  
