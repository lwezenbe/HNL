import glob, os
all_wrong_files = glob.glob('data/dataCards/UL201*/default-lowMassSRloose/*/HNL-*-m*/shapes/*test.txt')
for f in all_wrong_files:
    file_path, file_name = f.rsplit('/', 1)
    fixed_file_name = file_name.split('test')[0]+file_name.split('test')[1]
    os.system('mv '+file_path+'/'+file_name+' '+file_path+'/'+fixed_file_name)
