#
# Code to make trees to use in training
#

#
# Argument parser and logging
#
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
submission_parser = argParser.add_argument_group('submission', 'Arguments for submission. Any arguments not in this group will not be regarded for submission.')
submission_parser.add_argument('--isChild',  action='store_true', default=False,  help='mark as subjob, will never submit subjobs by itself')
submission_parser.add_argument('--year',     action='store',      default=None,   help='Select year')
submission_parser.add_argument('--era',     action='store',       default='prelegacy', choices = ['UL', 'prelegacy'],   help='Select era')
submission_parser.add_argument('--sample',   action='store',      default=None,   help='Select sample by entering the name as defined in the conf file')
submission_parser.add_argument('--subJob',   action='store',      default=None,   help='The number of the subjob for this sample')
submission_parser.add_argument('--isTest',   action='store_true', default=False,  help='Run a small test')
submission_parser.add_argument('--batchSystem', action='store',         default='HTCondor',  help='choose batchsystem', choices=['local', 'HTCondor', 'Cream02'])
submission_parser.add_argument('--dryRun',   action='store_true', default=False,  help='do not launch subjobs, only show them')
submission_parser.add_argument('--logLevel',  action='store',     default='INFO', help='Log level for logging', nargs='?', choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE'])

submission_parser.add_argument('--cutString',   action='store', default=None,  help='Additional cutstrings for training')
submission_parser.add_argument('--trainingEras',  action='store',   nargs='*',   default=None, choices = ['UL', 'prelegacy'],   help='Select era')
submission_parser.add_argument('--summaryFile', action='store_true', default=False,  help='Create text file that shows all selected arguments')
submission_parser.add_argument('--noskim', action='store_true', default=False,  help='Use unskimmed files')
submission_parser.add_argument('--customList',  action='store',      default=None,               help='Name of a custom sample list. Otherwise it will use the appropriate noskim file.')
submission_parser.add_argument('--selection',   action='store', default='default',  help='Select the type of selection for objects', choices=['leptonMVAtop', 'AN2017014', 'default', 'Luka', 'TTT'])
submission_parser.add_argument('--region',   action='store', default='baseline', 
    help='apply the cuts of high or low mass regions, use "all" to run both simultaniously', choices=['baseline', 'highMassSR', 'lowMassSR', 'ZZ', 'WZ', 'Conversion'])
submission_parser.add_argument('--analysis',   action='store', default='HNL',  help='Select the strategy to use to separate signal from background', choices=['HNL', 'AN2017014', 'ewkino'])

argParser.add_argument('--plotNonpromptSpectrum', action='store_true', default=False,  help='Use unskimmed files')
argParser.add_argument('--makePlots',   action='store_true', default=False,  help='merge existing subjob output')


args = argParser.parse_args()

from HNL.Tools.logger import getLogger, closeLogger
log = getLogger(args.logLevel)

import ROOT
import os
from HNL.Tools.helpers import isValidRootFile, makeDirIfNeeded
from HNL.Weights.reweighter import Reweighter
from random import randrange
nl = 3 if args.region != 'ZZCR' else 4

#
# Set some args for when performing a test
#
if args.isTest:
    if args.sample is None: args.sample = 'DYJetsToLL-M-50'
    if args.year is None: args.year = '2017'
    if args.subJob is None: args.subJob = 0
    args.isChild = True

era_to_use = args.era if args.trainingEras is None else '-'.join(args.trainingEras)

from HNL.TMVA.inputHandler import InputHandler
ih = InputHandler(era_to_use, 'all', args.region, args.selection)

#
#Load in samples
#
from HNL.Samples.sampleManager import SampleManager
file_list = 'TMVA/checklist_'+args.era+args.year+'_mconly' if args.customList is None else args.customList
skim_str = 'noskim' if args.noskim else 'Reco'
sample_manager = SampleManager(args.era, args.year, skim_str, file_list, skim_selection=args.selection, region = args.region)
jobs = []
for sample_name in sample_manager.sample_names:
    if sample_name == 'Data': continue
    sample = sample_manager.getSample(sample_name)
    try:
        for njob in xrange(sample.returnSplitJobs()): 
            jobs += [(sample.name, str(njob))]
    except:
        continue

from HNL.EventSelection.eventCategorization import SUPER_CATEGORIES

#
# Create new reduced tree (except if it already exists and overwrite option is not used)
#
output_base = os.path.expandvars(os.path.join('$CMSSW_BASE', 'src', 'HNL', 'TMVA', 'data', 'checkMVAefficiencyInFullSelection')) if not args.isTest else os.path.expandvars(os.path.join('$CMSSW_BASE', 'src', 'HNL', 'TMVA', 'data', 'testArea', 'checkMVAefficiencyInFullSelection'))

out_cut_str = "".join(i for i in args.cutString if i not in "\/:*?<>|& ") if args.cutString else None
if out_cut_str is None:
    output_name = lambda mva, typ : os.path.join(output_base, era_to_use, args.era+args.year, args.region + '-'+args.selection, 
                            'tmp_'+sample.output, sample.name + '_'+sample.output+'-'+mva.replace('_', '-')+'-'+typ+'_'+ str(args.subJob) + '.root')
else:
    output_name = lambda mva, typ : os.path.join(output_base, era_to_use, args.era+args.year, args.region + '-'+args.selection, out_cut_str,
                        'tmp_'+sample.output, sample.name + '_'+sample.output+'-'+mva.replace('_', '-')+'-'+typ+'_'+ str(args.subJob) + '.root')

from HNL.TMVA.reader import MVA_of_choice as mvas
from HNL.TMVA.mvaVariables import region_dict
from HNL.Tools.ROC import ROC


reduced_mvas = {}
for mva in ih.signal_names:
    if not any([k in mva for k in region_dict[args.region]]): continue
    reduced_mvas[mva] = mvas[args.cutString][mva]

if not args.makePlots:

    #
    # Submit subjobs
    #
    if not args.isChild:
        from HNL.Tools.jobSubmitter import submitJobs

        submitJobs(__file__, ('sample', 'subJob'), jobs, argParser, jobLabel = 'checkMVAeff')
        exit(0)


    #
    #Get specific sample for this subjob
    #
    sample = sample_manager.getSample(args.sample)
    chain = sample.initTree(needhcount=False)
    chain.year = args.year
    chain.era = args.era
    chain.is_signal = 'HNL' in sample.name
    chain.selection = args.selection
    chain.strategy = 'MVA'
    chain.analysis = args.analysis

    reweighter = Reweighter(sample, sample_manager)

    # Import and create cutter to provide cut flow
    #
    from HNL.EventSelection.cutter import Cutter
    cutter = Cutter(chain = chain)

    # if not args.isTest and isValidRootFile(output_name):
    #     log.info('Finished: valid outputfile already exists')
    #     exit(0)

    #
    # make ROC's and efficiencies
    #
    import numpy as np
    from HNL.Tools.histogram import Histogram
    from HNL.Analysis.analysisTypes import var_mva
    workingpoints = [str(x) for x in np.arange(-1., 1.01, 0.01)]
    list_of_roc = {}
    list_of_hist = {}
    for mva in reduced_mvas.keys():
        makeDirIfNeeded(output_name(mva, 'ROC'))
        list_of_roc[mva] = ROC(mva, output_name(mva, 'ROC'), working_points = workingpoints)

        makeDirIfNeeded(output_name(mva, 'hist'))
        list_of_hist[mva] = {
            'prompt': Histogram(mva+'-prompt', var_mva[mva][0], var_mva[mva][2], var_mva[mva][1]),
            'nonprompt': Histogram(mva+'-nonprompt', var_mva[mva][0], var_mva[mva][2], var_mva[mva][1]),
        }


    #
    # Start event loop
    #
    if args.isTest:
        max_events = 20000
        event_range = xrange(max_events) if max_events < len(sample.getEventRange(args.subJob)) else sample.getEventRange(args.subJob)
    else:
        event_range = sample.getEventRange(args.subJob)    

    from HNL.Tools.helpers import progress
    from HNL.EventSelection.event import Event

    #prepare object  and event selection
    event = Event(chain, chain, is_reco_level=True, selection=args.selection, strategy='MVA', region=args.region)

    #Load TMVA readers
    from HNL.TMVA.reader import Reader
    tmvas = {}
    for mva in reduced_mvas.keys():  
        tmvas[mva] = Reader(chain, 'kBDT', mva, args.region, era_to_use, cut_string = args.cutString)

    for entry in event_range:
        chain.GetEntry(entry)
        if args.isTest: progress(entry - event_range[0], len(event_range))
    
        cutter.cut(True, 'Total')

        event.initEvent()
        # First run sideband for non-prompt
        chain.obj_sel['ele_wp'] = 'FO'
        chain.obj_sel['mu_wp'] = 'FO'

        if not event.passedFilter(cutter, sample.output): continue
        if len(chain.l_flavor) == chain.l_flavor.count(2): continue

        #Reset object selection
        event.resetObjSelection()
        passes_full_selection = event.passedFilter(cutter, sample.output)

        prompt_str = 'nonprompt' if not passes_full_selection else 'prompt'

        category = event.event_category.returnCategory()
        super_cat = event.event_category.returnSuperCategory()

        if super_cat != 'NoTau': continue

        nprompt = 0
        for index in chain.l_indices:
            if chain._lIsPrompt[index]: nprompt += 1
        
        for v in tmvas.keys():
            tmvas[v].predictAndWriteToChain(chain)

        weight = reweighter.getLumiWeight()
        if prompt_str == 'nonprompt': 
            weight *= reweighter.getFakeRateWeight()

        for roc in list_of_roc.keys():
            passed_workingpoints = [getattr(chain, "".join(i for i in roc if i not in "-")) > float(wp) for wp in workingpoints]
            if chain.is_signal:
                list_of_roc[roc].fillEfficiency(passed_workingpoints, [weight]*len(workingpoints))
            else:
                list_of_roc[roc].fillMisid(passed_workingpoints, [weight]*len(workingpoints))

        for h in list_of_hist.keys():
            list_of_hist[h][prompt_str].fill(chain, weight)


    for roc in list_of_roc:
        list_of_roc[roc].write()

    for h in list_of_hist:
        for ip, p in enumerate(list_of_hist[h]):
            list_of_hist[h][p].write(output_name(h, 'eff'), subdirs=[p], append=ip > 0)

    closeLogger(log)

    # cutter.saveCutFlow(output_name(var, 'eff'))

else:

    import glob
    from HNL.Tools.mergeFiles import merge
    merge_files = glob.glob(output_name('*', '*').rsplit('/', 2)[0])
    for mf in merge_files:
        if "Results" in mf: merge_files.pop(merge_files.index(mf))
    merge(merge_files, __file__, jobs, ('sample', 'subJob'), argParser, istest=args.isTest)

    all_outputs = sample_manager.getOutputs()
    
    from HNL.TMVA.mvaVariables import mass_ranges_for_validation as mass_ranges
    from HNL.TMVA.mvaVariables import all_masses

    all_outputs_grouped = {}
    for mva in ih.signal_names:
        all_outputs_grouped[mva] = [x for x in all_outputs if 'HNL' in  x and '-'+mva.split('-')[-1]+'-' in x and min(mass_ranges[mva.split('-')[0]]) <= int(x.split('-m')[-1]) <= max(mass_ranges[mva.split('-')[0]])]

    all_backgrounds = [x for x in all_outputs if not 'HNL' in  x]

    extended_output_base = output_base+'/'+ era_to_use+'/'+args.era+args.year +'/'+ args.region + '-'+args.selection
    if args.cutString is not None:
        extended_output_base += "/"+"".join(i for i in args.cutString if i not in "\/:*?<>|& ")
    for mva in reduced_mvas.keys():    
        os.system('hadd -f '+extended_output_base + '/' + mva.replace('_', '-')+'-'+mva.replace('_', '-')+'-ROC.root ' +  ' '.join([extended_output_base + '/' + s +'-'+mva.replace('_', '-')+'-ROC.root' for s in all_outputs_grouped[mva]]))

    makeDirIfNeeded(extended_output_base+'/MERGEDROC/x')

    list_of_hist = {}

    if not args.plotNonpromptSpectrum:
        background_collection = [k for k in sample_manager.sample_groups.keys()]+['nonprompt']
    else:
        background_collection = sample_manager.sample_outputs

    from HNL.Plotting.plot import Plot
    from HNL.Tools.helpers import getObjFromFile
    for mva in reduced_mvas.keys(): 
        list_of_hist[mva] = {'signal': [], 'bkgr' : {}}   

        for o in [x for x in all_outputs if not 'HNL' in x]:

            tmp_hist_prompt = getObjFromFile(extended_output_base+'/'+o+'-'+mva+'-eff.root', 'prompt/'+mva+'-prompt')
            tmp_hist_nonprompt = getObjFromFile(extended_output_base+'/'+o+'-'+mva+'-eff.root', 'nonprompt/'+mva+'-nonprompt')

            if not args.plotNonpromptSpectrum:
                sg = [sk for sk in sample_manager.sample_groups.keys() if o in sample_manager.sample_groups[sk]]
                if len(sg) > 0:
                    if sg[0] not in list_of_hist[mva]['bkgr'].keys():
                        list_of_hist[mva]['bkgr'][sg[0]] = tmp_hist_prompt.Clone()
                    else:
                        list_of_hist[mva]['bkgr'][sg[0]].Add(tmp_hist_prompt)

                if 'nonprompt' not in list_of_hist[mva]['bkgr'].keys():
                    list_of_hist[mva]['bkgr']['nonprompt'] = tmp_hist_nonprompt.Clone()
                else:
                    list_of_hist[mva]['bkgr']['nonprompt'].Add(tmp_hist_nonprompt)
            else:
                if o not in list_of_hist[mva]['bkgr'].keys():
                    list_of_hist[mva]['bkgr'][o] = tmp_hist_nonprompt.Clone()
                else:
                    list_of_hist[mva]['bkgr'][o].Add(tmp_hist_nonprompt)
                    
        for o in [x for x in all_outputs if 'HNL' in x] + [x.replace('_', '-') for x in all_outputs_grouped.keys()]:
            try:
                if int(o.split('-m')[-1]) not in all_masses: continue
                if o.split('-')[1] != mva.split('-')[1]: continue 
            except:
                if mva != o: continue

            os.system('hadd -f '+extended_output_base + '/MERGEDROC/' + o+'-'+mva.replace('_', '-')+'-ROC.root ' + extended_output_base + '/' + o +'-'+mva.replace('_', '-')+'-ROC.root ' + ' '.join([extended_output_base + '/' + b +'-'+mva.replace('_', '-')+'-ROC.root' for b in all_backgrounds]))
            roc = ROC(mva, extended_output_base + '/MERGEDROC/' + o+'-'+mva.replace('_', '-')+'-ROC.root')
            g = roc.returnGraph(no_error_bars=True)
            # g.RemovePoint(20)
            auc = roc.getAUC()
            from HNL.Plotting.plottingTools import extraTextFormat
            extra_text = [extraTextFormat('AUC: '+str(auc), xpos = 0.2, ypos = 0.32, textsize = 1.2, align = 12)]  #Text to display event type in plot

            p = Plot(g, o, o+'_'+mva, '1 - misid', 'efficiency', extra_text=extra_text)
            p.drawGraph(output_dir = extended_output_base +'/' + mva + '/RESULT/NonpromptSpectrum/ROC')

            if 'HNL' in o:
                hist = getObjFromFile(extended_output_base+'/'+o+'-'+mva+'-eff.root', 'prompt/'+mva+'-prompt')
                
                bkgr_hist = []
                bkgr_names = []
                for b in background_collection:
                    if b not in list_of_hist[mva]['bkgr'].keys(): continue
                    bkgr_hist.append(list_of_hist[mva]['bkgr'][b])
                    bkgr_names.append(b)


                hp = Plot(hist, [o] + bkgr_names, o+'_'+mva, 'MVA score', 'Events', bkgr_hist = bkgr_hist, y_log=True, color_palette_bkgr='AN2017' if not args.plotNonpromptSpectrum else 'StackTauPOG')
                # hp = Plot(hist, [o] + background_collection, o+'_'+mva, 'MVA score', 'Events', y_log=True, color_palette_bkgr='AN2017')
                hp.drawHist(output_dir = extended_output_base +'/' + mva + '/RESULT/NonpromptSpectrum/SCORE', normalize_signal = True, draw_option = 'EHist')
                # hp.drawHist(output_dir = extended_output_base +'/' + mva + '/RESULT/SCORE')








