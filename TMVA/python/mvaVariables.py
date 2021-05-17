input_variables = {
    'M3l' : {'type' : 'F', 'var' : lambda c : c.M3l},
    'MT3l' : {'type' : 'F', 'var' : lambda c : c.mt3},
    'minMss' : {'type' : 'F', 'var' : lambda c : c.minMss},
    'minMos' : {'type' : 'F', 'var' : lambda c : c.minMos},
    'maxMss' : {'type' : 'F', 'var' : lambda c : c.maxMss},
    'maxMos' : {'type' : 'F', 'var' : lambda c : c.maxMos},
    'minMossf' : {'type' : 'F', 'var' : lambda c : c.minMossf},
    'maxMossf' : {'type' : 'F', 'var' : lambda c : c.maxMossf},
    'mtOther' : {'type' : 'F', 'var' : lambda c : c.mtOther},
    'mtl1' : {'type' : 'F', 'var' : lambda c : c.mtl1},
    'mtl2' : {'type' : 'F', 'var' : lambda c : c.mtl2},
    'ptConeLeading' : {'type' : 'F', 'var' : lambda c : c.pt_cone[0]},
    'met' : {'type' : 'F', 'var' : lambda c : c._met},
    'metPhi' : {'type' : 'F', 'var' : lambda c : c._metPhi},
    'njets' : {'type' : 'F', 'var' : lambda c : c.njets},
    'l1_charge' : {'type' : 'F', 'var' : lambda c : c.l_charge[0]},
    'l2_charge' : {'type' : 'F', 'var' : lambda c : c.l_charge[1]},
    'l3_charge' : {'type' : 'F', 'var' : lambda c : c.l_charge[2]},
    'l1_pt' : {'type' : 'F', 'var' : lambda c : c.l_pt[0]},
    'l2_pt' : {'type' : 'F', 'var' : lambda c : c.l_pt[1]},
    'l3_pt' : {'type' : 'F', 'var' : lambda c : c.l_pt[2]},
    'l1_eta' : {'type' : 'F', 'var' : lambda c : c.l_eta[0]},
    'l2_eta' : {'type' : 'F', 'var' : lambda c : c.l_eta[1]},
    'l3_eta' : {'type' : 'F', 'var' : lambda c : c.l_eta[2]},
    'l1_phi' : {'type' : 'F', 'var' : lambda c : c.l_phi[0]},
    'l2_phi' : {'type' : 'F', 'var' : lambda c : c.l_phi[1]},
    'l3_phi' : {'type' : 'F', 'var' : lambda c : c.l_phi[2]},
    'j1_pt' : {'type' : 'F', 'var' : lambda c : c.j_pt[0]},
    'j2_pt' : {'type' : 'F', 'var' : lambda c : c.j_pt[1]},
    'j1_eta' : {'type' : 'F', 'var' : lambda c : c.j_eta[0]},
    'j2_eta' : {'type' : 'F', 'var' : lambda c : c.j_eta[1]},
    'j1_phi' : {'type' : 'F', 'var' : lambda c : c.j_phi[0]},
    'j2_phi' : {'type' : 'F', 'var' : lambda c : c.j_phi[1]},
    'j1_btag' : {'type' : 'F', 'var' : lambda c : c.j_btag[0]},
    'j2_btag' : {'type' : 'F', 'var' : lambda c : c.j_btag[1]},
    'HT' : {'type' : 'F', 'var' : lambda c : c.HT},
    'LT' : {'type' : 'F', 'var' : lambda c : c.LT},
    'dRl1l2' : {'type' : 'F', 'var' : lambda c : c.dr_l1l2},
    'dRl1l3' : {'type' : 'F', 'var' : lambda c : c.dr_l1l3},
    'dRl2l3' : {'type' : 'F', 'var' : lambda c : c.dr_l2l3},
    'dRminl1' : {'type' : 'F', 'var' : lambda c : c.mindr_l1},
    'dRminl2' : {'type' : 'F', 'var' : lambda c : c.mindr_l2},
    'dRminl3' : {'type' : 'F', 'var' : lambda c : c.mindr_l3},
    'dRmaxl1' : {'type' : 'F', 'var' : lambda c : c.maxdr_l1},
    'dRmaxl2' : {'type' : 'F', 'var' : lambda c : c.maxdr_l2},
    'dRmaxl3' : {'type' : 'F', 'var' : lambda c : c.maxdr_l3},
    'dRminMos' : {'type' : 'F', 'var' : lambda c : c.dr_minOS},
    'dRmaxMos' : {'type' : 'F', 'var' : lambda c : c.dr_maxOS},
    'dRminMss' : {'type' : 'F', 'var' : lambda c : c.dr_minSS},
    'dRmaxMss' : {'type' : 'F', 'var' : lambda c : c.dr_maxSS},
    'dRminMossf' : {'type' : 'F', 'var' : lambda c : c.dr_minOSSF},
    'dRmaxMossf' : {'type' : 'F', 'var' : lambda c : c.dr_maxOSSF},
    'dRjl1' : {'type' : 'F', 'var' : lambda c : c.dr_closestJet[0]},
    'dRjl2' : {'type' : 'F', 'var' : lambda c : c.dr_closestJet[1]},
    'dRjl3' : {'type' : 'F', 'var' : lambda c : c.dr_closestJet[2]},
    'Ml1l2' : {'type' : 'F', 'var' : lambda c : c.Ml12},
    'Ml1l3' : {'type' : 'F', 'var' : lambda c : c.Ml13},
    'Ml2l3' : {'type' : 'F', 'var' : lambda c : c.Ml23},
}

var_lists = {
    'low_e': ['M3l', 'minMos', 'mtOther', 'l1_pt', 'l2_pt', 'l3_pt', 'l1_eta', 'l2_eta', 'l3_eta', 'met', 'njets', 'maxMossf',
                'l1_phi', 'l2_phi', 'l3_phi', 'HT', 'LT', 'MT3l', 'j1_pt', 'j1_eta', 'j1_phi', 'j2_pt', 'j2_eta', 'j2_phi', 
                'dRl1l2', 'dRl1l3', 'dRl2l3', 'dRjl1', 'dRjl2', 'dRjl3', 'Ml1l2', 'Ml1l3', 'Ml2l3', 'dRminMos', 'dRmaxMossf'],
    'high_e': ['M3l', 'minMos', 'mtOther', 'l1_pt', 'l2_pt', 'l3_pt', 'l1_eta', 'l2_eta', 'l3_eta', 'met', 'njets', 'maxMossf', 
                'l1_phi', 'l2_phi', 'l3_phi', 'HT', 'LT', 'MT3l', 'j1_pt', 'j1_eta', 'j1_phi', 'j2_pt', 'j2_eta', 'j2_phi',
                'dRl1l2', 'dRl1l3', 'dRl2l3', 'dRjl1', 'dRjl2', 'dRjl3', 'Ml1l2', 'Ml1l3', 'Ml2l3', 'dRminMos', 'dRmaxMossf'],
    'low_mu': ['M3l', 'minMos', 'mtOther', 'l1_pt', 'l2_pt', 'l3_pt', 'l1_eta', 'l2_eta', 'l3_eta', 'met', 'njets', 'maxMossf', 
                'l1_phi', 'l2_phi', 'l3_phi', 'HT', 'LT', 'MT3l', 'j1_pt', 'j1_eta', 'j1_phi', 'j2_pt', 'j2_eta', 'j2_phi',
                'dRl1l2', 'dRl1l3', 'dRl2l3', 'dRjl1', 'dRjl2', 'dRjl3', 'Ml1l2', 'Ml1l3', 'Ml2l3', 'dRminMos', 'dRmaxMossf'],
    'high_mu': ['M3l', 'minMos', 'mtOther', 'l1_pt', 'l2_pt', 'l3_pt', 'l1_eta', 'l2_eta', 'l3_eta', 'met', 'njets', 'maxMossf', 
                'l1_phi', 'l2_phi', 'l3_phi', 'HT', 'LT', 'MT3l', 'j1_pt', 'j1_eta', 'j1_phi', 'j2_pt', 'j2_eta', 'j2_phi',
                'dRl1l2', 'dRl1l3', 'dRl2l3', 'dRjl1', 'dRjl2', 'dRjl3', 'Ml1l2', 'Ml1l3', 'Ml2l3', 'dRminMos', 'dRmaxMossf'],
    'low_tau': ['M3l', 'minMos', 'mtOther', 'l1_pt', 'l2_pt', 'l3_pt', 'l1_eta', 'l2_eta', 'l3_eta', 'met', 'njets', 'maxMossf', 
                'l1_phi', 'l2_phi', 'l3_phi', 'HT', 'LT', 'MT3l', 'j1_pt', 'j1_eta', 'j1_phi', 'j2_pt', 'j2_eta', 'j2_phi',
                'dRl1l2', 'dRl1l3', 'dRl2l3', 'dRjl1', 'dRjl2', 'dRjl3', 'Ml1l2', 'Ml1l3', 'Ml2l3', 'dRminMos', 'dRmaxMossf'],
    'high_tau': ['M3l', 'minMos', 'mtOther', 'l1_pt', 'l2_pt', 'l3_pt', 'l1_eta', 'l2_eta', 'l3_eta', 'met', 'njets', 'maxMossf', 
                'l1_phi', 'l2_phi', 'l3_phi', 'HT', 'LT', 'MT3l', 'j1_pt', 'j1_eta', 'j1_phi', 'j2_pt', 'j2_eta', 'j2_phi',
                'dRl1l2', 'dRl1l3', 'dRl2l3', 'dRjl1', 'dRjl2', 'dRjl3', 'Ml1l2', 'Ml1l3', 'Ml2l3', 'dRminMos', 'dRmaxMossf'],
    'other': ['M3l', 'minMos', 'mtOther', 'l1_pt', 'l2_pt', 'l3_pt', 'l1_eta', 'l2_eta', 'l3_eta', 'met', 'njets', 'maxMossf', 
                'l1_phi', 'l2_phi', 'l3_phi', 'HT', 'LT', 'MT3l', 'j1_pt', 'j1_eta', 'j1_phi', 'j2_pt', 'j2_eta', 'j2_phi',
                'dRl1l2', 'dRl1l3', 'dRl2l3', 'dRjl1', 'dRjl2', 'dRjl3', 'Ml1l2', 'Ml1l3', 'Ml2l3', 'dRminMos', 'dRmaxMossf'],
}

# var_lists = {
#     'low_e': ['M3l', 'minMos', 'mtOther', 'l1_pt', 'l2_pt', 'l3_pt', 'l1_eta', 'l2_eta', 'l3_eta', 'met', 'njets', 'maxMossf', 'l1_phi', 'l2_phi', 'l3_phi', 'HT', 'LT', 'MT3l', 'j1_pt', 'j1_eta', 'j1_phi', 'j2_pt', 'j2_eta', 'j2_phi'],
#     'high_e': ['M3l', 'minMos', 'mtOther', 'l1_pt', 'l2_pt', 'l3_pt', 'l1_eta', 'l2_eta', 'l3_eta', 'met', 'njets', 'maxMossf', 'l1_phi', 'l2_phi', 'l3_phi', 'HT', 'LT', 'MT3l', 'j1_pt', 'j1_eta', 'j1_phi', 'j2_pt', 'j2_eta', 'j2_phi'],
#     'low_mu': ['M3l', 'minMos', 'mtOther', 'l1_pt', 'l2_pt', 'l3_pt', 'l1_eta', 'l2_eta', 'l3_eta', 'met', 'njets', 'maxMossf', 'l1_phi', 'l2_phi', 'l3_phi', 'HT', 'LT', 'MT3l', 'j1_pt', 'j1_eta', 'j1_phi', 'j2_pt', 'j2_eta', 'j2_phi'],
#     'high_mu': ['M3l', 'minMos', 'mtOther', 'l1_pt', 'l2_pt', 'l3_pt', 'l1_eta', 'l2_eta', 'l3_eta', 'met', 'njets', 'maxMossf', 'l1_phi', 'l2_phi', 'l3_phi', 'HT', 'LT', 'MT3l', 'j1_pt', 'j1_eta', 'j1_phi', 'j2_pt', 'j2_eta', 'j2_phi'],
#     'low_tau': ['M3l', 'minMos', 'mtOther', 'l1_pt', 'l2_pt', 'l3_pt', 'l1_eta', 'l2_eta', 'l3_eta', 'met', 'njets', 'maxMossf', 'l1_phi', 'l2_phi', 'l3_phi', 'HT', 'LT', 'MT3l', 'j1_pt', 'j1_eta', 'j1_phi', 'j2_pt', 'j2_eta', 'j2_phi'],
#     'high_tau': ['M3l', 'minMos', 'mtOther', 'l1_pt', 'l2_pt', 'l3_pt', 'l1_eta', 'l2_eta', 'l3_eta', 'met', 'njets', 'maxMossf', 'l1_phi', 'l2_phi', 'l3_phi', 'HT', 'LT', 'MT3l', 'j1_pt', 'j1_eta', 'j1_phi', 'j2_pt', 'j2_eta', 'j2_phi'],
# }
def getVariableValue(name):
    return input_variables[name]['var']

def getVariables():
    # out_dict = {}
    # for input_var in var_lists[region_name]:
    #     out_dict[input_var] = {input_variables[input_var]}
    # return out_dict
    return input_variables.keys()

def getVariableNames(region_name):
    region_name = region_name if region_name  in var_lists.keys() else 'other'
    return var_lists[region_name]

def getVariableList(region_name):
    out_list = []
    region_name = region_name if region_name  in var_lists.keys() else 'other'
    for input_var in var_lists[region_name]:
        out_list.append('/'.join([input_var, input_variables[input_var]['type']]))
    return out_list

def getAllVariableList():
    out_list = []
    for input_var in input_variables.keys():
        out_list.append('/'.join([input_var, input_variables[input_var]['type']]))
    return out_list

if __name__ == '__main__':
    var_list = getVariableList('low-e')
    # print var_list