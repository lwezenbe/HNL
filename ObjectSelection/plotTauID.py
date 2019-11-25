from HNL.Tools.ROC import ROC
from HNL.Tools.mergeFiles import merge
import os
import glob
from HNL.Tools.helpers import makePathTimeStamped


#Merges subfiles if needed
merge_files = glob.glob(os.getcwd()+'/data/compareTauID/*')
for mf in merge_files:
    if "Results" in mf: continue
    merge(mf)


import glob
inputFiles = glob.glob(os.getcwd()+'/data/compareTauID/*HNL*/*-none-none.root')
bkgr_base = os.getcwd()+'/data/compareTauID/WZ'
samples = {f.split('/')[-2] for f in inputFiles}
f_names = {f.split('/')[-1].split('.')[0] for f in inputFiles}

print samples

import ROOT
from HNL.Tools.helpers import rootFileContent, getObjFromFile
from HNL.Plotting.plot import Plot
from HNL.Tools.ROC import ROC

output_dir = makePathTimeStamped(os.getcwd()+'/data/Results/compareTauID')
for sample in samples:
    print 'plotting', sample
    curves = []
    for f_name in f_names:
        keyNames = []
        sub_files = glob.glob(os.getcwd()+'/data/compareTauID/'+sample+'/'+f_name+'.root')
        for f in sub_files:
            roc_curve = ROC(f_name, 1., '', f, misid_path =bkgr_base + '/'+f_name+'.root')
            curves.append(roc_curve.return_graph())
    p = Plot(curves, f_names, sample, 'efficiency', 'misid')
    p.drawGraph(output_dir = output_dir)
        
#graph = roc_curve.return_graph()
#import ROOT
#c = ROOT.TCanvas('x', 'x')
#graph.Draw()
