def objectSelectionCollection(tau_algo, light_algo, tau_wp, ele_wp, mu_wp, notau = False):
    object_selection_collection = {}
    object_selection_collection["tau_algo"] = tau_algo
    object_selection_collection["light_algo"] = light_algo
    object_selection_collection["tau_wp"] = tau_wp
    object_selection_collection["ele_wp"] = ele_wp
    object_selection_collection["mu_wp"] = mu_wp
    object_selection_collection["notau"] = notau

    return object_selection_collection
