import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
submission_parser = argParser.add_argument_group('submission', 'Arguments for submission. Any arguments not in this group will not be regarded for submission.')
submission_parser.add_argument('--year',     action='store', nargs='*',       default=None,   help='Select year')
submission_parser.add_argument('--era',     action='store',       default='prelegacy', choices = ['UL', 'prelegacy'],   help='Select era')
submission_parser.add_argument('--batchSystem', action='store',         default='HTCondor',  help='choose batchsystem', choices=['local', 'HTCondor', 'Cream02'])
submission_parser.add_argument('--dryRun',   action='store_true',       default=False,  help='do not launch subjobs, only show them')
submission_parser.add_argument('--selection',   action='store', default='default',  help='Select the type of selection for objects', choices=['leptonMVAtop', 'AN2017014', 'default', 'tZq', 'TTT', ])
submission_parser.add_argument('--sample',   action='store',            default=None,   help='Select sample by entering the name as defined in the conf file')
submission_parser.add_argument('--subJob',   action='store',            default=None,   help='The number of the subjob for this sample')
submission_parser.add_argument('--isChild',  action='store_true',       default=False,  help='mark as subjob, will never submit subjobs by itself')
argParser.add_argument('--checkLog',  action='store_true',       default=False,  help='mark as subjob, will never submit subjobs by itself')

args = argParser.parse_args()

from HNL.Samples.sampleManager import SampleManager
#
# Prepare jobs
#
jobs = {}
for year in args.year:
    jobs[year] = []
    sample_manager = SampleManager(args.era, year, 'Reco', 'Testing/fulllist_'+args.era+year, skim_selection=args.selection, region=None)

    for sample_name in sample_manager.sample_names:
        sample = sample_manager.getSample(sample_name)
        for njob in xrange(sample.returnSplitJobs()): 
            jobs[year] += [(sample.name, str(njob), None)]

#
# Submit subjobs
#
if not args.isChild and not args.checkLog:
    from HNL.Tools.jobSubmitter import submitJobs, checkShouldMerge
    # if not args.dryRun and checkShouldMerge(__file__, argParser):
    #     raise RuntimeError("Already existing files available. You would be overwriting")
    for year in jobs.keys():
        submitJobs(__file__, ('sample', 'subJob'), jobs[year], argParser, jobLabel = 'scanForFileCorruption-'+str(year), additionalArgs= [('year', year)])
    exit(0)


if not args.checkLog:
    year = args.year[0]
    
    from HNL.Tools.logger import getLogger, closeLogger
    from HNL.Tools.helpers import progress
    log = getLogger('INFO')
    
    sample_manager = SampleManager(args.era, year, 'Reco', 'fulllist_'+args.era+year, skim_selection=args.selection, region=None)
    sample = sample_manager.getSample(args.sample)
    chain = sample.initTree(needhcount = False)
    #
    # Loop over all events
    #
    
    event_range = sample.getEventRange(args.subJob)
    for entry in event_range:
    
        chain.GetEntry(entry)
        progress(entry - event_range[0], len(event_range))
    
    closeLogger(log)

else:
    from HNL.Tools.jobSubmitter import checkCompletedJobs
    for y in args.year:
        print '\n \n YEAR', y, '\n \n '
        checkCompletedJobs(__file__, jobs[y], argParser, additionalArgs= [('year', year)], level=1)
