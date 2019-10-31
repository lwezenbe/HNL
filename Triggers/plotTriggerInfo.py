from HNL.Tools.mergeFiles import merge
import os
import glob

#Merges subfiles if needed
merge_files = glob.glob(os.getcwd()+'/data/*')
for mf in merge_files:
    if "Results" in mf: continue
    print mf
    merge(mf)


import glob
f_name = 'TrigEff'
inputFiles = glob.glob(os.getcwd()+'/data/*/'+f_name+'.root')

import ROOT
from HNL.Tools.helpers import rootFileContent, getObjFromFile
from HNL.Plotting.plot import Plot
from HNL.Plotting.plottingTools import draw2DHist
from HNL.Plotting.style import setDefault2D
from HNL.Tools.efficiency import efficiency

hists = {}
samples = []
keyNames = []
for f in inputFiles:
    sample = f.split('/')[-2]
    samples.append(sample)
    rf = ROOT.TFile(f)
    keyNames = [k[0] for k in rootFileContent(rf)]
    for k in keyNames:
        h = getObjFromFile(f, k+k+'_num').Clone(k.split('/')[1]+'_efficiency')
        h.Divide(getObjFromFile(f, k+k+'_denom'))
        if '2D' in k:
            p = Plot(k, h, samples, 'p_{T}^{trailing} [GeV]','p_{T}^{subleading} [GeV]' )
            p.draw2D(output_dir = os.getcwd()+'/data/Results/'+f_name+'/'+sample)
        else:
            try:
                hists[k].append(h)
            except:
                hists[k] = [h]

for k in keyNames:
    if '2D' in k:       continue
    if 'pt' in k:
        axis_labels = ('p_{T}^{trailing} [GeV]','efficiency')
    else:
        axis_labels = ('|#eta|_{trailing} [GeV]','efficiency')
        
    p = Plot(k, hists[k], samples, axis_labels[0], axis_labels[1] )
    p.drawHist(output_dir = os.getcwd()+'/data/Results/'+f_name)
    
