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
argParser.add_argument('signal',     action='store',      default=None,   help='Select bkgr')
argParser.add_argument('bkgr',     action='store',      default=None,   help='Select bkgr')
argParser.add_argument('flavor',     action='store',      default=None,   help='0: electrons, 1:muons')
args = argParser.parse_args()


#Merges subfiles if needed
merge_files = glob.glob(os.getcwd()+'/data/compareLightLeptonId/*')
for mf in merge_files:
    if "Results" in mf: continue
    merge(mf)

input_signal = glob.glob(os.getcwd()+'/data/compareLightLeptonId/'+args.signal+'/*ROC-'+args.flavor+'.root')
bkgr_prefix = os.getcwd()+'/data/compareLightLeptonId/'+args.bkgr

from HNL.Plotting.plot import Plot

output_dir = makePathTimeStamped(os.getcwd()+'/data/Results/compareLightLeptonId/ROC/'+args.signal+'-'+args.bkgr)
curves = []
ordered_f_names = []
for f_path in input_signal:
    f_name = f_path.rsplit('/', 1)[1].split('.')[0]
    ordered_f_names.append(f_name)
    roc_curve = ROC(f_name.split('-')[0], 1., '', f_path, misid_path =bkgr_prefix + '/'+f_name+'.root')
    curves.append(roc_curve.returnGraph())
p = Plot(curves, ordered_f_names, args.signal+'_'+args.flavor, 'efficiency', 'misid', y_log=True)
p.drawGraph(output_dir = output_dir)
       
from HNL.Tools.efficiency import Efficiency
from HNL.Tools.helpers import rootFileContent
from ROOT import TFile
var = ['pt', 'eta']
inputFiles = {'efficiency' : glob.glob(os.getcwd()+'/data/compareLightLeptonId/'+args.signal+'/*efficiency*'), 'fakerate': glob.glob(os.getcwd()+'/data/compareLightLeptonId/'+args.bkgr+'/*fakerate*')}
for eff_name in ['efficiency', 'fakerate']:
    for f in inputFiles[eff_name]:
        print f
        rf = TFile(f)
        key_names = [k[0] for k in rootFileContent(rf)]
        filtered_key_names = {fk.rsplit('-', 1)[0] for fk in key_names}
        for fk in filtered_key_names:
            sample = f.split('/')[-2]
            fk_name = fk.split('/')[1]
            wp_list = []
            for k in key_names:
                print k
                if not fk_name in k: continue
                algo = k.rsplit('-', 1)[0]
                wp = k.rsplit('-', 1)[-1]
                wp_list.append(wp)
                for v in var:
                    efficiency = Efficiency(eff_name+'_'+v, None, None, f, subdirs = [k, eff_name+'_'+v])
                    p = Plot(efficiency.getEfficiency(), wp_list,  eff_name+'_'+args.flavor+'_'+v)
                    p.drawHist(output_dir = os.getcwd()+'/data/Results/compareLightLeptonId/'+algo+'/var/'+sample, draw_option = 'Hist')
        
 
#graph = roc_curve.return_graph()
#import ROOT
#c = ROOT.TCanvas('x', 'x')
#graph.Draw()
