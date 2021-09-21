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

args = argParser.parse_args()

import glob
import os
tomove_files = glob.glob('/storage_mnt/storage/user/'+os.path.expandvars('$USER')+'/public/ntuples/HNL/'+args.skimSelection+'/'+args.year+'/'+args.skimName+'/*.root')

pnfs_base = os.path.join('srm://maite.iihe.ac.be:8443/pnfs/iihe/cms/store/user', os.path.expandvars('$USER'), 'skimmedTuples/HNL', args.skimSelection, args.year, args.skimName)
pnfs_backup_base = os.path.join('srm://maite.iihe.ac.be:8443/pnfs/iihe/cms/store/user', os.path.expandvars('$USER'), 'skimmedTuples/HNL/Backup', args.skimSelection, args.year, args.skimName)
try:
    os.system('gfal-mkdir '+pnfs_base)
    os.system('gfal-mkdir '+pnfs_backup_base)
except:
    pass

for mf in tomove_files:
    path, name = mf.rsplit('/', 1)
    os.system('gfal-rm '+pnfs_backup_base+'/'+name)
    os.system('gfal-copy '+pnfs_base+'/'+name+' '+pnfs_backup_base+'/'+name)
    os.system('gfal-rm '+pnfs_base+'/'+name)

    #Move to pnfs once it is merged locally
    os.system('gfal-copy file://'+path+'/'+name+' '+pnfs_base+'/'+name)
    # os.system('rm '+path+'/'+name)