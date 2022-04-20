import ROOT
import os
from HNL.Tools.helpers import makeDirIfNeeded
from HNL.Tools.jobSubmitter import submitJobs, getSubmitArgs

import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
submission_parser = argParser.add_argument_group('submission', 'Arguments for submission. Any arguments not in this group will not be regarded for submission.')
submission_parser.add_argument('--isChild',  action='store_true', default=False,  help='mark as subjob, will never submit subjobs by itself')
submission_parser.add_argument('--year',     action='store',       default=None,   help='Select year. Enter "all" for all years', required=True)
submission_parser.add_argument('--era',     action='store',   nargs='*',   default=None, choices = ['UL', 'prelegacy'],   help='Select era')
submission_parser.add_argument('--region', action='store', default='baseline', type=str,  help='What region do you want to select for?', 
    choices=['baseline', 'lowMassSR', 'lowMassSRloose', 'highMassSR'])
submission_parser.add_argument('--selection',   action='store', default='default',  help='Select the type of selection for objects', choices=['leptonMVAtop', 'AN2017014', 'default', 'Luka', 'TTT'])
submission_parser.add_argument('--signalname',   action='store', default=None,  help='Signal name')
submission_parser.add_argument('--batchSystem', action='store',         default='foreground',  help='choose batchsystem', choices=['local', 'HTCondor', 'foreground'])
submission_parser.add_argument('--dryRun',   action='store_true', default=False,  help='do not launch subjobs, only show them')
submission_parser.add_argument('--dummy',   action='store', default=None,  help='do not launch subjobs, only show them')
submission_parser.add_argument('--cutString',   action='store', default=None,  help='Additional cutstrings for training')
submission_parser.add_argument('--isTest',   action='store_true', default=False,  help='do not launch subjobs, only show them')
submission_parser.add_argument('--checkTreeContent',   action='store_true', default=False,  help='do not launch subjobs, only show them')

argParser.add_argument('--writeInTree',   action='store_true', default=False,  help='Write out the tree used for training to be able to analyze it')
argParser.add_argument('--gui',     action='store_true',      default=False,   help='Open GUI at the end')
argParser.add_argument('--plots',     action='store_true',      default=False,   help='Store plots')
argParser.add_argument('--plotDetailedMVA',     action='store_true',      default=False,   help='Store plots')
argParser.add_argument('--saveTrainings',     action='store',      default=None,   help='Store MVA for use in other portions of the code. Should always be of the form "<era>/<region>"')
argParser.add_argument('--skipTraining',     action='store_true',      default=False,   help='Store plots')

args = argParser.parse_args()

ROOT.gROOT.SetBatch(True)

if args.checkTreeContent or args.plots or args.saveTrainings: 
    args.skipTraining = True

from HNL.TMVA.inputHandler import InputHandler
eras = "-".join(sorted(args.era))

ih = InputHandler(eras, args.year, args.region, args.selection)

ntrees = ih.NTREES
maxdepth = ih.MAXDEPTH
boosttypes = ih.BOOSTTYPES
shrinkage = ih.SHRINKAGE
 
def getOutFileName(eras, signal_name):
    if args.cutString is None:
        return os.path.expandvars(os.path.join('$CMSSW_BASE', 'src', 'HNL', 'TMVA', 'data', 'training', eras+args.year, 
                                                            args.region+'-'+args.selection, 'full', signal_name, signal_name+'.root'))
    else:
        out_cut_str = "".join(i for i in args.cutString if i not in " &\/:*?<>|")
        return os.path.expandvars(os.path.join('$CMSSW_BASE', 'src', 'HNL', 'TMVA', 'data', 'training', eras+args.year, 
                            args.region+'-'+args.selection, out_cut_str, signal_name, signal_name+'.root'))        


if not any([args.isChild, args.plots, args.plotDetailedMVA, args.saveTrainings]):
    if args.batchSystem != 'foreground': 
        jobs = []
        for signal in ih.signal_names:
            jobs += [(signal, '0')]
        submitJobs(__file__, ('signalname', 'dummy'), jobs, argParser, jobLabel = 'TMVAtrainer'+args.region)
    else:
        args.isChild = True
        submitArgs = getSubmitArgs(argParser, args)
        for signal in ih.signal_names:
            if args.signalname is not None and signal != args.signalname: continue
            command = 'python trainer.py'
            for arg, value in submitArgs.iteritems():
                if value == False:
                    continue
                elif isinstance(value, list):
                    command += ' ' + '--' + arg + ' ' + ' '.join([str(x) for x in sorted(value)])
                elif arg == 'cutString':
                    command += ' ' + '--' + arg + '="' + str(value) +'"'
                else:
                    command += ' ' + '--' + arg + '=' + str(value)
            command += ' --signalname='+signal
            command = command.replace('=True','')
            if args.isTest or args.checkTreeContent:
                os.system(command)
            else:
                makeDirIfNeeded(getOutFileName(eras, signal))
                os.system(command + ' > '+getOutFileName(eras, signal).split('.root')[0]+'.txt')
    exit(0)

#
# List the input variables here
#
from HNL.TMVA.mvaVariables import getVariableList

print 'Processing', args.signalname

if args.checkTreeContent:
    if 'had' in args.signalname:
        channel = 'SingleTau'
    else:
        channel = 'NoTau'
    in_tree = ih.getTree(args.signalname, name = channel+'/trainingtree')

    additional_cut_str = ih.getAdditionalCutString(args.cutString)
    nsignal = in_tree.Draw("1", "is_signal"+additional_cut_str)
    nbkgr = in_tree.Draw("1", "!is_signal"+additional_cut_str)

    print "FOR SIGNAL NAME", args.signalname
    print "Number of signal events:", nsignal
    print "Total number of bkgr events:", nbkgr
    print "Breakdown of all backgrounds:"
    ih.getReportOnBackgrounds(channel=channel, cut_string = args.cutString if args.cutString is not None else "")

if not args.skipTraining:
    input_var = getVariableList(args.signalname, args.cutString)
    print input_var

    makeDirIfNeeded(getOutFileName(eras, args.signalname))
    out_file = ROOT.TFile(getOutFileName(eras, args.signalname), 'RECREATE') 
    factory = ROOT.TMVA.Factory("factory", out_file,"")


    if args.writeInTree:
        if args.signalname.split('_')[-1] in ['e', 'mu']:
            name = 'NoTau/trainingtree'
        else:
            name = 'Total/trainingtree'
        in_tree = ih.getTree(args.signalname, name=name).CloneTree()
        in_tree.Write('backuptree')

    loader = ih.getLoader(args.signalname, input_var, args.cutString)

    preselection = ROOT.TCut("")
    # options = ""
    options = "nTrain_Signal="+str(700)+':nTrain_Background='+str(4000)+ ":nTest_Signal="+str(100)+ ":nTest_Background="+str(500)
    if ih.numbers is not None:
        n_train_s = ih.numbers[0] if args.signalname.split('-')[0] != 'mediummass85100' else 50000
        n_train_b = ih.numbers[1] 
        n_test_s = ih.numbers[2] 
        n_test_b = ih.numbers[3]
        options = "nTrain_Signal="+str(n_train_s)+':nTrain_Background='+str(n_train_b)+ ":nTest_Signal="+str(n_test_s)+ ":nTest_Background="+str(n_test_b)
    loader.PrepareTrainingAndTestTree(preselection, options)

    # factory.BookMethod(loader, ROOT.TMVA.Types.kBDT, 'kBDT', "NegWeightTreatment=NoNegWeightsInTraining:NTrees=200:MaxDepth=3:BoostType=Grad:Shrinkage=0.3")
    for nt in ntrees:
        for md in maxdepth:
            for bt in boosttypes:
                for s in shrinkage:
                    factory.BookMethod(loader, ROOT.TMVA.Types.kBDT, 'kBDT-boostType={0}-ntrees={1}-maxdepth={2}-shrinkage={3}'.format(bt, nt, md, s), 
                                        "NegWeightTreatment=NoNegWeightsInTraining:NTrees={0}:MaxDepth={1}:BoostType={2}:Shrinkage={3}".format(nt, md, bt, s))
    # factory.BookMethod(loader, ROOT.TMVA.Types.kBDT, 'kBDT-2', "NegWeightTreatment=NoNegWeightsInTraining:NTrees=300:MaxDepth=3:BoostType=Grad:Shrinkage=0.1")

    factory.TrainAllMethods()
    factory.TestAllMethods()
    factory.EvaluateAllMethods()

    out_file.Close()


if args.plots:
    for signal in ih.signal_names:
        if args.signalname is not None and signal != args.signalname: continue
        print("Plotting...", signal)
        starting_dir = os.path.join(getOutFileName(eras, signal).rsplit('/', 1)[0], 'kBDT').split('/TMVA/')[1]
        ROOT.gROOT.SetBatch(True)
        ROOT.TMVA.variables(starting_dir, getOutFileName(eras, signal))
        ROOT.TMVA.correlationscatters(starting_dir, getOutFileName(eras, signal))
        ROOT.TMVA.correlations(starting_dir, getOutFileName(eras, signal))
        ROOT.TMVA.mvas(starting_dir, getOutFileName(eras, signal))
        # ROOT.TMVA.mvas(starting_dir, getOutFileName(signal), 1)
        # ROOT.TMVA.mvas(starting_dir, getOutFileName(signal), 2)
        ROOT.TMVA.mvas(starting_dir, getOutFileName(eras, signal), 3)
        ROOT.TMVA.efficiencies(starting_dir, getOutFileName(eras, signal))
        # ROOT.TMVA.paracoor(starting_dir, getOutFileName(signal))
        # ROOT.TMVA.bdtcontrolplots(starting_dir, getOutFileName(signal))

        ### open gui
        if args.gui:
            if(not ROOT.gROOT.IsBatch()):
                ROOT.TMVA.TMVAGui(getOutFileName(eras, signal))
            raw_input("Press enter to exit...")
        
if args.plotDetailedMVA:
    from HNL.TMVA.reader import getAllMVAhist, getNonPromptMVAhist
    from HNL.Plotting.plot import Plot

    dict_of_hist = {}
    dict_of_hist['NoTau'] = getAllMVAhist(ih, 'NoTau', args.region, eras, cut_string = args.cutString)
    dict_of_hist['SingleTau'] = getAllMVAhist(ih, 'SingleTau', args.region, eras, cut_string = args.cutString)
    for signal in ih.signal_names:
        channel_of_choice = 'SingleTau' if 'tauhad' in signal else 'NoTau'
        list_of_hist = []
        list_of_names = []
        for sample in dict_of_hist[channel_of_choice].keys():
            list_of_hist.append(dict_of_hist[channel_of_choice][sample][signal])
            list_of_names.append(sample)
        
        p = Plot(list_of_hist, list_of_names, signal, "MVA score", "Events", year='all', era='UL', color_palette='Large')
        p.drawHist(output_dir = getOutFileName(eras, signal).rsplit('/', 1)[0]+'/DetailedPlots', draw_option='Stack')

if args.saveTrainings is not None:
    base_folder = os.path.join(os.path.expandvars('$CMSSW_BASE'), 'src', 'HNL', 'TMVA', 'data', 'FinalTrainings', args.saveTrainings)
    makeDirIfNeeded(os.path.join(base_folder, 'x'))

    confirmation_message = raw_input("This will store the MVA as defined in the reader into the folder to use them in the rest of the code. Have you properly defined those? (y/n) ")
    if confirmation_message not in ['y', 'Y']: exit(0)
    from HNL.TMVA.mvaDefinitions import  MVA_dict

    # Check if there are already weights stored
    existing_files = [signal for signal in ih.signal_names if os.path.isfile(os.path.join(base_folder, signal+'.xml'))]
    if len(existing_files) != 0:
        warning_message = raw_input("Weight files are already defined for: \n \n  "+ '\n'.join(existing_files) + "\n\n Are you sure you want to overwrite these? (y/n) ")
        if warning_message not in ['y', 'Y']: exit(0)

    for signal in ih.signal_names:
        # Open a text file to save information about the training for posterity
        info_file = open(os.path.join(base_folder, signal+'.txt'), 'w')
        info_file.write(' '.join(['eras: \t \t', ' '.join(args.era), '\n']))
        info_file.write(' '.join(['years: \t \t', args.year, '\n']))
        info_file.write(' '.join(['region: \t \t', args.region, '\n']))
        info_file.write(' '.join(['selection: \t \t', args.selection, '\n']))
        info_file.write(' '.join(['cut string: \t \t', str(args.cutString), '\n']))
        info_file.write(' '.join(['training: \t \t', MVA_dict[args.region][signal][0], '\n']))
        info_file.close()

        #copy the weights file
        os.system('scp '+os.path.join(os.path.expandvars('$CMSSW_BASE'), 'src', 'HNL', 'TMVA', 'data', 'training', 
                            eras+'all', args.region+'-'+args.selection, "".join(i for i in args.cutString if i not in "\/:*?<>|& ") if args.cutString is not None else 'full',
                            signal, 'kBDT', 'weights', 'factory_'+MVA_dict[args.region][signal][0]+'.weights.xml') + ' '
                            + os.path.join(base_folder, signal+'.xml'))

