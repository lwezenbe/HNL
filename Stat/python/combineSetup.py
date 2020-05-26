#
# Basic setup script to set Combine up 
#

from HNL.Stat.combineTools import release, arch, version
import os
import socket

# # Try the arch
# try:
#     os.system('export SCRAM_ARCH='+arch)
#     print 'export SCRAM_ARCH='+arch
# except:
#     print 'The system you are on does not support slc7. Combine will not be installed.'

current_CMSSWBASE = os.path.expandvars('$CMSSW_BASE')
combine_CMSSWBASE = os.path.abspath(os.path.join(current_CMSSWBASE, '..', release))

print arch, current_CMSSWBASE
os.system('export SCRAM_ARCH='+arch)
os.chdir(os.path.dirname(combine_CMSSWBASE))
if not os.path.exists(combine_CMSSWBASE):
    os.system('source $VO_CMS_SW_DIR/cmsset_default.sh;' if 'lxp' not in socket.gethostname() else '')
    os.system('scramv1 project CMSSW ' + release)
    os.chdir(combine_CMSSWBASE + '/src')
    os.system('eval `scramv1 runtime -sh`')
    os.system('git clone https://github.com/cms-analysis/HiggsAnalysis-CombinedLimit.git HiggsAnalysis/CombinedLimit')
    os.chdir('HiggsAnalysis/CombinedLimit')
    os.system('git fetch origin;git checkout ' + version)
    os.system('scramv1 b clean;scramv1 b -j 8')
    os.system('curl -s "https://raw.githubusercontent.com/cms-analysis/CombineHarvester/master/CombineTools/scripts/sparse-checkout-ssh.sh" | bash')
    os.system('scramv1 b -j 8')


