years = ['2018']
regions = {
        'lowMassSRloose' : 'MVA', 
        'highMassSR'    : 'MVA', 
        'WZCR'          : 'MVA', 
        'ZZCR'          : 'cutbased', 
        'ConversionCR'  : 'MVA'
    }

out = '{:50s} {:15s} {:15s}'
import os
from HNL.Samples.sampleManager import SampleManager
for year in years:
    output_dir = os.path.expandvars(os.path.join('$CMSSW_BASE', 'src', 'HNL', 'Test', 'data', 'statForPruning', year+'.txt'))
    from HNL.Tools.helpers import makeDirIfNeeded
    makeDirIfNeeded(output_dir)
    f = open(output_dir, 'w')
    sm = SampleManager('UL', year, 'Reco', 'fulllist_UL'+year, skim_selection = 'default')
    #sm = SampleManager('UL', year, 'noskim', 'fulllist_UL'+year, skim_selection = 'default')
    for output in [x for x in sm.sample_outputs if not ('HNL' in x or 'Data' in x)]:
        print 'Processing', output
        f.write(output+'\n')
        f.write('-'.join(['' for x in output])+'\n\n')
        f.write('Sample Name \t \t #jobs \t \t hcounter'+'\t \t'+'\t \t'.join(regions.keys())+'\n')

        sorted_sample_names = {}
        for sample_name in sm.getNamesForOutput(output):
            sample = sm.getSample(sample_name)
            sorted_sample_names[sample_name] = sample.returnSplitJobs()
            print sample_name, sorted_sample_names[sample_name]
    

        for sample_name in sorted(sorted_sample_names, key=sorted_sample_names.get):
            sample = sm.getSample(sample_name)
            hcounter = sample.getHist('hCounter')
            line = [out.format(sample_name, str(sample.returnSplitJobs()), str(round(hcounter.GetSumOfWeights()))+'/'+str(hcounter.GetEntries()))]
            for region in regions:
                run_analysis_inputdir = os.path.expandvars(os.path.join('$CMSSW_BASE', 'src', 'HNL', 'Analysis', 'data', 'runAnalysis', 'HNL', regions[region]+'-default-'+region+'-reco', 'UL-'+year, 'bkgr', output, 'variables-'+sample_name+'.root'))
                from HNL.Tools.outputTree import OutputTree
                intree = OutputTree('events_nominal', run_analysis_inputdir)
                import numpy as np
                inhist = intree.getHistFromTree('searchregion', 'test', np.arange(0., 2., 1.), 'category<33&&category>18&&isprompt')
                line.append(str(round(inhist.GetSumOfWeights()))+'/'+str(inhist.GetEntries()))
                del intree
                del inhist
            f.write('\t \t'.join(line)+'\n')
        f.write('\n')
            
    f.close()
