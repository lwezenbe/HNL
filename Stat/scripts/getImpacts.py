import os, argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('--inputfile', action='store', default=None,  help='save limits as function of xsec')
args = argParser.parse_args()

#input_file = "/ada_mnt/ada/user/lwezenbe/private/PhD/Analysis_CMSSW_10_2_22/CMSSW_10_2_22/src/HNL/Stat/data/output/Majorana/UL2016post-2016pre-2017-2018/default-highMassSR/e/HNL-e-m200-Vsq5.0em03-prompt/shapes/custom-mediummass150200/Impacts/NoTau/impacts.json"
#input_file = "/ada_mnt/ada/user/lwezenbe/private/PhD/Analysis_CMSSW_10_2_22/CMSSW_10_2_22/src/HNL/Stat/data/output/Majorana/UL2016post-2016pre-2017-2018/default-lowMassSRloose/e/HNL-e-m40-Vsq6.0em06-prompt/shapes/cutbased/Impacts/NoTau/impacts.json"
#input_file = "/ada_mnt/ada/user/lwezenbe/private/PhD/Analysis_CMSSW_10_2_22/CMSSW_10_2_22/src/HNL/Stat/data/output/Majorana/UL2016post-2016pre-2017-2018/default-lowMassSRloose/e/HNL-e-m40-Vsq6.0em06-prompt/shapes/MVA-lowestmass/Impacts/NoTau-CD/impacts.json"
input_file = "/ada_mnt/ada/user/lwezenbe/private/PhD/Analysis_CMSSW_10_2_22/CMSSW_10_2_22/src/HNL/Stat/data/output/Majorana/UL2016post-2016pre-2017-2018/default-highMassSR/tau/HNL-tau-m200-Vsq4.0em01-prompt/shapes/cutbased/Impacts/MaxOneTau/impacts.json"

import json
f = open(args.inputfile+'/impacts.json')
data = json.load(f)
f.close()


out_dict = {}
for d in data["params"]:
    if len(d['groups']) == 0:
        group_str = 'Stat'
    else:
        group_str = d['groups'][0]
    
    if group_str not in out_dict.keys():
        out_dict[group_str] = []

    #print d['impact_r'], d['r'][1]-d['r'][0], d['r'][2] - d['r'][1]
    #out_dict[group_str].append(abs(d['impact_r']/d['r'][1]))

    #print abs(d["fit"][2]-d["fit"][1])
    try:
        out_val = abs(d['impact_r'])/max([abs(d["fit"][2]-d["fit"][1]), abs(d["fit"][1]-d["fit"][0])])
    except:
        out_val = 0
    out_dict[group_str].append(out_val)

import numpy as np
for group in out_dict.keys():
    print group, max(out_dict[group])*100
