#
#       Code to run timing tests for different samples
#       Some samples' subjobs tale significantly longer and here you can get a grasp of that before finding out the hard way that one job is taking 8 hours
#

import os
import time
import datetime
base_path = os.path.join(os.path.expandvars('$CMSSW_BASE'), 'src', 'HNL')

#
# This part requires manual input for the moment
#
code_to_test = os.path.join(base_path, 'Analysis', 'plotVariables.py --isTest --year 2016 --selection AN2017014 --region WZCR --includeData')
sublist = 'test'
year = '2016'
skim = 'Old'

from HNL.Samples.sampleManager import SampleManager
sample_manager = SampleManager(year, skim, sublist)
# sample_manager = SampleManager(year, skim, sublist+'_'+year)

out_file = open('data/timeMeasurements.txt', 'w')
out_file.write('SAMPLE \t \t #subjobs \t #events in subjob 0 \t tot events \t time for 500 events \t extrapolated time \n' )
for sample in sample_manager.sample_list:
    if sample.name not in sample_manager.sample_names: continue
    chain = sample.initTree(needhcount=False)


    print '\x1b[6;30;42m' + 'ANALYZING '+ sample.name + ' \x1b[0m'
    print '\x1b[6;30;42m' + 'Number of subjobs: '+ str(sample.split_jobs) + ' \x1b[0m'
    print '\x1b[6;30;42m' + 'Number of events in first subjob: '+ str(len(sample.getEventRange(0))) + ' \x1b[0m'
    start_time = time.time()
    os.system('python '+code_to_test+' --sample '+sample.name)
    passed_time = time.time()-start_time
    n_events = chain.GetEntries()

    extrapolated_time = passed_time * n_events/(sample.split_jobs*500)
    out_file.write(' \t '.join([sample.name+' \t', str(sample.split_jobs), str(len(sample.getEventRange(0))), str(n_events), str(passed_time)+'s', str(datetime.timedelta(seconds=extrapolated_time))]))
    out_file.write('\n')
    print datetime.timedelta(seconds=extrapolated_time)
out_file.close()

