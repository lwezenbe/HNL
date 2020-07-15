import os
import glob

#Merges subfiles if needed
merge_files = glob.glob('/storage_mnt/storage/user/lwezenbe/public/ntuples/HNL/OldAnalysis/*/*/tmp*')
# merge_files = glob.glob('/storage_mnt/storage/user/lwezenbe/public/ntuples/HNL/*/*/tmp*')
for mf in merge_files:
    path, name = mf.rsplit('/', 1)
    print path+'/'+name.split('_', 1)[1]+'.root'
    os.system('hadd -f '+path+'/'+name.split('_', 1)[1]+'.root '+mf+'/*root')
    os.system('rm -r '+ mf)
