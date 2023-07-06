input_path = "/pnfs/iihe/cms/store/user/lwezenbe/heavyNeutrino/ZZ_TuneCP5_13TeV-pythia8/crab_RunIISummer20UL16MiniAOD-106X_mcRun2_asymptotic_v13-v2_singlelepton_MC_2016_ULpostVFPv4/211120_223016/0000"

import glob
from HNL.Tools.helpers import getObjFromFile
all_paths = glob.glob(input_path+"/single*root")
total_hcount = 0.
for path in all_paths:
    
    hcounter = getObjFromFile(path, 'blackJackAndHookers/hCounter')
    print path.rsplit('/', 1)[-1], hcounter.GetSumOfWeights()
    total_hcount += hcounter.GetSumOfWeights()

print 'total', total_hcount
