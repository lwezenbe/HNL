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
from HNL.EventSelection.cutter import CutterCollection
from HNL.Weights.reweighter import Reweighter
from HNL.TMVA.reader import Reader
from HNL.Samples.sampleManager import SampleManager
from HNL.Tools.helpers import progress

from ROOT import TChain
chain = TChain('blackJackAndHookers/blackJackAndHookersTree')
import glob
paths = glob.glob('/pnfs/iihe/cms/store/user/joknolle/hnltuples/HNL3l_displaced_M30p0_Vsq2p0em06_mu_LO_230426_120259_Run2SIM_UL2018MiniAOD_230426_140604/230428_132823/*root')
#paths = glob.glob('/pnfs/iihe/cms/store/user/lwezenbe/heavyNeutrino/HeavyNeutrino_trilepton_M-30_V-0p01_mu_LO_TuneCP5_13TeV-madgraph-pythia8/crab_RunIISummer20UL18MiniAOD-106X_upgrade2018_realistic_v11_L1v1-v1_HNL_signal18v8/221006_191716/0000/*.root')
for p in paths:
    chain.Add(p)
#chain.Add('/storage_mnt/storage/user/lwezenbe/private/NTuplizer/SignalTester/CMSSW_10_6_27/src/heavyNeutrino/multilep/test/noskim.root')

#prepare object  and event selection
from HNL.ObjectSelection.objectSelection import getObjectSelection
from HNL.ObjectSelection.leptonSelector import isGoodLepton
from HNL.EventSelection.eventSelector import EventSelector
from HNL.EventSelection.signalLeptonMatcher import SignalLeptonMatcher
from HNL.EventSelection.eventSelectionTools import selectGenLeptonsGeneral, selectLeptonsGeneral

def matches(chain, lumi, evtnb):
    if chain._lumiBlock != lumi: return False
    if chain._eventNb != evtnb: return False
    return True

def isLooseMuonHNL(chain, index, cutter):
    if not cutter.cut(chain._lFlavor[index] == 1, 'baseline'):              return False
    if not cutter.cut(chain._lPtCorr > 10, 'pt cut'):                  return False
    if not cutter.cut(abs(chain._lEta[index]) < 2.4, 'eta cut'):          return False
    if not cutter.cut(abs(chain._dxy[index]) < 0.05, 'dxy cut'):          return False
    if not cutter.cut(abs(chain._dz[index]) < 0.1, 'dz cut'):            return False
    if not cutter.cut(chain._miniIso[index] < 0.4, 'mini iso'):            return False
    if not cutter.cut(chain._3dIPSig[index] < 8, 'IPSIG cut'):              return False
    if not cutter.cut(chain._lPOGMedium[index], 'POG medium'):            return False
    return True

def isTightMuonHNL(chain, index, cutter):
    if not isLooseMuonHNL(chain, index, cutter):        return False
    if not cutter.cut(chain._leptonMvaTOPUL[index] > 0.64, 'leptonMVA'):   return False
    return True

def isLooseElectronHNL(chain, index, cutter):
    if not cutter.cut(chain._lFlavor[index] == 0, 'baseline'):              return False
    #if not cutter.cut(isCleanFromMuons(chain, index)):      return False
    if not cutter.cut(chain._lPtCorr[index] >= 10, 'pt cut'):  return False
    if not cutter.cut(abs(chain._lEta[index]) <= 2.5, 'eta cut'):           return False
    if not cutter.cut(abs(chain._dxy[index]) < 0.05, 'dxy cut'):          return False
    if not cutter.cut(abs(chain._dz[index]) < 0.1, 'dz cut'):            return False
    if not cutter.cut(chain._miniIso[index] < 0.4, 'miniIso cut'):            return False
    if not cutter.cut(chain._3dIPSig[index] < 8, 'IPSIG cut'):              return False
    if not cutter.cut(chain._lElectronMissingHits[index] < 2, 'missing hits'):  return False
    return True

def isFOElectronHNLUL(chain, index, cutter):
    if not isLooseElectronHNL(chain, index, cutter):      return False
    if not cutter.cut(chain._lElectronPassConvVeto[index], 'conversion veto'): return False
    return True

def isTightElectronHNLUL(chain, index, cutter):
    if not isFOElectronHNLUL(chain, index, cutter):      return False
    if not cutter.cut(chain._leptonMvaTOPUL[index] > 0.81, 'lepton MVA'): return False
    return True



#Start a loop over samples
delete_branches = ['lhe', 'Lhe']
delete_branches.extend(['HLT']) #TODO: For now using pass_trigger, this may need to change
delete_branches.extend(['tau']) #Outdated tau
delete_branches.extend(['lMuon', 'prefire'])
delete_branches.extend(['_met'])
delete_branches.extend(['jet'])
for i in delete_branches:        chain.SetBranchStatus("*"+i+"*", 0)

cutter = CutterCollection(['electrons', 'muons'], chain, [1], [1])

#
# comparison with ewkino
#
tot_counter = 0.
ele_counter = 0.
mu_counter = 0.
tau_counter = 0.
event_range = xrange(20000)
for entry in event_range:
    chain.GetEntry(entry)
    progress(entry, len(event_range))
    chain.lumiweight=1.
    for l in xrange(chain._nLight):
        from HNL.ObjectSelection.leptonSelector import isGoodLeptonGeneral
        if not isGoodLeptonGeneral(chain, l, algo = 'prompt'): continue
        chain.category = 1
        chain.searchregion = 1
        isTightElectronHNLUL(chain, l, cutter.cutters['electrons'])
        isTightMuonHNL(chain, l, cutter.cutters['muons'])
        tot_counter += 1.
        if chain._lFlavor[l] == 0: ele_counter += 1.
        if chain._lFlavor[l] == 1: mu_counter += 1.
        if chain._lFlavor[l] == 2: tau_counter += 1.

cutter.saveCutFlow('displaced.root')


print tot_counter
print 'ele:', ele_counter/tot_counter*100, ele_counter
print 'mu:', mu_counter/tot_counter*100,  mu_counter
print 'tau:', tau_counter/tot_counter*100,  tau_counter
