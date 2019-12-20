from HNL.Tools.ROC import ROC
from HNL.Tools.mergeFiles import merge
import os
import sys
import glob
from HNL.Tools.helpers import makePathTimeStamped


#Merges subfiles if needed
merge_files = glob.glob(os.getcwd()+'/data/compareTauID/*')
for mf in merge_files:
    if "Results" in mf: continue
    merge(mf)

#
# Argument parser and logging
#
import os, argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('algo',     action='store',      default=None,   help='Select algorithms', choices=['iso', 'eleDiscr', 'muDiscr'])
argParser.add_argument('bkgr',     action='store',      default=None,   help='Select bkgr')
args = argParser.parse_args()

if args.algo == 'iso':
    input_name = '*-none-none.root'
elif args.algo == 'eleDiscr':
    input_name = 'none-*-none.root'
elif args.algo == 'muDiscr':
    input_name = 'none-none-*.root'

inputFiles = glob.glob(os.getcwd()+'/data/compareTauID/*HNL*/'+input_name)
bkgr_base = os.getcwd()+'/data/compareTauID/'+args.bkgr
samples = {f.split('/')[-2] for f in inputFiles}
f_names = {f.split('/')[-1].split('.')[0] for f in inputFiles}

print samples, f_names

from HNL.Plotting.plot import Plot

output_dir = makePathTimeStamped(os.getcwd()+'/data/Results/compareTauID/'+args.algo+'/'+args.bkgr)
for sample in samples:
    print 'plotting', sample
    curves = []
    for f_name in f_names:
        keyNames = []
        sub_files = glob.glob(os.getcwd()+'/data/compareTauID/'+sample+'/'+f_name+'.root')
        for f in sub_files:
            roc_curve = ROC(f_name, 1., '', f, misid_path =bkgr_base + '/'+f_name+'.root')
            curves.append(roc_curve.returnGraph())
    p = Plot(curves, f_names, sample, 'efficiency', 'misid', y_log=True)
    p.drawGraph(output_dir = output_dir)
        
#graph = roc_curve.return_graph()
#import ROOT
#c = ROOT.TCanvas('x', 'x')
#graph.Draw()
