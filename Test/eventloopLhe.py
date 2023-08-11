#! /usr/bin/env python

#
# General imports
#
import os
from ROOT import TFile
from HNL.Tools.histogram import Histogram
from HNL.Tools.mergeFiles import merge
from HNL.Tools.helpers import getObjFromFile, progress, makeDirIfNeeded
from HNL.EventSelection.eventCategorization import EventCategory
from HNL.EventSelection.cutter import Cutter
from HNL.Weights.reweighter import Reweighter
from HNL.TMVA.reader import Reader
from HNL.Samples.sampleManager import SampleManager

#prepare object  and event selection
from HNL.ObjectSelection.objectSelection import getObjectSelection
from HNL.ObjectSelection.leptonSelector import isGoodLightLepton
from HNL.EventSelection.eventSelector import EventSelector
from HNL.EventSelection.signalLeptonMatcher import SignalLeptonMatcher
from HNL.EventSelection.eventSelectionTools import selectGenLeptonsGeneral, selectLeptonsGeneral
import numpy as np

def matches(chain, lumi, evtnb):
    if chain._lumiBlock != lumi: return False
    if chain._eventNb != evtnb: return False
    return True


from ROOT import TChain
chain = TChain('blackJackAndHookers/blackJackAndHookersTree')
import glob
#paths = glob.glob('/pnfs/iihe/cms/store/user/lwezenbe/heavyNeutrino/230427_142455/localSubmission_test-v2/20230713_153253/0000/*.root')
#paths = glob.glob('/pnfs/iihe/cms/store/user/lwezenbe/heavyNeutrino/HeavyNeutrino_trilepton_M-30_V-0p01_mu_LO_TuneCP5_13TeV-madgraph-pythia8/localSubmission_test-v2/20230713_153353/0000/*.root')
paths = glob.glob('/pnfs/iihe/cms/store/user/lwezenbe/test/displaced.root')
#paths = glob.glob('/pnfs/iihe/cms/store/user/lwezenbe/test/prompt.root')
#paths = glob.glob('/user/lwezenbe/private/NTuplizer/SignalTester/CMSSW_10_6_27/src/heavyNeutrino/multilep/test/testoutput/prompt_1.root')
#paths = glob.glob('/user/lwezenbe/private/NTuplizer/SignalTester/CMSSW_10_6_27/src/heavyNeutrino/multilep/test/testoutput/rawprompt_1.root')
#paths = glob.glob('/pnfs/iihe/cms/store/user/lwezenbe/heavyNeutrino/230802_164933/localSubmission_test-nofilter/20230803_103440/0000/*root')
#paths = glob.glob('/pnfs/iihe/cms/store/user/lwezenbe/heavyNeutrino/230802_165247/localSubmission_test-nofilter/20230803_103501/0000/*root')
#paths = glob.glob('/pnfs/iihe/cms/store/user/lwezenbe/heavyNeutrino/230803_125117_displacedadapted/localSubmission_test-nofilter/20230803_162254/0000/*root')
#paths = glob.glob('/pnfs/iihe/cms/store/user/lwezenbe/heavyNeutrino/230803_172228_displacedfrankenstein/localSubmission_test-nofilter/20230804_103801/0000/*root')
for p in paths:
    chain.Add(p)



cutter = Cutter('test', chain, range(1, 40), [1])
#Start a loop over samples
#
# Load in sample and chain
#
chain.HNLmass = 30 

def lheParticleHistory(c, index):
    history = [abs(c._lhePdgId[index])]
    while c._lheMother1[index] != -1:
        index = c._lheMother1[index]
        history.append(abs(c._lhePdgId[index]))
    return history

def selectLeptons(chain):
    indices = []
    for l in xrange(chain._nLheParticles):
        if chain._lheStatus[l] != 1:
            continue
        if abs(chain._lhePdgId[l]) in [11, 13]:
            indices.append(l)
    return indices

def selectHNL(chain):
    for l in xrange(chain._nLheParticles):
        if abs(chain._lhePdgId[l]) == 9900012:
            return l

def selectNeutrino(chain, lepton_indices):
    for l in xrange(chain._nLheParticles):
        if chain._lheStatus[l] != 1: continue
        if abs(chain._lhePdgId[lepton_indices[2]]) == 11:
            if abs(chain._lhePdgId[l]) != 12: continue
        if abs(chain._lhePdgId[lepton_indices[2]]) == 13:
            if abs(chain._lhePdgId[l]) != 14: continue
        return l
    

def matchLeptons(chain, indices):
    l1_index = None
    l2_index = None
    l3_index = None
    for l in indices:
        hist = lheParticleHistory(chain, l)
        if not 9900012 in hist and abs(chain._lhePdgId[l]) == 13:
            l1_index = l
        elif abs(chain._lhePdgId[l]) == 13:
            l2_index = l
        else:
            l3_index = l
    if l1_index == l2_index:
        print 'weird'
    if l3_index == l2_index:
        print 'weird'
    if l1_index == l3_index:
        print 'weird'
    
    return l1_index, l2_index, l3_index

def getCategory(chain, indices):
    #Case 1
    if np.sign(chain._lhePdgId[indices[0]]) == -1 and np.sign(chain._lhePdgId[indices[1]]) == 1 and np.sign(chain._lhePdgId[indices[2]]) == -1: return 0
    #Case 2
    if np.sign(chain._lhePdgId[indices[0]]) == -1 and np.sign(chain._lhePdgId[indices[1]]) == -1 and np.sign(chain._lhePdgId[indices[2]]) == 1: return 1
    #Case 3
    if np.sign(chain._lhePdgId[indices[0]]) == 1 and np.sign(chain._lhePdgId[indices[1]]) == 1 and np.sign(chain._lhePdgId[indices[2]]) == -1: return 2
    #Case 4
    if np.sign(chain._lhePdgId[indices[0]]) == 1 and np.sign(chain._lhePdgId[indices[1]]) == -1 and np.sign(chain._lhePdgId[indices[2]]) == 1: return 3

    return 4

#def assignL1to3(chain, slm):
#    for l in chain.l_indices:
#        if abs(chain._gen_lMomPdg[l] != 9900012):
#            slm.l1 = l
#        elif chain._gen_lFlavor[l] == 1:
#            slm.l2 = l
#        elif chain._gen_lFlavor[l] == 0:
#            slm.l3 = l
#        else:
#            print 'stranger danger'
#            


#chain.Show(3249)

n1=0.
n2=0.
n3=0.
n4=0.

n1Dirac = 0.
n2Dirac = 0.
n3Dirac = 0.
n4Dirac = 0.

tot_dirac_0 = 0.
tot_dirac_1 = 0.
tot_dirac_2 = 0.
tot_dirac_3 = 0.

cutflow_1 = 0.
cutflow_2 = 0.
cutflow_3 = 0.

reco = 0.
reco_ossf = 0.
reco_nossf = 0.
tot_dirac_reco = 0.

tightlep = 0.
tightlep_ossf = 0.
tightlep_nossf = 0.
tot_dirac_tightlep = 0.

#Output hist
from HNL.Tools.outputTree import OutputTree
branches = []
branches.extend(['ctauHN/F'])
branches.extend(['HNLpt/F'])
branches.extend(['HNLmass/F'])
branches.extend(['combinedMassl1l2nu/F'])
branches.extend(['l1pt/F', 'l2pt/F', 'l3pt/F'])
branches.extend(['isLNC/F'])
output_tree = OutputTree('events', 'data/eventLoopLhe/events.root', branches = branches, branches_already_defined = False)

#
# comparison with ewkino
#
print chain.GetEntries()
event_range = xrange(28000)
#event_range = xrange(chain.GetEntries())
for entry in event_range:
    #if entry != 151: continue
    #chain.Show(entry)

    chain.GetEntry(entry)
    progress(entry, len(event_range))


#    if chain._eventNb == 185941:
#        print entry
#    else:
#        continue

    indices = selectLeptons(chain)
    if chain._gen_isDiracType: tot_dirac_0 += 1.
    if len(indices) != 3: continue
    cutflow_1 += 1.
    indices = matchLeptons(chain, indices)
    if chain._gen_isDiracType: tot_dirac_1 += 1.
    if indices.count(None) > 0: continue
    cutflow_2 += 1.
 
    category = getCategory(chain, indices)
    if chain._gen_isDiracType: tot_dirac_2 += 1.
    if category < 0: continue
    if chain._gen_isDiracType: tot_dirac_3 += 1.
    cutflow_3 += 1.


    output_tree.setTreeVariable('ctauHN', chain._ctauHN)
    hnl_index = selectHNL(chain)
    output_tree.setTreeVariable('HNLpt', chain._lhePt[hnl_index])
    import ROOT
    HNL_vector = ROOT.Math.PtEtaPhiEVector(chain._lhePt[hnl_index], chain._lheEta[hnl_index], chain._lhePhi[hnl_index], chain._lheE[hnl_index])
    output_tree.setTreeVariable('HNLmass', HNL_vector.M())
    l1_vector = ROOT.Math.PtEtaPhiEVector(chain._lhePt[indices[0]], chain._lheEta[indices[0]], chain._lhePhi[indices[0]], chain._lheE[indices[0]])
    l2_vector = ROOT.Math.PtEtaPhiEVector(chain._lhePt[indices[1]], chain._lheEta[indices[1]], chain._lhePhi[indices[1]], chain._lheE[indices[1]])
    l3_vector = ROOT.Math.PtEtaPhiEVector(chain._lhePt[indices[2]], chain._lheEta[indices[2]], chain._lhePhi[indices[2]], chain._lheE[indices[2]])
    neutrino_index = selectNeutrino(chain, indices)
    nu_vector = ROOT.Math.PtEtaPhiEVector(chain._lhePt[neutrino_index], chain._lheEta[neutrino_index], chain._lhePhi[neutrino_index], chain._lheE[neutrino_index])

    tot_vec = l2_vector+l3_vector+nu_vector
    output_tree.setTreeVariable('combinedMassl1l2nu', tot_vec.M())
    
    output_tree.setTreeVariable('l1pt', chain._lhePt[indices[0]])
    output_tree.setTreeVariable('l2pt', chain._lhePt[indices[1]])
    output_tree.setTreeVariable('l3pt', chain._lhePt[indices[2]])
    output_tree.setTreeVariable('isLNC', category in [0, 3])
    output_tree.fill()

    if category == 0:
        n1 += 1
        if chain._gen_isDiracType: n1Dirac += 1.
    if category == 1:
        n2 += 1
        if chain._gen_isDiracType: n2Dirac += 1.
    if category == 2:
        n3 += 1
        if chain._gen_isDiracType: 
            n3Dirac += 1.
 #           print entry
    if category == 3:
        n4 += 1
        if chain._gen_isDiracType: n4Dirac += 1.


    from HNL.Triggers.triggerSelection import passTriggers
    from HNL.EventSelection.eventSelectionTools import selectGenLeptonsGeneral
    chain.category = 1.
    chain.searchregion = 1.
    chain.met = chain._met
    chain.metPhi = chain._metPhi
    chain.selection = 'default'
    chain.strategy = 'MVA'
    chain.era = 'UL'
    chain.year = '2018'
    chain.need_sideband = None
    chain.is_data = False
    if not passTriggers(chain, 'HNL'): continue
    from HNL.ObjectSelection.objectSelection import getObjectSelection
    chain.obj_sel = getObjectSelection('default')
    if not selectLeptonsGeneral(chain, chain, 3, cutter): 
        #print entry
        continue
    tightlep += 1.

    from HNL.EventSelection.eventSelectionTools import calculateThreeLepVariables
    calculateThreeLepVariables(chain, chain, is_reco_level=True)
    if chain._gen_isDiracType: tot_dirac_tightlep += 1.
    from HNL.EventSelection.eventSelectionTools import containsOSSF
    if containsOSSF(chain):
        tightlep_ossf += 1.
    else:
        tightlep_nossf += 1.
    from HNL.EventSelection.eventFilters import passBaseCuts, passLowMassSelection
    if not passBaseCuts(chain, chain, cutter): continue
    if not passLowMassSelection(chain, chain, cutter, loose_selection=True):    continue
    reco += 1.
    if chain._gen_isDiracType: tot_dirac_reco += 1.
    from HNL.EventSelection.eventSelectionTools import containsOSSF
    if containsOSSF(chain):
        reco_ossf += 1.
    else:
        reco_nossf += 1.
    
    #if category == 5:
    #    print entry

output_tree.write(is_test = None, append = False)

print 'OSSF:', n1, '+', n4, '=', n1 + n4
print 'no OSSF:', n2, '+', n3, '=', n2 + n3

print n1Dirac
print n2Dirac
print n3Dirac
print n4Dirac

print 'All Dirac:', tot_dirac_0, 'out of', len(event_range), '({0})'.format(tot_dirac_0/len(event_range))
print 'All Dirac (step 1):', tot_dirac_1, 'out of', cutflow_1, '({0})'.format(tot_dirac_1/cutflow_1)
print 'All Dirac (step 2):', tot_dirac_2, 'out of', cutflow_2, '({0})'.format(tot_dirac_2/cutflow_2)
print 'All Dirac (step 3):', tot_dirac_3, 'out of', cutflow_3, '({0})'.format(tot_dirac_3/cutflow_3)
print 'All Dirac (tight lep):', tot_dirac_tightlep, 'out of', tightlep, '({0})'.format(tot_dirac_tightlep/tightlep)
print 'All Dirac (reco):', tot_dirac_reco, 'out of', reco, '({0})'.format(tot_dirac_reco/reco)

print 'cutflow:', len(event_range), '->', cutflow_1, '->', cutflow_2, '->', cutflow_3 
print 'tightlep', tightlep
print 'ossf', tightlep_ossf
print 'nossf', tightlep_nossf
print 'reco', reco
print 'ossf', reco_ossf
print 'nossf', reco_nossf
