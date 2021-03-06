
#
# General tool to merge files from a certain subjob
# Use convention in naming subjobs foo/1_2_3.root
# where 1 is the sample name, 2 is a group identifier like a category and 3 is the number of the subJob
#
import os
from HNL.Tools.helpers import getSubDir
import glob

def getListOfGroupID(path):
    list_of_files = glob.glob(path+'/*root')
    list_of_id = {f.rsplit('/')[-1].split('_')[1] for f in list_of_files if f.rsplit('/')[-1].split('_')[2]}
    return list_of_id

def checkForMerge(paths):
    
    # for i, p in enumerate(paths):
    #     if not 'tmp' in p:      paths[i] = None
    # return [p for p in paths if p is not None] 
    return [p for p in paths if 'tmp' in p]

#
#   Function to do the actual merging
#   Input path = path up to but not including the tmp folders
#
def merge_single_path(path):
    
    merge_paths = getSubDir(path)
    merge_paths = checkForMerge(merge_paths)

    if not merge_paths:
        return

    for p in merge_paths:
        print p, getListOfGroupID(p)
        for group_id in getListOfGroupID(p):
            os.system('hadd  -f '+ p.rsplit('/', 1)[0]+ '/'+group_id+'.root '+p+'/*_'+group_id+'_*root')
        os.system('rm -r '+p)

from HNL.Tools.jobSubmitter import checkCompletedJobs, submitJobs, cleanJobFiles
#For now also have argparser in there just to be able to automatically resubmit
def merge(paths, script, subjob_list, subjobargs, argparser = None, istest=False):
    
    if not istest:
        if argparser is None:
            pass
        else:
            failed_jobs = checkCompletedJobs(script, subjob_list, argparser)
            if failed_jobs is not None and len(failed_jobs) != 0:   
                should_resubmit = raw_input("Would you like to resubmit the failed jobs? (y/n) \n")
                if should_resubmit == 'y' or should_resubmit == 'Y':
                    print 'resubmitting:'
                    submitJobs(script, subjobargs, failed_jobs, argparser, resubmission=True)
                else:
                    pass    
                exit(0)

        cleanJobFiles(argparser, script)

    for f in paths:
        if '.txt' in f or '.root' in f: continue
        merge_single_path(f)


