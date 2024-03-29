import ROOT
import os
from HNL.Tools.helpers import rootFileContent, sortByOtherList, progress, makeDirIfNeeded
from HNL.Plotting.plottingTools import extraTextFormat

import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('--year',     action='store',      default=None,   help='Select year')
argParser.add_argument('--era',     action='store',  nargs='*',     default='prelegacy', choices = ['UL', 'prelegacy'],   help='Select era')
argParser.add_argument('--gui',     action='store_true',      default=False,   help='Open GUI at the end')
argParser.add_argument('--plots',     action='store_true',      default=False,   help='Store plots')
argParser.add_argument('--region', action='store', default='baseline', type=str,  help='What region do you want to select for?', 
    choices=['baseline', 'lowMassSR', 'highMassSR', 'lowMassSRloose'])
argParser.add_argument('--selection',   action='store', default='default',  help='Select the type of selection for objects', choices=['leptonMVAtop', 'AN2017014', 'default', 'Luka', 'TTT'])
argParser.add_argument('--cutString',   action='store', default=None,  help='Additional cutstrings for training')
args = argParser.parse_args()

ROOT.gROOT.SetBatch(True)
ROOT.gROOT.ProcessLine( "gErrorIgnoreLevel = 1001;")

eras = "-".join(sorted(args.era))

from HNL.TMVA.inputHandler import InputHandler
ih = InputHandler(eras, args.year, args.region, args.selection)

import uproot
from HNL.Plotting.plot import Plot
from fpdf import FPDF
import random

def fillRandGraph(in_graph, npoints):
    new_graph = ROOT.TGraph(npoints)
    npoints_ingraph = in_graph.GetN()
    for x in xrange(1, npoints+1):
        rand_index = random.randint(0, npoints_ingraph-1)
        new_graph.SetPoint(x, in_graph.GetX()[rand_index], in_graph.GetY()[rand_index])
    return new_graph

for signal in ih.signal_names:

    print 'Processing', signal 

    if args.cutString is None:
        out_file_name = os.path.expandvars(os.path.join('$CMSSW_BASE', 'src', 'HNL', 'TMVA', 'data', 'training', eras+args.year, args.region+'-'+args.selection, 'full', signal, signal+'.root'))
    else:
        out_file_name = os.path.expandvars(os.path.join('$CMSSW_BASE', 'src', 'HNL', 'TMVA', 'data', 'training', eras+args.year, args.region+'-'+args.selection, 
                                                            "".join(i for i in args.cutString if i not in "\/:*?<>|& "), signal, signal+'.root'))

    in_file = ROOT.TFile(out_file_name, 'read')
    starting_dir = os.path.join(out_file_name.rsplit('/', 1)[0], 'kBDT')
    subdir = rootFileContent(in_file, starting_dir=starting_dir.split('/TMVA/')[1])
    subdir = [s[0] for s in subdir if 'Method_' in s[0]]
    subdir = [s+'/'+s.split('Method_')[-1] for s in subdir]
    in_file.Close()

    test_tree_file = uproot.open(out_file_name)
    split_subdir = subdir[0].rsplit('/', 2)[0].split('/')
    if args.cutString is None:
        test_tree = test_tree_file['data']['training'][split_subdir[3]][split_subdir[4]][split_subdir[5]][split_subdir[6]][split_subdir[7]]['TestTree'].arrays()
    else:
        test_tree = test_tree_file['data']['training'][split_subdir[3]][split_subdir[4]][split_subdir[5]][split_subdir[6]][split_subdir[7]]['TestTree'].arrays()

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
        pdf.add_page('L')
        pdf.image(os.path.join(out_file_name.rsplit('/', 1)[0], 'kBDT', 'plots', 'roc_'+mname+'.png'), 40., 50., 100., 100.)
        pdf.image(os.path.join(out_file_name.rsplit('/', 1)[0], 'kBDT', 'plots', 'overtrain_'+mname+'.png'), 150., 50., 100., 100.)
    pdf.output(out_file_name.rsplit('.', 1)[0]+".pdf", "F")
    makeDirIfNeeded('/user/lwezenbe/public_html/HNL/'+out_file_name.split('/HNL/')[1].rsplit('.', 1)[0]+".pdf")
    pdf.output('/user/lwezenbe/public_html/HNL/'+out_file_name.split('/HNL/')[1].rsplit('.', 1)[0]+".pdf", "F")
