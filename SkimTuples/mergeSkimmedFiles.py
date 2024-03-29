import os
import glob
import itertools
from HNL.Tools.jobSubmitter import submitJobs

#
# Argument parser and logging
#
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
submission_parser = argParser.add_argument_group('submission', 'Arguments for submission. Any arguments not in this group will not be regarded for submission.')
submission_parser.add_argument('--year',     action='store',      default=None,   help='Select year')
submission_parser.add_argument('--era',     action='store',       default='UL', choices = ['UL', 'prelegacy'],   help='Select era')
submission_parser.add_argument('--skimSelection',  action='store',      default='default',               help='Name of the selection.')
submission_parser.add_argument('--skimName',  action='store',      default='Reco',               help='Name of the skim.')
submission_parser.add_argument('--sample',  action='store',      default=None,               help='Name of the skim.')
submission_parser.add_argument('--batchSystem', action='store',         default='HTCondor',  help='choose batchsystem', choices=['local', 'HTCondor', 'Cream02'])
submission_parser.add_argument('--subJob',   action='store',      default=0,   help='The number of the subjob for this sample')
submission_parser.add_argument('--isChild',  action='store_true', default=False,  help='mark as subjob, will never submit subjobs by itself')
submission_parser.add_argument('--dryRun',   action='store_true', default=False,  help='do not launch subjobs, only show them')
submission_parser.add_argument('--isTest',   action='store_true', default=False,  help='Run a small test')
submission_parser.add_argument('--backupName',   action='store', default=None,  help='Give backup a name for special cases')
submission_parser.add_argument('--region',   action='store', default=None,  help='Choose the selection region', 
    choices=['baseline', 'highMassSR', 'lowMassSR', 'ZZCR', 'WZCR', 'ConversionCR'])

args = argParser.parse_args()

if not args.isChild:
    abort_script = raw_input("Did you check if all log files are ok? (y/n) \n")
    if abort_script == 'n' or abort_script == 'N':
        exit(0)

if args.batchSystem == 'HTCondor' and not args.isChild and not args.isTest and args.region is None:
    jobs = [[0]]
    submitJobs(__file__, ['subJob'], jobs, argParser, jobLabel = 'mergeSkim')
    exit(0)

from HNL.Tools.helpers import fileSize, makeDirIfNeeded, isValidRootFile

def mergeSmallFile(merge_file):
    path, name = merge_file.rsplit('/', 1)
    if not args.isTest:
        os.system('hadd -f -v '+path+'/'+name.split('_', 1)[1]+'.root '+merge_file+'/*root')
#        os.system('rm -r -f '+ merge_file)
    else:
        makeDirIfNeeded(path+'/testArea/'+name.split('_', 1)[1]+'.root')
        os.system('hadd -f -v '+path+'/testArea/'+name.split('_', 1)[1]+'.root '+merge_file+'/*root')

def mergeLargeFile(merge_file):
    path, name = merge_file.rsplit('/', 1)
    sub_files = sorted(glob.glob(merge_file+'/*'))
    split_list = []
    tmp_list = []

    if args.isTest:
        makeDirIfNeeded(os.path.join(path, 'testArea', name, 'tmp_batches', 'x'))
    else:
        makeDirIfNeeded(os.path.join(path, name, 'tmp_batches', 'x'))

    for i, file_list in enumerate(sub_files):
        if i != 0 and (i % 20 == 0 or i == len(sub_files)-1):
            tmp_list.append(file_list)
            split_list.append([x for x in tmp_list])
            tmp_list = []
        else:
            tmp_list.append(file_list)

    for j, file_list in enumerate(split_list):
        if not args.isTest:
            os.system('hadd -f -v '+path+'/'+name+ '/tmp_batches/batch_'+str(j)+ '.root '+' '.join(file_list))
#            for f in file_list:
#                os.system('rm '+f)
        else:
            os.system('hadd -f -v '+path+'/testArea/'+name+ '/tmp_batches/batch_'+str(j)+ '.root '+' '.join(file_list))

    if args.isTest:
        os.system('hadd -f -v '+path+'/testArea/'+name.split('_', 1)[1]+'.root '+path+'/testArea/'+name+ '/tmp_batches/*root')
    else:
        os.system('hadd -f -v '+path+'/'+name.split('_', 1)[1]+'.root '+path+'/'+name+ '/tmp_batches/*root')
        os.system('rm -rf '+path+'/'+name+'/tmp_batches')

skim_selection_string = args.skimSelection if args.region is None else args.skimSelection+'/'+args.region 
pnfs_base = os.path.join('/pnfs/iihe/cms/store/user', os.path.expandvars('$USER'), 'skimmedTuples/HNL', skim_selection_string, args.era+args.year, args.skimName)
pnfs_backup_base = os.path.join('/pnfs/iihe/cms/store/user', os.path.expandvars('$USER'), 'skimmedTuples/HNL/Backup', skim_selection_string, args.era+args.year, args.skimName, args.backupName if args.backupName is not None else '')
#if not args.batchSystem == 'HTCondor':
#    pnfs_base = 'srm://maite.iihe.ac.be:8443'+pnfs_base
#    pnfs_backup_base = 'srm://maite.iihe.ac.be:8443'+pnfs_backup_base

#Merges subfiles if needed
sample_name = '*' if args.sample is None else args.sample
merge_files = glob.glob(pnfs_base+'/tmp_'+sample_name+'*')
print pnfs_base+'/tmp_'+sample_name+'*'
print merge_files
merge_files = sorted(merge_files)

makeDirIfNeeded(pnfs_base+'/x')
makeDirIfNeeded(pnfs_backup_base+'/x')

for mf in merge_files:
    path, name = mf.rsplit('/', 1)
    new_name = name.split('_', 1)[1]+'.root'
#    if not args.isTest and args.backupName != 'nobackup':
#        if isValidRootFile(pnfs_base+'/'+new_name):
#            continue
#            if isValidRootFile(pnfs_backup_base+'/'+new_name):
#                os.system('rm -f '+ pnfs_backup_base+'/'+new_name)
#            os.system('scp '+pnfs_base+'/'+new_name + ' '+ pnfs_backup_base+'/'+new_name)
   
    sub_files = glob.glob(mf+'/*')
    tot_size = 0
    for sf in sub_files:
        tot_size += fileSize(sf)
    
    if tot_size > 1000:
        mergeLargeFile(mf)
    else:
        mergeSmallFile(mf)
        
#    mergeSmallFile(mf)
