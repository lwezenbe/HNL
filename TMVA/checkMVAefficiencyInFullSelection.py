import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
submission_parser = argParser.add_argument_group('submission', 'Arguments for submission. Any arguments not in this group will not be regarded for submission.')
submission_parser.add_argument('--isChild',  action='store_true', default=False,  help='mark as subjob, will never submit subjobs by itself')
submission_parser.add_argument('--year',     action='store',       default=None,   help='Select year. Enter "all" for all years', required=True)
submission_parser.add_argument('--era',     action='store',   nargs='*',   default=None, choices = ['UL', 'prelegacy'],   help='Select era')
submission_parser.add_argument('--region', action='store', default='baseline', type=str,  help='What region do you want to select for?',
    choices=['baseline', 'lowMassSR', 'lowMassSRloose', 'highMassSR'])
submission_parser.add_argument('--selection',   action='store', default='default',  help='Select the type of selection for objects', choices=['leptonMVAtop', 'AN2017014', 'default', 'Luka', 'TTT'])
submission_parser.add_argument('--sample',   action='store', default=None,  help='Select sample name')
submission_parser.add_argument('--batchSystem', action='store',         default='HTCondor',  help='choose batchsystem', choices=['local', 'HTCondor', 'foreground'])
submission_parser.add_argument('--dryRun',   action='store_true', default=False,  help='do not launch subjobs, only show them')
submission_parser.add_argument('--cutString',   action='store', default=None,  help='Additional cutstrings for training')
submission_parser.add_argument('--isTest',   action='store_true', default=False,  help='do not launch subjobs, only show them')
submission_parser.add_argument('--dummy',   action='store_true', default=False,  help='to be ignored')
submission_parser.add_argument('--logLevel',  action='store', default='INFO',  help='Log level for logging', nargs='?', choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE'])
submission_parser.add_argument('--subJob',   action='store',            default=None,   help='The number of the subjob for this sample')


argParser.add_argument('--makePlots',     action='store_true',      default=False,   help='Store plots')

args = argParser.parse_args()

def calcSplitJobs(tot_events):
    max_events_per_job = 500000.
    split_jobs = int(round((max_events_per_job/tot_events)+0.5))
    return max(1, int(split_jobs))


def getEventRange(tot_events, subjob):
    split_jobs = calcSplitJobs(tot_events)
    limits = [entry*tot_events/split_jobs for entry in range(split_jobs)] + [tot_events]
    return xrange(limits[int(subjob)], limits[int(subjob)+1])


eras = "-".join(sorted(args.era))

from HNL.TMVA.inputHandler import InputHandler
ih = InputHandler(eras, args.year, args.region+'-forcheck', args.selection)

jobs = []
for sample_name in ih.signal_names:
    tree = ih.getTree(sample_name, name= 'Total/trainingtree', specific_sample = sample_name)
    for sub_job in range(calcSplitJobs(tree.GetEntries())):
        jobs += [(sample_name, str(sub_job))]
for sample_name in ih.background_names:
    tree = ih.getTree(ih.signal_names[0], name= 'Total/trainingtree', specific_sample = sample_name)
    for sub_job in range(calcSplitJobs(tree.GetEntries())):
        jobs += [(sample_name, str(sub_job))]

import os
argstring_reduced = "".join(i for i in args.cutString if i not in "\/:*?<>|& ") if args.cutString is not None else 'full'
output_base = os.path.expandvars(os.path.join('$CMSSW_BASE', 'src', 'HNL', 'TMVA', 'data', 'testArea' if args.isTest else '', 'checkMVAefficiencyInFullSelectionV2', eras+args.year, args.region+'-'+args.selection+'-'+argstring_reduced))

cut_string_dict = {
    None : lambda c:True,
    'lowMassSR' : lambda c: c.M3l<80 and c.l1_pt < 55 and c.met < 75 and c.minMossf < 0,
    'lowMassSRloose' : lambda c: c.M3l<80 and c.l1_pt < 55 and c.met < 75 and abs(c.MZossf-91) > 15,
}


custom_mva_dicts = {}
custom_mva_dicts['full'] = {
'lowestmass-e' : ('kBDT-boostType=Grad-ntrees=25-maxdepth=2-shrinkage=0.1', 'lowMassSR', lambda c : c.lowestmasse ),
'lowestmass-mu' : ('kBDT-boostType=Grad-ntrees=25-maxdepth=3-shrinkage=0.1', 'lowMassSR', lambda c : c.lowestmassmu ),
'lowestmass-tauhad' : ('kBDT-boostType=Grad-ntrees=75-maxdepth=2-shrinkage=0.1', 'lowMassSR', lambda c : c.lowestmasstauhad ),
'lowestmass-taulep' : ('kBDT-boostType=Grad-ntrees=75-maxdepth=1-shrinkage=0.3', 'lowMassSR', lambda c : c.lowestmasstaulep ),
'lowmass-e' : ('kBDT-boostType=Grad-ntrees=300-maxdepth=4-shrinkage=0.1', 'lowMassSR', lambda c : c.lowmasse ),
'lowmass-mu' : ('kBDT-boostType=Grad-ntrees=200-maxdepth=4-shrinkage=0.1', 'lowMassSR', lambda c : c.lowmassmu ),
'lowmass-tauhad' : ('kBDT-boostType=AdaBoost-ntrees=75-maxdepth=3-shrinkage=0.1', 'lowMassSR', lambda c : c.lowmasstauhad ),
'lowmass-taulep' : ('kBDT-boostType=AdaBoost-ntrees=200-maxdepth=3-shrinkage=0.1', 'lowMassSR', lambda c : c.lowmasstaulep ),
}
custom_mva_dicts['fullloose'] = {
    'lowestmass-e' : ('kBDT-boostType=Grad-ntrees=100-maxdepth=4-shrinkage=0.3', 'lowMassSR', lambda c : c.lowestmasse ),
    'lowestmass-mu' : ('kBDT-boostType=Grad-ntrees=300-maxdepth=4-shrinkage=0.1', 'lowMassSR', lambda c : c.lowestmassmu ),
    'lowestmass-tauhad' : ('kBDT-boostType=Grad-ntrees=100-maxdepth=4-shrinkage=0.3', 'lowMassSR', lambda c : c.lowestmasstauhad ),
    'lowestmass-taulep' : ('kBDT-boostType=Grad-ntrees=300-maxdepth=2-shrinkage=0.3', 'lowMassSR', lambda c : c.lowestmasstaulep ),
    'lowmass-e' : ('kBDT-boostType=Grad-ntrees=300-maxdepth=4-shrinkage=0.1', 'lowMassSR', lambda c : c.lowmasse ),
    'lowmass-mu' : ('kBDT-boostType=Grad-ntrees=200-maxdepth=4-shrinkage=0.1', 'lowMassSR', lambda c : c.lowmassmu ),
    'lowmass-tauhad' : ('kBDT-boostType=AdaBoost-ntrees=75-maxdepth=3-shrinkage=0.1', 'lowMassSR', lambda c : c.lowmasstauhad ),
    'lowmass-taulep' : ('kBDT-boostType=AdaBoost-ntrees=200-maxdepth=3-shrinkage=0.1', 'lowMassSR', lambda c : c.lowmasstaulep ),
}
custom_mva_dicts['M3l80met75minMossf0'] =  {
'lowmass-e' : ('kBDT-boostType=RealAdaBoost-ntrees=100-maxdepth=3-shrinkage=0.3', 'lowMassSR', lambda c : c.lowmasse ),
'lowmass-mu' : ('kBDT-boostType=Grad-ntrees=75-maxdepth=2-shrinkage=0.1', 'lowMassSR', lambda c : c.lowmassmu ),
'lowmass-taulep' : ('kBDT-boostType=RealAdaBoost-ntrees=300-maxdepth=3-shrinkage=1', 'lowMassSR', lambda c : c.lowmasstaulep ),
'lowmass-tauhad' : ('kBDT-boostType=Grad-ntrees=50-maxdepth=1-shrinkage=1', 'lowMassSR', lambda c : c.lowmasstauhad ),
'lowestmass-e' : ('kBDT-boostType=Grad-ntrees=50-maxdepth=1-shrinkage=1', 'lowMassSR', lambda c : c.lowestmasse ),
'lowestmass-mu' : ('kBDT-boostType=AdaBoost-ntrees=100-maxdepth=2-shrinkage=0.1', 'lowMassSR', lambda c : c.lowestmassmu ),
'lowestmass-taulep' : ('kBDT-boostType=Grad-ntrees=300-maxdepth=2-shrinkage=0.1', 'lowMassSR', lambda c : c.lowestmasstaulep ),
'lowestmass-tauhad' : ('kBDT-boostType=RealAdaBoost-ntrees=25-maxdepth=4-shrinkage=1', 'lowMassSR', lambda c : c.lowestmasstauhad ),
}
custom_mva_dicts['l1_pt55met75minMossf0'] = {
    'lowestmass-e' : ('kBDT-boostType=Grad-ntrees=100-maxdepth=3-shrinkage=0.1', 'lowMassSR', lambda c : c.lowestmasse ),
    'lowestmass-mu' : ('kBDT-boostType=Grad-ntrees=50-maxdepth=4-shrinkage=0.3', 'lowMassSR', lambda c : c.lowestmassmu ),
    'lowestmass-tauhad' : ('kBDT-boostType=Grad-ntrees=50-maxdepth=4-shrinkage=0.1', 'lowMassSR', lambda c : c.lowestmasstauhad ),
    'lowestmass-taulep' : ('kBDT-boostType=Grad-ntrees=25-maxdepth=2-shrinkage=0.3', 'lowMassSR', lambda c : c.lowestmasstaulep ),
    'lowmass-e' : ('kBDT-boostType=Grad-ntrees=75-maxdepth=4-shrinkage=0.1', 'lowMassSR', lambda c : c.lowmasse ),
    'lowmass-mu' : ('kBDT-boostType=Grad-ntrees=75-maxdepth=2-shrinkage=0.1', 'lowMassSR', lambda c : c.lowmassmu ),
    'lowmass-tauhad' : ('kBDT-boostType=Grad-ntrees=50-maxdepth=2-shrinkage=0.3', 'lowMassSR', lambda c : c.lowmasstauhad ),
    'lowmass-taulep' : ('kBDT-boostType=Grad-ntrees=50-maxdepth=4-shrinkage=0.1', 'lowMassSR', lambda c : c.lowmasstaulep ),
}
custom_mva_dicts['l1_pt55M3l80met75'] = {
    'lowestmass-e' : ('kBDT-boostType=Grad-ntrees=75-maxdepth=4-shrinkage=0.1', 'lowMassSR', lambda c : c.lowestmasse ),
    'lowestmass-mu' : ('kBDT-boostType=Grad-ntrees=50-maxdepth=3-shrinkage=0.1', 'lowMassSR', lambda c : c.lowestmassmu ),
    'lowestmass-tauhad' : ('kBDT-boostType=Grad-ntrees=300-maxdepth=4-shrinkage=0.1', 'lowMassSR', lambda c : c.lowestmasstauhad ),
    'lowestmass-taulep' : ('kBDT-boostType=Grad-ntrees=200-maxdepth=4-shrinkage=0.1', 'lowMassSR', lambda c : c.lowestmasstaulep ),
    'lowmass-e' : ('kBDT-boostType=Grad-ntrees=150-maxdepth=4-shrinkage=0.1', 'lowMassSR', lambda c : c.lowmasse ),
    'lowmass-mu' : ('kBDT-boostType=Grad-ntrees=150-maxdepth=4-shrinkage=0.1', 'lowMassSR', lambda c : c.lowmassmu ),
    'lowmass-tauhad' : ('kBDT-boostType=Grad-ntrees=75-maxdepth=4-shrinkage=0.3', 'lowMassSR', lambda c : c.lowmasstauhad ),
    'lowmass-taulep' : ('kBDT-boostType=Grad-ntrees=100-maxdepth=4-shrinkage=0.1', 'lowMassSR', lambda c : c.lowmasstaulep ),
}
custom_mva_dicts['l1_pt55M3l80minMossf0'] = {
'lowmass-e' : ('kBDT-boostType=Grad-ntrees=100-maxdepth=2-shrinkage=0.1', 'lowMassSR', lambda c : c.lowmasse ),
'lowmass-mu' : ('kBDT-boostType=Grad-ntrees=200-maxdepth=1-shrinkage=0.3', 'lowMassSR', lambda c : c.lowmassmu ),
'lowmass-taulep' : ('kBDT-boostType=AdaBoost-ntrees=50-maxdepth=1-shrinkage=0.3', 'lowMassSR', lambda c : c.lowmasstaulep ),
'lowmass-tauhad' : ('kBDT-boostType=Grad-ntrees=50-maxdepth=2-shrinkage=0.3', 'lowMassSR', lambda c : c.lowmasstauhad ),
'lowestmass-e' : ('kBDT-boostType=Grad-ntrees=75-maxdepth=2-shrinkage=0.1', 'lowMassSR', lambda c : c.lowestmasse ),
'lowestmass-mu' : ('kBDT-boostType=Grad-ntrees=75-maxdepth=3-shrinkage=0.1', 'lowMassSR', lambda c : c.lowestmassmu ),
'lowestmass-taulep' : ('kBDT-boostType=Grad-ntrees=25-maxdepth=4-shrinkage=0.3', 'lowMassSR', lambda c : c.lowestmasstaulep ),
'lowestmass-tauhad' : ('kBDT-boostType=Grad-ntrees=50-maxdepth=3-shrinkage=0.1', 'lowMassSR', lambda c : c.lowestmasstauhad ),
}


if not args.makePlots:

    from HNL.Tools.logger import getLogger, closeLogger
    log = getLogger(args.logLevel)

    #
    # Submit subjobs
    #
    if not args.isChild and not args.isTest:
        from HNL.Tools.jobSubmitter import submitJobs

        submitJobs(__file__, ('sample', 'subJob'), jobs, argParser, jobLabel = 'checkMVAeff')
        exit(0)

    output_name = lambda typ : os.path.join(output_base, 'tmp_'+args.sample, args.sample+'_'+typ+'_subJob{0}.root'.format(args.subJob))

    from HNL.Tools.histogram import Histogram
    from HNL.Tools.ROC import ROC
    from HNL.Tools.helpers import progress
    from HNL.TMVA.mvaDefinitions import MVA_dict
    from ROOT import TChain
    import numpy as np   
 
    def getMVAdistributions(input_handler, sample_name, channel, region, eras, cut_string, custom_mva_dict):
        is_signal = 'mass' in sample_name
        
        sample_tree = input_handler.getTree(sample_name if is_signal else input_handler.signal_names[0], name = channel+'/trainingtree', specific_sample = sample_name)

        sample_tree.selection='default'
        print "Filling ", sample_name
        print "     loading", channel
        list_of_hist = {}
        list_of_roc = {}
        workingpoints = [str(x) for x in np.arange(-1., 1.01, 0.01)]
        readers = {}
        from HNL.TMVA.reader import Reader
        for mva in input_handler.signal_names:
            reduced_cutstring = 'full' if cut_string is None else "".join(i for i in cut_string if i not in "\/:*?<>|& ")
            reduced_cutstring_forpath = 'fullloose' if reduced_cutstring == 'full' and args.region == 'lowMassSRloose' else reduced_cutstring
            path_to_use = os.path.join(os.path.expandvars('$CMSSW_BASE'), 'src', 'HNL', 'TMVA', 'data', 'training',
                                                eras+'all', region+'-'+args.selection, reduced_cutstring, mva, 'kBDT',
                                                'weights', 'factory_'+custom_mva_dict[reduced_cutstring_forpath][mva][0]+'.weights.xml')
            readers[mva] = Reader(sample_tree, 'kBDT', mva, region, eras, path_to_weights=path_to_use, cut_string = cut_string)
            list_of_hist[mva] = Histogram(mva, MVA_dict[region][mva][2], ('MVA score', 'Events'),  np.arange(-1., 1.1, 0.1))
            list_of_roc[mva] = ROC(mva, output_name('ROC'), working_points = workingpoints)
   
        nentries = sample_tree.GetEntries()
        event_range = getEventRange(nentries, args.subJob) 
        for entry in event_range:
            progress(entry, nentries)
            sample_tree.GetEntry(entry)
            if not cut_string_dict[region](sample_tree): continue
            for reader in readers:
                readers[reader].predictAndWriteToChain(sample_tree, trainingnames=True)
                list_of_hist[reader].fill(sample_tree, sample_tree.event_weight)
    
                passed_workingpoints = [getattr(sample_tree, "".join(i for i in reader if i not in "-")) > float(wp) for wp in workingpoints]
                weight = sample_tree.event_weight
    #            if sample_name == 'nonprompt': weight *= getattr(sample_tree, 'fake_weight_{0}'.format(region))

                if is_signal:
                    list_of_roc[reader].fillEfficiency(passed_workingpoints, [weight]*len(workingpoints))
                else:
                    list_of_roc[reader].fillMisid(passed_workingpoints, [weight]*len(workingpoints))
    
        return list_of_hist, list_of_roc
    
    
    dict_of_hist = {}
    dict_of_hist['NoTau'] = getMVAdistributions(ih, args.sample, 'NoTau', args.region, eras, args.cutString, custom_mva_dicts)
    dict_of_hist['SingleTau'] = getMVAdistributions(ih, args.sample, 'SingleTau', args.region, eras, args.cutString, custom_mva_dicts)
    for isignal, signal in enumerate(ih.signal_names):
        channel_of_choice = 'SingleTau' if 'tauhad' in signal else 'NoTau'
        dict_of_hist[channel_of_choice][0][signal].write(output_name('hist'), append = isignal > 0)
        dict_of_hist[channel_of_choice][1][signal].write(append = isignal > 0)

    closeLogger(log)

else:
    import glob
    in_files = glob.glob(output_base)
    from HNL.Tools.mergeFiles import merge
    from HNL.Tools.histogram import Histogram
    from HNL.Tools.helpers import getObjFromFile
    from HNL.Tools.ROC import ROC
    from HNL.Plotting.plot import Plot
    merge(in_files, __file__, jobs, ('sample, subJob'), argParser, istest = args.isTest)

    os.system('hadd -f '+output_base+'/ROC.root '+' '.join([output_base + '/ROC-'+x+'.root' for x in ih.background_names]))

    plot_output = os.path.join(output_base.split('/checkMVAefficiencyInFullSelectionV2/')[0], 'Results/checkMVAefficiencyInFullSelectionV2', output_base.split('/checkMVAefficiencyInFullSelectionV2/')[1])

    for signal in ih.signal_names:
        roc = ROC(signal, output_base + '/ROC.root')
        signal_roc = ROC(signal, output_base+'/ROC-'+signal+'.root') 
        roc.add(signal_roc)       
        g = roc.returnGraph(no_error_bars=True)
        # g.RemovePoint(20)
        auc = roc.getAUC()
        from HNL.Plotting.plottingTools import extraTextFormat
        extra_text = [extraTextFormat('AUC: '+str(auc), xpos = 0.2, ypos = 0.32, textsize = 1.2, align = 12)]  #Text to display event type in plot

        p = Plot(g, signal, signal+'_ROC', '1 - misid', 'efficiency', extra_text=extra_text, year = args.year, era = eras)
        p.drawGraph(output_dir = plot_output)

        
        bkgr_hist = []
        bkgr_names = []
        for bkgr in ih.background_names:
            if bkgr == 'ZZ-H': continue
            bkgr_hist.append(Histogram(getObjFromFile(output_base+'/hist-'+bkgr+'.root', signal)))
            bkgr_names.append(bkgr)

        signal_hist = Histogram(getObjFromFile(output_base+'/hist-'+signal+'.root', signal))
        p = Plot(signal_hist, [signal]+bkgr_names, signal+'_hist', bkgr_hist = bkgr_hist, y_log = False, year = args.year, era=eras,
                                    color_palette = 'Didar', color_palette_bkgr = 'HNLfromTau', x_name = 'output score', y_name = 'events')
        p.drawHist(output_dir = plot_output, normalize_signal=True)
