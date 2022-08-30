import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
submission_parser = argParser.add_argument_group('submission', 'Arguments for submission. Any arguments not in this group will not be regarded for submission.')
submission_parser.add_argument('--years',     action='store', nargs='*',       default=None,   help='Select year')
submission_parser.add_argument('--era',     action='store',       default='UL', choices = ['UL', 'prelegacy'],   help='Select era')
submission_parser.add_argument('--selection',   action='store', default='default',  help='Select the type of selection for objects', choices=['leptonMVAtop', 'AN2017014', 'default', 'tZq', 'TTT', ])
submission_parser.add_argument('--strategy',   action='store', default='MVA',  help='Select the strategy to use to separate signal from background', choices=['cutbased', 'MVA'])
submission_parser.add_argument('--analysis',   action='store', default='HNL',  help='Select the strategy to use to separate signal from background', choices=['HNL', 'AN2017014', 'ewkino', 'tZq'])
submission_parser.add_argument('--region', action='store', default='baseline', type=str,  help='What region do you want to select for?')
args = argParser.parse_args()

import os
def getOutputName(y):
        return os.path.join(os.path.expandvars('$CMSSW_BASE'), 'src', 'HNL', 'Analysis', 'data', 'runAnalysis', args.analysis+'-TauFakePurity', '-'.join([args.strategy, args.selection, args.region, 'reco']), args.era+'-'+y, 'bkgr')




list_of_numbers = {'total' : {}}


sample_groups = {
    'DYJetsToLL-M-10to50' : 'DY',
    'DYJetsToLL-M-50' : 'DY',

    'GluGluHToTauTau' : 'ZZ',
    'GluGluHToWWTo2L2Nu' : 'ZZ',
    'GluGluHToZZTo4L' : 'ZZ',
    'GluGluHToZZTo2L2Q' : 'ZZ',
    'GluGluToContinToZZTo2e2mu': 'ZZ',
    'GluGluToContinToZZTo2e2nu': 'ZZ',
    'GluGluToContinToZZTo2e2tau': 'ZZ',
    'GluGluToContinToZZTo2mu2nu' : 'ZZ',
    'GluGluToContinToZZTo2mu2tau' : 'ZZ',
    'GluGluToContinToZZTo4e': 'ZZ',
    'GluGluToContinToZZTo4mu': 'ZZ',
    'GluGluToContinToZZTo4tau' : 'ZZ',
    
    'ST-s-channel' : 'ST',
    'ST-t-channel-antitop' : 'ST',
    'ST-t-channel-top' : 'ST',
    'ST-tW-antitop-5f' : 'ST',
    'ST-tW-top-5f' : 'ST',
    'ST-tW-antitop-5f-nofullhadr' : 'ST',
    'ST-tW-top-5f-nofullhadr' : 'ST',

    'THQ' : 't(t)X',
    'tZq' : 't(t)X',
    'TTGJets'            : 't(t)X',
    'TTGamma-Dilep'      : 't(t)X',
    'TTGamma-SingleLep'  : 't(t)X',
    'TTGamma-Hadronic'   : 't(t)X',
    'TTHH'               : 't(t)X',
    'TTTT'               : 't(t)X',
    'TTTW'               : 't(t)X',
    'TTWH'               : 't(t)X',
    'TTWW'               : 't(t)X',
    'TTWZ'               : 't(t)X',
    'TTZH'               : 't(t)X',
    'TTZZ'               : 't(t)X',
    'ttZtoQQ'            : 't(t)X',
    'ttZtoLL-m-10'       : 't(t)X',
    'ttWToLNu'           : 't(t)X',
    'ttWtoQQ'            : 't(t)X',
    'ttHToNonbb'         : 't(t)X',
    'ttHTobb'            : 't(t)X',  
    'TTJets-Incl'    : 't(t)X',
    'TTJets-Dilep'   : 't(t)X',
    'TTJets-SemiLep' : 't(t)X',
    'TTJets-Had'     : 't(t)X',
    
    'VBFHToTauTau'  : 'ZZ',
    'VBFHToWW'      : 'ZZ',
    'VBFHToZZTo4L'  : 'ZZ',
    'VHToNonbb'     : 'ZZ',
    'ZZTo2L2Nu'         : 'ZZ',
    'ZZTo4L'    : 'ZZ',
    'ZZ'        : 'ZZ',
    
    'WG'    :   'W#gamma',
    'ZG'    :   'Z#gamma',
    
    'WJets' :   'W+jets',
    'WZTo3LNu'    : 'WZ',
    
    'WW': 'WW',
    'WWTo2L2Nu' : 'WW',
    
    'WWW' : 'Triboson',
    'WWZ' : 'Triboson',
    'WZG' : 'Triboson',
    'WZZ' :  'Triboson',
    'ZZZ' : 'Triboson'
}

import HNL.EventSelection.eventCategorization as cat
import numpy as np
def addContribution(list_of_yields, in_name, year):
    from HNL.Tools.outputTree import OutputTree
    intree = OutputTree('events_nominal', getOutputName(year)+'/'+sample_manager.output_dict[in_name]+'/variables-'+in_name+'.root')
    condition_to_use = '('+'||'.join(['category=={0}'.format(x) for x in cat.SUPER_CATEGORIES['TauFinalStates']])+')'
    #tmp_hist = intree.getHistFromTree('searchregion', 'searchregion-{0}-{1}'.format(in_name, year), np.arange(0., 2., 1.), condition = '('+condition_to_use+'&&!isprompt)', weight = 'lumiweight')
    tmp_hist = intree.getHistFromTree('searchregion', 'searchregion-{0}-{1}'.format(in_name, year), np.arange(0., 2., 1.), condition = '('+condition_to_use+'&&!isprompt)')
    #tmp_hist = intree.getHistFromTree('searchregion', 'searchregion-{0}-{1}'.format(in_name, year), np.arange(0., 2., 1.), condition = '('+condition_to_use+'&&istight)')
    number_of_events = tmp_hist.GetSumOfWeights()
    print in_name, '\t\t\t', number_of_events, tmp_hist.GetEntries()
    try:
        sample_group = sample_groups[in_name] 
    except:
        if not 'QCD' in in_name: print in_name, 'group not found for', year
        sample_group = 'Other'
    
    if sample_group not in list_of_yields[year].keys():
        list_of_yields[year][sample_group] = 0.
    if sample_group not in list_of_yields['total'].keys():
        list_of_yields['total'][sample_group] = 0.
    list_of_yields[year][sample_group] += number_of_events 
    list_of_yields['total'][sample_group] += number_of_events 
    return list_of_yields 

from HNL.Samples.sampleManager import SampleManager
for year in args.years:
    print 'loading', year
    list_of_numbers[year] = {}
    sample_manager = SampleManager(args.era, year, 'Reco', 'fulllist_{0}{1}'.format(args.era, year), skim_selection=args.selection, region=args.region)
    for sample in sample_manager.sample_names:
        if 'HNL' in sample: continue
        if 'Data' in sample: continue
        if 'QCD' in sample: continue   
        if args.region != 'TauFakesTT' and 'ZG' in sample: continue
        list_of_numbers = addContribution(list_of_numbers, sample, year)
    

    
#Make table
out_file = open("purity-{0}.txt".format(args.region), 'w')
samples_to_use = list_of_numbers['total'].keys()

list_of_numbers['total']['total'] = 0.
for s in samples_to_use:
    list_of_numbers['total']['total'] += list_of_numbers['total'][s]

out_file.write('\t \t \t'+'\t'.join(samples_to_use)+'\n')
for year in args.years+['total']:
    out_file.write(year + '\t' +'\t'.join(['%s'%float('%.1f' % list_of_numbers[year][sample]) for sample in samples_to_use])+'\n')

out_file.write('\n\n\n')
for year in args.years+['total']:
    out_file.write(year + '\t' +'\t'.join(['%s'%float('%.1f' % ((list_of_numbers[year][sample]/list_of_numbers['total']['total'])*100.)) for sample in samples_to_use])+'\n')

out_file.write('\n\n\n')
for year in args.years+['total']:
    out_file.write(year + '\t' +' & '.join(['%s'%float('%.1f' % list_of_numbers[year][sample]) for sample in samples_to_use])+'\n')

out_file.write('\n\n\n')
for year in args.years+['total']:
    out_file.write(year + '\t' +' & '.join(['%s'%float('%.1f' % ((list_of_numbers[year][sample]/list_of_numbers['total']['total'])*100.)) for sample in samples_to_use])+'\n')
out_file.close()

