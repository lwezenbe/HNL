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
submission_parser.add_argument('--year',     action='store',      default=None,   help='Select year', choices=['2016', '2017', '2018'], required = True)
submission_parser.add_argument('--overwrite', action='store_true', default=False,                help='overwrite if valid output file already exists')
submission_parser.add_argument('--customList',  action='store',      default=None,               help='Name of a custom sample list. Otherwise it will use the appropriate noskim file.')
submission_parser.add_argument('--skimSelection',  action='store',      default=None,               help='Name of the selection.')
submission_parser.add_argument('--skimName',  action='store',      default='Reco',               help='Name of the skim.')
submission_parser.add_argument('--batchSystem', action='store',         default='HTCondor',  help='choose batchsystem', choices=['local', 'HTCondor', 'Cream02'])
submission_parser.add_argument('--subJob',   action='store',      default=None,   help='The number of the subjob for this sample')
submission_parser.add_argument('--isChild',  action='store_true', default=False,  help='mark as subjob, will never submit subjobs by itself')
submission_parser.add_argument('--dryRun',   action='store_true', default=False,  help='do not launch subjobs, only show them')


args = argParser.parse_args()

if not args.isChild:
    abort_script = raw_input("Did you check if all log files are ok? (y/n) \n")
    if abort_script == 'n' or abort_script == 'N':
        exit(0)

if args.batchSystem == 'HTCondor' and not args.isChild:
    jobs = [[0]]
    submitJobs(__file__, ('subJob'), jobs, argParser, jobLabel = 'mergeSkim')
    exit(0)

from HNL.Tools.helpers import fileSize, makeDirIfNeeded, isValidRootFile

def mergeSmallFile(merge_file):
    path, name = merge_file.rsplit('/', 1)
    os.system('hadd -f -v '+path+'/'+name.split('_', 1)[1]+'.root '+merge_file+'/*root')
    os.system('rm -r '+ merge_file)

def mergeLargeFile(merge_file):
    path, name = merge_file.rsplit('/', 1)
    sub_files = sorted(glob.glob(merge_file+'/*'))
    split_list = []
    tmp_list = []

    makeDirIfNeeded(os.path.join(path, name, 'tmp_batches', 'x'))

    for i, file_list in enumerate(sub_files):
        if i != 0 and (i % 20 == 0 or i == len(merge_files)-1):
            tmp_list.append(file_list)
            split_list.append([x for x in tmp_list])
            tmp_list = []
        else:
            tmp_list.append(file_list)

    for j, file_list in enumerate(split_list):
        os.system('hadd -f -v '+path+'/'+name+ '/tmp_batches/batch_'+str(j)+ '.root '+' '.join(file_list))
        for f in file_list:
            os.system('rm '+f)

    os.system('hadd -f -v '+path+'/'+name.split('_', 1)[1]+'.root '+path+'/'+name+ '/tmp_batches/*root')
    os.system('rm -rf '+path+'/'+name)

pnfs_base = os.path.join('/pnfs/iihe/cms/store/user', os.path.expandvars('$USER'), 'skimmedTuples/HNL', args.skimSelection, args.year, args.skimName)
pnfs_backup_base = os.path.join('/pnfs/iihe/cms/store/user', os.path.expandvars('$USER'), 'skimmedTuples/HNL/Backup', args.skimSelection, args.year, args.skimName)
if not args.batchSystem == 'HTCondor':
    pnfs_base = 'srm://maite.iihe.ac.be:8443'+pnfs_base
    pnfs_backup_base = 'srm://maite.iihe.ac.be:8443'+pnfs_backup_base

#Merges subfiles if needed
if args.batchSystem != 'HTCondor':
    merge_files = glob.glob('/storage_mnt/storage/user/'+os.path.expandvars('$USER')+'/public/ntuples/HNL/'+args.skimSelection+'/'+args.year+'/'+args.skimName+'/tmp*')
else:
    merge_files = glob.glob(pnfs_base+'/tmp*')
merge_files = sorted(merge_files)

if args.batchSystem != 'HTCondor':
    os.system('gfal-mkdir '+pnfs_base)
    os.system('gfal-mkdir '+pnfs_backup_base)
else:
    makeDirIfNeeded(pnfs_base)
    makeDirIfNeeded(pnfs_backup_base)

for mf in merge_files:
    if 'Data' in mf: continue
    path, name = mf.rsplit('/', 1)
    new_name = name.split('_', 1)[1]+'.root'

    if args.batchSystem != 'HTCondor':
        os.system('gfal-rm '+pnfs_backup_base+'/'+new_name)
        os.system('gfal-copy '+pnfs_base+'/'+new_name+' '+pnfs_backup_base+'/'+new_name)
        os.system('gfal-rm '+pnfs_base+'/'+new_name)
    else:
        if isValidRootFile(pnfs_base+'/'+new_name):
            os.system('scp '+pnfs_base+'/'+new_name + ' '+ pnfs_backup_base+'/'+new_name)

    sub_files = glob.glob(mf+'/*')
    tot_size = 0
    for sf in sub_files:
        tot_size += fileSize(sf)
    
    if tot_size > 1000:
        mergeLargeFile(mf)
    else:
        mergeSmallFile(mf)

    if args.batchSystem != 'HTCondor':
        #Move to pnfs once it is merged locally
        os.system('gfal-copy file://'+path+'/'+new_name+' '+pnfs_base+'/'+new_name)
        os.system('rm '+path+'/'+new_name)
