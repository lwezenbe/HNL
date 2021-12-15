from HNL.Samples.sample import createSampleList
from HNL.Samples.sampleManager import SampleManager
from HNL.Tools.helpers import makeDirIfNeeded
import glob
import os

list_of_samplelists = glob.glob(os.path.expandvars('$CMSSW_BASE/src/HNL/Samples/InputFiles/*UL*noskim*conf'))

for sl in list_of_samplelists:
    name = sl.split('/')[-1].split('.')[0]
    print 'Checking '+name
    out_name = os.path.expandvars('$CMSSW_BASE/src/HNL/Samples/InputFiles/InputFileTests/'+name+'.txt')
    makeDirIfNeeded(out_name)
    out_file = open(out_name, 'w')
    
    sample_list = createSampleList(sl)
    for sample in sample_list:
        try:
            chain = sample.initTree(needhcount = False)
        except:
            out_file.write('Problem in '+sample.name + '\n')
    
    out_file.close()





# #
# # to test single RecoGeneral file, for now comment when not used
# #
# years = ['2016pre', '2016post', '2017', '2018']
# eras = ['UL']
# skims = ['noskim', 'Reco', 'RecoGeneral']
# settings = {'skim_selection' : 'default', 'region' : 'highMassSR'}
# for year in years:
#     for era in eras:
#         for skim in skims:
#             out_name = os.path.expandvars('$CMSSW_BASE/src/HNL/Samples/InputFiles/InputFileTests/'+era+year+skim+'.txt')
#             makeDirIfNeeded(out_name)
#             out_file = open(out_name, 'w')
#             sample_manager = SampleManager(era, year, skim, 'Skimmer/skimlist_'+era+year, skim_selection = 'default', region = 'highMassSR')
#             sample_list = sample_manager.createSampleList()
#             for sample in sample_list:
#                 try:
#                     chain = sample.initTree(needhcount = False)
#                 except:
#                     out_file.write('Problem in '+sample.name + '\n')

#             out_file.close()

