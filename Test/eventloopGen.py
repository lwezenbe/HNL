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
chain.Add('/storage_mnt/storage/user/lwezenbe/private/NTuplizer/SignalTester/CMSSW_10_6_27/src/heavyNeutrino/multilep/test/noskim.root')

#Start a loop over samples
#
# Load in sample and chain
#
chain.HNLmass = 30 

slm = SignalLeptonMatcher(chain)

#
# comparison with ewkino
#
# print chain.GetEntries()
event_range = xrange(10)
#event_range = xrange(chain.GetEntries())
for entry in event_range:
    # if entry != 999: continue
    # chain.Show(entry)

    chain.GetEntry(entry)
    print 'EVENT', entry
    slm.initEvent()
    if not selectGenLeptonsGeneral(chain, chain, 3): continue
    slm.isZevent()

