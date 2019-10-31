
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
    
    for p in paths:
        if not 'tmp' in p:      paths.pop(p)
    return paths 

def merge(path):
    
    merge_paths = getSubDir(path)
    merge_paths = checkForMerge(merge_paths)
    if not merge_paths:
        print "Nothing to merge"
        return

    for p in merge_paths:
        print p, getListOfGroupID(p)
        for id in getListOfGroupID(p):
            os.system('hadd -f '+ p.rsplit('/', 1)[0]+ '/'+id+'.root '+p+'/*'+id+'*root')
            os.system('rm -r '+p)
    
