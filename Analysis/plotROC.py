#! /usr/bin/env python

#########################################################################
#                                                                       #
#   Code to plot basic variables and calculate yields                   # 
#                                                                       #                                   
#########################################################################

#
# Argument parser and logging
#
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
submission_parser = argParser.add_argument_group('submission', 'Arguments for submission. Any arguments not in this group will not be regarded for submission.')
submission_parser.add_argument('--isChild',  action='store_true',       default=False,  help='mark as subjob, will never submit subjobs by itself')
submission_parser.add_argument('--year',     action='store', nargs='*',       default=None,   help='Select year')
submission_parser.add_argument('--era',     action='store',       default='UL', choices = ['UL', 'prelegacy'],   help='Select era')
submission_parser.add_argument('--sample',   action='store',            default=None,   help='Select sample by entering the name as defined in the conf file')
submission_parser.add_argument('--subJob',   action='store',            default=None,   help='The number of the subjob for this sample')
submission_parser.add_argument('--isTest',   action='store_true',       default=False,  help='Run a small test')
submission_parser.add_argument('--batchSystem', action='store',         default='HTCondor',  help='choose batchsystem', choices=['local', 'HTCondor', 'Cream02'])
submission_parser.add_argument('--dryRun',   action='store_true',       default=False,  help='do not launch subjobs, only show them')
submission_parser.add_argument('--genLevel',   action='store_true',     default=False,  help='Use gen level variables')
submission_parser.add_argument('--selection',   action='store', default='default',  help='Select the type of selection for objects', choices=['leptonMVAtop', 'AN2017014', 'default', 'tZq', 'TTT', 'HNLtauTest', 'corrMet', 'prompt'])
submission_parser.add_argument('--strategy',   action='store', default='MVA',  help='Select the strategy to use to separate signal from background', choices=['cutbased', 'MVA'])
submission_parser.add_argument('--analysis',   action='store', default='HNL',  help='Select the strategy to use to separate signal from background', choices=['HNL', 'AN2017014', 'ewkino', 'tZq'])
submission_parser.add_argument('--region', action='store', default='baseline', type=str,  help='What region do you want to select for?')
submission_parser.add_argument('--includeData',   action='store', default=None, help='Also run over data', choices=['includeSideband', 'signalregion'])
submission_parser.add_argument('--logLevel',  action='store', default='INFO',  help='Log level for logging', nargs='?', choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE'])
submission_parser.add_argument('--skimLevel',  action='store', default='Reco',  choices=['noskim', 'Reco', 'RecoGeneral', 'auto'])
submission_parser.add_argument('--customList',  action='store',      default=None,               help='Name of a custom sample list. Otherwise it will use the appropriate noskim file.')
submission_parser.add_argument('--systematics',  action='store',      default='nominal',               help='Choose level of systematics.', choices = ['nominal', 'limited', 'full'])
submission_parser.add_argument('--tag',  action='store',      default=None,               help='Tag with additional information for the output, e.g. TauFakes, sidebandInMC')
submission_parser.add_argument('--bkgrOnly',   action='store_true',     default=False,  help='Run only the background')
submission_parser.add_argument('--blindStorage',   action='store_true',     default=False,  help='Do not store any signal region data')

argParser.add_argument('--masses', type=float, nargs='*',  help='Only run or plot signal samples with mass given in this list')
argParser.add_argument('--flavor', action='store', default='',  help='Which coupling should be active?' , choices=['tau', 'e', 'mu', '2l', ''])
argParser.add_argument('--signalOnly',   action='store_true',   default=False,  help='Run or plot a only the signal')
argParser.add_argument('--plotBkgrOnly',   action='store_true',     default=False,  help='Plot only the background')
argParser.add_argument('--categoriesToPlot',   action='store',     default='super',  help='What categories to use', choices=['original', 'analysis', 'super', 'splitanalysis', 'leadingflavor', 'trigger', 'sign'])
argParser.add_argument('--category',   action='store',     default=None,  help='What specific category to use')
argParser.add_argument('--searchregion',   action='store',  nargs='*',   default=None,  help='Is there a specific search region to probe?')
argParser.add_argument('--additionalCondition',   action='store',     default=None,  help='Additional condition for selection')
argParser.add_argument('--variables', nargs='*',  help='list of variables to process')
argParser.add_argument('--ignoreSystematics',   action='store_true',     default=False,  help='ignore systematics in plots')
argParser.add_argument('--combineYears',   action='store_true',     default=False,  help='combine all years specified in year arg in plots')
argParser.add_argument('--submitPlotting',   action='store_true',     default=False,  help='Send the plotting code to HTCondor')
argParser.add_argument('--ignoreSideband',   action='store_true',     default=False,  help='if there is a sideband nonprompt selection, please ignore it in the plotting')
argParser.add_argument('--paperPlots',   action='store',     default=None,  help='Slightly adapt the plots to be paper-approved')

args = argParser.parse_args()

print '\033[93m Warning: dr_closestJet contained a bug where it was always 0. In order to be consistent with the MVA training, it is now still manually set to 0 at all times. Please change this in the eventSelectionTools when retraining has occured.\033[0m'

from HNL.Tools.logger import getLogger, closeLogger
log = getLogger(args.logLevel)

if args.includeData is not None and args.region == 'NoSelection':
    raise RuntimeError('inData does not work with this selection region')

if args.strategy == 'MVA':
    if args.selection not in ['default', 'corrMet']:
        raise RuntimeError("No MVA available for this selection")
    if args.genLevel:
        raise RuntimeError("No MVA available for at genLevel")
    if args.region == 'ZZCR':
        raise RuntimeError("No MVA available for 4 lepton selection")

if args.genLevel and args.selection == 'AN2017014':
    raise RuntimeError('gen level is currently not implemented on AN2017014 analysis selection')

if args.genLevel and args.tag == 'TauFakes':
    raise RuntimeError('gen level can not be used for estimating TauFake fractions')

if args.combineYears:
    print '\033[93m Warning: Make sure you did a "mergeYears" first\033[0m'


#
# General imports
#
import os
from HNL.Tools.histogram import Histogram
from HNL.Tools.mergeFiles import merge
from HNL.Tools.helpers import getObjFromFile, progress, makeDirIfNeeded
from HNL.EventSelection.cutter import CutterCollection
from HNL.Weights.reweighter import Reweighter
from HNL.TMVA.reader import ReaderArray
from HNL.Samples.sampleManager import SampleManager
from HNL.Samples.sample import Sample
from HNL.EventSelection.event import Event
from HNL.Triggers.triggerSelection import passTriggers
from ROOT import TFile
import numpy as np

def customizeListToUse(y):
    custom_list_to_use = args.customList
    if args.customList is not None:
        for tmp_year in args.year:
            if tmp_year in custom_list_to_use:
                custom_list_to_use = custom_list_to_use.replace(tmp_year, str(y))
    return custom_list_to_use


def getSampleManager(y):
    if args.genLevel:
        skim_str = 'noskim'
#    elif args.includeData == 'includeSideband':
#        skim_str = 'Reco'
    else:
        skim_str = args.skimLevel
    
    #Translate the custom list to the correct year if needed
    custom_list_to_use = customizeListToUse(y)
    file_list = 'fulllist_'+args.era+str(y) if custom_list_to_use is None else custom_list_to_use

    sm = SampleManager(args.era, y, skim_str, file_list, skim_selection=args.selection, region=args.region)
    return sm

if args.isTest:
    if args.year is None: args.year = ['2017']
    args.isChild = True
    if args.subJob is None: args.subJob = '0'
    from HNL.Tools.helpers import generateArgString
    arg_string =  generateArgString(argParser)
else:
    arg_string = None

#
# Some constants to make referring to signal leptons more readable
#
l1 = 0
l2 = 1
l3 = 2
l4 = 3

nl = 3 if args.region != 'ZZCR' else 4

import HNL.EventSelection.eventCategorization as cat

#
# Define categories to use
#
def listOfCategories(region):
    if nl == 3:
        return cat.CATEGORIES
    else:
        return [max(cat.CATEGORIES)]

categories = listOfCategories(args.region) if args.category is None else [args.category]
reco_or_gen_str = 'reco' if not args.genLevel else 'gen'

import HNL.Analysis.analysisTypes as at
if args.region == 'NoSelection':
    var = at.var_noselection
elif args.strategy == 'MVA':
    var = at.returnVariables(nl, not args.genLevel, args.region)
else:
    var = at.returnVariables(nl, not args.genLevel)

#Loading something in for plot jobs
sorted_analysis_categories = cat.ANALYSIS_CATEGORIES.keys() if args.category is None else [args.category]
sorted_splitanalysis_categories = cat.ANALYSIS_SPLITOSSF_CATEGORIES.keys() if args.category is None else [args.category]
sorted_leadingflavor_categories = cat.LEADING_FLAVOR_CATEGORIES.keys() if args.category is None else [args.category]
sorted_sign_categories = cat.SIGN_CATEGORIES.keys() if args.category is None else [args.category]
sorted_trigger_categories = cat.TRIGGER_CATEGORIES.keys() if args.category is None else [args.category]
from HNL.Analysis.analysisTypes import getRelevantSuperCategories
sorted_super_categories = getRelevantSuperCategories(cat.SUPER_CATEGORIES.keys(), args.region) if args.category is None else [args.category]

#Reset list_of_hist
category_dict = {}
if args.categoriesToPlot == 'analysis':
    category_dict['analysis'] = (sorted_analysis_categories, ['('+'||'.join(['category=={0}'.format(x) for x in cat.ANALYSIS_CATEGORIES[y]])+')' for y in sorted_analysis_categories], {y :[str(x) for x in cat.ANALYSIS_CATEGORIES[y]] for y in sorted_analysis_categories})
if args.categoriesToPlot == 'splitanalysis':
    category_dict['splitanalysis'] = (sorted_splitanalysis_categories, ['('+'||'.join(['category=={0}'.format(x) for x in cat.ANALYSIS_SPLITOSSF_CATEGORIES[y]])+')' for y in sorted_splitanalysis_categories], {y :[str(x) for x in cat.ANALYSIS_SPLITOSSF_CATEGORIES[y]] for y in sorted_splitanalysis_categories})
if args.categoriesToPlot == 'leadingflavor':
    category_dict['leadingflavor'] = (sorted_leadingflavor_categories, ['('+'||'.join(['category=={0}'.format(x) for x in cat.LEADING_FLAVOR_CATEGORIES[y]])+')' for y in sorted_leadingflavor_categories], {y :[str(x) for x in cat.LEADING_FLAVOR_CATEGORIES[y]] for y in sorted_leadingflavor_categories})
if args.categoriesToPlot == 'sign':
    category_dict['sign'] = (sorted_sign_categories, ['('+'||'.join(['category=={0}'.format(x) for x in cat.SIGN_CATEGORIES[y]])+')' for y in sorted_sign_categories], {y :[str(x) for x in cat.SIGN_CATEGORIES[y]] for y in sorted_sign_categories})
if args.categoriesToPlot == 'super':
    category_dict['super'] = (sorted_super_categories, ['('+'||'.join(['category=={0}'.format(x) for x in cat.SUPER_CATEGORIES[y]])+')' for y in sorted_super_categories], {y:[str(x) for x in cat.SUPER_CATEGORIES[y]] for y in sorted_super_categories})
if args.categoriesToPlot == 'trigger':
    category_dict['trigger'] = (sorted_trigger_categories, ['('+'||'.join(['category=={0}'.format(x) for x in cat.TRIGGER_CATEGORIES[y]])+')' for y in sorted_trigger_categories], {y:[str(x) for x in cat.TRIGGER_CATEGORIES[y]] for y in sorted_trigger_categories})
category_dict['original'] = ([x for x in categories], ['(category=={0})'.format(x) for x in categories], {y : [str(y)] for y in categories})

#
# Prepare jobs
#
if args.submitPlotting and not args.isChild:

    if args.variables is None:
        subjob_var = var.keys()
    else:
        subjob_var = args.variables
    subjob_var.append('searchregion')
    n_var = 8
    subjob_var = [subjob_var[i:i+n_var] for i in range(0, len(subjob_var), n_var)]
    
    if args.category is None:
        subjob_cat = [x for x in category_dict[args.categoriesToPlot][0]]
    else:
        subjob_cat = [args.category] 
   
    jobs = [] 
    for c in subjob_cat:
        for v in subjob_var:
            jobs += [(c, v)]

#
# Submit subjobs
#

from HNL.Tools.jobSubmitter import submitJobs, checkShouldMerge
if args.submitPlotting and not args.isChild:
    args_of_interest = ['category', 'variables']
    submitJobs(__file__, args_of_interest, jobs, argParser, jobLabel='BDTROC-'+args.region, include_all_groups = True)
    exit(0)

from HNL.EventSelection.eventSelector import signal_regions

def getInputName(st, y, tag=None):
    translated_tag = '' if tag is None else '-'+tag
    if not args.isTest:
        return os.path.join(os.path.expandvars('$CMSSW_BASE'), 'src', 'HNL', 'Analysis', 'data', 'runAnalysis', args.analysis+translated_tag, '-'.join([args.strategy, args.selection, args.region, reco_or_gen_str]), args.era+'-'+y, st)
    else:
        return os.path.join(os.path.expandvars('$CMSSW_BASE'), 'src', 'HNL', 'Analysis', 'data', 'testArea', 'runAnalysis', args.analysis+translated_tag, '-'.join([args.strategy, args.selection, args.region, reco_or_gen_str]), args.era+'-'+y, st)

def getSystToRun(year, proc, split_corr = False):
    from HNL.Systematics.systematics import SystematicJSONreader
    sjr = SystematicJSONreader(datadriven_processes = ['non-prompt'] if args.includeData == 'includeSideband' else None)
    syst_to_run = ['nominal']
    if args.systematics == 'full' and not args.ignoreSystematics: syst_to_run += sjr.compileListOfGeneralSystematics('rerun', proc, year.split('-'), split_syst=True, split_corr=split_corr)
    return syst_to_run    


#
# Extra imports for dividing by region
#
from HNL.EventSelection.searchRegions import SearchRegionManager
srm = {}
srm[args.region] = SearchRegionManager(args.region)


################################
#                              # 
#       HELPER FUNCTIONS       #
#                              # 
################################ 

#
# Create variable distributions
#

def createSingleVariableDistributions(tree, vname, hname, bins, condition, proc, year, include_systematics = 'nominal', split_corr = False, additional_weight = None, ignore_sideband = False, decorrelate_sr = None):
    out_dict = {}

    weight = 'weight'
    if additional_weight is not None:
        weight += '*'+additional_weight
    out_dict['nominal'] = Histogram(tree.getHistFromTree(vname, hname, bins, condition, weight=weight))
    if include_systematics != 'nominal':
        from HNL.Systematics.systematics import returnWeightShapes
        out_dict.update(returnWeightShapes(tree, vname, hname, bins, condition, year, proc, ['non-prompt'] if not ignore_sideband else None, additional_weight=additional_weight, decorrelate_sr = decorrelate_sr))
    return out_dict 

def createVariableDistributions(categories_dict, var_dict, signal, background, data, sample_manager, year, additional_condition = None, include_systematics = 'nominal', sr = None, split_corr = False, for_datacards = False, ignore_sideband = False, custom_bins = None, decorrelate_sr = None):

    from HNL.Analysis.analysisTypes import getBinning
    bins = lambda c, v: getBinning(v, args.region, var_dict[v][1]) if custom_bins is None else custom_bins[c][v] 

    if additional_condition is None:
        additional_condition = ''
    else:
        additional_condition = '&&({0})'.format(additional_condition)
    
    #Add additional cuts
    if args.region == 'highMassSR':
        tmp_searchregion = srm[args.region].getGroupValues('F')
        searchregion_condition = '&&'.join(['searchregion != {0}'.format(x) for x in tmp_searchregion])
        inv_searchregion_condition = '||'.join(['searchregion == {0}'.format(x) for x in tmp_searchregion])
        category_condition = 'category!=27&&category!=28&&category!=29'
        inv_category_condition = 'category==27||category==28||category==29'
        final_condition = '((('+searchregion_condition+')||('+category_condition+'))||(('+inv_category_condition+')&&('+inv_category_condition+')&&(passedChargeConsistency&&abs(minMsssf-91)>15)))'
        additional_condition += '&&'+final_condition

    from HNL.Tools.outputTree import OutputTree
    def getTree(name, path):
        if not args.combineYears:
            return OutputTree(name, path+'/variables.root')
        elif args.region not in signal_regions:
            in_paths = [path+'/variables_{0}.root'.format(y) for y in args.year]
            return OutputTree(name, in_paths)
        else:
            return OutputTree(name, path+'/variables.root')

    from HNL.EventSelection.eventCategorization import isLightLeptonFinalState
    categories_to_use = categories_dict[0]
    category_conditions = categories_dict[1]
    print "Preparing the hist list"
    tmp_list_of_hist = {}
    for c in categories_to_use:
        tmp_list_of_hist[c] = {}
        for v in var_dict:
            tmp_list_of_hist[c][v] = {'signal':{}, 'bkgr':{}, 'data':{}}

    # Load in the signal histograms from the files
    print "Loading signal histograms"
    for isignal, s in enumerate(signal):
        progress(isignal, len(signal))
        sample_name = s.split('/')[-1]
        sample_mass = Sample.getSignalMass(sample_name)
        cleaned_sample_name = sample_name
        #if 'HNL-tau' in sample_name: cleaned_sample_name = 'HNL-tau-m{0}'.format(int(sample_mass))
        if '-tau' in sample_name: 
            cleaned_sample_name = sample_name.split('-', 1)[0] + '-tau-'+sample_name.split('-', 2)[-1]

        split_syst_to_run = getSystToRun(year, sample_name, split_corr=True) if include_systematics in ['full'] else ['nominal']           

        additional_condition_to_use = additional_condition
        for corr_syst in split_syst_to_run:
            intree = getTree('events_{0}'.format(corr_syst), s)
            for c, cc in zip(categories_to_use, category_conditions): 
                if 'taulep' in sample_name and not isLightLeptonFinalState(c): continue
                if 'tauhad' in sample_name and isLightLeptonFinalState(c): continue
                for v in var_dict.keys():
                    coupling_squared = signal_couplingsquared[args.flavor][sample_mass]
                    vsquared_translated = str(coupling_squared)
                    vsquared_translated = vsquared_translated.replace('e-', 'em')
                    new_name = cleaned_sample_name.split('-Vsq')[0]+'-Vsq'+vsquared_translated + '-' + Sample.getSignalDisplacedString(cleaned_sample_name)
                    additional_weight = str(coupling_squared/Sample.getSignalCouplingSquared(sample_name))

                    #tmp
                    #additional_weight += '*(isDiracType*1.2+!isDiracType*0.73)'
                    
                    if corr_syst == 'nominal':
                        tmp_list_of_hist[c][v]['signal'][new_name] = createSingleVariableDistributions(intree, v, str(c)+'-'+v+'-'+corr_syst+'-'+sample_name+'-'+str(sr)+'-'+str(year), bins(c, v), '('+cc+'&&!issideband)'+additional_condition_to_use, sample_name, year, include_systematics, split_corr = split_corr, additional_weight = additional_weight, ignore_sideband=ignore_sideband, decorrelate_sr = decorrelate_sr)
                    else:
                        tmp_list_of_hist[c][v]['signal'][new_name][corr_syst] = createSingleVariableDistributions(intree, v, str(c)+'-'+v+'-'+corr_syst+'-'+sample_name+'-'+str(sr)+'-'+str(year), bins(c, v), '('+cc+'&&!issideband)'+additional_condition_to_use, sample_name, year, split_corr = split_corr, additional_weight = additional_weight, ignore_sideband=ignore_sideband, decorrelate_sr = decorrelate_sr)['nominal'] 

    print '\n'

    if args.includeData is not None:
        print "Loading data"
        split_syst_to_run = getSystToRun(year, 'non-prompt', split_corr=True) if not ignore_sideband and include_systematics in ['full'] else ['nominal']           
        for isyst, corr_syst in enumerate(split_syst_to_run):
            progress(isyst, len(split_syst_to_run))
            intree = getTree('events_{0}'.format(corr_syst), data[0])
            for ic, (c, cc) in enumerate(zip(categories_to_use, category_conditions)):
                for v in var_dict:
                    proc_to_use = 'non-prompt' if not ignore_sideband else 'Data'
                    if corr_syst == 'nominal':
                        tmp_list_of_hist[c][v]['data']['sideband'] = createSingleVariableDistributions(intree, v, str(c)+'-'+v+'-'+corr_syst+'-Data-sideband'+'-'+str(sr)+'-'+str(year), bins(c, v), '('+cc+'&&issideband)'+additional_condition, proc_to_use, year, include_systematics, split_corr=split_corr, ignore_sideband=ignore_sideband, decorrelate_sr = decorrelate_sr)
                        tmp_list_of_hist[c][v]['data']['signalregion'] = {'nominal' : Histogram(intree.getHistFromTree(v, str(c)+'-'+v+'-'+'-nominal-Data-signalregion'+'-'+str(sr)+'-'+str(year), bins(c, v), '('+cc+'&&!issideband)'+additional_condition))}
                    else:
                        tmp_list_of_hist[c][v]['data']['sideband'][corr_syst] = createSingleVariableDistributions(intree, v, str(c)+'-'+v+'-'+corr_syst+'-Data-sideband'+'-'+str(sr)+'-'+str(year), bins(c, v), '('+cc+'&&issideband)'+additional_condition, proc_to_use, year, split_corr=split_corr, ignore_sideband=ignore_sideband, decorrelate_sr = decorrelate_sr)['nominal']


    #
    # Tmp SF for ZZ and ZG
    #
    def getPromptWeight(name):
        if name == 'ZZ-H':
            return '1.11'
        elif name == 'XG':
            return '1.12'
        else:
             return '1.'
    
    print "Loading background histograms"
    for ib, b in enumerate(background):
        for c, cc in zip(categories_to_use, category_conditions):
            for iv, v in enumerate(var_dict.keys()): 
                tmp_list_of_hist[c][v]['bkgr'][b] = {}

    for ib, b in enumerate(background):
        progress(ib, len(background))

        if b in ['non-prompt', 'charge-misid']: continue
        split_syst_to_run = getSystToRun(year, b, split_corr=True) if include_systematics in ['full'] else ['nominal']       
        for corr_syst in split_syst_to_run:
            intree = getTree('events_{0}'.format(corr_syst), getInputName('bkgr', year, args.tag)+'/'+b)                 
            for c, cc in zip(categories_to_use, category_conditions):
                for iv, v in enumerate(var_dict.keys()): 
                    if corr_syst == 'nominal':
                        tmp_list_of_hist[c][v]['bkgr'][b] = createSingleVariableDistributions(intree, v, 'tmp_'+b+v+str(c)+'p'+corr_syst+'-'+str(sr)+'-'+str(year), bins(c, v), '('+cc+'&&!isChargeFlipEvent&&isprompt&&!issideband)'+additional_condition, b, year, include_systematics, split_corr=split_corr, ignore_sideband=ignore_sideband, additional_weight = getPromptWeight(b), decorrelate_sr = decorrelate_sr)
                        #tmp_list_of_hist[c][v]['bkgr'][b] = createSingleVariableDistributions(intree, v, 'tmp_'+b+v+str(c)+'p'+corr_syst+'-'+str(sr)+'-'+str(year), bins(c, v), '('+cc+'&&!isChargeFlipEvent&&isprompt&&!issideband)'+additional_condition, b, year, include_systematics, split_corr=split_corr, ignore_sideband=ignore_sideband, decorrelate_sr = decorrelate_sr)
                    else:
                        tmp_list_of_hist[c][v]['bkgr'][b][corr_syst] = createSingleVariableDistributions(intree, v, 'tmp_'+b+v+str(c)+'p'+corr_syst+'-'+str(sr)+'-'+str(year), bins(c, v), '('+cc+'&&!isChargeFlipEvent&&isprompt&&!issideband)'+additional_condition, b, year, split_corr=split_corr, ignore_sideband=ignore_sideband, additional_weight = getPromptWeight(b), decorrelate_sr = decorrelate_sr)['nominal']
                    
                    #charge
                    if corr_syst == 'nominal': 
                        tmp_hist = createSingleVariableDistributions(intree, v, 'tmp_'+b+'-chargemisid'+v+str(c)+'p'+corr_syst+'-'+str(sr)+'-'+str(year), bins(c, v), '('+cc+'&&isChargeFlipEvent&&isprompt&&!issideband)'+additional_condition, b, year, include_systematics, split_corr=split_corr, ignore_sideband=ignore_sideband, decorrelate_sr = decorrelate_sr)
                    else:
                        tmp_hist = {corr_syst : createSingleVariableDistributions(intree, v, 'tmp_'+b+'-chargemisid'+v+str(c)+'p'+corr_syst+'-'+str(sr)+'-'+str(year), bins(c, v), '('+cc+'&&isChargeFlipEvent&&isprompt&&!issideband)'+additional_condition, b, year, split_corr=split_corr, ignore_sideband=ignore_sideband, decorrelate_sr = decorrelate_sr)['nominal']}
                        
                    if corr_syst not in tmp_list_of_hist[c][v]['bkgr']['charge-misid'].keys():
                        tmp_list_of_hist[c][v]['bkgr']['charge-misid'].update(tmp_hist)
                    else:
                        for sk in tmp_hist.keys():
                            tmp_list_of_hist[c][v]['bkgr']['charge-misid'][sk].add(tmp_hist[sk])
                    del(tmp_hist)
                    
                    if ignore_sideband:
                        if corr_syst == 'nominal': 
                            tmp_hist = createSingleVariableDistributions(intree, v, 'tmp_'+b+v+str(c)+'np'+corr_syst+'-'+str(sr)+'-'+str(year), bins(c, v), '('+cc+'&&!isprompt&&!issideband)'+additional_condition, 'non-prompt', year, include_systematics, ignore_sideband=ignore_sideband, decorrelate_sr = decorrelate_sr)
                        else:
                            tmp_hist = {corr_syst : createSingleVariableDistributions(intree, v, 'tmp_'+b+v+str(c)+'np'+corr_syst+'-'+str(sr)+'-'+str(year), bins(c, v), '('+cc+'&&!isprompt&&!issideband)'+additional_condition, b, year, ignore_sideband=ignore_sideband, decorrelate_sr = decorrelate_sr)['nominal']}
    
                        if corr_syst not in tmp_list_of_hist[c][v]['bkgr']['non-prompt'].keys():
                            tmp_list_of_hist[c][v]['bkgr']['non-prompt'].update(tmp_hist)
                        else:
                            for sk in tmp_hist.keys():
                                tmp_list_of_hist[c][v]['bkgr']['non-prompt'][sk].add(tmp_hist[sk])
                        del(tmp_hist)
                    else:
                        #Load in the prompt sideband so we can remove it from our datadriven estimation
                        if corr_syst == 'nominal': 
                            tmp_list_of_hist[c][v]['data'][b] = createSingleVariableDistributions(intree, v, 'tmp_'+b+v+str(c)+'p'+corr_syst+'-'+str(sr)+'-'+str(year)+'-sideband', bins(c, v), '('+cc+'&&isprompt&&issideband)'+additional_condition, b, year, include_systematics, split_corr=split_corr, ignore_sideband=ignore_sideband, decorrelate_sr = decorrelate_sr)
                        else:
                            tmp_list_of_hist[c][v]['data'][b][corr_syst] = createSingleVariableDistributions(intree, v, 'tmp_'+b+v+str(c)+'p'+corr_syst+'-'+str(sr)+'-'+str(year)+'-sideband', bins(c, v), '('+cc+'&&isprompt&&issideband)'+additional_condition, b, year, split_corr=split_corr, ignore_sideband=ignore_sideband, decorrelate_sr = decorrelate_sr)['nominal']
                
    if not ignore_sideband:
        for c, cc in zip(categories_to_use, category_conditions):
            for iv, v in enumerate(var_dict.keys()):
                tmp_list_of_hist[c][v]['bkgr']['non-prompt'] = tmp_list_of_hist[c][v]['data']['sideband']
               
                #Remove prompt contribution
                for b in background:  
                    if b in ['charge-misid', 'non-prompt']: continue
                    #if b == 'XG': continue
                    for k in tmp_list_of_hist[c][v]['bkgr']['non-prompt'].keys():
                        tmp_list_of_hist[c][v]['bkgr']['non-prompt'][k].getHist().Add(tmp_list_of_hist[c][v]['data'][b]['nominal'].getHist(), -1.) 
                
                for k in tmp_list_of_hist[c][v]['bkgr']['non-prompt'].keys():
                    tmp_list_of_hist[c][v]['bkgr']['non-prompt'][k].removeNegativeBins(error=1.0)

    if args.paperPlots is not None:
        for c, cc in zip(categories_to_use, category_conditions):
            for iv, v in enumerate(var_dict.keys()):
                if 'TotBkgr' not in tmp_list_of_hist[c][v]['bkgr'].keys():
                    tmp_list_of_hist[c][v]['bkgr']['TotBkgr'] = {}
                list_to_rm = []
                for btm in tmp_list_of_hist[c][v]['bkgr']:
                    if btm == 'TotBkgr': continue
                    list_to_rm.append(btm)
                    for k in tmp_list_of_hist[c][v]['bkgr'][btm].keys():
                        if k not in tmp_list_of_hist[c][v]['bkgr']['TotBkgr'].keys():
                            tmp_list_of_hist[c][v]['bkgr']['TotBkgr'][k] = tmp_list_of_hist[c][v]['bkgr'][btm]['nominal'].clone('TotBkgr')
                        else:
                            tmp_list_of_hist[c][v]['bkgr']['TotBkgr'][k].getHist().Add(tmp_list_of_hist[c][v]['bkgr'][btm]['nominal'].getHist())

                for btm in list_to_rm:
                    tmp_list_of_hist[c][v]['bkgr'].pop(btm)
    return tmp_list_of_hist

def getMergedYears(signal_list, bkgr_list, data_list):
    # Translate tree if years need to be combined
    year_to_plot = '-'.join(sorted(args.year))
    signal_list[year_to_plot] = []
    bkgr_list[year_to_plot] = []
    data_list[year_to_plot] = []


    #Translate the input lists
    input_lists = {'signal' : {}, 'bkgr' : {}, 'data' : {}}
    for y in args.year:
        for signal in signal_list[y]:
            if signal.split('/')[-1] not in input_lists['signal'].keys():
                input_lists['signal'][signal.split('/')[-1]] = {y:signal}
            else:
                input_lists['signal'][signal.split('/')[-1]][y] = signal
        for bkgr in bkgr_list[y]:
            if bkgr.split('/')[-1] not in input_lists['bkgr'].keys():
                input_lists['bkgr'][bkgr.split('/')[-1]] = {y:bkgr}
            else:
                input_lists['bkgr'][bkgr.split('/')[-1]][y] = bkgr
        for data in data_list[y]:
            if data.split('/')[-1] not in input_lists['data'].keys():
                input_lists['data'][data.split('/')[-1]] = {y:data}
            else:
                input_lists['data'][data.split('/')[-1]][y] = data

    for sob in ['signal', 'bkgr', 'data']:
        for sample_name in input_lists[sob]:
            if len(input_lists[sob][sample_name].keys()) != len(args.year):
                continue
            else:
                output_name = input_lists[sob][sample_name][args.year[0]].replace(args.era+'-'+args.year[0], args.era+'-'+year_to_plot)

                if sob == 'signal':
                    signal_list[year_to_plot].append(output_name)
                elif sob == 'bkgr':
                    bkgr_list[year_to_plot].append(output_name)
                elif sob == 'data':
                    data_list[year_to_plot].append(output_name)

    print 'End translation'
    return signal_list, bkgr_list, data_list
    

def insertRebin(in_var, year, signal_list, bkgr_list, data_list, additional_condition, ignore_sideband, searchregion = None, for_datacards = False):
    from HNL.Analysis.analysisTypes import getBinning
    var_to_rebin = {}

    for v in in_var:
            var_to_rebin[v] = [x for x in in_var[v]]
            var_to_rebin[v][1] = np.arange(-1.0, 1.001, 0.001)

    binning = {}
    from HNL.TMVA.rebinning import getEwkinoBinning
    for c in category_dict[args.categoriesToPlot][0]:
        binning[c] = {}
        for v in in_var.keys():
             binning[c][v] = np.arange(-1.0, 1.001, 0.001)

    return binning

def translateSearchRegions():
    out_regions = set()
    for r in args.searchregion:
        if r in srm[args.region].getListOfSearchRegionGroups():
            out_regions.update(srm[args.region].getGroupValues(r))
        else:
            out_regions.update([r])
    return out_regions

#############################################
#                                           #
#           Actual Plotting Code            #
#                                           #
#############################################

from ROOT import gROOT
gROOT.SetBatch(True)
import glob
from HNL.Analysis.analysisTypes import signal_couplingsquared
from HNL.Tools.helpers import getHistFromTree

ignore_sideband = args.includeData != 'includeSideband' or args.ignoreSideband 

# Merge and collect histograms
if args.bkgrOnly: args.plotBkgrOnly = True

#Add entry for the search regions in the var dictionary
from HNL.Weights.reweighter import var_weights
if not args.genLevel:    var.update(var_weights)
#var['searchregion'] = (lambda c : c.searchregion, 'placeholder', ('Search region', 'Events'))
#var = {
#    'leadingFakeLeptonPt' : (lambda c : c.leadingFakeLeptonPt[0],       np.arange(0., 300., 15.),       ('p_{T} (leading fake lepton) [GeV]', 'Events')),
#    'leadingFakeElectronPt' : (lambda c : c.leadingFakeElectronPt[0],       np.arange(0., 300., 15.),       ('p_{T} (leading fake electron) [GeV]', 'Events')),
#    'leadingFakeMuonPt' : (lambda c : c.leadingFakeMuonPt[0],       np.arange(0., 300., 15.),       ('p_{T} (leading fake muon) [GeV]', 'Events')),
#    'l1pt':      (lambda c : c.l_pt[0],       np.arange(0., 300., 15.),       ('p_{T} (l1) [GeV]', 'Events'))
#}

# Custom Var that you can create from existing var (i.e. 2D plots)
# var['l3pt-met'] = (lambda c : [c.l3pt, c.met], (np.array([20., 25., 35., 50., 70., 100.]), np.array([0., 20., 35., 50., 100.])), ('p_{T}(l3) [GeV]', 'met'))

signal_list = {}
bkgr_list = {}
background_collection = {}
data_list = {}
for year in args.year:
    print 'Processing ', year

    sample_manager = getSampleManager(year)

    if not args.plotBkgrOnly:
        signal_list[year] = [s for s in glob.glob(getInputName('signal', year, args.tag)+'/*') if s.split('/')[-1] in sample_manager.sample_outputs]
        for i, s in enumerate(signal_list):
            if 'signalOrdering' in s:
                signal_list[year].pop(i)
    else:
        signal_list[year] = []

    # Collect background file locations
    if not args.signalOnly:
        bkgr_list[year] = [getInputName('bkgr', year, args.tag)+'/'+b for b in sample_manager.sample_outputs if os.path.isdir(getInputName('bkgr', year, args.tag)+'/'+b)]
    else:
        bkgr_list[year] = []

    # data
    if args.includeData is not None:
        data_list[year] = glob.glob(getInputName('data', year, args.tag)+'/Data')
    else:
        data_list[year] = []

    print 'check merge'
    # Merge files if necessary
    mixed_list = signal_list[year] + bkgr_list[year] + data_list[year]
    custom_list_to_use = customizeListToUse(year)
    full_path = os.path.expandvars(os.path.join('$CMSSW_BASE', 'src', 'HNL', 'Analysis'))
    #merge(mixed_list, __file__, jobs[year], ('sample', 'subJob'), argParser, istest=args.isTest, additionalArgs= [('year', year)], man_changed_args = {'customList':custom_list_to_use}, full_path = full_path)

    background_collection[year] = []
    for x in sample_manager.sample_outputs:
        if 'HNL' in x: continue
        if 'Data' in x: continue
        if not os.path.isdir(getInputName('bkgr', year, args.tag)+'/'+x): continue
        background_collection[year].append(x)
    
    background_collection[year] += ['non-prompt', 'charge-misid']

    #Clean list of hist
    tmp_signal_list = []
    signal_legendnames = []
    for i_s, s in enumerate(signal_list[year]):
        sample_name = s.split('/')[-1]
        sample_mass = Sample.getSignalMass(sample_name)
        if args.sample is not None and args.sample != sample_name:      continue
        if sample_name not in sample_manager.sample_outputs:              continue    
        if args.masses is not None and sample_mass not in args.masses:  continue 
        if args.flavor != '' and '-'+args.flavor not in sample_name:  continue 
        if Sample.getSignalDisplacedString(sample_name) == 'displaced': continue
        tmp_signal_list.append(s)
        signal_legendnames.append('HNL '+str(int(Sample.getSignalMass(sample_name)))+ '#scale[0.5]{ }GeV')

    signal_list[year] = [x for x in tmp_signal_list]

years_to_plot = [y for y in args.year]
if args.combineYears: 
    years_to_plot = ['-'.join(sorted(args.year))]

if args.combineYears:
    signal_list, bkgr_list, data_list = getMergedYears(signal_list, bkgr_list, data_list)
    background_collection[years_to_plot[0]] = [x for x in background_collection[args.year[0]]]

#
#       Plot!
#

#
# Necessary imports
#
from HNL.Plotting.plot import Plot
from HNL.Plotting.plottingTools import extraTextFormat
from HNL.Tools.helpers import makePathTimeStamped
from HNL.TMVA.mvaVariables import getAllRelevantNames

list_of_hist = {}
#list_of_hist_forbar = {}

var_to_use = {}
if args.variables is None:
    var_to_use = var
else:
    for v in var:
        if v in args.variables:
            var_to_use[v] = var[v]

print var_to_use.keys()

additional_condition = args.additionalCondition
if args.searchregion is not None:
    searchregion_condition = '||'.join(['searchregion == {0}'.format(x) for x in translateSearchRegions()])
    if additional_condition is None:
        additional_condition = searchregion_condition
    else:
        additional_condition += '&&('+searchregion_condition+')'
print "Scouting binning"

print years_to_plot
for year in years_to_plot:
    binning = insertRebin(var_to_use, year, signal_list, background_collection, data_list, additional_condition = additional_condition, ignore_sideband = ignore_sideband, searchregion = args.searchregion)
    print "Creating list of histograms"
    list_of_hist[year] = createVariableDistributions(category_dict[args.categoriesToPlot], var_to_use, signal_list[year], background_collection[year], data_list[year], sample_manager, year, additional_condition = additional_condition, include_systematics = args.systematics if not args.ignoreSystematics else 'nominal', ignore_sideband = ignore_sideband, custom_bins = binning)

    #
    # Set output directory, taking into account the different options
    #
    from HNL.Tools.outputTree import cleanName
    output_dir = os.path.join(os.getcwd(), 'data', 'testArea' if args.isTest else '', 'Results', 'ROC', '-'.join([args.strategy, args.selection, args.region, cleanName(args.additionalCondition) if args.additionalCondition is not None else '']), args.era+str(year))

    if args.flavor:         output_dir = os.path.join(output_dir, args.flavor+'_coupling')
    else:                   output_dir = os.path.join(output_dir, 'all_coupling')

    output_dir_unstamped = output_dir
    output_dir = makePathTimeStamped(output_dir)

    #
    # Create variable plots for each category
    #
    print "Creating variable plots"

    from HNL.EventSelection.eventCategorization import CATEGORY_NAMES
    # for c in list_of_hist.keys():
    for c in category_dict[args.categoriesToPlot][0]:
        if args.categoriesToPlot == 'original':
            c_name = CATEGORY_NAMES[float(c)]
        elif args.categoriesToPlot == 'analysis':
            from HNL.EventSelection.eventCategorization import ANALYSIS_CATEGORIES_TEX
            c_name = ANALYSIS_CATEGORIES_TEX[c] 
        elif args.categoriesToPlot == 'splitanalysis':
            from HNL.EventSelection.eventCategorization import ANALYSIS_SPLITOSSF_CATEGORIES_TEX
            c_name = ANALYSIS_SPLITOSSF_CATEGORIES_TEX[c] 
        elif args.categoriesToPlot == 'leadingflavor':
            from HNL.EventSelection.eventCategorization import LEADING_FLAVOR_CATEGORIES_TEX
            c_name = LEADING_FLAVOR_CATEGORIES_TEX[c] 
        elif args.categoriesToPlot == 'sign':
            from HNL.EventSelection.eventCategorization import SIGN_CATEGORIES_TEX
            c_name = SIGN_CATEGORIES_TEX[c] 
        elif args.categoriesToPlot == 'trigger':
            from HNL.EventSelection.eventCategorization import TRIGGER_CATEGORIES_TEX
            c_name = TRIGGER_CATEGORIES_TEX[c] 
        else:
            from HNL.EventSelection.eventCategorization import SUPER_CATEGORIES_TEX
            c_name = SUPER_CATEGORIES_TEX[c] 

        extra_text = [] 
        if args.region in signal_regions: 
            #extra_text.append(extraTextFormat('#bf{'+c_name+'}', xpos = 0.2, ypos = 0.74, textsize = None, align = 12))  #Text to display event type in plot
            extra_text.append(extraTextFormat(c_name, xpos = 0.7, ypos = 0.3, textsize = None, align = 12))  #Text to display event type in plot
        else: 
            extra_text.append(extraTextFormat("", xpos = 0.7, ypos = 0.3, textsize = None, align = 12))  #Text to display event type in plot
#        if args.flavor: 
#            from decimal import Decimal
#            et_flavor = args.flavor if args.flavor == 'e' else '#'+args.flavor
#            default_coupling = signal_couplingsquared[args.flavor][args.masses[0]]
#            extra_text.append(extraTextFormat('|V_{'+et_flavor+'N}|^{2} = '+'%.0E' % Decimal(str(default_coupling)), textsize = 0.8))

        # Plots that display chosen for chosen signal masses and backgrounds the distributions for the different variables
        # S and B in same canvas for each variable
        for v in var_to_use.keys():
            signal_hist = []
            for sk in sorted(list_of_hist[year][c][v]['signal'].keys()):
                signal_hist.append(list_of_hist[year][c][v]['signal'][sk]['nominal'].getHist())

            bkgr_hist = list_of_hist[year][c][v]['bkgr']['TotBkgr']['nominal'].getHist()
            
            roc_list = []

            for s in signal_hist:
                def getROCGraph(signal, background):
                    from ROOT import TGraphErrors
                    roc = TGraphErrors(signal.GetNbinsX()+1)
                    sow_s = signal.GetSumOfWeights()
                    sow_b = background.GetSumOfWeights()
                    int_s = sow_s
                    int_b = sow_b
                    roc.SetPoint(0, 1., 1.)
                    for b in range(1, signal.GetNbinsX()+1):
                        int_s -= signal.GetBinContent(b)
                        int_b -= background.GetBinContent(b)
                        roc.SetPoint(b, int_b/sow_b, int_s/sow_s)

                    return roc

                roc_list.append(getROCGraph(s, bkgr_hist))

            p = Plot(roc_list, signal_legendnames, v, 'background efficiency', 'signal efficiency', extra_text = extra_text)
            p.setLegend(x1 = 0.55, y1 = 0.4, y2 = 0.55)
            p.drawGraph(output_dir, "APLine", 1, .1)

    

            

