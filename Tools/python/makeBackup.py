from HNL.Tools.helpers import makeDirIfNeeded, makePathTimeStamped
import os

skipDirs  = ['documents', 'log', '.git', 'virenv', 'utils']
skipFiles = []
extensions_to_copy = ['root', 'pdf', 'png']

file_paths = []
base_path = os.path.join(os.path.expandvars('$CMSSW_BASE'), 'src', 'HNL')
for root, dirs, files in os.walk(base_path, topdown=True):
    dirs[:]  = [d for d in dirs  if d not in skipDirs]
    root_files = [os.path.join(root, f) for f in files if f.split('.')[-1] in extensions_to_copy and f not in skipFiles]
    if len(root_files) != 0:
        for ext in extensions_to_copy:
            file_paths.append(os.path.join(root, '*.'+ext))

cmssw_version = os.path.expandvars('$CMSSW_BASE').rsplit('/', 1)[-1]
central_destination =  makePathTimeStamped('/user/lwezenbe/private/Backup/'+cmssw_version+'/AllOutput')
for rf in file_paths:
    try:
        index_for_backup = rf.split('/').index('src')
    except:
        index_for_backup = None

    backup_path = '/'.join([central_destination]+rf.split('/')[index_for_backup+1:-1])
    makeDirIfNeeded(backup_path+'/x')
    os.system('scp '+rf+' '+backup_path+'/.')