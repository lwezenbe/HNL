def returnTheoryUnc(sample_name):
    coupling_flavor = sample_name.split('-')[1]
    mass = int(sample_name.split('-m')[-1])
    
    if mass < 80:
        return 1.04
    elif mass < 600:
        return 1.03
    else:
        import json
        import os
        in_path = os.path.expandvars(os.path.join('$CMSSW_BASE', 'src', 'HNL', 'Systematics', 'data', 'VBFcontributions', coupling_flavor+'.json'))
        with open(in_path, 'r') as openfile:
            # Reading from json file
            json_object = json.load(openfile)
        frac = json_object[str(mass)]
        return round(1 + (0.03*(1-frac)+0.15*frac), 2)

def returnUncFunc(function_name, kwargs):
    if func == 'theory':
        sample_name = kwargs.get('process')
        if sample_name is None: raise RuntimeError("Invalid argument in returnUncFunc")
        return returnTheoryUnc(sample_name)
    else:
        raise RuntimeError("Unknown uncFunc")

if __name__ == '__main__':
    for flav in ['e', 'mu', 'tau']:
        print flav
        for mass in [20, 30, 40, 50, 60, 70, 75, 85, 100, 125, 150, 200, 250, 300, 350, 400, 450, 500, 600, 700, 800, 900, 1000]:    
            print '\t', mass, ' : ', returnTheoryUnc('HNL-{0}-m{1}'.format(flav, mass))
