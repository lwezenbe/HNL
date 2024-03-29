#
#Tau scale factor class using the tau POG tool
#

from TauPOG.TauIDSFs.TauIDSFTool import TauIDSFTool
from HNL.ObjectSelection.tauSelector import getCorrespondingLightLepDiscr

YEARLIB = {'prelegacy2016' : '2016Legacy',
            'prelegacy2017': '2017ReReco',
            'prelegacy2018': '2018ReReco',
            'UL2016pre' : 'UL2016_preVFP',
            'UL2016post' : 'UL2016_postVFP',
            'UL2017': 'UL2017',
            'UL2018': 'UL2018',
            }

ISOLIB = {'deeptauVSjets' : 'DeepTau2017v2p1VSjet', 'MVA2017v2': 'MVAoldDM2017v2'}
ELIB = {'deeptauVSe' : 'DeepTau2017v2p1VSe', 'againstElectron': 'antiEleMVA6'}
MULIB = {'deeptauVSmu' : 'DeepTau2017v2p1VSmu', 'againstMuon': 'antiMu3'}

WPLIB = {'vvvloose': 'VVVLoose', 
            'vvloose': 'VVLoose',
            'vloose': 'VLoose',
            'loose': 'Loose',
            'medium': 'Medium',
            'tight': 'Tight',
            'vtight': 'VTight',
            'vvtight': 'VVTight'
}

UNC_LIB = {
    'nominal' : None,
    'up' : 'Up',
    'down' : 'Down'
}

class TauSF:
    
    def __init__(self, era, year, algorithm, wp_iso, wp_e, wp_mu):
        self.sftool_iso = TauIDSFTool(YEARLIB[era+year], ISOLIB[algorithm], WPLIB[wp_iso])
        self.sftool_e = TauIDSFTool(YEARLIB[era+year], ELIB[getCorrespondingLightLepDiscr(algorithm)[0]],  WPLIB[wp_e])
        # self.sftool_mu = TauIDSFTool(YEARLIB[era+year], MULIB[getCorrespondingLightLepDiscr(algorithm)[1]],  WPLIB[wp_mu])
        self.sftool_mu = TauIDSFTool(YEARLIB['prelegacy'+year.split('p')[0]], MULIB[getCorrespondingLightLepDiscr(algorithm)[1]],  WPLIB[wp_mu]) #For now use the prelegacy as advised by TauPOG

    def getSF(self, chain, index, syst = 'nominal'):
        if chain._tauGenStatus[index] == 1 or chain._tauGenStatus[index] == 3:
            return self.sftool_e.getSFvsEta(chain._lEta[index], chain._tauGenStatus[index], unc = UNC_LIB[syst])
        elif chain._tauGenStatus[index] == 2 or chain._tauGenStatus[index] == 4:
            return self.sftool_mu.getSFvsEta(chain._lEta[index], chain._tauGenStatus[index], unc = UNC_LIB[syst])
        elif chain._tauGenStatus[index] == 5:
            return self.sftool_iso.getSFvsPT(chain._lPt[index], chain._tauGenStatus[index], unc = UNC_LIB[syst])
        else:
            return 1.

    def getTotalSF(self, chain, syst = 'nominal'):
        total_sf = 1.
        for l in chain.l_indices:
            if chain._lFlavor[l] == 2: total_sf *= self.getSF(chain, l, syst)
        return total_sf

if __name__ == "__main__":
    iso_wp = ['vvvloose', 'vvloose', 'vloose', 'loose', 'medium', 'tight', 'vtight', 'vvtight']
    ele_wp = ['vvloose', 'vloose', 'loose', 'medium', 'tight', 'vtight', 'vvtight']
    mu_wp = ['vloose', 'loose', 'medium', 'tight']

    import numpy as np
    import os
    from HNL.Tools.helpers import makeDirIfNeeded
    from HNL.Tools.logger import getLogger, closeLogger
    log = getLogger('INFO')
    pt_range = np.arange(30, 70, 10)

    out_name_tex = os.path.join(os.path.expandvars('$CMSSW_BASE'), 'src', 'HNL', 'Weights', 'data', 'Results', __file__.split('.')[0], 'deeptauVSjets.txt')
    makeDirIfNeeded(out_name_tex)
    # out_file_tex = open(out_name_tex, 'w')
    # out_file_tex.write('\\begin{table}[] \n')
    column_str = '|'.join(['c' for _ in pt_range])
    # out_file_tex.write("\\begin{tabular}{|c|"+column_str+"|} \n")
    # out_file_tex.write("\hline \n")
    # out_file_tex.write('& '+'&'.join(['$p_T = $'+str(m)+ ' GeV' for m in pt_range])+' \\\\ \n')
    # out_file_tex.write("\hline \n")

    for iso in iso_wp:
        tausftool = TauSF('UL', '2017', 'deeptauVSjets', iso, ele_wp[0], mu_wp[0])
        # out_file_tex.write(iso)
        for pt in pt_range:
            sf = tausftool.sftool_iso.getSFvsPT(pt)
            up = tausftool.sftool_iso.getSFvsPT(pt, unc='Up') - tausftool.sftool_iso.getSFvsPT(pt)
            down = tausftool.sftool_iso.getSFvsPT(pt) - tausftool.sftool_iso.getSFvsPT(pt, unc='Down')
            # out_file_tex.write(' & $%.3f'%sf+'^{+%.3f'%up+'}_{-%.3f'%down+'}$')
        # out_file_tex.write('\\\\ \hline \n')
    # out_file_tex.write('\end{tabular} \n')
    # out_file_tex.write('\end{table} \n')
    # out_file_tex.close()



    eta_range = [0.7, 1.5, 2.]

    out_name_tex = os.path.join(os.path.expandvars('$CMSSW_BASE'), 'src', 'HNL', 'Weights', 'data', 'Results', __file__.split('.')[0], 'deeptauVSe.txt')
    makeDirIfNeeded(out_name_tex)
    # out_file_tex = open(out_name_tex, 'w')
    # out_file_tex.write('\\begin{table}[] \n')
    column_str = '|'.join(['c' for _ in eta_range])
    # out_file_tex.write("\\begin{tabular}{|c|"+column_str+"|} \n")
    # out_file_tex.write("\hline \n")
    # out_file_tex.write('& '+'&'.join(['$|\eta| = $'+str(m) for m in eta_range])+' \\\\ \n')
    # out_file_tex.write("\hline \n")

    for ele in ele_wp:
        tausftool = TauSF('UL', '2017', 'deeptauVSjets', iso_wp[0], ele, mu_wp[0])
        # out_file_tex.write(ele)
        for eta in eta_range:
            sf = tausftool.sftool_e.getSFvsEta(eta, 1)
            up = tausftool.sftool_e.getSFvsEta(eta, 1, unc='Up') - tausftool.sftool_e.getSFvsEta(eta, 1)
            down = tausftool.sftool_e.getSFvsEta(eta, 1) - tausftool.sftool_e.getSFvsEta(eta, 1, unc='Down')
            # out_file_tex.write(' & $%.2f'%sf+'^{+%.2f'%up+'}_{-%.2f'%down+'}$')
        # out_file_tex.write('\\\\ \hline \n')
    # out_file_tex.write('\end{tabular} \n')
    # out_file_tex.write('\end{table} \n')
    # out_file_tex.close()

    eta_range = [0.2, 0.6, 1, 1.5, 2.]


    out_name_tex = os.path.join(os.path.expandvars('$CMSSW_BASE'), 'src', 'HNL', 'Weights', 'data', 'Results', __file__.split('.')[0], 'deeptauVSmu.txt')
    makeDirIfNeeded(out_name_tex)
    # out_file_tex = open(out_name_tex, 'w')
    # out_file_tex.write('\\begin{table}[] \n')
    column_str = '|'.join(['c' for _ in eta_range])
    # out_file_tex.write("\\begin{tabular}{|c|"+column_str+"|} \n")
    # out_file_tex.write("\hline \n")
    # out_file_tex.write('& '+'&'.join(['$|\eta| = $'+str(m) for m in eta_range])+' \\\\ \n')
    # out_file_tex.write("\hline \n")

    for mu in mu_wp:
        tausftool = TauSF('UL', '2017', 'deeptauVSjets', iso_wp[0], ele_wp[0], mu)
        # out_file_tex.write(mu)
        for eta in eta_range:
            sf = tausftool.sftool_mu.getSFvsEta(eta, 2)
            up = tausftool.sftool_mu.getSFvsEta(eta, 2, unc='Up') - tausftool.sftool_mu.getSFvsEta(eta, 2)
            down = tausftool.sftool_mu.getSFvsEta(eta, 2) - tausftool.sftool_mu.getSFvsEta(eta, 2, unc='Down')
            # out_file_tex.write(' & $%.2f'%sf+'^{+%.2f'%up+'}_{-%.2f'%down+'}$')
        # out_file_tex.write('\\\\ \hline \n')
    # out_file_tex.write('\end{tabular} \n')
    # out_file_tex.write('\end{table} \n')
    # out_file_tex.close()

    closeLogger(log)
