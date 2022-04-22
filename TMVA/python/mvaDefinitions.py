
#Each entry should contain name of model, region to be applied, name to write to in chain

MVA_dict = {
    'highMassSR':
        {'mediummass85100-e' : ('kBDT-boostType=Grad-ntrees=300-maxdepth=4-shrinkage=0.3', 'highMassSR', lambda c : c.mediummass85100e ),
        'mediummass85100-mu' : ('kBDT-boostType=Grad-ntrees=300-maxdepth=4-shrinkage=0.3', 'highMassSR', lambda c : c.mediummass85100mu ),
        'mediummass150200-e' : ('kBDT-boostType=Grad-ntrees=300-maxdepth=4-shrinkage=0.3', 'highMassSR', lambda c : c.mediummass150200e ),
        'mediummass150200-mu' : ('kBDT-boostType=Grad-ntrees=300-maxdepth=4-shrinkage=0.3', 'highMassSR', lambda c : c.mediummass150200mu ),
        'mediummass250400-e' : ('kBDT-boostType=Grad-ntrees=300-maxdepth=4-shrinkage=0.3', 'highMassSR', lambda c : c.mediummass250400e ),
        'mediummass250400-mu' : ('kBDT-boostType=Grad-ntrees=300-maxdepth=4-shrinkage=0.3', 'highMassSR', lambda c : c.mediummass250400mu )},
    'lowMassSR':
        {
        'lowmass-e' : ('kBDT-boostType=Grad-ntrees=100-maxdepth=2-shrinkage=0.1', 'lowMassSR', lambda c : c.lowmasse ),
        'lowmass-mu' : ('kBDT-boostType=RealAdaBoost-ntrees=300-maxdepth=3-shrinkage=0.1', 'lowMassSR', lambda c : c.lowmassmu ),
        'lowmass-taulep' : ('kBDT-boostType=Grad-ntrees=75-maxdepth=3-shrinkage=0.1', 'lowMassSR', lambda c : c.lowmasstaulep ),
        'lowmass-tauhad' : ('kBDT-boostType=Grad-ntrees=200-maxdepth=3-shrinkage=0.1', 'lowMassSR', lambda c : c.lowmasstauhad ),
        'lowestmass-e' : ('kBDT-boostType=Grad-ntrees=100-maxdepth=4-shrinkage=0.1', 'lowMassSR', lambda c : c.lowestmasse ),
        'lowestmass-mu' : ('kBDT-boostType=RealAdaBoost-ntrees=300-maxdepth=4-shrinkage=0.1', 'lowMassSR', lambda c : c.lowestmassmu ),
        'lowestmass-taulep' : ('kBDT-boostType=Grad-ntrees=25-maxdepth=4-shrinkage=0.3', 'lowMassSR', lambda c : c.lowestmasstaulep ),
        'lowestmass-tauhad' : ('kBDT-boostType=Grad-ntrees=300-maxdepth=4-shrinkage=0.1', 'lowMassSR', lambda c : c.lowestmasstauhad )
        },
    'lowMassSRloose':
        {
            'lowestmass-e' : ('kBDT-boostType=Grad-ntrees=150-maxdepth=2-shrinkage=1.', 'lowMassSR', lambda c : c.lowestmasse ),
            'lowestmass-mu' : ('kBDT-boostType=Grad-ntrees=400-maxdepth=4-shrinkage=0.1', 'lowMassSR', lambda c : c.lowestmassmu ),
            'lowestmass-tauhad' : ('kBDT-boostType=Grad-ntrees=75-maxdepth=2-shrinkage=0.1', 'lowMassSR', lambda c : c.lowestmasstauhad ),
            'lowestmass-taulep' : ('kBDT-boostType=Grad-ntrees=150-maxdepth=4-shrinkage=0.3', 'lowMassSR', lambda c : c.lowestmasstaulep ),
            'lowmass-e' : ('kBDT-boostType=Grad-ntrees=300-maxdepth=3-shrinkage=0.1', 'lowMassSR', lambda c : c.lowmasse ),
            'lowmass-mu' : ('kBDT-boostType=Grad-ntrees=75-maxdepth=4-shrinkage=0.3', 'lowMassSR', lambda c : c.lowmassmu ),
            'lowmass-tauhad' : ('kBDT-boostType=Grad-ntrees=50-maxdepth=2-shrinkage=0.1', 'lowMassSR', lambda c : c.lowmasstauhad ),
            'lowmass-taulep' : ('kBDT-boostType=Grad-ntrees=25-maxdepth=4-shrinkage=0.3', 'lowMassSR', lambda c : c.lowmasstaulep ),

        }
}

def getMVAdict(region):
    if region not in MVA_dict.keys():
        final_dict = {region : {}}
        from HNL.Analysis.analysisTypes import final_signal_regions
        for sr in final_signal_regions:
            for k in MVA_dict[sr].keys():
                final_dict[region][k] = MVA_dict[sr][k]
        return final_dict
    else:
        return MVA_dict
    

def listAvailableMVAs(region, custom_dict = None):
    if custom_dict is None: custom_dict = MVA_dict
    #TODO: This is a temporary fix, but otherwise everything has to be rerun because in the analysis trees the variables need to be renamed
    if region not in custom_dict.keys():
        return getMVAdict(region).keys()
    return custom_dict[region].keys()

def readMVAFromChain(region, mva_name):
    return MVA_dict[region, mva_name][2]
