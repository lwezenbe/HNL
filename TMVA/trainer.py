import ROOT
import os
from HNL.Tools.helpers import makeDirIfNeeded
from HNL.Tools.jobSubmitter import submitJobs, getSubmitArgs

import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
submission_parser = argParser.add_argument_group('submission', 'Arguments for submission. Any arguments not in this group will not be regarded for submission.')
submission_parser.add_argument('--isChild',  action='store_true', default=False,  help='mark as subjob, will never submit subjobs by itself')
submission_parser.add_argument('--year',     action='store',      default=None,   help='Select year', choices=['2016', '2017', '2018', 'all'])
submission_parser.add_argument('--region', action='store', default='baseline', type=str,  help='What region do you want to select for?', 
    choices=['baseline', 'lowMassSR', 'highMassSR'])
submission_parser.add_argument('--selection',   action='store', default='default',  help='Select the type of selection for objects', choices=['leptonMVAtop', 'AN2017014', 'default', 'Luka', 'TTT'])
submission_parser.add_argument('--signalname',   action='store', default=None,  help='Signal name')
submission_parser.add_argument('--batchSystem', action='store',         default='foreground',  help='choose batchsystem', choices=['local', 'HTCondor', 'Cream02', 'foreground'])
submission_parser.add_argument('--dryRun',   action='store_true', default=False,  help='do not launch subjobs, only show them')
submission_parser.add_argument('--dummy',   action='store', default=None,  help='do not launch subjobs, only show them')
submission_parser.add_argument('--isTest',   action='store_true', default=False,  help='do not launch subjobs, only show them')

argParser.add_argument('--writeInTree',   action='store_true', default=False,  help='Write out the tree used for training to be able to analyze it')
argParser.add_argument('--gui',     action='store_true',      default=False,   help='Open GUI at the end')
argParser.add_argument('--plots',     action='store_true',      default=False,   help='Store plots')
argParser.add_argument('--skipTraining',     action='store_true',      default=False,   help='Store plots')

args = argParser.parse_args()

ROOT.gROOT.SetBatch(True)

from HNL.TMVA.inputHandler import InputHandler
ih = InputHandler(args.year, args.region, args.selection)

ntrees = ['100', '200', '300']
maxdepth = ['2', '3', '4']
boosttypes = ['Grad', 'AdaBoost', 'RealAdaBoost']
shrinkage = ['0.1', '0.3', '1']

# ntrees = ['300']
# maxdepth = ['4']
# boosttypes=['RealAdaBoost']
# shrinkage=['0.1']

out_file_name = lambda signal_name : os.path.expandvars(os.path.join('$CMSSW_BASE', 'src', 'HNL', 'TMVA', 'data', 'training', args.year, 
                                                            args.region+'-'+args.selection, signal_name, signal_name+'.root'))


if not args.isChild and not args.plots:
    if args.batchSystem != 'foreground': 
        jobs = []
        for signal in ih.signal_names:
            jobs += [(signal, '0')]
        submitJobs(__file__, ('signalname', 'dummy'), jobs, argParser, jobLabel = 'TMVAtrainer')
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
                    command += ' ' + '--' + arg + '=' + ' '.join([str(x) for x in sorted(value)])
                else:
                    command += ' ' + '--' + arg + '=' + str(value)
            command += ' --signalname='+signal
            command = command.replace('=True','')
            if args.isTest:
                os.system(command)
            else:
                os.system(command + ' > '+out_file_name(signal).split('.root')[0]+'.txt')
    exit(0)

#
# List the input variables here
#
from HNL.TMVA.mvaVariables import getVariableList

print 'Processing', args.signalname 

if not args.skipTraining:
    input_var = getVariableList(args.signalname)

    makeDirIfNeeded(out_file_name(args.signalname))
    out_file = ROOT.TFile(out_file_name(args.signalname), 'RECREATE') 
    factory = ROOT.TMVA.Factory("factory", out_file,"")


    if args.writeInTree:
        if args.signalname.split('_')[-1] in ['e', 'mu']:
            name = 'NoTau/trainingtree'
        else:
            name = 'Total/trainingtree'
        in_tree = ih.getTree(args.signalname, name=name).CloneTree()
        in_tree.Write('backuptree')

    loader = ih.getLoader(args.signalname, input_var)

    preselection = ROOT.TCut("")
    # options = ""
    options = "nTrain_Signal="+str(700)+':nTrain_Background='+str(4000)+ ":nTest_Signal="+str(100)+ ":nTest_Background="+str(500)
    if ih.numbers is not None:
        n_train_s = ih.numbers[0] 
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
        print "Plotting..."
        ROOT.gROOT.SetBatch(True)
        ROOT.TMVA.variables('data/training/'+str(args.year)+'/'+args.region+'-'+args.selection+'/'+signal+'/kBDT', out_file_name(signal))
        ROOT.TMVA.correlationscatters('data/training/'+str(args.year)+'/'+args.region+'-'+args.selection+'/'+signal+'/kBDT', out_file_name(signal))
        ROOT.TMVA.correlations('data/training/'+str(args.year)+'/'+args.region+'-'+args.selection+'/'+signal+'/kBDT', out_file_name(signal))
        ROOT.TMVA.mvas('data/training/'+str(args.year)+'/'+args.region+'-'+args.selection+'/'+signal+'/kBDT', out_file_name(signal))
        # ROOT.TMVA.mvas('data/training/'+str(args.year)+'/'+args.region+'-'+args.selection+'/'+signal+'/kBDT', out_file_name(signal), 1)
        # ROOT.TMVA.mvas('data/training/'+str(args.year)+'/'+args.region+'-'+args.selection+'/'+signal+'/kBDT', out_file_name(signal), 2)
        ROOT.TMVA.mvas('data/training/'+str(args.year)+'/'+args.region+'-'+args.selection+'/'+signal+'/kBDT', out_file_name(signal), 3)
        ROOT.TMVA.efficiencies('data/training/'+str(args.year)+'/'+args.region+'-'+args.selection+'/'+signal+'/kBDT', out_file_name(signal))
        # ROOT.TMVA.paracoor('data/training/'+str(args.year)+'/'+args.region+'-'+args.selection+'/'+signal+'/kBDT', out_file_name(signal))
        # ROOT.TMVA.bdtcontrolplots('data/training/'+str(args.year)+'/'+args.region+'-'+args.selection+'/'+signal+'/kBDT', out_file_name(signal))

        ### open gui
        if args.gui:
            if(not ROOT.gROOT.IsBatch()):
                ROOT.TMVA.TMVAGui(out_file_name(signal))
            raw_input("Press enter to exit...")
        