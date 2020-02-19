def applyCustomTriggers(chain, triggers):
    multiple_triggers = isinstance(triggers, (list,))   #cuts should always be an array of cuts for the three leptons, so no error expected
    if multiple_triggers:
        passed = [applyCustomTriggers(chain, trigger) for trigger in triggers]
        return any(passed)
    else:
        return triggers

def applyTriggersPerCategory(chain, cat):
    triggers = returnCategoryTriggers(cat)
    return applyCustomTriggers(chain, triggers)


