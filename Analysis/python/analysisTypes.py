import numpy as np

l1 = 0
l2 = 1
l3 = 2
l4 = 3

var_gen_3l = {'minMos':        (lambda c : c.minMos,   np.arange(0., 120., 12.),         ('min(M_{OS}) [GeV]', 'Events')),
        'm3l':          (lambda c : c.M3l,      np.arange(0., 240., 5.),         ('M_{3l} [GeV]', 'Events')),
        'ml12':          (lambda c : c.Ml12,      np.arange(0., 240., 5.),         ('M_{l1l2} [GeV]', 'Events')),
        'ml23':          (lambda c : c.Ml23,      np.arange(0., 240., 5.),         ('M_{l2l3} [GeV]', 'Events')),
        'ml13':          (lambda c : c.Ml13,      np.arange(0., 240., 5.),         ('M_{l1l3} [GeV]', 'Events')),
        'met':          (lambda c : c._gen_met,     np.arange(0., 300., 15.),         ('p_{T}^{miss} [GeV]', 'Events')),
        'mtOther':      (lambda c : c.mtOther,  np.arange(0., 300., 5.),       ('M_{T} (other min(M_{OS}) [GeV])', 'Events')),
        'l1pt':      (lambda c : c.l_pt[l1],       np.arange(0., 300., 5.),       ('p_{T} (l1) [GeV]', 'Events')),
        'l2pt':      (lambda c : c.l_pt[l2],       np.arange(0., 300., 5.),       ('p_{T} (l2) [GeV]', 'Events')),
        'l3pt':      (lambda c : c.l_pt[l3],       np.arange(0., 300., 5.),       ('p_{T} (l3) [GeV]', 'Events')),
        'l1eta':      (lambda c : c.l_eta[l1],       np.arange(-2.5, 3.0, 0.5),       ('#eta (l1)', 'Events')),
        'l2eta':      (lambda c : c.l_eta[l2],       np.arange(-2.5, 3.0, 0.5),       ('#eta (l2)', 'Events')),
        'l3eta':      (lambda c : c.l_eta[l3],       np.arange(-2.5, 3.0, 0.5),       ('#eta (l3)', 'Events')),
        'l1phi':      (lambda c : c.l_eta[l1],       np.arange(0, 3.0, 0.5),       ('#phi (l1)', 'Events')),
        'l2phi':      (lambda c : c.l_eta[l2],       np.arange(0, 3.0, 0.5),       ('#phi (l2)', 'Events')),
        'l3phi':      (lambda c : c.l_eta[l3],       np.arange(0, 3.0, 0.5),       ('#phi (l3)', 'Events')),
        # 'l1vispt':      (lambda c : c.l_vispt[l1],       np.arange(0., 100., 2.),       ('p_{T}^{vis} (l1) [GeV]', 'Events')),
        # 'l2vispt':      (lambda c : c.l_vispt[l2],       np.arange(0., 100., 2.),       ('p_{T}^{vis} (l2) [GeV]', 'Events')),
        # 'l3vispt':      (lambda c : c.l_vispt[l3],       np.arange(0., 100., 2.),       ('p_{T}^{vis} (l3) [GeV]' 'Events')),
        }

var_reco_3l = {
        'minMos':        (lambda c : c.minMos,   np.arange(0., 160., 10.),         ('min(M_{OS}) [GeV]', 'Events')),
        'm3l':          (lambda c : c.M3l,      np.arange(0., 240., 15.),         ('M_{3l} [GeV]', 'Events')),
        'met':          (lambda c : c._met,     np.arange(0., 300., 15.),         ('p_{T}^{miss} [GeV]', 'Events')),
        'mtOther':      (lambda c : c.mtOther,  np.arange(0., 300., 15.),       ('M_{T} (other min(M_{OS}) [GeV])', 'Events')),
        'l1pt':      (lambda c : c.l_pt[0],       np.arange(0., 300., 15.),       ('p_{T} (l1) [GeV]', 'Events')),
        'l2pt':      (lambda c : c.l_pt[1],       np.arange(0., 200., 10.),       ('p_{T} (l2) [GeV]', 'Events')),
        'l3pt':      (lambda c : c.l_pt[2],       np.arange(0., 150., 5.),       ('p_{T} (l3) [GeV]', 'Events')),
        'j1pt':      (lambda c : c.j_pt[0],       np.arange(0., 300., 15.),       ('p_{T} (j1) [GeV]', 'Events')),
        'j2pt':      (lambda c : c.j_pt[1],       np.arange(0., 300., 15.),       ('p_{T} (j2) [GeV]', 'Events')),
        'l1eta':      (lambda c : c.l_eta[0],       np.arange(-2.5, 3.0, 0.5),       ('#eta (l1)', 'Events')),
        'l2eta':      (lambda c : c.l_eta[1],       np.arange(-2.5, 3.0, 0.5),       ('#eta (l2)', 'Events')),
        'l3eta':      (lambda c : c.l_eta[2],       np.arange(-2.5, 3.0, 0.5),       ('#eta (l3)', 'Events')),
        'j1eta':      (lambda c : c.j_eta[0],       np.arange(-2.5, 3.0, 0.5),       ('#eta (j1)', 'Events')),
        'j2eta':      (lambda c : c.j_eta[1],       np.arange(-2.5, 3.0, 0.5),       ('#eta (j2)', 'Events')),
        'l1phi':      (lambda c : c.l_phi[0],       np.arange(-2.5, 3.0, 0.5),       ('#phi (l1)', 'Events')),
        'l2phi':      (lambda c : c.l_phi[1],       np.arange(-2.5, 3.0, 0.5),       ('#phi (l2)', 'Events')),
        'l3phi':      (lambda c : c.l_phi[2],       np.arange(-2.5, 3.0, 0.5),       ('#phi (l3)', 'Events')),
        'j1phi':      (lambda c : c.j_phi[0],       np.arange(-2.5, 3.0, 0.5),       ('#phi (j1)', 'Events')),
        'j2phi':      (lambda c : c.j_phi[1],       np.arange(-2.5, 3.0, 0.5),       ('#phi (j2)', 'Events')),
        'NJet':      (lambda c : c.njets,       np.arange(0., 12., 1.),       ('#Jets', 'Events')),
        'NbJet':      (lambda c : c.nbjets,       np.arange(0., 12., 1.),       ('#B Jets', 'Events')),
        #'drminOS':      (lambda c : c.dr_minOS,       np.arange(0., 5.5, .25),       ('#Delta R(min(OS))', 'Events')),
        'mt3':   (lambda c : c.mt3,      np.arange(0., 315., 15.),         ('M_{T}(3l) [GeV]', 'Events')),
        'LT':   (lambda c : c.LT,      np.arange(0., 915., 15.),         ('L_{T} [GeV]', 'Events')),
        'HT':   (lambda c : c.HT,      np.arange(0., 915., 15.),         ('H_{T} [GeV]', 'Events')),
        #'rawNlight': (lambda c : c._nLight,      np.arange(0., 10., 1.),         ('N_{light, tuple}', 'Events')),
        #'rawNl': (lambda c : c._nL,      np.arange(0., 10., 1.),         ('N_{l, tuple}', 'Events')),
        #'mtl1':          (lambda c : c.mtl1,      np.arange(0., 240., 5.),         ('M_{l1l3} [GeV]', 'Events')),
        #'mtl2':          (lambda c : c.mtl2,      np.arange(0., 240., 5.),         ('M_{l1l3} [GeV]', 'Events')),
        #'mtl3':          (lambda c : c.mtl3,      np.arange(0., 240., 5.),         ('M_{l1l3} [GeV]', 'Events')),
        'mzossf':          (lambda c : c.MZossf,      np.arange(0., 240., 5.),         ('M_{ll,Z} [GeV]', 'Events')),
        #'mtnonossf':          (lambda c : c.mtNonZossf,      np.arange(0., 240., 5.),         ('M_{ll,Z} [GeV]', 'Events')),
        'NJet':      (lambda c : c.njets,       np.arange(0., 12., 1.),       ('#Jets', 'Events')),
        'NbJet':      (lambda c : c.nbjets,       np.arange(0., 12., 1.),       ('#B Jets', 'Events')),
    }

var_reco_4l = {
        'minMos':        (lambda c : c.minMos,   np.arange(0., 240., 12.),         ('min(M_{OS}) [GeV]', 'Events')),
        'm4l':          (lambda c : c.M4l,      np.arange(0., 303., 3.),         ('M_{4l} [GeV]', 'Events')),
        'met':          (lambda c : c._met,     np.arange(0., 300., 15.),         ('p_{T}^{miss} [GeV]', 'Events')),
        'l1pt':      (lambda c : c.l_pt[0],       np.arange(0., 300., 15.),       ('p_{T} (l1) [GeV]', 'Events')),
        'l2pt':      (lambda c : c.l_pt[1],       np.arange(0., 300., 15.),       ('p_{T} (l2) [GeV]', 'Events')),
        'l3pt':      (lambda c : c.l_pt[2],       np.arange(0., 300., 15.),       ('p_{T} (l3) [GeV]', 'Events')),
        'l4pt':      (lambda c : c.l_pt[3],       np.arange(0., 300., 15.),       ('p_{T} (l4) [GeV]', 'Events')),
        'l1eta':      (lambda c : c.l_eta[0],       np.arange(-2.5, 3.0, 0.5),       ('#eta (l1)', 'Events')),
        'l2eta':      (lambda c : c.l_eta[1],       np.arange(-2.5, 3.0, 0.5),       ('#eta (l2)', 'Events')),
        'l3eta':      (lambda c : c.l_eta[2],       np.arange(-2.5, 3.0, 0.5),       ('#eta (l3)', 'Events')),
        'l4eta':      (lambda c : c.l_eta[3],       np.arange(-2.5, 3.0, 0.5),       ('#eta (l4)', 'Events')),
        'NJet':      (lambda c : c.njets,       np.arange(0., 12., 1.),       ('#Jets', 'Events')),
        'NbJet':      (lambda c : c.nbjets,       np.arange(0., 12., 1.),       ('#B Jets', 'Events')),
        'MllZ1':       (lambda c : c.Mll_Z1,      np.arange(70., 112., 2.),         ('M_{ll}(Z_{1}) [GeV]', 'Events')), 
        'MllZ2':       (lambda c : c.Mll_Z2,      np.arange(70., 112., 2.),         ('M_{ll}(Z_{2}) [GeV]', 'Events')),
        # 'ptConeLeading':   (lambda c : c.pt_cone[0],      np.arange(0., 205., 5.),         ('P_{T}^{cone}(leading) [GeV]', 'Events'))
    }

var_gen_4l = {'minMos':        (lambda c : c.minMos,   np.arange(0., 120., 12.),         ('min(M_{OS}) [GeV]', 'Events')),
        'm4l':          (lambda c : c.M4l,      np.arange(0., 240., 5.),         ('M_{4l} [GeV]', 'Events')),
        'met':          (lambda c : c._gen_met,     np.arange(0., 300., 15.),         ('p_{T}^{miss} [GeV]', 'Events')),
        'l1pt':      (lambda c : c.l_pt[l1],       np.arange(0., 300., 5.),       ('p_{T} (l1) [GeV]', 'Events')),
        'l2pt':      (lambda c : c.l_pt[l2],       np.arange(0., 300., 5.),       ('p_{T} (l2) [GeV]', 'Events')),
        'l3pt':      (lambda c : c.l_pt[l3],       np.arange(0., 300., 5.),       ('p_{T} (l3) [GeV]', 'Events')),
        'l4pt':      (lambda c : c.l_pt[l4],       np.arange(0., 300., 5.),       ('p_{T} (l4) [GeV]', 'Events')),
        'l1eta':      (lambda c : c.l_eta[l1],       np.arange(-2.5, 3.0, 0.5),       ('#eta (l1)', 'Events')),
        'l2eta':      (lambda c : c.l_eta[l2],       np.arange(-2.5, 3.0, 0.5),       ('#eta (l2)', 'Events')),
        'l3eta':      (lambda c : c.l_eta[l3],       np.arange(-2.5, 3.0, 0.5),       ('#eta (l3)', 'Events')),
        'l4eta':      (lambda c : c.l_eta[l4],       np.arange(-2.5, 3.0, 0.5),       ('#eta (l4)', 'Events')),
        'l1phi':      (lambda c : c.l_eta[l1],       np.arange(0, 3.0, 0.5),       ('#phi (l1)', 'Events')),
        'l2phi':      (lambda c : c.l_eta[l2],       np.arange(0, 3.0, 0.5),       ('#phi (l2)', 'Events')),
        'l3phi':      (lambda c : c.l_eta[l3],       np.arange(0, 3.0, 0.5),       ('#phi (l3)', 'Events')),
        'l4phi':      (lambda c : c.l_eta[l4],       np.arange(0, 3.0, 0.5),       ('#phi (l4)', 'Events')),
        # 'l1vispt':      (lambda c : c.l_vispt[l1],       np.arange(0., 100., 2.),       ('p_{T}^{vis} (l1) [GeV]', 'Events')),
        # 'l2vispt':      (lambda c : c.l_vispt[l2],       np.arange(0., 100., 2.),       ('p_{T}^{vis} (l2) [GeV]', 'Events')),
        # 'l3vispt':      (lambda c : c.l_vispt[l3],       np.arange(0., 100., 2.),       ('p_{T}^{vis} (l3) [GeV]' 'Events'))
        }


var_noselection = {
        'rawNlight': (lambda c : c._nLight,      np.arange(0., 10., 1.),         ('N_{light, tuple}', 'Events')),
        'rawNl': (lambda c : c._nL,      np.arange(0., 10., 1.),         ('N_{l, tuple}', 'Events')),
}

from HNL.Tools.helpers import mergeTwoDictionaries
from HNL.Tools.outputTree import cleanName
def returnVariables(nl, is_reco, include_mva = None):
        var_of_choice = {}
        if is_reco:
            if nl == 4: var_of_choice = var_reco_4l
            elif nl == 3: var_of_choice = var_reco_3l
        else:
            if nl == 3: var_of_choice = var_gen_3l
            elif nl == 4: var_of_choice = var_gen_4l

        if include_mva is not None:
                from HNL.TMVA.mvaDefinitions import getMVAdict
                MVA_dict = getMVAdict(include_mva)
                for k in MVA_dict[include_mva].keys():
                        var_of_choice[cleanName(k)] = (MVA_dict[include_mva][k][2],   np.arange(-1., 1.1, 0.1),         ('MVA score', 'Events'))
        
        return var_of_choice


signal_couplingsquared = {
        'tau' : {5 : 0.1, 10 : 0.1, 20:0.1, 30:0.1,  40:0.1, 50:0.1, 60:0.1, 70:0.1, 75:0.1, 80:0.1, 85:0.1,  100:0.1, 120:0.1, 125:0.1, 150:0.1,  200:0.1, 250:0.1, 300:0.1, 350:0.1, 400:0.1, 450:0.1, 500:0.1, 600:0.1, 700:0.1, 800:0.1, 900:0.1, 1000:0.1 },
        'e' : {5 : 1e-4, 10 : 1e-4, 20:1e-4, 30:10e-4, 40:1e-4, 50:1e-4,  60:1e-4, 70:1e-4, 75:1e-4, 80:1e-4, 85:1e-4,  100:0.1,  120:0.1, 125:0.1, 150:0.1,  200:0.1, 250:0.1, 300:0.1, 350:0.1,  400:0.1, 450:0.1, 500:0.1, 600:0.1, 700:0.1,  600:0.1,  800:0.1, 900:0.1, 1000:0.1, 1200:1., 1500:1. },
        'mu' : {5 : 1e-4, 10 : 1e-4, 20:1e-4, 30:10e-4, 40:1e-4, 50:1e-4,  60:1e-4, 70:1e-4, 75:1e-4, 80:1e-4, 85:1e-4,  100:0.1,  120:0.1, 125:0.1, 150:0.1,  200:0.1, 250:0.1, 300:0.1, 350:0.1,  400:0.1, 450:0.1, 500:0.1, 600:0.1, 700:0.1,  600:0.1,  800:0.1, 900:0.1, 1000:0.1, 1200:1., 1500:1.},
}

signal_couplingsquaredinsample = {
        'tau' : {5 : 1e-4, 10 : 1e-4, 20:1e-4, 30:1e-4,  40:1e-4, 50:1e-4, 60:1e-4, 70:1e-4, 75:1e-4, 80:1e-4, 85:1e-4,  100:1e-4, 120:1e-4, 125:1e-4, 150:1e-4,  200:1e-4, 250:1e-4, 300:1e-4, 350:1e-4, 400:1e-4, 450:1e-4, 500:1e-4, 600:1e-4, 700:1e-4, 800:1e-4, 900:1e-4, 1000:1e-4 },
        'e' : {5 : 1e-4, 10 : 1e-4, 20:1e-4, 30:10e-4, 40:1e-4, 50:1e-4,  60:1e-4, 70:1e-4, 75:1e-4, 80:1e-4, 85:1e-4,  100:1e-4,  120:1e-4, 125:1e-4, 150:1e-4,  200:1e-4, 250:1e-4, 300:1e-4, 350:1e-4,  400:1e-4, 450:1e-4, 500:1e-4, 600:1e-4, 700:1e-4,  600:1e-4,  800:1e-4, 900:1e-4, 1000:1e-4, 1200:1e-4, 1500:1e-4 },
        'mu' : {5 : 1e-4, 10 : 1e-4, 20:1e-4, 30:1e-4, 40:1e-4, 50:1e-4,  60:1e-4, 70:1e-4, 75:1e-4, 80:1e-4, 85:1e-4,  100:1e-4,  120:1e-4, 125:1e-4, 150:1e-4,  200:1e-4, 250:1e-4, 300:1e-4, 350:1e-4,  400:1e-4, 450:1e-4, 500:1e-4, 600:1e-4, 700:1e-4,  600:1e-4,  800:1e-4, 900:1e-4, 1000:1e-4, 1200:1e-4, 1500:1e-4},
}

final_signal_regions = ['lowMassSR', 'highMassSR']

if __name__ == '__main__':
        print returnVariables(3, True, True)['mva']
