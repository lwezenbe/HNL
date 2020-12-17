default_tau_algo = 'HNL'
default_light_algo = 'leptonMVAtop'
default_jet_selection = 'HNL'
default_tau_wp = 'tight'
default_ele_wp = 'tight'
default_mu_wp = 'tight'
default_analysis = 'HNL'

def objectSelectionCollection(tau_algo = default_tau_algo, light_algo = default_light_algo, 
        tau_wp = default_tau_wp, ele_wp = default_ele_wp, mu_wp = default_mu_wp, notau = False, 
        analysis = default_analysis, jet_algo = default_jet_selection):
    object_selection_collection = {}
    object_selection_collection["tau_algo"] = tau_algo
    object_selection_collection["light_algo"] = light_algo
    object_selection_collection["jet_algo"] = jet_algo
    object_selection_collection["tau_wp"] = tau_wp
    object_selection_collection["ele_wp"] = ele_wp
    object_selection_collection["mu_wp"] = mu_wp
    object_selection_collection["notau"] = notau
    object_selection_collection["analysis"] = analysis

    return object_selection_collection

def getObjectSelection(selection):
    object_selection = None
    if selection == 'MVA' or selection == 'cutbased':
        object_selection = objectSelectionCollection(tau_algo='HNL', light_algo='leptonMVAtop', notau=False, analysis='HNL', jet_algo = 'HNL')          
    elif selection == 'AN2017014':
        object_selection = objectSelectionCollection(tau_algo='HNL', light_algo='cutbased', notau=True, analysis='HNL', jet_algo = 'AN2017014')          
    elif selection == 'ewkino':
        object_selection = objectSelectionCollection(tau_algo='ewkino', light_algo='ewkino', analysis='ewkino', jet_algo = 'HNL')      
    elif selection == 'TTT':
        object_selection = objectSelectionCollection(tau_algo='HNL', light_algo='TTT', analysis='HNL', jet_algo = 'TTT')
    elif selection == 'Luka':
        object_selection = objectSelectionCollection(tau_algo='HNL', light_algo='TTT', analysis='HNL', jet_algo = 'Luka')
    else:
        print 'No valid selection parameter for object selection given, using defaults'

    return object_selection