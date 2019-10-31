from HNL.Samples.sample import createSampleList
import ROOT

sampleList = createSampleList('/storage_mnt/storage/user/lwezenbe/private/PhD/CMSSW_10_2_17/src/HNL/Samples/InputFiles/signalCompression.conf')

import HNL.Tools.jobSubmitter as sub
for sample in sampleList:
    print sample.splitJobs
    for subJob in xrange(sample.splitJobs):
        log = 'log/'+sample.name+'_'+str(subJob)+'.txt'
        command = 'python /storage_mnt/storage/user/lwezenbe/private/PhD/CMSSW_10_2_17/src/HNL/Test/signalCompression.py --sampleName='+ sample.name +' --subJob='+str(subJob)
        sub.launchCream02(command, log, False)
