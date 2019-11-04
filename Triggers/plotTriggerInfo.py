from HNL.Tools.mergeFiles import merge
import os
import glob
from HNL.Tools.helpers import makePathTimeStamped

#Merges subfiles if needed
merge_files = glob.glob(os.getcwd()+'/data/*')
for mf in merge_files:
    if "Results" in mf: continue
    merge(mf)


import glob
f_name = 'TrigEff'
inputFiles = glob.glob(os.getcwd()+'/data/*/'+f_name+'.root')

import ROOT
from HNL.Tools.helpers import rootFileContent, getObjFromFile
from HNL.Plotting.plot import Plot
from HNL.Plotting.plottingTools import draw2DHist
from HNL.Plotting.style import setDefault2D

output_dir = makePathTimeStamped(os.getcwd()+'/data/Results/'+f_name)
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
            p = Plot(k, h, samples, h.GetXaxis().GetTitle(), h.GetYaxis().GetTitle())
            p.draw2D(output_dir = output_dir+'/'+sample)
        else:
            try:
                hists[k].append(h)
            except:
                hists[k] = [h]

for k in keyNames:
    if '2D' in k:       continue
        
    p = Plot(k, hists[k], samples, hists[k][0].GetXaxis().GetTitle(), hists[k][0].GetYaxis().GetTitle() )
    p.drawHist(output_dir = output_dir)
    
