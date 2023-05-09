import hepdata_lib
from hepdata_lib import Table, Uncertainty, Variable

#Qualifiers
COUPLINGE = [["Limits", "Primary exclusion limit on $|V_{Ne}|^2$"], ["Limits", "Secondary exclusion limit on $|V_{Ne}|^2$"], ["Limits", "Tertiary exclusion limit on $|V_{Ne}|^2$"]]
COUPLINGMU = [["Limits", "Primary exclusion limit on $|V_{N\mu}|^2$"], ["Limits", "Secondary exclusion limit on $|V_{N\mu}|^2$"], ["Limits", "Tertiary exclusion limit on $|V_{N\mu}|^2$"]]
COUPLINGTAU = [["Limits", "Primary exclusion limit on $|V_{N\tau}|^2$"], ["Limits", "Secondary exclusion limit on $|V_{N\tau}|^2$"], ["Limits", "Tertiary exclusion limit on $|V_{N\tau}|^2$"]]

#COUPLING = {
#    'e' : COUPLINGE,
#    'mu' : COUPLINGMU,
#    'tau' : COUPLINGTAU
#}
COUPLING = {
    'e' : ["Limits", "Exclusion limit on $|V_{Ne}|^2$"],
    'mu' : ["Limits", "Exclusion limit on $|V_{N\mu}|^2$"],
    'tau' : ["Limits", "Exclusion limit on $|V_{N\tau}|^2$"]
}

#Units
GEV = "GeV"

def gatherLimits(in_files, flavor):
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
        return float(limit_dict['-1.0'])


    for m in merged_limits.keys():
        if len(merged_limits[m]) > 1:
            merged_limits[m] = [x for x in sorted(merged_limits[m], key = sortkey)]

    sorted_masses = sorted(merged_limits.keys())
    #Append extra if needed
    sorted_masses_for_var = []
    for m in sorted_masses:
        sorted_masses_for_var.extend([m]*len(merged_limits[m]))

    #Mass variable
    mass_points = Variable('HNL mass')
    mass_points.is_independent = True
    mass_points.is_binned = False
    mass_points.units = GEV
    mass_points.values = sorted_masses_for_var

    observed = []
    expected = []
    onesup = []
    onesdown = []
    twosup = []
    twosdown = []
    for m in sorted_masses:
        tmp_observed = []
        tmp_expected = []
        tmp_1sup = []
        tmp_1sdown = []
        tmp_2sup = []
        tmp_2sdown = []
        for i in range(len(merged_limits[m])):
            tmp_observed.append(merged_limits[m][i]['-1.0'])
            tmp_expected.append(merged_limits[m][i]['0.5'])
            tmp_1sup.append(merged_limits[m][i]['0.84'])
            tmp_1sdown.append(merged_limits[m][i]['0.16'])
            tmp_2sup.append(merged_limits[m][i]['0.975'])
            tmp_2sdown.append(merged_limits[m][i]['0.025'])

        observed.extend(tmp_observed)
        expected.extend(tmp_expected)
        onesup.extend(tmp_1sup)
        twosup.extend(tmp_2sup)
        onesdown.extend(tmp_1sdown)
        twosdown.extend(tmp_2sdown)
            
        
    observed_var = Variable('Observed',
                            is_independent=False,
                            is_binned=False,
                            units = "") 
    observed_var.add_qualifier(*COUPLING[flavor])
    observed_var.values = [x for x in observed]
    
    expected_var = Variable('Expected',
                            is_independent=False,
                            is_binned=False,
                            units = "")
    expected_var.add_qualifier(*COUPLING[flavor])
    expected_var.values = [x for x in expected]
    
    onesup_var = Variable('68% exp. higher',
                            is_independent=False,
                            is_binned=False,
                            units = "")
    onesup_var.add_qualifier(*COUPLING[flavor])
    onesup_var.values = [x for x in onesup]
    
    onesdown_var = Variable('68% exp. lower',
                            is_independent=False,
                            is_binned=False,
                            units = "")
    onesdown_var.add_qualifier(*COUPLING[flavor])
    onesdown_var.values = [x for x in onesdown]

    twosup_var = Variable('95% exp. higher',
                            is_independent=False,
                            is_binned=False,
                            units = "") 
    twosup_var.add_qualifier(*COUPLING[flavor])
    twosup_var.values = [x for x in twosup]
    
    twosdown_var = Variable('95% exp. lower',
                            is_independent=False,
                            is_binned=False,
                            units = "")
    twosdown_var.add_qualifier(*COUPLING[flavor])
    twosdown_var.values = [x for x in twosdown]

    return [
        mass_points,
        observed_var,
        expected_var,
        onesdown_var,
        onesup_var,
        twosdown_var,
        twosup_var
    ]
        

def gatherLimitsObnoxious(in_files, flavor):
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
        return float(limit_dict['-1.0'])
        
    
    for m in merged_limits.keys():
        if len(merged_limits[m]) > 1:
            merged_limits[m] = [x for x in sorted(merged_limits[m], key = sortkey)]

    sorted_masses = sorted(merged_limits.keys())

    #Mass variable
    mass_points = Variable('HNL mass')
    mass_points.is_independent = True
    mass_points.is_binned = False
    mass_points.units = GEV
    mass_points.values = sorted_masses

    max_overlap = max([len(merged_limits[m]) for m in merged_limits.keys()])
    
    def getLimit(limits, mass, quantile, iteration):
        if iteration < len(limits[mass]):
            return limits[mass][i][quantile]
        else:
            return -1.

    observed = []
    expected = []
    onesup = []
    onesdown = []
    twosup = []
    twosdown = []
    for i in range(max_overlap):
        tmp_observed = []
        tmp_expected = []
        tmp_1sup = []
        tmp_1sdown = []
        tmp_2sup = []
        tmp_2sdown = []
        for m in sorted_masses:
            tmp_observed.append(getLimit(merged_limits, m, '-1.0', i))
            tmp_expected.append(getLimit(merged_limits, m, '0.5', i))
            tmp_1sup.append(getLimit(merged_limits, m, '0.84', i))
            tmp_1sdown.append(getLimit(merged_limits, m, '0.16', i))
            tmp_2sup.append(getLimit(merged_limits, m, '0.975', i))
            tmp_2sdown.append(getLimit(merged_limits, m, '0.025', i))

        observed.append(Variable('Observed',
                                is_independent=False,
                                is_binned=False,
                                units = "")) 
        observed[i].add_qualifier(*COUPLING[flavor][i])
        observed[i].values = [x for x in tmp_observed]
        
        expected.append(Variable('Expected',
                                is_independent=False,
                                is_binned=False,
                                units = "")) 
        expected[i].add_qualifier(*COUPLING[flavor][i])
        expected[i].values = [x for x in tmp_expected]
        
        onesup.append(Variable('68% exp. higher',
                                is_independent=False,
                                is_binned=False,
                                units = "")) 
        onesup[i].add_qualifier(*COUPLING[flavor][i])
        onesup[i].values = [x for x in tmp_1sup]
        
        onesdown.append(Variable('68% exp. lower',
                                is_independent=False,
                                is_binned=False,
                                units = "")) 
        onesdown[i].add_qualifier(*COUPLING[flavor][i])
        onesdown[i].values = [x for x in tmp_1sdown]

        twosup.append(Variable('95% exp. higher',
                                is_independent=False,
                                is_binned=False,
                                units = "")) 
        twosup[i].add_qualifier(*COUPLING[flavor][i])
        twosup[i].values = [x for x in tmp_2sup]
        
        twosdown.append(Variable('95% exp. lower',
                                is_independent=False,
                                is_binned=False,
                                units = "")) 
        twosdown[i].add_qualifier(*COUPLING[flavor][i])
        twosdown[i].values = [x for x in tmp_2sdown]

    variables_reordered = [mass_points]
    for i in range(max_overlap):
        variables_reordered.append([observed[i], expected[i], onesdown[i], onesup[i], twosup[i], twosdown[i]])

    return variables_reordered


def addFiguresTo(submission):
    
    #Majorana electron limits
    figure_maj_e = Table("Limits on Majorana HNL with electron coupling")
    figure_maj_e.description =     "The 95% CL limits on $|V_{Ne}|^2$ as a function of the HNL mass for a Majorana HNL."
    figure_maj_e.add_image('/user/lwezenbe/private/PhD/Analysis_CMSSW_10_2_22/CMSSW_10_2_22/src/HNL/Stat/data/output/Majorana-prompt/UL2016post-2016pre-2017-2018/NoTau-e/limits.png')
    in_files = [
        '/user/lwezenbe/private/PhD/Analysis_CMSSW_10_2_22/CMSSW_10_2_22/src/HNL/Stat/data/output/Majorana-prompt/UL2016post-2016pre-2017-2018/custom-lowmass-default-e-asymptotic/NoTau',
        '/user/lwezenbe/private/PhD/Analysis_CMSSW_10_2_22/CMSSW_10_2_22/src/HNL/Stat/data/output/Majorana-displaced/UL2016post-2016pre-2017-2018/custom-lowestmass-default-e-asymptotic/NoTau',
        '/user/lwezenbe/private/PhD/Analysis_CMSSW_10_2_22/CMSSW_10_2_22/src/HNL/Stat/data/output/Majorana-prompt/UL2016post-2016pre-2017-2018/custom-lowestmass-default-e-asymptotic/NoTau',
        '/user/lwezenbe/private/PhD/Analysis_CMSSW_10_2_22/CMSSW_10_2_22/src/HNL/Stat/data/output/Majorana-prompt/UL2016post-2016pre-2017-2018/custom-mediummass85100-default-e-asymptotic/NoTau',
        '/user/lwezenbe/private/PhD/Analysis_CMSSW_10_2_22/CMSSW_10_2_22/src/HNL/Stat/data/output/Majorana-prompt/UL2016post-2016pre-2017-2018/custom-mediummass150200-default-e-asymptotic/NoTau',
        '/user/lwezenbe/private/PhD/Analysis_CMSSW_10_2_22/CMSSW_10_2_22/src/HNL/Stat/data/output/Majorana-prompt/UL2016post-2016pre-2017-2018/custom-mediummass250400-default-e-asymptotic/NoTau', 
        '/user/lwezenbe/private/PhD/Analysis_CMSSW_10_2_22/CMSSW_10_2_22/src/HNL/Stat/data/output/Majorana-prompt/UL2016post-2016pre-2017-2018/cutbased-default-e-asymptotic/NoTau'
    ]
    for variable in gatherLimits(in_files, 'e'):
        figure_maj_e.add_variable(variable)
    submission.add_table(figure_maj_e)
    
    #Majorana muon limits
    figure_maj_mu = Table("Limits on Majorana HNL with muon coupling")
    figure_maj_mu.description =     "The 95% CL limits on $|V_{N\mu}|^2$ as a function of the HNL mass for a Majorana HNL."
    figure_maj_mu.add_image('/user/lwezenbe/private/PhD/Analysis_CMSSW_10_2_22/CMSSW_10_2_22/src/HNL/Stat/data/output/Majorana-prompt/UL2016post-2016pre-2017-2018/NoTau-mu/limits.png')
    in_files = [
        '/user/lwezenbe/private/PhD/Analysis_CMSSW_10_2_22/CMSSW_10_2_22/src/HNL/Stat/data/output/Majorana-prompt/UL2016post-2016pre-2017-2018/custom-lowmass-default-mu-asymptotic/NoTau',
        '/user/lwezenbe/private/PhD/Analysis_CMSSW_10_2_22/CMSSW_10_2_22/src/HNL/Stat/data/output/Majorana-prompt/UL2016post-2016pre-2017-2018/custom-lowestmass-default-mu-asymptotic/NoTau',
        '/user/lwezenbe/private/PhD/Analysis_CMSSW_10_2_22/CMSSW_10_2_22/src/HNL/Stat/data/output/Majorana-displaced/UL2016post-2016pre-2017-2018/custom-lowestmass-default-mu-asymptotic/NoTau',
        '/user/lwezenbe/private/PhD/Analysis_CMSSW_10_2_22/CMSSW_10_2_22/src/HNL/Stat/data/output/Majorana-prompt/UL2016post-2016pre-2017-2018/custom-mediummass85100-default-mu-asymptotic/NoTau',
        '/user/lwezenbe/private/PhD/Analysis_CMSSW_10_2_22/CMSSW_10_2_22/src/HNL/Stat/data/output/Majorana-prompt/UL2016post-2016pre-2017-2018/custom-mediummass150200-default-mu-asymptotic/NoTau',
        '/user/lwezenbe/private/PhD/Analysis_CMSSW_10_2_22/CMSSW_10_2_22/src/HNL/Stat/data/output/Majorana-prompt/UL2016post-2016pre-2017-2018/custom-mediummass250400-default-mu-asymptotic/NoTau', 
        '/user/lwezenbe/private/PhD/Analysis_CMSSW_10_2_22/CMSSW_10_2_22/src/HNL/Stat/data/output/Majorana-prompt/UL2016post-2016pre-2017-2018/cutbased-default-mu-asymptotic/NoTau'
    ]
    for variable in gatherLimits(in_files, 'mu'):
        figure_maj_mu.add_variable(variable)
    submission.add_table(figure_maj_mu)

    #Majorana muon limits
    figure_maj_tau = Table("Limits on Majorana HNL with tau coupling")
    figure_maj_tau.description =     "The 95% CL limits on $|V_{N\tau}|^2$ as a function of the HNL mass for a Majorana HNL."
    figure_maj_tau.add_image('/user/lwezenbe/private/PhD/Analysis_CMSSW_10_2_22/CMSSW_10_2_22/src/HNL/Stat/data/output/Majorana-prompt/UL2016post-2016pre-2017-2018/MaxOneTau-tau/limits.png')
    in_files = [
        '/user/lwezenbe/private/PhD/Analysis_CMSSW_10_2_22/CMSSW_10_2_22/src/HNL/Stat/data/output/Majorana-prompt/UL2016post-2016pre-2017-2018/custom-lowmass-default-tau-asymptotic/MaxOneTau',
        '/user/lwezenbe/private/PhD/Analysis_CMSSW_10_2_22/CMSSW_10_2_22/src/HNL/Stat/data/output/Majorana-prompt/UL2016post-2016pre-2017-2018/custom-lowestmass-default-tau-asymptotic/MaxOneTau', 
        '/user/lwezenbe/private/PhD/Analysis_CMSSW_10_2_22/CMSSW_10_2_22/src/HNL/Stat/data/output/Majorana-prompt/UL2016post-2016pre-2017-2018/cutbased-default-tau-asymptotic/MaxOneTau'
    ]
    for variable in gatherLimits(in_files, 'tau'):
        figure_maj_tau.add_variable(variable)
    submission.add_table(figure_maj_tau)


if __name__ == '__main__':
    from hepdata_lib import Submission

    submission = Submission()
    addFiguresTo(submission)
    submission.create_files('./submission')

    
