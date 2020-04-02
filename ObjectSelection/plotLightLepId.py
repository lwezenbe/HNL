from HNL.Tools.ROC import ROC
from HNL.Tools.mergeFiles import merge
import os
import glob
from HNL.Tools.helpers import makePathTimeStamped, getObjFromFile

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
inputFiles = {'efficiency' : glob.glob(os.getcwd()+'/data/compareLightLeptonId/'+args.signal+'/efficiency-'+str(args.flavor)+'.root'), 'fakerate': glob.glob(os.getcwd()+'/data/compareLightLeptonId/'+args.bkgr+'/fakerate-'+str(args.flavor)+'.root')}
for eff_name in ['efficiency', 'fakerate']:
    for f in inputFiles[eff_name]:
        print f
        rf = TFile(f)
        key_names = [k[0] for k in rootFileContent(rf)]
        filtered_key_names = {fk.rsplit('-', 1)[0].split('/')[-1] for fk in key_names}
        list_of_eff = {}
        for fk in filtered_key_names: #algo
            list_of_eff[fk] = {}
            sample = f.split('/')[-2]
            for k in [i.split('-', 1)[1] for i in key_names if fk in i]: #wps
                list_of_eff[fk][k] = {}
                for v in var:
                    list_of_eff[fk][k][v] = Efficiency(eff_name+'_'+v, None, None, f, subdirs = [fk+'-'+k, eff_name+'_'+v])
                
        for fk in filtered_key_names: #algo
            for v in var:
                bkgr_hist = getObjFromFile(f, fk+'-'+k+'/'+eff_name+'_'+v+'/'+eff_name+'_'+v+'_denom')
                tmp_list = [list_of_eff[fk][i][v] for i in list_of_eff[fk].keys()]
                scale_factor = 0.25 if v == 'pt' else 1.
                bkgr_hist.Scale(scale_factor*tmp_list[0].getEfficiency().GetSumOfWeights()/bkgr_hist.GetSumOfWeights())
                p = Plot([efficiency.getEfficiency() for efficiency in tmp_list], [i+' '+fk for i in list_of_eff[fk].keys()]+['lepton distribution'],  eff_name+'_'+args.flavor+'_'+v, bkgr_hist = bkgr_hist)
                p.drawHist(output_dir = os.getcwd()+'/data/Results/compareLightLeptonId/'+fk+'/var/'+sample, draw_option = 'Hist')
                
        
 
#graph = roc_curve.return_graph()
#import ROOT
#c = ROOT.TCanvas('x', 'x')
#graph.Draw()
