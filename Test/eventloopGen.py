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

def matches(chain, lumi, evtnb):
    if chain._lumiBlock != lumi: return False
    if chain._eventNb != evtnb: return False
    return True


from ROOT import TChain
chain = TChain('blackJackAndHookers/blackJackAndHookersTree')
import glob
#paths = glob.glob('/pnfs/iihe/cms/store/user/lwezenbe/heavyNeutrino/230427_142455/localSubmission_test-v2/20230713_153253/0000/*.root')
paths = glob.glob('/pnfs/iihe/cms/store/user/joknolle/hnltuples/HNL3l_displaced_nomadspin_M20p0_Vsq1p0em06_e_LO_230810_120749_Run2SIM_UL2018MiniAOD_230810_200715_v4/230821_124759/*root')
for p in paths:
    chain.Add(p)



cutter = Cutter('test', chain, range(1, 40), [1])
#Start a loop over samples
#
# Load in sample and chain
#
chain.HNLmass = 30 

slm = SignalLeptonMatcher(chain)

def getCategory(chain):
    if chain.l_flavor.count(1) != 2 or chain.l_flavor.count(0) != 1: return -1.
    if chain.l_flavor[2] != 0: 
        print 'WHAT', chain.entry
        return -1.

    #Case 1
    if chain.l_charge[0] == 1 and chain.l_charge[1] == -1 and chain.l_charge[2] == 1: return 0
    #Case 2
    if chain.l_charge[0] == 1 and chain.l_charge[1] == 1 and chain.l_charge[2] == -1: return 1
    #Case 3
    if chain.l_charge[0] == -1 and chain.l_charge[1] == -1 and chain.l_charge[2] == 1: return 2
    #Case 4
    if chain.l_charge[0] == -1 and chain.l_charge[1] == 1 and chain.l_charge[2] == -1: return 3

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




n1=0.
n2=0.
n3=0.
n4=0.
#
# comparison with ewkino
#
# print chain.GetEntries()
event_range = xrange(200)
#event_range = xrange(chain.GetEntries())
for entry in event_range:
    #if entry != 68: continue
    #chain.Show(entry)

    chain.GetEntry(entry)
    progress(entry, len(event_range))
    chain.entry = entry
    chain.lumiweight = 1.
    chain.category = 1.
    chain.searchregion = 1.
    slm.initEvent()
    if not selectGenLeptonsGeneral(chain, chain, 3, cutter): continue
    slm.matchSelectedLeptons()
    if slm.l1 is None or slm.l2 is None or slm.l3 is None: continue
    slm.saveNewOrder()
    #print chain.l_flavor
    
    category = getCategory(chain)
    if category < 0: continue

    print entry, category

    if category == 0:
        n1 += 1
    if category == 1:
        n2 += 1
    if category == 2:
        n3 += 1
    if category == 3:
        n4 += 1

    #if category == 5:
    #    print entry

print 'OSSF:', n1, '+', n4, '=', n1 + n4
print 'no OSSF:', n2, '+', n3, '=', n2 + n3
