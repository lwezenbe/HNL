from HNL.Tools.ROC import ROC
from HNL.Tools.mergeFiles import merge
import os
import glob
from HNL.Tools.helpers import makePathTimeStamped, getObjFromFile
from HNL.Plotting.plottingTools import extraTextFormat

#
# Argument parser and logging
#
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
submission_parser = argParser.add_argument_group('submission', 'Arguments for submission. Any arguments not in this group will not be regarded for submission.')
submission_parser.add_argument('--year',     action='store',      default=None,   help='Select year', choices=['2016', '2017', '2018'])
submission_parser.add_argument('--batchSystem', action='store',         default='HTCondor',  help='choose batchsystem', choices=['local', 'HTCondor', 'Cream02'])
submission_parser.add_argument('--flavor', required = True, type=int, default=0,  help='flavor of lepton under consideration. 0 = electron, 1 = muon', choices = [0, 1])
submission_parser.add_argument('--dryRun',   action='store_true', default=False,  help='do not launch subjobs, only show them')
submission_parser.add_argument('--includeReco', action='store_true', default=False, 
    help='look at the efficiency for a gen tau to be both reconstructed and identified. Currently just fills the efficiency for isolation')
submission_parser.add_argument('--onlyReco',   action='store_true', default=False,  help='look at the efficiency for a gen tau to be reconstructed. Currently just fills the efficiency for isolation')
submission_parser.add_argument('--isTest',   action='store_true', default=False,  help='Run a small test')

argParser.add_argument('--signal',  required=True,   action='store',      default=None,   help='Select bkgr')
argParser.add_argument('--bkgr',  required=True,   action='store',      default=None,   help='Select bkgr')

args = argParser.parse_args()


# from HNL.Samples.sampleManager import SampleManager
# sample_manager = SampleManager(2016, 'prelegacy', 'noskim', 'compareTauIdList_2016')
# jobs = []
# for sample_name in sample_manager.sample_names:
#     sample = sample_manager.getSample(sample_name)
#     for njob in xrange(sample.split_jobs):
#         jobs += [(sample.name, str(njob))]

# #Merges subfiles if needed
# if args.isTest:
#     merge_files = glob.glob(os.getcwd()+'/data/testArea/compareLightLeptonId/*')
# else:
#     merge_files = glob.glob(os.getcwd()+'/data/compareLightLeptonId/*')
# for mf in merge_files:
#     if "Results" in mf: merge_files.pop(merge_files.index(mf))
# script = os.path.expandvars(os.path.join('$CMSSW_BASE', 'src', 'HNL', 'ObjectSelection', 'compareLightLeptonId.py'))
# merge(merge_files, script, jobs, ('sample', 'subJob'), argParser, istest=args.isTest)

if not args.isTest:
    input_signal = glob.glob(os.getcwd()+'/data/compareLightLeptonId/'+args.signal+'/*ROC-'+str(args.flavor)+'.root')
    bkgr_prefix = os.getcwd()+'/data/compareLightLeptonId/'+args.bkgr
else:
    input_signal = glob.glob(os.getcwd()+'/data/testArea/compareLightLeptonId/'+args.signal+'/*ROC-'+str(args.flavor)+'.root')
    bkgr_prefix = os.getcwd()+'/data/testArea/compareLightLeptonId/'+args.bkgr

from HNL.Plotting.plot import Plot

if args.isTest: 
    output_dir = makePathTimeStamped(os.getcwd()+'/data/Results/compareLightLeptonId/ROC/'+args.signal+'-'+args.bkgr)
else:
    output_dir = makePathTimeStamped(os.getcwd()+'/data/testArea/Results/compareLightLeptonId/ROC/'+args.signal+'-'+args.bkgr)
curves = []
ordered_f_names = []
extra_text = [extraTextFormat('efficiency: '+args.signal, xpos = 0.2, ypos = 0.82, textsize = 1.2, align = 12)]  #Text to display event type in plot
extra_text.append(extraTextFormat('misid: '+args.bkgr, textsize = 1.2, align = 12))  #Text to display event type in plot

for f_path in input_signal:
    f_name = f_path.rsplit('/', 1)[1].split('.')[0]
    ordered_f_names.append(f_name.split('-')[0])
    roc_curve = ROC(f_name.split('-')[0], f_path, misid_path =bkgr_prefix + '/'+f_name+'.root')
    curves.append(roc_curve.returnGraph())
p = Plot(curves, ordered_f_names, args.signal+'_'+str(args.flavor), 'efficiency', 'misid', y_log=True, extra_text=extra_text)
print output_dir
p.drawGraph(output_dir = output_dir)
       
from HNL.Tools.efficiency import Efficiency
from HNL.Tools.helpers import rootFileContent
from ROOT import TFile
var = ['pt', 'eta']
inputFiles = {'efficiency' : glob.glob(os.getcwd()+'/data/compareLightLeptonId/'+args.signal+'/efficiency-'+str(args.flavor)+'.root'), 
        'fakerate': glob.glob(os.getcwd()+'/data/compareLightLeptonId/'+args.bkgr+'/fakerate-'+str(args.flavor)+'.root')}
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
                p = Plot([efficiency.getEfficiency() for efficiency in tmp_list], [i+' '+fk for i in list_of_eff[fk].keys()]+['lepton distribution']
                        ,  eff_name+'_'+str(args.flavor)+'_'+v, bkgr_hist = bkgr_hist)
                p.drawHist(output_dir = os.getcwd()+'/data/Results/compareLightLeptonId/'+fk+'/var/'+sample, draw_option = 'Hist')