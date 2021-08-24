import ROOT 
from HNL.TMVA.inputHandler import InputHandler
from HNL.Tools.helpers import makeDirIfNeeded

import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
submission_parser.add_argument('--year',     action='store',      default=None,   help='Select year. Enter "all" for all years')
submission_parser.add_argument('--era',     action='store',       default='prelegacy', choices = ['UL', 'prelegacy'],   help='Select era', required=True)
argParser.add_argument('--region', action='store', default='baseline', type=str,  help='What region do you want to select for?', 
    choices=['baseline', 'lowMassSR', 'highMassSR'])
argParser.add_argument('--selection',   action='store', default='default',  help='Select the type of selection for objects', choices=['leptonMVAtop', 'AN2017014', 'default', 'Luka', 'TTT'])
args = argParser.parse_args()

ih = InputHandler(args.era, args.year, args.region, args.selection)

#use getTree and scramble background
for signal in ih.signal_names:
    if signal.split('_')[-1] in ['e', 'mu']:
        name = 'NoTau/trainingtree'
    else:
        name = 'Total/trainingtree'
    signal_tree = ih.getTree(signal, name=name, signal_only=True).CloneTree()
    bkgr_tree = ih.getTree(signal, name=name, bkgr_only=True).CloneTree()
    
    fname = '/storage_mnt/storage/user/lwezenbe/public/ntuples/HNL/TMVA/'+args.era+args.year+'/'+args.region+'-'+args.selection+'/ForExternalTraining/'+signal+'.root'
    makeDirIfNeeded(fname)
    out_file = ROOT.TFile(fname, 'recreate')
    signal_tree.Write('signaltree')
    bkgr_tree.Write('backgroundtree')
    out_file.Close()