import numpy as np

l1 = 0
l2 = 1
l3 = 2

var_gen_3l = {'minMos':        (lambda c : c.minMos,   np.arange(0., 120., 12.),         ('min(M_{OS}) [GeV]', 'Events')),
        'm3l':          (lambda c : c.M3l,      np.arange(0., 240., 5.),         ('M_{3l} [GeV]', 'Events')),
        'ml12':          (lambda c : c.Ml12,      np.arange(0., 240., 5.),         ('M_{l1l2} [GeV]', 'Events')),
        'ml23':          (lambda c : c.Ml23,      np.arange(0., 240., 5.),         ('M_{l2l3} [GeV]', 'Events')),
        'ml13':          (lambda c : c.Ml13,      np.arange(0., 240., 5.),         ('M_{l1l3} [GeV]', 'Events')),
        'met':          (lambda c : c._met,     np.arange(0., 300., 15.),         ('p_{T}^{miss} [GeV]', 'Events')),
        'mtOther':      (lambda c : c.mtOther,  np.arange(0., 300., 5.),       ('M_{T} (other min(M_{OS}) [GeV])', 'Events')),
        'l1pt':      (lambda c : c.l_pt[l1],       np.arange(0., 300., 5.),       ('p_{T} (l1) [GeV]', 'Events')),
        'l2pt':      (lambda c : c.l_pt[l2],       np.arange(0., 300., 5.),       ('p_{T} (l2) [GeV]', 'Events')),
        'l3pt':      (lambda c : c.l_pt[l3],       np.arange(0., 300., 5.),       ('p_{T} (l3) [GeV]', 'Events'))
        }

var_reco_3l = {
        'minMos':        (lambda c : c.minMos,   np.arange(0., 160., 10.),         ('min(M_{OS}) [GeV]', 'Events')),
        'maxMos':        (lambda c : c.maxMos,   np.arange(0., 240., 12.),         ('max(M_{OS}) [GeV]', 'Events')),
        'minMss':        (lambda c : c.minMss,   np.arange(0., 240., 12.),         ('min(M_{SS}) [GeV]', 'Events')),
        'maxMss':        (lambda c : c.maxMss,   np.arange(0., 240., 12.),         ('max(M_{SS}) [GeV]', 'Events')),
        'minMossf':        (lambda c : c.minMossf,   np.arange(0., 240., 12.),         ('min(M_{OSSF}) [GeV]', 'Events')),
        'maxMossf':        (lambda c : c.maxMossf,   np.arange(0., 240., 12.),         ('max(M_{OSSF}) [GeV]', 'Events')),
        'minMsssf':        (lambda c : c.minMsssf,   np.arange(0., 240., 12.),         ('min(M_{SSSF}) [GeV]', 'Events')),
        'maxMsssf':        (lambda c : c.maxMsssf,   np.arange(0., 240., 12.),         ('max(M_{SSSF}) [GeV]', 'Events')),
        'm3l':          (lambda c : c.M3l,      np.arange(0., 240., 15.),         ('M_{3l} [GeV]', 'Events')),
        'ml12':          (lambda c : c.Ml12,      np.arange(0., 240., 5.),         ('M_{l1l2} [GeV]', 'Events')),
        'ml23':          (lambda c : c.Ml23,      np.arange(0., 240., 5.),         ('M_{l2l3} [GeV]', 'Events')),
        'ml13':          (lambda c : c.Ml13,      np.arange(0., 240., 5.),         ('M_{l1l3} [GeV]', 'Events')),
        'met':          (lambda c : c._met,     np.arange(0., 300., 15.),         ('p_{T}^{miss} [GeV]', 'Events')),
        'mtOther':      (lambda c : c.mtOther,  np.arange(0., 300., 15.),       ('M_{T} (other min(M_{OS}) [GeV])', 'Events')),
        'l1pt':      (lambda c : c.l_pt[0],       np.arange(0., 300., 15.),       ('p_{T} (l1) [GeV]', 'Events')),
        'l2pt':      (lambda c : c.l_pt[1],       np.arange(0., 300., 15.),       ('p_{T} (l2) [GeV]', 'Events')),
        'l3pt':      (lambda c : c.l_pt[2],       np.arange(0., 300., 15.),       ('p_{T} (l3) [GeV]', 'Events')),
        'l1eta':      (lambda c : c.l_eta[0],       np.arange(-2.5, 3.0, 0.5),       ('#eta (l1)', 'Events')),
        'l2eta':      (lambda c : c.l_eta[1],       np.arange(-2.5, 3.0, 0.5),       ('#eta (l2)', 'Events')),
        'l3eta':      (lambda c : c.l_eta[2],       np.arange(-2.5, 3.0, 0.5),       ('#eta (l3)', 'Events')),
        'NJet':      (lambda c : c.njets,       np.arange(0., 12., 1.),       ('#Jets', 'Events')),
        'NbJet':      (lambda c : c.nbjets,       np.arange(0., 12., 1.),       ('#B Jets', 'Events')),
        'drl1l2':      (lambda c : c.dr_l1l2,       np.arange(0., 5.5, .25),       ('#Delta R(l1, l2)', 'Events')),
        'drl1l3':      (lambda c : c.dr_l1l3,       np.arange(0., 5.5, .25),       ('#Delta R(l1, l3)', 'Events')),
        'drl2l3':      (lambda c : c.dr_l2l3,       np.arange(0., 5.5, .25),       ('#Delta R(l2, l3)', 'Events')),
        'drminOS':      (lambda c : c.dr_minOS,       np.arange(0., 5.5, .25),       ('#Delta R(min(OS))', 'Events')),
        'drmaxOS':      (lambda c : c.dr_maxOS,       np.arange(0., 5.5, .25),       ('#Delta R(max(OS))', 'Events')),
        'drminSS':      (lambda c : c.dr_minSS,       np.arange(0., 5.5, .25),       ('#Delta R(min(SS))', 'Events')),
        'drmaxSS':      (lambda c : c.dr_maxSS,       np.arange(0., 5.5, .25),       ('#Delta R(max(SS))', 'Events')),
        'drminOSSF':      (lambda c : c.dr_minOSSF,       np.arange(0., 5.5, .25),       ('#Delta R(min(OSSF))', 'Events')),
        'drmaxOSSF':      (lambda c : c.dr_maxOSSF,       np.arange(0., 5.5, .25),       ('#Delta R(max(OSSF))', 'Events')),
        'drminSSSF':      (lambda c : c.dr_minSSSF,       np.arange(0., 5.5, .25),       ('#Delta R(min(SSSF))', 'Events')),
        'drmaxSSSF':      (lambda c : c.dr_maxSSSF,       np.arange(0., 5.5, .25),       ('#Delta R(max(SSSF))', 'Events')),
        'mindrl1':      (lambda c : c.mindr_l1,       np.arange(0., 5.5, .25),       ('min(#Delta R(l1ln))', 'Events')),
        'maxdrl1':      (lambda c : c.maxdr_l1,       np.arange(0., 5.5, .25),       ('max(#Delta R(l1ln))', 'Events')),
        'mindrl2':      (lambda c : c.mindr_l2,       np.arange(0., 5.5, .25),       ('min(#Delta R(l2ln))', 'Events')),
        'maxdrl2':      (lambda c : c.maxdr_l2,       np.arange(0., 5.5, .25),       ('max(#Delta R(l2ln))', 'Events')),
        'mindrl3':      (lambda c : c.mindr_l3,       np.arange(0., 5.5, .25),       ('min(#Delta R(l3ln))', 'Events')),
        'maxdrl3':      (lambda c : c.maxdr_l3,       np.arange(0., 5.5, .25),       ('max(#Delta R(l3ln))', 'Events')),
        'ptConeLeading':   (lambda c : c.pt_cone[0],      np.arange(0., 205., 5.),         ('P_{T}^{cone}(leading) [GeV]', 'Events'))
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
        'MllZ1':       (lambda c : c.Mll_Z1,      np.arange(0., 157.5, 7.5),         ('M_{ll}(Z_{1}) [GeV]', 'Events')), 
        'MllZ2':       (lambda c : c.Mll_Z2,      np.arange(0., 153.75, 3.75),         ('M_{ll}(Z_{2}) [GeV]', 'Events')),
        'ptConeLeading':   (lambda c : c.pt_cone[0],      np.arange(0., 205., 5.),         ('P_{T}^{cone}(leading) [GeV]', 'Events'))
    }

def returnVariables(nl, is_reco):
        if nl == 4:
                return var_reco_4l
        elif nl == 3:
                if is_reco: return var_reco_3l
                else: return var_gen_3l