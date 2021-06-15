def applyCustomTriggers(triggers):
    if isinstance(triggers, (list,)):
        return any(triggers)
    else:
        return triggers

from HNL.EventSelection.eventCategorization import returnCategoryTriggers
def applyTriggersPerCategory(chain, cat):
    triggers = returnCategoryTriggers(chain, cat)
    return applyCustomTriggers(triggers)

def listOfTriggersAN2017014(chain):
    list_of_triggers = []
    list_of_triggers.append(chain._HLT_Ele16_Ele12_Ele8_CaloIdL_TrackIdL)
    list_of_triggers.append(chain._HLT_Mu8_DiEle12_CaloIdL_TrackIdL)
    list_of_triggers.append(chain._HLT_DiMu9_Ele9_CaloIdL_TrackIdL)
    list_of_triggers.append(chain._HLT_TripleMu_12_10_5)
    list_of_triggers.append(chain._HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL_DZ)
    list_of_triggers.append(chain._HLT_Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ)
    list_of_triggers.append(chain._HLT_Mu23_TrkIsoVVL_Ele8_CaloIdL_TrackIdL_IsoVL_DZ)
    # list_of_triggers.append(chain._HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL_DZ)
    list_of_triggers.append(chain._HLT_Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL)
    list_of_triggers.append(chain._HLT_Mu23_TrkIsoVVL_Ele8_CaloIdL_TrackIdL_IsoVL)
    list_of_triggers.append(chain._HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ)
    list_of_triggers.append(chain._HLT_Mu17_TrkIsoVVL_TkMu8_TrkIsoVVL_DZ)
    list_of_triggers.append(chain._HLT_TkMu17_TrkIsoVVL_TkMu8_TrkIsoVVL_DZ)
    list_of_triggers.append(chain._HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL)
    list_of_triggers.append(chain._HLT_Mu17_TrkIsoVVL_TkMu8_TrkIsoVVL)
    list_of_triggers.append(chain._HLT_TkMu17_TrkIsoVVL_TkMu8_TrkIsoVVL)
    list_of_triggers.append(chain._HLT_Ele27_WPTight_Gsf)
    list_of_triggers.append(chain._HLT_IsoMu24)
    list_of_triggers.append(chain._HLT_IsoTkMu24)
    # list_of_triggers.append(chain._passTrigger_eee)
    # list_of_triggers.append(chain._passTrigger_eem)
    # list_of_triggers.append(chain._passTrigger_emm)
    # list_of_triggers.append(chain._passTrigger_mmm)
    # list_of_triggers.append(chain._HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL_DZ)
    # list_of_triggers.append(chain._passTrigger_em)
    # list_of_triggers.append(chain._passTrigger_mm)
    # list_of_triggers.append(chain._HLT_Ele27_WPTight_Gsf)
    # list_of_triggers.append(chain._HLT_IsoMu24)
    # list_of_triggers.append(chain._HLT_IsoTkMu24)
    return list_of_triggers

def listOfTriggers2016(chain):
    list_of_triggers = []
    # list_of_triggers.append(chain._HLT_DoubleMediumCombinedIsoPFTau35_Trk1_eta2p1_Reg)
    # list_of_triggers.append(chain._passTrigger_mt)
    # list_of_triggers.append(chain._passTrigger_et)
    list_of_triggers.append(chain._passTrigger_eee)
    list_of_triggers.append(chain._passTrigger_eem)
    list_of_triggers.append(chain._passTrigger_emm)
    list_of_triggers.append(chain._passTrigger_mmm)
    list_of_triggers.append(chain._HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL_DZ)
    list_of_triggers.append(chain._passTrigger_em)
    list_of_triggers.append(chain._passTrigger_mm)
    list_of_triggers.append(chain._HLT_Ele27_WPTight_Gsf)
    list_of_triggers.append(chain._HLT_IsoMu24)
    list_of_triggers.append(chain._HLT_IsoTkMu24)
    return list_of_triggers

def listOfTriggers2017(chain):
    list_of_triggers = []
    # list_of_triggers.append(chain._HLT_DoubleMediumCombinedIsoPFTau35_Trk1_eta2p1_Reg)
    # list_of_triggers.append(chain._passTrigger_mt)
    # list_of_triggers.append(chain._passTrigger_et)
    list_of_triggers.append(chain._passTrigger_eee)
    list_of_triggers.append(chain._passTrigger_eem)
    list_of_triggers.append(chain._passTrigger_emm)
    list_of_triggers.append(chain._passTrigger_mmm)
    list_of_triggers.append(chain._passTrigger_ee)
    list_of_triggers.append(chain._passTrigger_em)
    list_of_triggers.append(chain._passTrigger_mm)
    list_of_triggers.append(chain._HLT_Ele32_WPTight_Gsf)
    list_of_triggers.append(chain._passTrigger_m)
    return list_of_triggers

def listOfTriggers2018(chain):
    list_of_triggers = []
    # list_of_triggers.append(chain._HLT_DoubleMediumCombinedIsoPFTau35_Trk1_eta2p1_Reg)
    # list_of_triggers.append(chain._passTrigger_mt)
    # list_of_triggers.append(chain._passTrigger_et)
    list_of_triggers.append(chain._passTrigger_eee)
    list_of_triggers.append(chain._passTrigger_eem)
    list_of_triggers.append(chain._passTrigger_emm)
    list_of_triggers.append(chain._passTrigger_mmm)
    list_of_triggers.append(chain._passTrigger_ee)
    list_of_triggers.append(chain._passTrigger_em)
    list_of_triggers.append(chain._passTrigger_mm)
    list_of_triggers.append(chain._HLT_Ele32_WPTight_Gsf)
    list_of_triggers.append(chain._passTrigger_m)
    return list_of_triggers

def listOfTriggersEwkino(chain):
    list_of_triggers = []
    list_of_triggers.append(chain._passTrigger_em)
    list_of_triggers.append(chain._passTrigger_mm)
    list_of_triggers.append(chain._passTrigger_ee)
    list_of_triggers.append(chain._passTrigger_m)
    list_of_triggers.append(chain._passTrigger_e)
    return list_of_triggers

def passTriggers(chain, analysis = 'HNL'):
    if analysis == 'AN2017014':
        if chain.year == 2016: return applyCustomTriggers(listOfTriggersAN2017014(chain))
        else:   return passTriggers(chain, analysis = 'HNL')
    elif analysis == 'ewkino':
        return applyCustomTriggers(listOfTriggersEwkino(chain))
    else:
        if chain.year == 2016 and any(listOfTriggers2016(chain)): return True
        elif chain.year == 2017 and any(listOfTriggers2017(chain)): return True
        elif chain.year == 2018 and any(listOfTriggers2018(chain)): return True
    return False