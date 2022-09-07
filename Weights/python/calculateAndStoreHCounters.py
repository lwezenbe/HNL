import ROOT
from HNL.Samples.sampleManager import SampleManager
from HNL.Weights.lumiweight import LumiWeight

#
# Argument parser and logging
#
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
submission_parser = argParser.add_argument_group('submission', 'Arguments for submission. Any arguments not in this group will not be regarded for submission.')
submission_parser.add_argument('--isChild',  action='store_true',       default=False,  help='mark as subjob, will never submit subjobs by itself')
submission_parser.add_argument('--year',     action='store', nargs='*',       default=None,   help='Select year')
submission_parser.add_argument('--era',     action='store',       default='prelegacy', choices = ['UL', 'prelegacy'],   help='Select era')
submission_parser.add_argument('--sample',   action='store',            default=None,   help='Select sample by entering the name as defined in the conf file')
submission_parser.add_argument('--subJob',   action='store',            default=None,   help='The number of the subjob for this sample')
submission_parser.add_argument('--batchSystem', action='store',         default='HTCondor',  help='choose batchsystem', choices=['local', 'HTCondor', 'Cream02', 'None'])
submission_parser.add_argument('--dryRun',   action='store_true',       default=False,  help='do not launch subjobs, only show them')
submission_parser.add_argument('--isTest',   action='store_true',       default=False,  help='Run a small test')

argParser.add_argument('--merge', action='store_true', default=False)
args = argParser.parse_args()

if args.isTest:
    if args.year is None: args.year = ['2017']
    if args.era is None: args.era = 'UL'
    if args.sample is None: args.sample = 'DYJetsToLL-M-10to50'
    args.isChild = True

def getSampleManager(y):
    sm = SampleManager(args.era, y, 'noskim', 'Skimmer/skimlist_'+args.era+y, skim_selection=None, region=None)
    return sm

#
# Prepare jobs
#
jobs = {}
for year in args.year:
    jobs[year] = []
    sample_manager = getSampleManager(year)
    for sample_name in sample_manager.sample_names:
        if args.sample is not None and sample_name != args.sample: continue
        for njob in xrange(1): 
            jobs[year] += [(sample_name, str(njob))]

#
# Submit subjobs
#
if not args.isChild and not args.merge and args.batchSystem != 'None': 
    from HNL.Tools.jobSubmitter import submitJobs, checkShouldMerge
    # if not args.dryRun and checkShouldMerge(__file__, argParser):
    #     raise RuntimeError("Already existing files available. You would be overwriting")
    for year in jobs.keys():
        submitJobs(__file__, ('sample', 'subJob'), jobs[year], argParser, jobLabel = 'calculateHcounters', additionalArgs= [('year', year)])
    exit(0)


import os
year = args.year[0]
import json
if not args.merge:
    if args.sample is not None:
        output_file = os.path.expandvars(os.path.join('$CMSSW_BASE', 'src', 'HNL', 'Weights', 'data', 'hcounters', args.era+year, 'tmp_'+args.era+year, 'hcounter-'+args.sample+'.json'))
    else:
        output_file = os.path.expandvars(os.path.join('$CMSSW_BASE', 'src', 'HNL', 'Weights', 'data', 'hcounters', args.era+year, 'tmp_'+args.era+year, 'hcounter.json'))
    from HNL.Tools.helpers import makeDirIfNeeded
    makeDirIfNeeded(output_file)
    
    sample_manager = getSampleManager(year)
    hcounter = {}
    for sample_name in sample_manager.sample_names:
        if args.sample is not None and sample.name != args.sample: continue
        print sample_name
        sample = sample_manager.getSample(sample_name)
        if sample.is_data: continue
        chain = sample.initTree()
    
        lw = LumiWeight(sample, sample_manager, recalculate=True)
        hcounter[sample.name] = lw.total_hcount
    

else:
    import glob
    base_path = os.path.expandvars(os.path.join('$CMSSW_BASE', 'src', 'HNL', 'Weights', 'data', 'hcounters', args.era+year))
    all_files = glob.glob(base_path+'/tmp_'+args.era+year+'/*.json')
    if os.path.isfile(base_path+'/hcounter.json'):
        f = open(base_path+'/hcounter.json',)
        hcounter = json.load(f)
        f.close()
    else:
        hcounter = {}
    for in_path in all_files:
        f = open(in_path,)
        weights = json.load(f)
        for w in weights:
            hcounter[w] = weights[w]
        f.close()
    os.system('rm -r '+base_path+'/tmp_'+args.era+year)
    
    output_file = os.path.expandvars(os.path.join('$CMSSW_BASE', 'src', 'HNL', 'Weights', 'data', 'hcounters', args.era+year, 'hcounter.json'))
    
json_f = json.dumps(hcounter)
out_file = open(output_file, 'w')
out_file.write(json_f)
out_file.close()
