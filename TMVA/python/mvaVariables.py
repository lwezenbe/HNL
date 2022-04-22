mass_ranges = {
    'lowestmass' : [10, 20, 30, 40],
    'lowmass' : [50, 60, 70, 75],
    'mediummass85100' : [85, 100],
    'mediummass150200' : [150, 200],
    'mediummass250400' : [250, 300, 400],
    'highestmass' : [400, 600, 800, 1000],
}

mass_ranges_for_validation= {
    'lowestmass' : [10, 20, 30, 40],
    'lowmass' : [50, 60, 70, 75],
    'mediummass85100' : [85, 100],
    'mediummass150200' : [125, 150, 200],
    'mediummass250400' : [250, 300, 350, 400],
    'highestmass' : [450, 500, 600, 700, 800, 900, 1000, 1200, 1500],
}

all_masses = [10, 20, 30, 40, 50, 60, 70, 75, 85, 100, 125, 150, 200, 250, 300, 350, 400, 450, 500, 600, 700, 800, 900, 1000, 1200, 1500]

def getNameFromMass(mass):
    for k in mass_ranges:
        if mass in mass_ranges_for_validation[k]:
            return k
    return None

input_variables = {
    'M3l' : {'type' : 'F', 'var' : lambda c : c.M3l},
    'MT3l' : {'type' : 'F', 'var' : lambda c : c.mt3},
    'minMss' : {'type' : 'F', 'var' : lambda c : c.minMss},
    'minMos' : {'type' : 'F', 'var' : lambda c : c.minMos},
    'maxMss' : {'type' : 'F', 'var' : lambda c : c.maxMss},
    'maxMos' : {'type' : 'F', 'var' : lambda c : c.maxMos},
    'minMossf' : {'type' : 'F', 'var' : lambda c : c.minMossf},
    'maxMossf' : {'type' : 'F', 'var' : lambda c : c.maxMossf},
    'MZossf' : {'type' : 'F', 'var' : lambda c : c.MZossf},
    'mtOther' : {'type' : 'F', 'var' : lambda c : c.mtOther},
    'mtl1' : {'type' : 'F', 'var' : lambda c : c.mtl1},
    'mtl2' : {'type' : 'F', 'var' : lambda c : c.mtl2},
    'met' : {'type' : 'F', 'var' : lambda c : c._met},
    'metPhi' : {'type' : 'F', 'var' : lambda c : c._metPhi},
    'njets' : {'type' : 'F', 'var' : lambda c : c.njets},
    'nbjets' : {'type' : 'F', 'var' : lambda c : c.nbjets},
    'l1_charge' : {'type' : 'F', 'var' : lambda c : c.l_charge[0]},
    'l2_charge' : {'type' : 'F', 'var' : lambda c : c.l_charge[1]},
    'l3_charge' : {'type' : 'F', 'var' : lambda c : c.l_charge[2]},
    'l1_flavor' : {'type' : 'F', 'var' : lambda c : c.l_flavor[0]},
    'l2_flavor' : {'type' : 'F', 'var' : lambda c : c.l_flavor[1]},
    'l3_flavor' : {'type' : 'F', 'var' : lambda c : c.l_flavor[2]},
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
    'dPhij1met' : {'type' : 'F', 'var' : lambda c : abs(c.dphi_j1met)},
    'dPhij2met' : {'type' : 'F', 'var' : lambda c : abs(c.dphi_j2met)},
    'HT' : {'type' : 'F', 'var' : lambda c : c.HT},
    'LT' : {'type' : 'F', 'var' : lambda c : c.LT},
    'dRl1l2' : {'type' : 'F', 'var' : lambda c : c.dr_l1l2},
    'dRl1l3' : {'type' : 'F', 'var' : lambda c : c.dr_l1l3},
    'dRl2l3' : {'type' : 'F', 'var' : lambda c : c.dr_l2l3},
    'dPhil1met' : {'type' : 'F', 'var' : lambda c : abs(c.dphi_l1met)},
    'dPhil2met' : {'type' : 'F', 'var' : lambda c : abs(c.dphi_l2met)},
    'dPhil3met' : {'type' : 'F', 'var' : lambda c : abs(c.dphi_l3met)},
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
    'rawNlight' : {'type' : 'I', 'var' : lambda c : c._nLight},
    'rawNl' : {'type' : 'I', 'var' : lambda c : c._nL},
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
    'lowmass-e': ['M3l', 'minMos', 'mtOther', 'l1_pt', 'l2_pt', 'l3_pt', 'l1_eta', 'l2_eta', 'l3_eta', 'met', 'njets', 
                'l1_phi', 'l2_phi', 'l3_phi', 'HT', 'LT', 'MT3l', 'j1_pt', 'j1_eta', 'j1_phi', 'j2_pt', 'j2_eta', 'j2_phi',
                'dRl1l2', 'dRl1l3', 'dRl2l3', 'Ml1l2', 'Ml1l3', 'Ml2l3', 'dRminMos', 'l1_flavor', 'l1_charge', 'l2_flavor', 'l2_charge', 'l3_flavor', 'l3_charge',
                'dPhil1met', 'dPhil2met', 'dPhil3met', 'dPhij1met', 'dPhij2met'],
    'lowmass-mu': ['M3l', 'minMos', 'mtOther', 'l1_pt', 'l2_pt', 'l3_pt', 'l1_eta', 'l2_eta', 'l3_eta', 'met', 'njets', 
                'l1_phi', 'l2_phi', 'l3_phi', 'HT', 'LT', 'MT3l', 'j1_pt', 'j1_eta', 'j1_phi', 'j2_pt', 'j2_eta', 'j2_phi',
                'dRl1l2', 'dRl1l3', 'dRl2l3', 'Ml1l2', 'Ml1l3', 'Ml2l3', 'dRminMos', 'l1_flavor', 'l1_charge', 'l2_flavor', 'l2_charge', 'l3_flavor', 'l3_charge',
                'dPhil1met', 'dPhil2met', 'dPhil3met', 'dPhij1met', 'dPhij2met'],
    'lowmass-taulep': ['M3l', 'minMos', 'mtOther', 'l1_pt', 'l2_pt', 'l3_pt', 'l1_eta', 'l2_eta', 'l3_eta', 'met', 'njets', 
                'l1_phi', 'l2_phi', 'l3_phi', 'HT', 'LT', 'MT3l', 'j1_pt', 'j1_eta', 'j1_phi', 'j2_pt', 'j2_eta', 'j2_phi',
                'dRl1l2', 'dRl1l3', 'dRl2l3', 'Ml1l2', 'Ml1l3', 'Ml2l3', 'dRminMos', 'l1_flavor', 'l1_charge', 'l2_flavor', 'l2_charge', 'l3_flavor', 'l3_charge',
                'dPhil1met', 'dPhil2met', 'dPhil3met', 'dPhij1met', 'dPhij2met'],
    'lowmass-tauhad': ['M3l', 'minMos', 'mtOther', 'l1_pt', 'l2_pt', 'l3_pt', 'l1_eta', 'l2_eta', 'l3_eta', 'met', 'njets', 
                'l1_phi', 'l2_phi', 'l3_phi', 'HT', 'LT', 'MT3l', 'j1_pt', 'j1_eta', 'j1_phi', 'j2_pt', 'j2_eta', 'j2_phi',
                'dRl1l2', 'dRl1l3', 'dRl2l3', 'Ml1l2', 'Ml1l3', 'Ml2l3', 'dRminMos', 
                'dPhil1met', 'dPhil2met', 'dPhil3met', 'dPhij1met', 'dPhij2met'],
    'lowestmass-e': ['M3l', 'minMos', 'mtOther', 'l1_pt', 'l2_pt', 'l3_pt', 'l1_eta', 'l2_eta', 'l3_eta', 'met', 'njets', 
                'l1_phi', 'l2_phi', 'l3_phi', 'HT', 'LT', 'MT3l', 'j1_pt', 'j1_eta', 'j1_phi', 'j2_pt', 'j2_eta', 'j2_phi',
                'dRl1l2', 'dRl1l3', 'dRl2l3', 'Ml1l2', 'Ml1l3', 'Ml2l3', 'dRminMos', 'l1_flavor', 'l1_charge', 'l2_flavor', 'l2_charge', 'l3_flavor', 'l3_charge', 
                'dPhil1met', 'dPhil2met', 'dPhil3met', 'dPhij1met', 'dPhij2met'],
    'lowestmass-mu': ['M3l', 'minMos', 'mtOther', 'l1_pt', 'l2_pt', 'l3_pt', 'l1_eta', 'l2_eta', 'l3_eta', 'met', 'njets', 
                'l1_phi', 'l2_phi', 'l3_phi', 'HT', 'LT', 'MT3l', 'j1_pt', 'j1_eta', 'j1_phi', 'j2_pt', 'j2_eta', 'j2_phi',
                'dRl1l2', 'dRl1l3', 'dRl2l3', 'Ml1l2', 'Ml1l3', 'Ml2l3', 'dRminMos', 'l1_flavor', 'l1_charge', 'l2_flavor', 'l2_charge', 'l3_flavor', 'l3_charge', 
                'dPhil1met', 'dPhil2met', 'dPhil3met', 'dPhij1met', 'dPhij2met'],
    'lowestmass-taulep': ['M3l', 'minMos', 'mtOther', 'l1_pt', 'l2_pt', 'l3_pt', 'l1_eta', 'l2_eta', 'l3_eta', 'met', 'njets', 
                'l1_phi', 'l2_phi', 'l3_phi', 'HT', 'LT', 'MT3l', 'j1_pt', 'j1_eta', 'j1_phi', 'j2_pt', 'j2_eta', 'j2_phi',
                'dRl1l2', 'dRl1l3', 'dRl2l3', 'Ml1l2', 'Ml1l3', 'Ml2l3', 'dRminMos', 'l1_flavor', 'l1_charge', 'l2_flavor', 'l2_charge', 'l3_flavor', 'l3_charge',
                'dPhil1met', 'dPhil2met', 'dPhil3met', 'dPhij1met', 'dPhij2met'],
    'lowestmass-tauhad': ['M3l', 'minMos', 'mtOther', 'l1_pt', 'l2_pt', 'l3_pt', 'l1_eta', 'l2_eta', 'l3_eta', 'met', 'njets', 
                'l1_phi', 'l2_phi', 'l3_phi', 'HT', 'LT', 'MT3l', 'j1_pt', 'j1_eta', 'j1_phi', 'j2_pt', 'j2_eta', 'j2_phi',
                'dRl1l2', 'dRl1l3', 'dRl2l3', 'Ml1l2', 'Ml1l3', 'Ml2l3', 'dRminMos',
                'dPhil1met', 'dPhil2met', 'dPhil3met', 'dPhij1met', 'dPhij2met'],
}

var_to_ignore = {
    None : [],
    "l1_pt<55&&M3l<80&&met<75" : ['minMossf', 'minMos', 'dRminMos'],
    "l1_pt<55&&M3l<80&&minMossf<0" : ['met'],
    "l1_pt<55&&met<75&&minMossf<0" : ['M3l', 'minMos', 'Ml1l2', 'Ml1l3', 'MT3l'],
    "M3l<80&&met<75&&minMossf<0" : ['l1_pt'],
    "M3l<80&&minMossf<0" : ['l1_pt', 'met']
}

def getVariableValue(name):
    #For now this is a fix (there's already abs in the variable) and this should be removed as soon as we have the new trainings
    if 'abs' in name:
        return input_variables[name.replace('abs(', '').replace(')', '')]['var']
    else:
        return input_variables[name]['var']

def getVariables():
    return input_variables.keys()

def getVariableNames(region_name, cut_string = None):
    region_name = region_name if region_name  in var_lists.keys() else 'other'
    if cut_string is None:
        return var_lists[region_name]
    else:
        return [x for x in var_lists[region_name] if not x in var_to_ignore[cut_string]]

def getVariableList(region_name, cut_string = None):
    out_list = []
    region_name = region_name if region_name  in var_lists.keys() else 'other'
    for input_var in var_lists[region_name]:
        if cut_string is not None:
            if input_var in var_to_ignore[cut_string]: continue
        out_list.append('/'.join([input_var, input_variables[input_var]['type']]))
    return out_list

def getAllVariableList():
    out_list = []
    for input_var in input_variables.keys():
        out_list.append('/'.join([input_var, input_variables[input_var]['type']]))
    return out_list

if __name__ == '__main__':
    var_list = getVariableList('low-e')
