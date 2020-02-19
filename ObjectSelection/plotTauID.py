from HNL.Tools.ROC import ROC
from HNL.Tools.mergeFiles import merge
import os
import glob
from HNL.Tools.helpers import makePathTimeStamped

#
# Argument parser and logging
#
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('algo',     action='store',      default=None,   help='Select algorithms', choices=['iso', 'eleDiscr', 'muDiscr'])
argParser.add_argument('bkgr',     action='store',      default=None,   help='Select bkgr')
args = argParser.parse_args()


#Merges subfiles if needed
merge_files = glob.glob(os.getcwd()+'/data/compareTauID/*')
for mf in merge_files:
    if "Results" in mf: continue
    merge(mf)

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
    ordered_f_names = []
    for f_name in f_names:
        keyNames = []
        ordered_f_names.append(f_name)
        sub_files = glob.glob(os.getcwd()+'/data/compareTauID/'+sample+'/'+f_name+'.root')
        for f in sub_files:
            roc_curve = ROC(f_name, 1., '', f, misid_path =bkgr_base + '/'+f_name+'.root')
            curves.append(roc_curve.returnGraph())
    p = Plot(curves, ordered_f_names, sample, 'efficiency', 'misid', y_log=True)
    p.drawGraph(output_dir = output_dir)
       
from HNL.Tools.efficiency import Efficiency
from HNL.Tools.helpers import rootFileContent
from ROOT import TFile
var = ['pt', 'eta']
inputFiles = {'efficiency' : glob.glob(os.getcwd()+'/data/compareTauID/*/*efficiency*'), 'fakerate': glob.glob(os.getcwd()+'/data/compareTauID/*/*fakerate*')}
for eff in ['efficiency', 'fakerate']:
    for f in inputFiles[eff]:
        rf = TFile(f)
        key_names = [k[0] for k in rootFileContent(rf)]
        filtered_key_names = {fk.rsplit('-', 1)[0] for fk in key_names}
        for fk in filtered_key_names:
            sample = f.split('/')[-2]
            fk_name = fk.split('/')[1]
            wp_list = []
            efficiency = []
            for k in key_names:
                if not fk_name in k: continue
                wp = k.rsplit('-', 1)[-1]
                wp_list.append(wp)
                for v in var:
                    print f, v
                    efficiency.append(Efficiency(eff+'_'+v, None, None, f, subdirs = [k, eff+'_'+v]))
            p = Plot([eff.getEfficiency() for eff in efficiency], wp_list)
            p.drawHist(output_dir = os.getcwd()+'/data/Results/compareTauID/'+args.algo+'/var/'+sample, draw_option = 'Hist')
        
 
#graph = roc_curve.return_graph()
#import ROOT
#c = ROOT.TCanvas('x', 'x')
#graph.Draw()
