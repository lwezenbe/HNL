import os
import glob
import itertools


#Merges subfiles if needed
# merge_files = glob.glob('/storage_mnt/storage/user/lwezenbe/public/ntuples/HNL/Tycho/*/*/tmp*')
# merge_files = glob.glob('/storage_mnt/storage/user/lwezenbe/public/ntuples/HNL/2017/*/tmp*')
merge_files = glob.glob('/storage_mnt/storage/user/lwezenbe/public/ntuples/HNL/2018/*/tmp*/*')

keyfunc = lambda x:x[:3]
merge_files = sorted(merge_files, key=keyfunc)

split_list = []
tmp_list = []

for i, file_list in enumerate(merge_files):
    if i != 0 and (i % 20 == 0 or i == len(merge_files)-1):
        # print i, [x for x in tmp_list]

        split_list.append([x for x in tmp_list])
        tmp_list = []
    else:
        # print file_list, tmp_list
        tmp_list.append(file_list)
        # print 
            
# print split_list


for i, file_list in enumerate(split_list):
    # print i, file_list
    batches_index = -1
    for j, f in enumerate(file_list):
        if 'batches' in f:
            batches_index = j

    if batches_index != -1:
        file_list.pop(batches_index)

    path, name = file_list[0].rsplit('/', 1)
    file_names = ' '.join(file_list)
    # print 'hadd -f -v /storage_mnt/storage/user/lwezenbe/public/ntuples/HNL/2017/Reco/tmp_DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/batches/'+name.split('_', 1)[1].split('.root')[0]+'_'+str(i)+'.root '+file_names
    os.system('hadd -f -v /storage_mnt/storage/user/lwezenbe/public/ntuples/HNL/2018/Reco/tmp_DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/batches/'+name.split('_', 1)[1].split('.root')[0]+'_'+str(i)+'.root '+file_names)

# for mf in merge_files:
#     path, name = mf.rsplit('/', 1)
#     print path+'/'+name.split('_', 1)[1]+'.root'
#     os.system('hadd -f -v '+path+'/'+name.split('_', 1)[1]+'.root '+mf+'/*root')
# #    os.system('rm -r '+ mf)
