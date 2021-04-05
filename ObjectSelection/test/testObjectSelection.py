import ROOT

in_file = ROOT.TFile('/pnfs/iihe/cms/store/user/wverbeke/heavyNeutrino/DYJetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/crab_MiniAOD2016v3_ext1-v2_singlelepton_MC_2016_iTuple/200429_093839/0000/singlelep_12.root')
tree = in_file.Get('blackJackAndHookers/blackJackAndHookersTree')
        
from HNL.ObjectSelection.objectSelection import getObjectSelection
tree.obj_sel = getObjectSelection('Luka') #Working points are set in controlRegionManager.py
from HNL.ObjectSelection.leptonSelector import isGoodLepton

for entry in xrange(10000):
    if entry != 4632: continue
    tree.GetEntry(entry)

    tree.year = 2016
    print entry

    for l in xrange(tree._nLight):
        if not isGoodLepton(tree, l, 'loose'): continue
        # print 'loose', tree._lPt[l]
        print 'is muon?', 1 if tree._lFlavor[l] == 1 else 0
        print tree._lPtCorr[l], tree._lPt[l]
        print 'loose'
        if isGoodLepton(tree, l, 'FO'):     print 'FO'
        if isGoodLepton(tree, l, 'tight'):  print 'tight'

    