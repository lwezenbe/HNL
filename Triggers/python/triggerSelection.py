l1 = 0
l2 = 1
l3 = 2

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

def listOfTriggerstZq(chain):
    list_of_triggers = []
    list_of_triggers.append(chain._passTrigger_e)
    list_of_triggers.append(chain._passTrigger_ee)
    list_of_triggers.append(chain._passTrigger_eee)
    list_of_triggers.append(chain._passTrigger_m)
    list_of_triggers.append(chain._passTrigger_mm)
    list_of_triggers.append(chain._passTrigger_mmm)
    list_of_triggers.append(chain._passTrigger_em)
    list_of_triggers.append(chain._passTrigger_eem)
    list_of_triggers.append(chain._passTrigger_emm)
    return list_of_triggers


def passTriggers(chain, analysis = 'HNL'):
    if analysis == 'AN2017014':
        if '2016' in chain.year: return applyCustomTriggers(listOfTriggersAN2017014(chain))
        else:   return passTriggers(chain, analysis = 'HNL')
    elif analysis == 'ewkino':
        return applyCustomTriggers(listOfTriggersEwkino(chain))
    elif analysis in ['HNL']:
        if '2016' in chain.year and any(listOfTriggers2016(chain)): return True
        elif chain.year == '2017' and any(listOfTriggers2017(chain)): return True
        elif chain.year == '2018' and any(listOfTriggers2018(chain)): return True
    elif analysis in ['tZq']:
        return any(listOfTriggerstZq(chain))
    else:
        raise RuntimeError('No known trigger strategy for analysis {}'.format(analysis))
    return False

def offlineThresholdsAN2017014(chain, new_chain):
    if new_chain.l_pt[l1] < 15: return False
    if new_chain.l_pt[l2] < 10: return False
    if new_chain.l_flavor[l3] == 1 and new_chain.l_pt[l3] < 5:      return False    
    if new_chain.l_flavor[l3] == 0 and new_chain.l_pt[l3] < 10:      return False

    from HNL.EventSelection.eventCategorization import TRIGGER_CATEGORIES

    if chain.category in TRIGGER_CATEGORIES['EEE']:
        return (chain.l_pt[l1] > 19 and chain.l_pt[l2] > 15) or chain.l_pt[l1] > 30
    if chain.category in TRIGGER_CATEGORIES['EEMu']:
        if new_chain.l_flavor[l3] == 0 and new_chain.l_pt[l3] < 15:
            return new_chain.l_pt[l1] > 23
        elif new_chain.l_flavor[l3] == 1:
            if new_chain.l_pt[l3] < 8:
                return new_chain.l_pt[l1] > 25 and new_chain.l_pt[l2] > 15
            else:
                return new_chain.l_pt[l1] > 23 or new_chain.l_pt[l2] > 15
    if chain.category in TRIGGER_CATEGORIES['EMuMu']:
        if new_chain.l_flavor[l3] == 1 and new_chain.l_pt[l3] < 9:
            return new_chain.l_pt[l1] > 23

    return True

def offlineThresholds2016(chain, new_chain):
    if new_chain.l_pt[l1] < 15: return False
    if new_chain.l_pt[l2] < 10: return False
    if new_chain.l_pt[l3] < 10: return False

    from HNL.EventSelection.eventCategorization import TRIGGER_CATEGORIES
    if chain.category in TRIGGER_CATEGORIES['EEE']:
        return (new_chain.l_pt[l1] > 19 and new_chain.l_pt[l2] > 15) or new_chain.l_pt[l1] > 30
    elif chain.category in TRIGGER_CATEGORIES['EEMu']:
        if new_chain.l_flavor[l3] == 0 and new_chain.l_pt[l3] < 15:
            return new_chain.l_pt[l1] > 23
        elif new_chain.l_flavor[l3] == 1:
            return new_chain.l_pt[l1] > 23 or new_chain.l_pt[l2] > 15

    elif chain.category in TRIGGER_CATEGORIES['TauEE']:
        if new_chain.l_flavor[l3] == 2:
            return new_chain.l_pt[l1] > 23
        elif new_chain.l_flavor[l2] == 2:
            return (new_chain.l_pt[l1] > 25 and new_chain.l_pt[l3] > 15) or new_chain.l_pt[l1] > 30
        else:
            return (new_chain.l_pt[l2] > 25 and new_chain.l_pt[l3] > 15) or new_chain.l_pt[l2] > 30  
    elif chain.category in TRIGGER_CATEGORIES['TauMuMu']:
        if new_chain.l_flavor[l1] == 2:
            return new_chain.l_pt[l2] > 20 
    elif chain.category in TRIGGER_CATEGORIES['TauEMu']:
        if new_chain.l_flavor[l1] == 2:
            if new_chain.l_flavor[l2] == 0:
                return new_chain.l_pt[l2] > 25
            else:
                return new_chain.l_pt[l2] > 23
        else:
           return new_chain.l_pt[l1] > 23          
    
    return True


def offlineThresholds2017(chain, new_chain):
    if new_chain.l_pt[l1] < 15: return False
    if new_chain.l_pt[l2] < 10: return False
    if new_chain.l_pt[l3] < 10: return False

    from HNL.EventSelection.eventCategorization import TRIGGER_CATEGORIES
    if chain.category in TRIGGER_CATEGORIES['EEE']:
        return (new_chain.l_pt[l1] > 19 and new_chain.l_pt[l2] > 15) or new_chain.l_pt[l1] > 35
    elif chain.category in TRIGGER_CATEGORIES['EEMu']:
        if new_chain.l_flavor[l3] == 0 and new_chain.l_pt[l3] < 15:
            return new_chain.l_pt[l1] > 25
        elif new_chain.l_flavor[l3] == 1:
            return new_chain.l_pt[l1] > 23 or new_chain.l_pt[l2] > 15

    elif chain.category in TRIGGER_CATEGORIES['TauEE']:
        if new_chain.l_flavor[l3] == 2:
            return new_chain.l_pt[l1] > 23
        elif new_chain.l_flavor[l2] == 2:
            return (new_chain.l_pt[l1] > 25 and new_chain.l_pt[l3] > 15) or new_chain.l_pt[l1] > 35
        else:
            return (new_chain.l_pt[l2] > 25 and new_chain.l_pt[l3] > 15) or new_chain.l_pt[l2] > 35  
    elif chain.category in TRIGGER_CATEGORIES['TauMuMu']:
        if new_chain.l_flavor[l1] == 2:
            return new_chain.l_pt[l2] > 20 
    elif chain.category in TRIGGER_CATEGORIES['TauEMu']:
        if new_chain.l_flavor[l1] == 2:
            return new_chain.l_pt[l2] > 25
        else:
           return new_chain.l_pt[l1] > 25 
    
    return True

def offlineThresholds2018(chain, new_chain):
    #Same as 2017
    return offlineThresholds2017(chain, new_chain)

def passOfflineThresholds(chain, new_chain, analysis):
    if analysis == 'AN2017014':
        if '2016' not in chain.year: 
            raise RuntimeError("No 2017 and 2018 triggers for AN2017014 available")
        else:
            return offlineThresholdsAN2017014(chain, new_chain)
    elif analysis == 'HNL':
        if '2016' in chain.year: return offlineThresholds2016(chain, new_chain)
        if chain.year == '2017': return offlineThresholds2017(chain, new_chain)
        if chain.year == '2018': return offlineThresholds2018(chain, new_chain)
    elif analysis == 'ewkino':
        return True

    elif analysis == 'tZq':
        if chain.l_pt[l1] < 25: return False
        if chain.l_pt[l2] < 15: return False
        if chain.l_pt[l3] < 10: return False
        return True
    else:
        raise RuntimeError('No known offline thresholds for analysis {}'.format(analysis))


