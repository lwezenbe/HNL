import ROOT
import os
from HNL.Tools.helpers import makeDirIfNeeded, rootFileContent, getObjFromFile, sortByOtherList, progress
from HNL.TMVA.reader import Reader
from HNL.Plotting.plottingTools import extraTextFormat

import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('--year',     action='store',      default=None,   help='Select year', choices=['2016', '2017', '2018', 'all'])
argParser.add_argument('--gui',     action='store_true',      default=False,   help='Open GUI at the end')
argParser.add_argument('--plots',     action='store_true',      default=False,   help='Store plots')
argParser.add_argument('--region', action='store', default='baseline', type=str,  help='What region do you want to select for?', 
    choices=['baseline', 'lowMassSR', 'highMassSR'])
argParser.add_argument('--selection',   action='store', default='default',  help='Select the type of selection for objects', choices=['leptonMVAtop', 'AN2017014', 'default', 'Luka', 'TTT'])
args = argParser.parse_args()

ROOT.gROOT.SetBatch(True)

from HNL.TMVA.inputHandler import InputHandler
ih = InputHandler(args.year, args.region, args.selection)

import uproot
import itertools
from HNL.Plotting.plot import Plot
from fpdf import FPDF
import random

def fillRandGraph(in_graph, npoints):
    new_graph = ROOT.TGraph(npoints)
    npoints_ingraph = in_graph.GetN()
    for x in xrange(1, npoints+1):
        rand_index = random.randint(0, npoints_ingraph)
        new_graph.SetPoint(x, in_graph.GetX()[rand_index], in_graph.GetY()[rand_index])
    return new_graph

#
# List the input variables here
#
from HNL.TMVA.mvaVariables import getVariableList


for signal in ih.signal_names:

    print 'Processing', signal 

    out_file_name = os.path.expandvars(os.path.join('$CMSSW_BASE', 'src', 'HNL', 'TMVA', 'data', 'training', args.year, args.region+'-'+args.selection, signal, signal+'.root'))

    in_file = ROOT.TFile(out_file_name, 'read')
    subdir = rootFileContent(in_file, starting_dir=os.path.join('data', 'training', args.year, args.region+'-'+args.selection, signal, 'kBDT'))
    subdir = [s[0] for s in subdir if 'Method_' in s[0]]
    subdir = [s+'/'+s.split('Method_')[-1] for s in subdir]
    in_file.Close()

    test_tree_file = uproot.open(out_file_name)
    split_subdir = subdir[0].rsplit('/', 2)[0].split('/')
    test_tree = test_tree_file['data']['training'][split_subdir[3]][split_subdir[4]][split_subdir[5]][split_subdir[6]]['TestTree'].arrays()

    print 'Making ROC curves'
    mnames = []
    ROCs = {}
    class_id = ROOT.vector('bool')()
    for s in subdir:
        mname = s.rsplit('/', 1)[-1]
        mnames.append(mname)

    mva_output = {mname : ROOT.vector('float')() for mname in mnames}
    class_id = ROOT.vector('bool')()
    weight = ROOT.vector('float')()
    for i in xrange(len(test_tree['classID'])):
        class_id.push_back(not test_tree['classID'][i])
        weight.push_back(test_tree['weight'][i])
        for mname in mnames:
            mva_output[mname].push_back(test_tree[mname][i])
    
    ROC_integrals = []
    for iname, mname in enumerate(mnames):
        progress(iname, len(mnames))
        ROCs[mname] = ROOT.TMVA.ROCCurve(mva_output[mname], class_id, weight)
        ROC_integrals.append(ROCs[mname].GetROCIntegral())
        ROC_curve = ROCs[mname].GetROCCurve()
        ROC_curve = fillRandGraph(ROC_curve, 10)
        extra_text = [extraTextFormat("AUC: "+str(ROCs[mname].GetROCIntegral()))]
        p = Plot(signal_hist = [ROC_curve], tex_names = [mname], name='roc_'+mname, extra_text=extra_text)
        p.drawGraph(output_dir = out_file_name.rsplit('/', 1)[0]+'/kBDT/plots', draw_style="AP")


    print 'Making pdf'
    mnames = sortByOtherList(mnames, ROC_integrals)
    mnames.reverse()
    pdf = FPDF()
    for mname in mnames:
        pdf.add_page()
        pdf.image(os.path.join(out_file_name.rsplit('/', 1)[0], 'kBDT', 'plots', 'roc_'+mname+'.png'),50.,50.,100.,100.)
        pdf.image(os.path.join(out_file_name.rsplit('/', 1)[0], 'kBDT', 'plots', 'overtrain_'+mname+'.png'),50.,150.,100.,100.)
    pdf.output(out_file_name.rsplit('.', 1)[0]+".pdf", "F")