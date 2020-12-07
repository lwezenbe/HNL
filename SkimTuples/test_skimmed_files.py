#
# Argument parser and logging
#
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('--year',     action='store',      default=None,   help='Select year', choices=['2016', '2017', '2018'], required = True)
args = argParser.parse_args()

input_path = '/storage_mnt/storage/user/lwezenbe/public/ntuples/HNL/'+args.year+'/Reco/tmp_DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/'

import ROOT
import glob
for f in glob.glob(input_path+'*'):
    in_file = ROOT.TFile(f, 'read')
    in_file.Close()
