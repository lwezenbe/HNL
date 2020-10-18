input_variables = {
    'M3l' : {'type' : 'F', 'var' : lambda c : c.M3l},
    'MT3l' : {'type' : 'F', 'var' : lambda c : c.mt3},
    'minMss' : {'type' : 'F', 'var' : lambda c : c.minMss},
    'minMos' : {'type' : 'F', 'var' : lambda c : c.minMos},
    'maxMos' : {'type' : 'F', 'var' : lambda c : c.maxMos},
    'maxMossf' : {'type' : 'F', 'var' : lambda c : c.maxMossf},
    'mtOther' : {'type' : 'F', 'var' : lambda c : c.mtOther},
    'mtl1' : {'type' : 'F', 'var' : lambda c : c.mtl1},
    'mtl2' : {'type' : 'F', 'var' : lambda c : c.mtl2},
    'ptConeLeading' : {'type' : 'F', 'var' : lambda c : c.pt_cone[0]},
    'met' : {'type' : 'F', 'var' : lambda c : c._met},
    'drMinOS' : {'type' : 'F', 'var' : lambda c : c.dr_minOS},
    'njets' : {'type' : 'F', 'var' : lambda c : c.njets},
    'l1_pt' : {'type' : 'F', 'var' : lambda c : c.l_pt[0]},
    'l2_pt' : {'type' : 'F', 'var' : lambda c : c.l_pt[1]},
    'l3_pt' : {'type' : 'F', 'var' : lambda c : c.l_pt[2]},
    'l1_eta' : {'type' : 'F', 'var' : lambda c : c.l_eta[0]},
    'l2_eta' : {'type' : 'F', 'var' : lambda c : c.l_eta[1]},
    'l3_eta' : {'type' : 'F', 'var' : lambda c : c.l_eta[2]},
    'l1_phi' : {'type' : 'F', 'var' : lambda c : c.l_eta[0]},
    'l2_phi' : {'type' : 'F', 'var' : lambda c : c.l_eta[1]},
    'l3_phi' : {'type' : 'F', 'var' : lambda c : c.l_eta[2]},
    'j1_pt' : {'type' : 'F', 'var' : lambda c : c.j_pt[0]},
    'j2_pt' : {'type' : 'F', 'var' : lambda c : c.j_pt[1]},
    'j1_eta' : {'type' : 'F', 'var' : lambda c : c.j_eta[0]},
    'j2_eta' : {'type' : 'F', 'var' : lambda c : c.j_eta[1]},
    'j1_phi' : {'type' : 'F', 'var' : lambda c : c.j_eta[0]},
    'j2_phi' : {'type' : 'F', 'var' : lambda c : c.j_eta[1]},
    'HT' : {'type' : 'F', 'var' : lambda c : c.HT},
    'LT' : {'type' : 'F', 'var' : lambda c : c.LT},
}

var_lists = {
    'low_e': ['M3l', 'minMos', 'mtOther', 'l1_pt', 'l2_pt', 'l3_pt', 'l1_eta', 'l2_eta', 'l3_eta', 'met', 'njets', 'maxMossf', 'l1_phi', 'l2_phi', 'l3_phi', 'HT', 'LT', 'MT3l', 'j1_pt', 'j1_eta', 'j1_phi', 'j2_pt', 'j2_eta', 'j2_phi'],
    # 'low_e': ['M3l', 'minMos', 'mtOther', 'met', 'njets', 'maxMossf',  'HT', 'LT'],
    'high_e': ['M3l', 'minMos', 'mtOther', 'l1_pt', 'l2_pt', 'l3_pt', 'l1_eta', 'l2_eta', 'l3_eta', 'met', 'njets', 'maxMossf', 'l1_phi', 'l2_phi', 'l3_phi', 'HT', 'LT', 'MT3l', 'j1_pt', 'j1_eta', 'j1_phi', 'j2_pt', 'j2_eta', 'j2_phi'],
    'low_mu': ['M3l', 'minMos', 'mtOther', 'l1_pt', 'l2_pt', 'l3_pt', 'l1_eta', 'l2_eta', 'l3_eta', 'met', 'njets', 'maxMossf', 'l1_phi', 'l2_phi', 'l3_phi', 'HT', 'LT', 'MT3l', 'j1_pt', 'j1_eta', 'j1_phi', 'j2_pt', 'j2_eta', 'j2_phi'],
    # 'low_mu': ['M3l', 'minMos', 'mtOther', 'met', 'njets', 'maxMossf', 'HT', 'LT'],
    'high_mu': ['M3l', 'minMos', 'mtOther', 'l1_pt', 'l2_pt', 'l3_pt', 'l1_eta', 'l2_eta', 'l3_eta', 'met', 'njets', 'maxMossf', 'l1_phi', 'l2_phi', 'l3_phi', 'HT', 'LT', 'MT3l', 'j1_pt', 'j1_eta', 'j1_phi', 'j2_pt', 'j2_eta', 'j2_phi'],
    'low_tau': ['M3l', 'minMos', 'mtOther', 'l1_pt', 'l2_pt', 'l3_pt', 'l1_eta', 'l2_eta', 'l3_eta', 'met', 'njets', 'maxMossf', 'l1_phi', 'l2_phi', 'l3_phi', 'HT', 'LT', 'MT3l', 'j1_pt', 'j1_eta', 'j1_phi', 'j2_pt', 'j2_eta', 'j2_phi'],
    # 'low_tau': ['M3l', 'minMos', 'mtOther', 'met', 'njets', 'maxMossf', 'HT', 'LT'],
    'high_tau': ['M3l', 'minMos', 'mtOther', 'l1_pt', 'l2_pt', 'l3_pt', 'l1_eta', 'l2_eta', 'l3_eta', 'met', 'njets', 'maxMossf', 'l1_phi', 'l2_phi', 'l3_phi', 'HT', 'LT', 'MT3l', 'j1_pt', 'j1_eta', 'j1_phi', 'j2_pt', 'j2_eta', 'j2_phi'],
    # 'high_tau': ['M3l', 'minMos', 'mtOther', 'l1_pt', 'MT3l', '_met', 'njets'],
}

def getVariables():
    # out_dict = {}
    # for input_var in var_lists[region_name]:
    #     out_dict[input_var] = {input_variables[input_var]}
    # return out_dict
    return input_variables

def getVariableNames(region_name):
    return var_lists[region_name]

def getVariableList(region_name):
    out_list = []
    for input_var in var_lists[region_name]:
        print input_var
        out_list.append('/'.join([input_var, input_variables[input_var]['type']]))
    return out_list

def getAllVariableList():
    out_list = []
    for input_var in input_variables.keys():
        out_list.append('/'.join([input_var, input_variables[input_var]['type']]))
    return out_list

if __name__ == '__main__':
    var_list = getVariableList('low-e')
    print var_list