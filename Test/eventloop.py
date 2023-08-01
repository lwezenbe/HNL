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

sample_manager = SampleManager('UL', '2018', 'noskim', 'fulllist_UL2018', skim_selection='default')
samplename = 'HNL-mu-m30-Vsq1em4-prompt'
# sample_manager = SampleManager('2016', 'noskim', 'allsignal_2016')
#samplename = 'ZG'

#prepare object  and event selection
from HNL.ObjectSelection.objectSelection import getObjectSelection
from HNL.ObjectSelection.leptonSelector import isGoodLepton, isPromptLepton
from HNL.EventSelection.eventSelector import EventSelector
from HNL.EventSelection.signalLeptonMatcher import SignalLeptonMatcher
from HNL.EventSelection.eventSelectionTools import selectGenLeptonsGeneral, selectLeptonsGeneral

def matches(chain, lumi, evtnb):
    if chain._lumiBlock != lumi: return False
    if chain._eventNb != evtnb: return False
    return True

#Start a loop over samples
for sample in sample_manager.sample_list:
    if sample.name not in sample_manager.sample_names: continue
    if sample.name != samplename: continue
    #
    # Load in sample and chain
    #
    chain = sample.initTree(needhcount=False)
    chain.HNLmass = sample.mass
#    slm = SignalLeptonMatcher(chain)

    delete_branches = ['lhe', 'Lhe']
    delete_branches.extend(['HLT']) #TODO: For now using pass_trigger, this may need to change
    delete_branches.extend(['tau']) #Outdated tau
    delete_branches.extend(['lMuon', 'prefire'])
    delete_branches.extend(['_met'])
    delete_branches.extend(['jet'])
    for i in delete_branches:        chain.SetBranchStatus("*"+i+"*", 0)


    #
    # comparison with ewkino
    #
    event_range = xrange(1000)
    for entry in event_range:
       
        chain.GetEntry(entry)
        #selectGenLeptonsGeneral(chain, chain, 3)
        #slm.isZevent()

