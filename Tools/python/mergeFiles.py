
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
    list_of_id = []
    for f in list_of_files:
        tmp_entry = f.rsplit('/')[-1].split('_')[:2]
        if tmp_entry not in list_of_id and f.rsplit('/')[-1].split('_')[2]:
            list_of_id.append([x for x in tmp_entry])
    return list_of_id

def checkForMerge(paths):
    merge_paths = [p for p in paths if 'tmp' in p]
    if len(merge_paths) > 0:
        return [p for p in paths if 'tmp' in p]
    else:
        return None


#
#   Function to do the actual merging
#   Input path = path up to but not including the tmp folders
#
def mergeSinglePath(path, groups_to_merge=None):
    
    merge_paths = getSubDir(path)
    merge_paths = checkForMerge(merge_paths)

    if merge_paths is None:
        return

    for p in merge_paths:
        for group_id in getListOfGroupID(p):
            gname, gid = group_id
            if groups_to_merge is not None and group_id not in groups_to_merge: continue
            os.system('hadd  -f '+ p.rsplit('/', 1)[0]+ '/'+gid+'-'+gname+'.root '+p+'/'+gname+'_'+gid+'_*root')
        print {t[1] for t in getListOfGroupID(p)}
        for x in {t[1] for t in getListOfGroupID(p)}:
            print x
            os.system('hadd  -f '+ p.rsplit('/', 1)[0]+ '/'+x+'.root '+p.rsplit('/', 1)[0]+'/'+x+'-*root')
            os.system('rm -r '+p+'/*_'+gid+'_*root')
        if len(os.listdir(p)) == 0:
            os.system('rm -r '+p)

#
def moveToBackup(path):
    backup_path = os.path.expandvars('/pnfs/iihe/cms/store/user/$USER/HNL/')
    try:
        backup_path += path.split('src/HNL/')[1]
    except:
        backup_path += path.split('ntuples/HNL/')[1]
    from HNL.Tools.helpers import makeDirIfNeeded
    makeDirIfNeeded(backup_path+'/x')
    #Move
    all_files = [x for x in glob.glob(path+'/*') if '.txt' in x or '.root' in x]
    for f in all_files:
        os.system('mv -f '+f+ ' '+backup_path+'/'+f.split('/')[-1])

from HNL.Tools.jobSubmitter import checkCompletedJobs, submitJobs, cleanJobFiles, checkShouldMerge, disableShouldMerge
#For now also have argparser in there just to be able to automatically resubmit
def merge(paths, script, subjob_list, subjobargs, argparser = None, istest=False, groups_to_merge=None, additionalArgs=None, man_changed_args = None, full_path = None):

    try:
        if not istest and not checkShouldMerge(script, argparser, additionalArgs=additionalArgs, man_changed_args = man_changed_args, full_path = full_path):
            print "Nothing to merge"
            return
    except:
        should_abort = raw_input("The log files you are asking for do not exist. Would you like to skip merging? (y/n) \n")
        if should_abort in ['y', 'Y']: return

    if not istest:
        if argparser is None:
            pass
        else:
            failed_jobs = checkCompletedJobs(script, subjob_list, argparser, additionalArgs=additionalArgs)
            if failed_jobs is not None and len(failed_jobs) != 0:   
                should_resubmit = raw_input("Would you like to resubmit the failed jobs? (y/n) \n")
                if should_resubmit == 'y' or should_resubmit == 'Y':
                    print 'resubmitting:'
                    submitJobs(script, subjobargs, failed_jobs, argparser, resubmission=True, jobLabel = "-".join([script.split('.')[0], 'resubmission']), man_changed_args = man_changed_args)
                else:
                    pass    
                if should_resubmit != 'skip': exit(0)

        cleanJobFiles(argparser, script)

    # First clean up the directory
    for f in paths:
        if '.txt' in f or '.root' in f: continue
    #    moveToBackup(f)
        mergeSinglePath(f, groups_to_merge=groups_to_merge)

    if not istest: disableShouldMerge(script, argparser, additionalArgs=additionalArgs)
