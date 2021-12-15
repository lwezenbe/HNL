import ROOT
import glob, os
from HNL.Tools.helpers import makeDirIfNeeded, progress

list_of_datafiles = ['SingleMuon', 'SingleElectron', 'DoubleMuon', 'DoubleEG', 'MuonEG']


import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")

submission_parser = argParser.add_argument_group('submission', 'Arguments for submission. Any arguments not in this group will not be regarded for submission.')
submission_parser.add_argument('--year',     action='store',      default=None,   help='Select year')
submission_parser.add_argument('--era',     action='store',       default='prelegacy', choices = ['UL', 'prelegacy'],   help='Select era')
submission_parser.add_argument('--skimSelection',  action='store',      default='default',               help='Name of the selection.')
submission_parser.add_argument('--skimName',  action='store',      default='Reco',               help='Name of the skim.')
submission_parser.add_argument('--batchSystem', action='store',         default='HTCondor',  help='choose batchsystem', choices=['local', 'HTCondor', 'Cream02'])
submission_parser.add_argument('--subJob',   action='store',      default=None,   help='The number of the subjob for this sample')
submission_parser.add_argument('--isChild',  action='store_true', default=False,  help='mark as subjob, will never submit subjobs by itself')
submission_parser.add_argument('--dryRun',   action='store_true', default=False,  help='do not launch subjobs, only show them')
submission_parser.add_argument('--isTest',   action='store_true', default=False,  help='Run a small test')
submission_parser.add_argument('--region',   action='store', default=None,  help='Choose the selection region', 
    choices=['baseline', 'highMassSR', 'lowMassSR', 'ZZCR', 'WZCR', 'ConversionCR'])


args = argParser.parse_args()


if not args.isChild:
    abort_script = raw_input("Did you check if all log files are ok? (y/n) \n")
    if abort_script == 'n' or abort_script == 'N':
        exit(0)

if args.batchSystem == 'HTCondor' and not args.isChild and not args.isTest and args.region is None:
    from HNL.Tools.jobSubmitter import submitJobs
    jobs = [[0]]
    submitJobs(__file__, ('subJob'), jobs, argParser, jobLabel = 'mergeSkim')
    exit(0)


if args.batchSystem == 'Cream02':
    input_folder = '/storage_mnt/storage/user/lwezenbe/public/ntuples/HNL/'+args.skimSelection+'/'+args.era+args.year+ '/' + args.skimName +'/tmp_Data/'
    output_folder = '/storage_mnt/storage/user/lwezenbe/public/ntuples/HNL/'+args.skimSelection+'/'+args.era+args.year+ '/' + args.skimName +'/tmp_DataFiltered'
else:
    pnfs_base =  os.path.join('/pnfs/iihe/cms/store/user', os.path.expandvars('$USER'), 'skimmedTuples/HNL', args.skimSelection, args.era+args.year, args.skimName)
    input_folder = pnfs_base +'/tmp_Data'
    output_folder = pnfs_base +'/tmp_DataFiltered'
makeDirIfNeeded(output_folder+'/x')

event_information_set = set()

file_list =  glob.glob(input_folder+'/*.root')
for i, sub_f_name in enumerate(file_list):
    progress(i, len(file_list))


    f = ROOT.TFile(sub_f_name)
    c = f.Get('blackJackAndHookers/blackJackAndHookersTree')
    try:
        c.GetEntry()
    except:
        continue     

    if not args.isTest:
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
    
    if not args.isTest:
        output_file.cd('blackJackAndHookers')
        output_file.Write()

    f.Close()
    if not args.isTest:
        output_file.Close()

os.system('hadd -f '+output_folder+'/../Data_'+args.era+args.year+'.root '+output_folder + '/*.root')
