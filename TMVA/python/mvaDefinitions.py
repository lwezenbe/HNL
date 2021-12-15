
#Each entry should contain name of model, region to be applied, name to write to in chain


MVA_dict = {
    'mediummass85100-e' : ('kBDT-boostType=Grad-ntrees=300-maxdepth=4-shrinkage=0.3', 'highMassSR', lambda c : c.mediummass85100e ),
    'mediummass85100-mu' : ('kBDT-boostType=Grad-ntrees=300-maxdepth=4-shrinkage=0.3', 'highMassSR', lambda c : c.mediummass85100mu ),
    'mediummass150200-e' : ('kBDT-boostType=Grad-ntrees=300-maxdepth=4-shrinkage=0.3', 'highMassSR', lambda c : c.mediummass150200e ),
    'mediummass150200-mu' : ('kBDT-boostType=Grad-ntrees=300-maxdepth=4-shrinkage=0.3', 'highMassSR', lambda c : c.mediummass150200mu ),
    'mediummass250400-e' : ('kBDT-boostType=Grad-ntrees=300-maxdepth=4-shrinkage=0.3', 'highMassSR', lambda c : c.mediummass250400e ),
    'mediummass250400-mu' : ('kBDT-boostType=Grad-ntrees=300-maxdepth=4-shrinkage=0.3', 'highMassSR', lambda c : c.mediummass250400mu ),
    'lowmass-e' : ('kBDT-boostType=Grad-ntrees=50-maxdepth=3-shrinkage=0.1', 'lowMassSR', lambda c : c.lowmasse ),
    'lowmass-mu' : ('kBDT-boostType=Grad-ntrees=25-maxdepth=3-shrinkage=0.1', 'lowMassSR', lambda c : c.lowmassmu ),
    'lowmass-taulep' : ('kBDT-boostType=Grad-ntrees=100-maxdepth=2-shrinkage=0.1', 'lowMassSR', lambda c : c.lowmasstaulep ),
    'lowmass-tauhad' : ('kBDT-boostType=Grad-ntrees=100-maxdepth=3-shrinkage=0.3', 'lowMassSR', lambda c : c.lowmasstauhad ),
    'lowestmass-e' : ('kBDT-boostType=Grad-ntrees=300-maxdepth=4-shrinkage=0.3', 'lowMassSR', lambda c : c.lowestmasse ),
    'lowestmass-mu' : ('kBDT-boostType=AdaBoost-ntrees=200-maxdepth=3-shrinkage=1', 'lowMassSR', lambda c : c.lowestmassmu ),
    'lowestmass-taulep' : ('kBDT-boostType=Grad-ntrees=75-maxdepth=2-shrinkage=0.3', 'lowMassSR', lambda c : c.lowestmasstaulep ),
    'lowestmass-tauhad' : ('kBDT-boostType=Grad-ntrees=200-maxdepth=4-shrinkage=0.1', 'lowMassSR', lambda c : c.lowestmasstauhad ),
}

def listAvailableMVAs(region = None):
    if region is not None:
        return [k for k in MVA_dict.keys() if MVA_dict[k][1] == region]
    else:
        return MVA_dict.keys()

def readMVAFromChain(mva_name):
    return MVA_dict[mva_name][2]