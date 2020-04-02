def applyCustomTriggers(triggers):
    if isinstance(triggers, (list,)):
        return any(triggers)
    else:
        return triggers

def applyTriggersPerCategory(chain, cat):
    triggers = returnCategoryTriggers(chain, cat)
    return applyCustomTriggers(triggers)

def listOfTriggersAN2017014(chain):
    list_of_triggers = []
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


    


