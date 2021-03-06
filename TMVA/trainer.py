import ROOT
import os
from HNL.Tools.helpers import makeDirIfNeeded

import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('--year',     action='store',      default=None,   help='Select year', choices=['2016', '2017', '2018'])
argParser.add_argument('--gui',     action='store_true',      default=False,   help='Open GUI at the end')
argParser.add_argument('--plots',     action='store_true',      default=False,   help='Store plots')
argParser.add_argument('--skipTraining',     action='store_true',      default=False,   help='Store plots')
args = argParser.parse_args()

ROOT.gROOT.SetBatch(True)

from HNL.TMVA.inputHandler import InputHandler
ih = InputHandler(os.path.expandvars(os.path.join('$CMSSW_BASE', 'src', 'HNL', 'TMVA', 'data', 'InputLists', args.year+'.conf')))

#
# List the input variables here
#
from HNL.TMVA.mvaVariables import getVariableList

print "CHECK IF SOMETHING IS WRONG IN SKIMMER, WE WENT FROM INPUT_FILES WITH 35.5MB TO 14 MB"

for signal in ih.signal_names:

	print 'Processing', signal 

	input_var = getVariableList(signal)

	out_file_name = os.path.expandvars(os.path.join('$CMSSW_BASE', 'src', 'HNL', 'TMVA', 'data', 'training', args.year, signal, signal+'.root'))

	if not args.skipTraining:
		makeDirIfNeeded(out_file_name)
		out_file = ROOT.TFile(out_file_name, 'RECREATE') 
		factory = ROOT.TMVA.Factory("factory", out_file,"")

		loader = ih.getLoader(signal, input_var, args.year)

		preselection = ROOT.TCut("")
		# options = ""
		options = "nTrain_Signal="+str(700)+':nTrain_Background='+str(4000)+ "nTest_Signal="+str(100)+ "nTest_Background="+str(500)
		if ih.numbers is not None:
			n_train_s = ih.numbers[0] 
			n_train_b = ih.numbers[1] 
			n_test_s = ih.numbers[2] 
			n_test_b = ih.numbers[3]
			options = "nTrain_Signal="+str(n_train_s)+':nTrain_Background='+str(n_train_b)+ "nTest_Signal="+str(n_test_s)+ "nTest_Background="+str(n_test_b)
		loader.PrepareTrainingAndTestTree(preselection, options)

		factory.BookMethod(loader, ROOT.TMVA.Types.kBDT, 'kBDT', "")

		factory.TrainAllMethods()
		factory.TestAllMethods()
		factory.EvaluateAllMethods()

		out_file.Close()

	if args.plots:
		ROOT.gROOT.SetBatch(True)
		ROOT.TMVA.variables('data/training/'+str(args.year)+'/'+signal+'/kBDT', out_file_name)
		ROOT.TMVA.correlationscatters('data/training/'+str(args.year)+'/'+signal+'/kBDT', out_file_name)
		ROOT.TMVA.correlations('data/training/'+str(args.year)+'/'+signal+'/kBDT', out_file_name)
		ROOT.TMVA.mvas('data/training/'+str(args.year)+'/'+signal+'/kBDT', out_file_name)
		# ROOT.TMVA.mvaeffs('data/training/'+str(args.year)+'/'+signal+'/kBDT', out_file_name)
		ROOT.TMVA.efficiencies('data/training/'+str(args.year)+'/'+signal+'/kBDT', out_file_name)
		ROOT.TMVA.paracoor('data/training/'+str(args.year)+'/'+signal+'/kBDT', out_file_name)

	### open gui
	if args.gui:
		if(not ROOT.gROOT.IsBatch()):
			ROOT.TMVA.TMVAGui(out_file_name)
		raw_input("Press enter to exit...")



	
