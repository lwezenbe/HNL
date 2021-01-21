import ROOT
import glob, os
from HNL.Tools.helpers import makeDirIfNeeded, progress

list_of_datafiles = ['SingleMuon', 'SingleElectron', 'DoubleMuon', 'DoubleEG', 'MuonEG']


import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('--year',        action='store',         default='2016')
argParser.add_argument('--skim',        action='store',         default='Reco')
argParser.add_argument('--skimSelection',        action='store',         default='Reco')

args = argParser.parse_args()

output_folder = '/storage_mnt/storage/user/lwezenbe/public/ntuples/HNL/'+args.skimSelection+'/'+args.year+ '/' + args.skim +'/tmp_DataFiltered'
makeDirIfNeeded(output_folder+'/x')

event_information_set = set()

file_list =  glob.glob('/storage_mnt/storage/user/lwezenbe/public/ntuples/HNL/'+args.skimSelection+'/'+args.year+ '/' + args.skim +'/tmp_Data/*.root')
for i, sub_f_name in enumerate(file_list):
    progress(i, len(file_list))


    f = ROOT.TFile(sub_f_name)
    c = f.Get('blackJackAndHookers/blackJackAndHookersTree')
    try:
        c.GetEntry()
    except:
        continue     

    output_file = ROOT.TFile(output_folder +'/'+ sub_f_name.split('/')[-1], 'recreate')
    output_file.mkdir('blackJackAndHookers')
    output_file.cd('blackJackAndHookers')
    output_tree = c.CloneTree(0)

    for entry in xrange(c.GetEntries()):
        c.GetEntry(entry)
        event_information = (c._runNb, c._lumiBlock, c._eventNb)
        if event_information in event_information_set:      continue
        else:
            event_information_set.add(event_information)
            output_tree.Fill()        
    
    output_file.cd('blackJackAndHookers')
    output_file.Write()


    f.Close()
    output_file.Close()

os.system('hadd -f '+output_folder+'/../Data_'+args.year+'.root '+output_folder + '/*.root')
