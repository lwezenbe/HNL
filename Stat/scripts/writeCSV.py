import csv


def gatherLimits(in_files, output_name):
    import numpy as np
    import json
    in_limits = []
    for f in in_files:
        with open(f+'/limits.json', 'r') as open_file:
            in_limits.append(json.load(open_file))

    merged_limits = {}
    for l in in_limits:
        for m in l.keys():
            if float(m) not in merged_limits.keys():
                merged_limits[float(m)] = [l[m]]
            else:
                merged_limits[float(m)].append(l[m])

    #Now sort all the ones with length longer than one according to the observed limit
    def sortkey(limit_dict):
        return float(limit_dict['0.5'])


    for m in merged_limits.keys():
        if len(merged_limits[m]) > 1:
            merged_limits[m] = [x for x in sorted(merged_limits[m], key = sortkey)]

    sorted_masses = sorted(merged_limits.keys())
    #Append extra if needed
    sorted_masses_for_var = []
    for m in sorted_masses:
        sorted_masses_for_var.extend([m]*len(merged_limits[m]))

    observed = []
    for m in sorted_masses:
        tmp_observed = []
        for i in range(len(merged_limits[m])):
            tmp_observed.append(merged_limits[m][i]['-1.0'])
        observed.extend(tmp_observed)


    with open(output_name, 'w') as outfile:
        writer = csv.writer(outfile)
        for m, o in zip(sorted_masses_for_var, observed):
            writer.writerow([m, o])

if __name__ == '__main__':
    in_files = [
        '/user/lwezenbe/private/PhD/Analysis_CMSSW_10_2_22/CMSSW_10_2_22/src/HNL/Stat/data/output/Majorana-prompt/UL2016post-2016pre-2017-2018/custom-lowmass-default-e-asymptotic/NoTau',
        '/user/lwezenbe/private/PhD/Analysis_CMSSW_10_2_22/CMSSW_10_2_22/src/HNL/Stat/data/output/Majorana-displaced/UL2016post-2016pre-2017-2018/custom-lowestmass-default-e-asymptotic/NoTau',
        '/user/lwezenbe/private/PhD/Analysis_CMSSW_10_2_22/CMSSW_10_2_22/src/HNL/Stat/data/output/Majorana-prompt/UL2016post-2016pre-2017-2018/custom-lowestmass-default-e-asymptotic/NoTau',
        '/user/lwezenbe/private/PhD/Analysis_CMSSW_10_2_22/CMSSW_10_2_22/src/HNL/Stat/data/output/Majorana-prompt/UL2016post-2016pre-2017-2018/custom-mediummass85100-default-e-asymptotic/NoTau',
        '/user/lwezenbe/private/PhD/Analysis_CMSSW_10_2_22/CMSSW_10_2_22/src/HNL/Stat/data/output/Majorana-prompt/UL2016post-2016pre-2017-2018/custom-mediummass150200-default-e-asymptotic/NoTau',
        '/user/lwezenbe/private/PhD/Analysis_CMSSW_10_2_22/CMSSW_10_2_22/src/HNL/Stat/data/output/Majorana-prompt/UL2016post-2016pre-2017-2018/custom-mediummass250400-default-e-asymptotic/NoTau',
        '/user/lwezenbe/private/PhD/Analysis_CMSSW_10_2_22/CMSSW_10_2_22/src/HNL/Stat/data/output/Majorana-prompt/UL2016post-2016pre-2017-2018/cutbased-default-e-asymptotic/NoTau'
    ]
    out_file = '/user/lwezenbe/public_html/forComb/majorana-e-exp.csv'
    gatherLimits(in_files, out_file)     

    in_files = [
        '/user/lwezenbe/private/PhD/Analysis_CMSSW_10_2_22/CMSSW_10_2_22/src/HNL/Stat/data/output/Majorana-prompt/UL2016post-2016pre-2017-2018/custom-lowmass-default-mu-asymptotic/NoTau',
        '/user/lwezenbe/private/PhD/Analysis_CMSSW_10_2_22/CMSSW_10_2_22/src/HNL/Stat/data/output/Majorana-prompt/UL2016post-2016pre-2017-2018/custom-lowestmass-default-mu-asymptotic/NoTau',
        '/user/lwezenbe/private/PhD/Analysis_CMSSW_10_2_22/CMSSW_10_2_22/src/HNL/Stat/data/output/Majorana-displaced/UL2016post-2016pre-2017-2018/custom-lowestmass-default-mu-asymptotic/NoTau',
        '/user/lwezenbe/private/PhD/Analysis_CMSSW_10_2_22/CMSSW_10_2_22/src/HNL/Stat/data/output/Majorana-prompt/UL2016post-2016pre-2017-2018/custom-mediummass85100-default-mu-asymptotic/NoTau',
        '/user/lwezenbe/private/PhD/Analysis_CMSSW_10_2_22/CMSSW_10_2_22/src/HNL/Stat/data/output/Majorana-prompt/UL2016post-2016pre-2017-2018/custom-mediummass150200-default-mu-asymptotic/NoTau',
        '/user/lwezenbe/private/PhD/Analysis_CMSSW_10_2_22/CMSSW_10_2_22/src/HNL/Stat/data/output/Majorana-prompt/UL2016post-2016pre-2017-2018/custom-mediummass250400-default-mu-asymptotic/NoTau',
        '/user/lwezenbe/private/PhD/Analysis_CMSSW_10_2_22/CMSSW_10_2_22/src/HNL/Stat/data/output/Majorana-prompt/UL2016post-2016pre-2017-2018/cutbased-default-mu-asymptotic/NoTau'
    ]
    out_file = '/user/lwezenbe/public_html/forComb/majorana-mu-exp.csv'
    gatherLimits(in_files, out_file)     


    in_files = [
        '/user/lwezenbe/private/PhD/Analysis_CMSSW_10_2_22/CMSSW_10_2_22/src/HNL/Stat/data/output/Majorana-prompt/UL2016post-2016pre-2017-2018/custom-lowmass-default-tau-asymptotic/MaxOneTau',
        '/user/lwezenbe/private/PhD/Analysis_CMSSW_10_2_22/CMSSW_10_2_22/src/HNL/Stat/data/output/Majorana-displaced/UL2016post-2016pre-2017-2018/custom-lowestmass-default-tau-asymptotic/MaxOneTau',
        '/user/lwezenbe/private/PhD/Analysis_CMSSW_10_2_22/CMSSW_10_2_22/src/HNL/Stat/data/output/Majorana-prompt/UL2016post-2016pre-2017-2018/custom-lowestmass-default-tau-asymptotic/MaxOneTau',
        '/user/lwezenbe/private/PhD/Analysis_CMSSW_10_2_22/CMSSW_10_2_22/src/HNL/Stat/data/output/Majorana-prompt/UL2016post-2016pre-2017-2018/cutbased-default-tau-asymptotic/MaxOneTau'
    ]
    out_file = '/user/lwezenbe/public_html/forComb/majorana-tau-exp.csv'
    gatherLimits(in_files, out_file)     

    in_files = [
        '/user/lwezenbe/private/PhD/Analysis_CMSSW_10_2_22/CMSSW_10_2_22/src/HNL/Stat/data/output/Dirac-prompt/UL2016post-2016pre-2017-2018/custom-lowmass-default-e-asymptotic/NoTau',
        '/user/lwezenbe/private/PhD/Analysis_CMSSW_10_2_22/CMSSW_10_2_22/src/HNL/Stat/data/output/Dirac-displaced/UL2016post-2016pre-2017-2018/custom-lowestmass-default-e-asymptotic/NoTau',
        '/user/lwezenbe/private/PhD/Analysis_CMSSW_10_2_22/CMSSW_10_2_22/src/HNL/Stat/data/output/Dirac-prompt/UL2016post-2016pre-2017-2018/custom-lowestmass-default-e-asymptotic/NoTau',
        '/user/lwezenbe/private/PhD/Analysis_CMSSW_10_2_22/CMSSW_10_2_22/src/HNL/Stat/data/output/Dirac-prompt/UL2016post-2016pre-2017-2018/custom-mediummass85100-default-e-asymptotic/NoTau',
        '/user/lwezenbe/private/PhD/Analysis_CMSSW_10_2_22/CMSSW_10_2_22/src/HNL/Stat/data/output/Dirac-prompt/UL2016post-2016pre-2017-2018/custom-mediummass150200-default-e-asymptotic/NoTau',
        '/user/lwezenbe/private/PhD/Analysis_CMSSW_10_2_22/CMSSW_10_2_22/src/HNL/Stat/data/output/Dirac-prompt/UL2016post-2016pre-2017-2018/custom-mediummass250400-default-e-asymptotic/NoTau',
        '/user/lwezenbe/private/PhD/Analysis_CMSSW_10_2_22/CMSSW_10_2_22/src/HNL/Stat/data/output/Dirac-prompt/UL2016post-2016pre-2017-2018/cutbased-default-e-asymptotic/NoTau'
    ]
    out_file = '/user/lwezenbe/public_html/forComb/dirac-e-exp.csv'
    gatherLimits(in_files, out_file)     

    in_files = [
        '/user/lwezenbe/private/PhD/Analysis_CMSSW_10_2_22/CMSSW_10_2_22/src/HNL/Stat/data/output/Dirac-prompt/UL2016post-2016pre-2017-2018/custom-lowmass-default-mu-asymptotic/NoTau',
        '/user/lwezenbe/private/PhD/Analysis_CMSSW_10_2_22/CMSSW_10_2_22/src/HNL/Stat/data/output/Dirac-prompt/UL2016post-2016pre-2017-2018/custom-lowestmass-default-mu-asymptotic/NoTau',
        '/user/lwezenbe/private/PhD/Analysis_CMSSW_10_2_22/CMSSW_10_2_22/src/HNL/Stat/data/output/Dirac-displaced/UL2016post-2016pre-2017-2018/custom-lowestmass-default-mu-asymptotic/NoTau',
        '/user/lwezenbe/private/PhD/Analysis_CMSSW_10_2_22/CMSSW_10_2_22/src/HNL/Stat/data/output/Dirac-prompt/UL2016post-2016pre-2017-2018/custom-mediummass85100-default-mu-asymptotic/NoTau',
        '/user/lwezenbe/private/PhD/Analysis_CMSSW_10_2_22/CMSSW_10_2_22/src/HNL/Stat/data/output/Dirac-prompt/UL2016post-2016pre-2017-2018/custom-mediummass150200-default-mu-asymptotic/NoTau',
        '/user/lwezenbe/private/PhD/Analysis_CMSSW_10_2_22/CMSSW_10_2_22/src/HNL/Stat/data/output/Dirac-prompt/UL2016post-2016pre-2017-2018/custom-mediummass250400-default-mu-asymptotic/NoTau',
        '/user/lwezenbe/private/PhD/Analysis_CMSSW_10_2_22/CMSSW_10_2_22/src/HNL/Stat/data/output/Dirac-prompt/UL2016post-2016pre-2017-2018/cutbased-default-mu-asymptotic/NoTau'
    ]
    out_file = '/user/lwezenbe/public_html/forComb/dirac-mu-exp.csv'
    gatherLimits(in_files, out_file)     

    in_files = [
        '/user/lwezenbe/private/PhD/Analysis_CMSSW_10_2_22/CMSSW_10_2_22/src/HNL/Stat/data/output/Dirac-prompt/UL2016post-2016pre-2017-2018/custom-lowmass-default-tau-asymptotic/MaxOneTau',
        '/user/lwezenbe/private/PhD/Analysis_CMSSW_10_2_22/CMSSW_10_2_22/src/HNL/Stat/data/output/Dirac-displaced/UL2016post-2016pre-2017-2018/custom-lowestmass-default-tau-asymptotic/MaxOneTau',
        '/user/lwezenbe/private/PhD/Analysis_CMSSW_10_2_22/CMSSW_10_2_22/src/HNL/Stat/data/output/Dirac-prompt/UL2016post-2016pre-2017-2018/custom-lowestmass-default-tau-asymptotic/MaxOneTau',
        '/user/lwezenbe/private/PhD/Analysis_CMSSW_10_2_22/CMSSW_10_2_22/src/HNL/Stat/data/output/Dirac-prompt/UL2016post-2016pre-2017-2018/cutbased-default-tau-asymptotic/MaxOneTau'
    ]
    out_file = '/user/lwezenbe/public_html/forComb/dirac-tau-exp.csv'
    gatherLimits(in_files, out_file)     

