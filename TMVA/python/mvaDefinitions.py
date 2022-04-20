
#Each entry should contain name of model, region to be applied, name to write to in chain

#MVA_dict = {
#    'mediummass85100-e' : ('kBDT-boostType=Grad-ntrees=300-maxdepth=4-shrinkage=0.3', 'highMassSR', lambda c : c.mediummass85100e ),
#    'mediummass85100-mu' : ('kBDT-boostType=Grad-ntrees=300-maxdepth=4-shrinkage=0.3', 'highMassSR', lambda c : c.mediummass85100mu ),
#    'mediummass150200-e' : ('kBDT-boostType=Grad-ntrees=300-maxdepth=4-shrinkage=0.3', 'highMassSR', lambda c : c.mediummass150200e ),
#    'mediummass150200-mu' : ('kBDT-boostType=Grad-ntrees=300-maxdepth=4-shrinkage=0.3', 'highMassSR', lambda c : c.mediummass150200mu ),
#    'mediummass250400-e' : ('kBDT-boostType=Grad-ntrees=300-maxdepth=4-shrinkage=0.3', 'highMassSR', lambda c : c.mediummass250400e ),
#    'mediummass250400-mu' : ('kBDT-boostType=Grad-ntrees=300-maxdepth=4-shrinkage=0.3', 'highMassSR', lambda c : c.mediummass250400mu ),
#    'lowmass-e' : ('kBDT-boostType=Grad-ntrees=50-maxdepth=3-shrinkage=0.1', 'lowMassSR', lambda c : c.lowmasse ),
#    'lowmass-mu' : ('kBDT-boostType=Grad-ntrees=25-maxdepth=3-shrinkage=0.1', 'lowMassSR', lambda c : c.lowmassmu ),
#    'lowmass-taulep' : ('kBDT-boostType=Grad-ntrees=100-maxdepth=2-shrinkage=0.1', 'lowMassSR', lambda c : c.lowmasstaulep ),
#    'lowmass-tauhad' : ('kBDT-boostType=Grad-ntrees=100-maxdepth=3-shrinkage=0.3', 'lowMassSR', lambda c : c.lowmasstauhad ),
#    'lowestmass-e' : ('kBDT-boostType=Grad-ntrees=300-maxdepth=4-shrinkage=0.3', 'lowMassSR', lambda c : c.lowestmasse ),
#    'lowestmass-mu' : ('kBDT-boostType=AdaBoost-ntrees=200-maxdepth=3-shrinkage=1', 'lowMassSR', lambda c : c.lowestmassmu ),
#    'lowestmass-taulep' : ('kBDT-boostType=Grad-ntrees=75-maxdepth=2-shrinkage=0.3', 'lowMassSR', lambda c : c.lowestmasstaulep ),
#    'lowestmass-tauhad' : ('kBDT-boostType=Grad-ntrees=200-maxdepth=4-shrinkage=0.1', 'lowMassSR', lambda c : c.lowestmasstauhad ),
#}

#MVA_dict = {
#    'mediummass85100-e' : ('kBDT-boostType=Grad-ntrees=300-maxdepth=4-shrinkage=0.3', 'highMassSR', lambda c : c.mediummass85100e ),
#    'mediummass85100-mu' : ('kBDT-boostType=Grad-ntrees=300-maxdepth=4-shrinkage=0.3', 'highMassSR', lambda c : c.mediummass85100mu ),
#    'mediummass150200-e' : ('kBDT-boostType=Grad-ntrees=300-maxdepth=4-shrinkage=0.3', 'highMassSR', lambda c : c.mediummass150200e ),
#    'mediummass150200-mu' : ('kBDT-boostType=Grad-ntrees=300-maxdepth=4-shrinkage=0.3', 'highMassSR', lambda c : c.mediummass150200mu ),
#    'mediummass250400-e' : ('kBDT-boostType=Grad-ntrees=300-maxdepth=4-shrinkage=0.3', 'highMassSR', lambda c : c.mediummass250400e ),
#    'mediummass250400-mu' : ('kBDT-boostType=Grad-ntrees=300-maxdepth=4-shrinkage=0.3', 'highMassSR', lambda c : c.mediummass250400mu ),
#    #'lowmass-e' : ('kBDT-boostType=Grad-ntrees=100-maxdepth=2-shrinkage=0.1', 'lowMassSR', lambda c : c.lowmasse ),
#    #'lowmass-mu' : ('kBDT-boostType=RealAdaBoost-ntrees=300-maxdepth=3-shrinkage=0.1', 'lowMassSR', lambda c : c.lowmassmu ),
#    #'lowmass-taulep' : ('kBDT-boostType=Grad-ntrees=75-maxdepth=3-shrinkage=0.1', 'lowMassSR', lambda c : c.lowmasstaulep ),
#    #'lowmass-tauhad' : ('kBDT-boostType=Grad-ntrees=200-maxdepth=3-shrinkage=0.1', 'lowMassSR', lambda c : c.lowmasstauhad ),
#    #'lowestmass-e' : ('kBDT-boostType=Grad-ntrees=100-maxdepth=4-shrinkage=0.1', 'lowMassSR', lambda c : c.lowestmasse ),
#    #'lowestmass-mu' : ('kBDT-boostType=RealAdaBoost-ntrees=300-maxdepth=4-shrinkage=0.1', 'lowMassSR', lambda c : c.lowestmassmu ),
#    #'lowestmass-taulep' : ('kBDT-boostType=Grad-ntrees=25-maxdepth=4-shrinkage=0.3', 'lowMassSR', lambda c : c.lowestmasstaulep ),
#    #'lowestmass-tauhad' : ('kBDT-boostType=Grad-ntrees=300-maxdepth=4-shrinkage=0.1', 'lowMassSR', lambda c : c.lowestmasstauhad ),
#    'lowmass-e' : ('kBDT-boostType=Grad-ntrees=200-maxdepth=4-shrinkage=0.3', 'lowMassSRloose', lambda c : c.lowmasse ),
#    'lowmass-mu' : ('kBDT-boostType=Grad-ntrees=300-maxdepth=4-shrinkage=0.1', 'lowMassSRloose', lambda c : c.lowmassmu ),
#    'lowmass-taulep' : ('kBDT-boostType=Grad-ntrees=100-maxdepth=3-shrinkage=0.3', 'lowMassSRloose', lambda c : c.lowmasstaulep ),
#    'lowmass-tauhad' : ('kBDT-boostType=RealAdaBoost-ntrees=50-maxdepth=1-shrinkage=1', 'lowMassSRloose', lambda c : c.lowmasstauhad ),
#    'lowestmass-e' : ('kBDT-boostType=Grad-ntrees=300-maxdepth=4-shrinkage=0.3', 'lowMassSRloose', lambda c : c.lowestmasse ),
#    'lowestmass-mu' : ('kBDT-boostType=Grad-ntrees=300-maxdepth=4-shrinkage=0.1', 'lowMassSRloose', lambda c : c.lowestmassmu ),
#    'lowestmass-taulep' : ('kBDT-boostType=Grad-ntrees=300-maxdepth=3-shrinkage=0.3', 'lowMassSRloose', lambda c : c.lowestmasstaulep ),
#    'lowestmass-tauhad' : ('kBDT-boostType=Grad-ntrees=100-maxdepth=4-shrinkage=0.3', 'lowMassSRloose', lambda c : c.lowestmasstauhad ),
#}

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
            'lowestmass-e' : ('kBDT-boostType=Grad-ntrees=100-maxdepth=4-shrinkage=0.3', 'lowMassSR', lambda c : c.lowestmasse ),
            'lowestmass-mu' : ('kBDT-boostType=Grad-ntrees=300-maxdepth=3-shrinkage=0.3', 'lowMassSR', lambda c : c.lowestmassmu ),
            'lowestmass-tauhad' : ('kBDT-boostType=Grad-ntrees=100-maxdepth=4-shrinkage=0.3', 'lowMassSR', lambda c : c.lowestmasstauhad ),
            'lowestmass-taulep' : ('kBDT-boostType=Grad-ntrees=300-maxdepth=4-shrinkage=0.1', 'lowMassSR', lambda c : c.lowestmasstaulep ),
            'lowmass-e' : ('kBDT-boostType=Grad-ntrees=300-maxdepth=4-shrinkage=0.1', 'lowMassSR', lambda c : c.lowmasse ),
            'lowmass-mu' : ('kBDT-boostType=Grad-ntrees=200-maxdepth=4-shrinkage=0.1', 'lowMassSR', lambda c : c.lowmassmu ),
            'lowmass-tauhad' : ('kBDT-boostType=AdaBoost-ntrees=75-maxdepth=3-shrinkage=0.1', 'lowMassSR', lambda c : c.lowmasstauhad ),
            'lowmass-taulep' : ('kBDT-boostType=AdaBoost-ntrees=200-maxdepth=3-shrinkage=0.1', 'lowMassSR', lambda c : c.lowmasstaulep ),
        }
}

def listAvailableMVAs(region, custom_dict = None):
    if custom_dict is None: custom_dict = MVA_dict
    return custom_dict[region].keys()

def readMVAFromChain(region, mva_name):
    return MVA_dict[region, mva_name][2]
