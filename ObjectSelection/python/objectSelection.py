default_tau_algo = 'deeptauVSjets'
default_light_algo = 'leptonMVAtop'
default_tau_wp = 'tight'
default_ele_wp = 'tight'
default_mu_wp = 'tight'
default_analysis = 'HNL'

def objectSelectionCollection(tau_algo = default_tau_algo, light_algo = default_light_algo, 
        tau_wp = default_tau_wp, ele_wp = default_ele_wp, mu_wp = default_mu_wp, notau = False, 
        analysis = default_analysis):
    object_selection_collection = {}
    object_selection_collection["tau_algo"] = tau_algo
    object_selection_collection["light_algo"] = light_algo
    object_selection_collection["tau_wp"] = tau_wp
    object_selection_collection["ele_wp"] = ele_wp
    object_selection_collection["mu_wp"] = mu_wp
    object_selection_collection["notau"] = notau
    object_selection_collection["analysis"] = analysis

    return object_selection_collection
