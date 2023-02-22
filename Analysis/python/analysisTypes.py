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
        # WZCR, ConversionCR
        'l1pt':      (lambda c : c.l_pt[0],       np.arange(0., 300., 15.),       ('p_{T} (l1) [GeV]', 'Events')),
        'light1pt':      (lambda c : c.light_pt[0],       np.arange(0., 300., 15.),       ('p_{T} (l1) [GeV]', 'Events')),
        'l2pt':      (lambda c : c.l_pt[1],       np.arange(0., 200., 10.),       ('p_{T} (l2) [GeV]', 'Events')),
        'light2pt':      (lambda c : c.light_pt[1],       np.arange(0., 200., 10.),       ('p_{T} (l2) [GeV]', 'Events')),
        'l3pt':      (lambda c : c.l_pt[2],       np.arange(0., 150., 5.),       ('p_{T} (l3) [GeV]', 'Events')),
        'l1eta':      (lambda c : c.l_eta[0],       np.arange(-2.5, 3.0, 0.5),       ('#eta (l1)', 'Events')),
        'l2eta':      (lambda c : c.l_eta[1],       np.arange(-2.5, 3.0, 0.5),       ('#eta (l2)', 'Events')),
        'l3eta':      (lambda c : c.l_eta[2],       np.arange(-2.5, 3.0, 0.5),       ('#eta (l3)', 'Events')),
        'minMos':        (lambda c : c.minMos,   np.arange(0., 210., 10.),         ('min m(2l|OS) [GeV]', 'Events')),
        'met':          (lambda c : c.met,     np.arange(0., 90., 15.),         ('p_{T}^{miss} [GeV]', 'Events')),
        'mtOther':      (lambda c : c.mtOther,  np.arange(0., 365., 15.),       ('m_{T} [GeV])', 'Events')),
        'mt3':   (lambda c : c.mt3,      np.arange(0., 415., 15.),         ('m_{T}(3l) [GeV]', 'Events')),
        
        # Full SR (mainly for BDT variables)
        'm3l':          (lambda c : c.M3l,      np.arange(0., 415., 15.),         ('m(3l) [GeV]', 'Events')),
        'j1pt':      (lambda c : c.j_pt[0],       np.arange(0., 160., 15.),       ('p_{T} (j1) [GeV]', 'Events')),
        'j2pt':      (lambda c : c.j_pt[1],       np.arange(0., 160., 15.),       ('p_{T} (j2) [GeV]', 'Events')),
        'j1eta':      (lambda c : c.j_eta[0],       np.arange(-2.5, 3.0, 0.5),       ('#eta (j1)', 'Events')),
        'j2eta':      (lambda c : c.j_eta[1],       np.arange(-2.5, 3.0, 0.5),       ('#eta (j2)', 'Events')),
        'l1phi':      (lambda c : c.l_phi[0],       np.arange(-3.5, 4.0, 0.5),       ('#phi (l1)', 'Events')),
        'l2phi':      (lambda c : c.l_phi[1],       np.arange(-3.5, 4.0, 0.5),       ('#phi (l2)', 'Events')),
        'l3phi':      (lambda c : c.l_phi[2],       np.arange(-3.5, 4.0, 0.5),       ('#phi (l3)', 'Events')),
        'j1phi':      (lambda c : c.j_phi[0],       np.arange(-3.5, 4.0, 0.5),       ('#phi (j1)', 'Events')),
        'j2phi':      (lambda c : c.j_phi[1],       np.arange(-3.5, 4.0, 0.5),       ('#phi (j2)', 'Events')),
        'NJet':      (lambda c : c.njets,       np.arange(0., 6., 1.),       ('#Jets', 'Events')),
        'LT':   (lambda c : c.LT,      np.arange(0., 915., 15.),         ('L_{T} [GeV]', 'Events')),
        'HT':   (lambda c : c.HT,      np.arange(0., 915., 15.),         ('H_{T} [GeV]', 'Events')),
        'mzossf':          (lambda c : c.MZossf,      np.arange(0., 240., 5.),         ('m_{ll,Z} [GeV]', 'Events')),
        'maxMossf':   (lambda c : c.maxMossf,      np.arange(0., 75., 5.),         ('max(m_{OSSF}) [GeV]', 'Events')),
        'minMossf':   (lambda c : c.minMossf,      np.arange(0., 75., 5.),         ('min(m_{OSSF}) [GeV]', 'Events')),
        'maxMsssf':   (lambda c : c.maxMsssf,      np.arange(0., 260., 20.),         ('max(m_{SSSF}) [GeV]', 'Events')),
        'minMsssf':   (lambda c : c.minMsssf,      np.arange(0., 260., 20.),         ('min(m_{SSSF}) [GeV]', 'Events')),
        'ml1l2':   (lambda c : c.Ml12,      np.arange(75., 205., 5.),         ('m_{l1l2} [GeV]', 'Events')),
        'ml1l3':   (lambda c : c.Ml13,      np.arange(75., 205., 5.),         ('m_{l1l3} [GeV]', 'Events')),
        'ml2l3':   (lambda c : c.Ml23,      np.arange(75., 205., 5.),         ('m_{l2l3} [GeV]', 'Events')),
        'drl1l2':      (lambda c : c.dr_l1l2,       np.arange(0., 4.5, .25),       ('#Delta R(l1,l2)', 'Events')),
        'drl1l3':      (lambda c : c.dr_l1l3,       np.arange(0., 4.5, .25),       ('#Delta R(l1,l3)', 'Events')),
        'drl2l3':      (lambda c : c.dr_l2l3,       np.arange(0., 4.5, .25),       ('#Delta R(l2,l3)', 'Events')),
        'drl1j':      (lambda c : c.dr_closestJet[0],       np.arange(0., 4.5, .25),       ('#Delta R(l1,j)', 'Events')),
        'drl2j':      (lambda c : c.dr_closestJet[1],       np.arange(0., 4.5, .25),       ('#Delta R(l2,j)', 'Events')),
        'drl3j':      (lambda c : c.dr_closestJet[2],       np.arange(0., 4.5, .25),       ('#Delta R(l3,j)', 'Events')),
        'drminOS':      (lambda c : c.dr_minOS,       np.arange(0., 4.5, .25),       ('#Delta R(min(OS))', 'Events')),
        'dphil1met':      (lambda c : abs(c.dphi_l1met),       np.arange(0., 3.5, .25),       ('#Delta #phi(l1,met)', 'Events')),
        'dphil2met':      (lambda c : abs(c.dphi_l2met),       np.arange(0., 3.5, .25),       ('#Delta #phi(l2,met)', 'Events')),
        'dphil3met':      (lambda c : abs(c.dphi_l3met),       np.arange(0., 3.5, .25),       ('#Delta #phi(l3,met)', 'Events')),
        'dphij1met':      (lambda c : abs(c.dphi_j1met),       np.arange(0., 3.5, .25),       ('#Delta #phi(j1,met)', 'Events')),
        'dphij2met':      (lambda c : abs(c.dphi_j2met),       np.arange(0., 3.5, .25),       ('#Delta #phi(j2,met)', 'Events')),

        #Remainder
        'mtl1':          (lambda c : c.mtl1,      np.arange(0., 240., 5.),         ('m_T(l1) [GeV]', 'Events')),
        'mtl2':          (lambda c : c.mtl2,      np.arange(0., 240., 5.),         ('m_T(l2) [GeV]', 'Events')),
        'mtl3':          (lambda c : c.mtl3,      np.arange(0., 240., 5.),         ('m_T(l3) [GeV]', 'Events')),
        'drmaxossf':      (lambda c : c.dr_maxOSSF,       np.arange(0., 5.5, .25),       ('#Delta R(max(OSSF))', 'Events')),
        'mtnonossf':          (lambda c : c.mtNonZossf,      np.arange(0., 240., 5.),         ('m_{ll,Z} [GeV]', 'Events')),
        
    }

var_reco_4l = {
        'minMos':        (lambda c : c.minMos,   np.arange(0., 120., 12.),         ('min m(2l|OS) [GeV]', 'Events')),
        #'m4l':          (lambda c : c.M4l,      np.arange(0., 303., 3.),         ('M_{4l} [GeV]', 'Events')),
        'm4l':          (lambda c : c.M4l,      np.arange(150., 350., 20.),         ('m(4l) [GeV]', 'Events')),
        'met':          (lambda c : c.met,     np.arange(0., 155., 5.),         ('p_{T}^{miss} [GeV]', 'Events')),
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
        'MllZ1':       (lambda c : c.Mll_Z1,      np.arange(70., 112., 2.),         ('m_{ll}(Z_{1}) [GeV]', 'Events')), 
        'MllZ2':       (lambda c : c.Mll_Z2,      np.arange(70., 112., 2.),         ('m_{ll}(Z_{2}) [GeV]', 'Events')),
        # 'ptConeLeading':   (lambda c : c.pt_cone[0],      np.arange(0., 205., 5.),         ('P_{T}^{cone}(leading) [GeV]', 'Events'))
    }

var_gen_4l = {'minMos':        (lambda c : c.minMos,   np.arange(0., 120., 12.),         ('min m(2l|OS) [GeV]', 'Events')),
        'm4l':          (lambda c : c.M4l,      np.arange(0., 240., 5.),         ('m(4l) [GeV]', 'Events')),
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


#binning = {
#    'minMos'    : {'ConversionCR' : np.arange(0., 95., 5.), 'WZCR' : np.arange(0., 130., 10.), 'lowMassSRloose' : np.arange(0., 65., 5.), 'highMassSR' : np.arange(0., 210., 10.)},
#    'm3l'       : {'ConversionCR' : np.arange(70., 115., 5.), 'WZCR' : np.arange(85., 500., 15.), 'lowMassSRloose' : np.arange(0., 120., 5.), 'highMassSR' : np.arange(0., 415., 15.)},
#    'met'       : {'ConversionCR' : np.arange(0., 85., 5.), 'WZCR' : np.arange(50., 185., 15.), 'lowMassSRloose' : np.arange(0., 95., 5.), 'highMassSR' : np.arange(0., 415., 15.)},   
#    'mtOther'   : {'ConversionCR' : np.arange(0., 135., 15.), 'WZCR' : np.arange(0., 350., 15.), 'lowMassSRloose' : np.arange(0., 125., 5.), 'highMassSR' : np.arange(0., 350., 10.)},   
#    'l1pt'      : {'ConversionCR' : np.arange(0., 95., 5.), 'WZCR' : np.arange(0., 300., 15.), 'lowMassSRloose' : np.arange(10., 65., 5.), 'highMassSR' : np.arange(50., 315., 15.)},   
#    'l2pt'      : {'ConversionCR' : np.arange(10., 55., 5.), 'WZCR' : np.arange(0., 200., 10.), 'lowMassSRloose' : np.arange(10., 47., 2.), 'highMassSR' : np.arange(0., 210., 10.)},   
#    'l3pt'      : {'ConversionCR' : np.arange(10., 45., 5.), 'WZCR' : np.arange(0., 125., 5.), 'lowMassSRloose' : np.arange(10., 36., 1.), 'highMassSR' : np.arange(0., 155., 5.)},   
#    'j1pt'      : {'ConversionCR' : np.arange(0., 120., 15.), 'WZCR' : np.arange(0., 200., 15.), 'lowMassSRloose' : np.arange(0., 110., 10.), 'highMassSR' : np.arange(0., 160., 15.)},   
#    'j2pt'      : {'ConversionCR' : np.arange(0., 75., 15.), 'WZCR' : np.arange(0., 205., 15.), 'lowMassSRloose' : np.arange(0., 90., 10.), 'highMassSR' : np.arange(0., 90., 15.)},   
#    'NJet'      : {'ConversionCR' : np.arange(0., 5., 1.), 'WZCR' : np.arange(0., 5., 1.), 'lowMassSRloose' : np.arange(0., 6., 1.), 'highMassSR' : np.arange(0., 6., 1.)},   
#    'mt3'       : {'ConversionCR' : np.arange(70., 315., 15.), 'WZCR' : np.arange(150., 800., 15.), 'lowMassSRloose' : np.arange(30., 270., 15.), 'highMassSR' : np.arange(0., 415., 15.)},   
#    'LT'        : {'ConversionCR' : np.arange(0., 260., 15.), 'WZCR' : np.arange(50., 600., 15.), 'lowMassSRloose' : np.arange(0., 270., 15.), 'highMassSR' : np.arange(0., 915., 15.)},   
#    'HT'        : {'ConversionCR' : np.arange(0., 165., 15.), 'WZCR' : np.arange(0., 250., 15.), 'lowMassSRloose' : np.arange(0., 105., 15.), 'highMassSR' : np.arange(0., 200., 15.)},   
#    'mzossf'    : {'ConversionCR' : np.arange(0., 95., 5.), 'WZCR' : np.arange(70., 115., 5.), 'lowMassSRloose' : np.arange(70., 115., 5.), 'highMassSR' : np.arange(0., 250., 15.)},   
#    'maxMossf'  : {'ConversionCR' : np.arange(0., 100., 10.), 'WZCR' : np.arange(60., 300., 15.), 'lowMassSRloose' : np.arange(0., 75., 5.), 'highMassSR' : np.arange(0., 250., 15.)},   
#    'ml1l2'     : {'ConversionCR' : np.arange(0., 95., 5.), 'WZCR' : np.arange(70., 300., 15.), 'lowMassSRloose' : np.arange(0., 75., 5.), 'highMassSR' : np.arange(0., 250., 15.)},   
#    'ml1l3'     : {'ConversionCR' : np.arange(0., 95., 5.), 'WZCR' : np.arange(0., 250., 15.), 'lowMassSRloose' : np.arange(0., 75., 5.), 'highMassSR' : np.arange(0., 250., 15.)},   
#    'ml2l3'     : {'ConversionCR' : np.arange(0., 95., 5.), 'WZCR' : np.arange(0., 200., 15.), 'lowMassSRloose' : np.arange(0., 75., 5.), 'highMassSR' : np.arange(0., 250., 15.)},   
#}
binning = {
    'minMos'    : {'ConversionCR' : np.arange(0., 95., 5.), 'WZCR' : np.arange(0., 130., 10.), 'lowMassSRloose' : np.arange(0., 65., 5.), 'highMassSR' : np.arange(0., 220., 20.)},
    'm3l'       : {'ConversionCR' : np.arange(70., 115., 5.), 'WZCR' : np.arange(85., 500., 15.), 'lowMassSRloose' : np.arange(0., 120., 5.), 'highMassSR' : np.arange(50., 420., 30.)},
    'met'       : {'ConversionCR' : np.arange(0., 85., 5.), 'WZCR' : np.arange(50., 185., 15.), 'lowMassSRloose' : np.arange(0., 95., 5.), 'highMassSR' : np.arange(0., 220., 20.)},   
    'mtOther'   : {'ConversionCR' : np.arange(0., 135., 15.), 'WZCR' : np.arange(0., 350., 15.), 'lowMassSRloose' : np.arange(0., 125., 5.), 'highMassSR' : np.arange(0., 275., 25.)},   
    'l1pt'      : {'ConversionCR' : np.arange(0., 95., 5.), 'WZCR' : np.arange(0., 300., 15.), 'lowMassSRloose' : np.arange(10., 65., 5.), 'highMassSR' : np.arange(50., 215., 15.)},   
    'l2pt'      : {'ConversionCR' : np.arange(10., 55., 5.), 'WZCR' : np.arange(0., 200., 10.), 'lowMassSRloose' : np.arange(10., 47., 2.), 'highMassSR' : np.arange(0., 135., 15.)},   
    'l3pt'      : {'ConversionCR' : np.arange(10., 45., 5.), 'WZCR' : np.arange(0., 125., 5.), 'lowMassSRloose' : np.arange(10., 36., 1.), 'highMassSR' : np.arange(10., 90., 10.)},   
    'j1pt'      : {'ConversionCR' : np.arange(0., 120., 15.), 'WZCR' : np.arange(0., 200., 15.), 'lowMassSRloose' : np.arange(0., 110., 10.), 'highMassSR' : np.arange(0., 160., 15.)},   
    'j2pt'      : {'ConversionCR' : np.arange(0., 75., 15.), 'WZCR' : np.arange(0., 205., 15.), 'lowMassSRloose' : np.arange(0., 90., 10.), 'highMassSR' : np.arange(0., 90., 15.)},   
    'NJet'      : {'ConversionCR' : np.arange(0., 5., 1.), 'WZCR' : np.arange(0., 5., 1.), 'lowMassSRloose' : np.arange(0., 6., 1.), 'highMassSR' : np.arange(0., 6., 1.)},   
    'mt3'       : {'ConversionCR' : np.arange(70., 315., 15.), 'WZCR' : np.arange(150., 800., 15.), 'lowMassSRloose' : np.arange(30., 270., 15.), 'highMassSR' : np.arange(0., 415., 15.)},   
    'LT'        : {'ConversionCR' : np.arange(0., 260., 15.), 'WZCR' : np.arange(50., 600., 15.), 'lowMassSRloose' : np.arange(0., 270., 15.), 'highMassSR' : np.arange(0., 915., 15.)},   
    'HT'        : {'ConversionCR' : np.arange(0., 165., 15.), 'WZCR' : np.arange(0., 250., 15.), 'lowMassSRloose' : np.arange(0., 105., 15.), 'highMassSR' : np.arange(0., 200., 15.)},   
    'mzossf'    : {'ConversionCR' : np.arange(0., 95., 5.), 'WZCR' : np.arange(70., 115., 5.), 'lowMassSRloose' : np.arange(70., 115., 5.), 'highMassSR' : np.arange(0., 250., 15.)},   
    'maxMossf'  : {'ConversionCR' : np.arange(0., 100., 10.), 'WZCR' : np.arange(60., 300., 15.), 'lowMassSRloose' : np.arange(0., 75., 5.), 'highMassSR' : np.arange(0., 250., 15.)},   
    'ml1l2'     : {'ConversionCR' : np.arange(0., 95., 5.), 'WZCR' : np.arange(70., 300., 15.), 'lowMassSRloose' : np.arange(0., 75., 5.), 'highMassSR' : np.arange(0., 250., 15.)},   
    'ml1l3'     : {'ConversionCR' : np.arange(0., 95., 5.), 'WZCR' : np.arange(0., 250., 15.), 'lowMassSRloose' : np.arange(0., 75., 5.), 'highMassSR' : np.arange(0., 250., 15.)},   
    'ml2l3'     : {'ConversionCR' : np.arange(0., 95., 5.), 'WZCR' : np.arange(0., 200., 15.), 'lowMassSRloose' : np.arange(0., 75., 5.), 'highMassSR' : np.arange(0., 250., 15.)},   
}


def getBinning(v, region, original_bins):
    if v not in binning.keys() or region not in binning[v].keys():
        return original_bins
    else:
        return binning[v][region]
    
def getRelevantSuperCategories(original_names, region):
    region_dict = {
        'ZZCR' : ['Other'],
        'WZCR' : ['NoTau', 'SingleTau'],
        'ConversionCR' : ['NoTau', 'SingleTau'],
    }
    if region not in region_dict.keys():
        return original_names
    else:
        return [x for x in original_names if x in region_dict[region]]

var_noselection = {
        'rawNlight': (lambda c : c._nLight,      np.arange(0., 10., 1.),         ('N_{light, tuple}', 'Events')),
        'rawNl': (lambda c : c._nL,      np.arange(0., 10., 1.),         ('N_{l, tuple}', 'Events')),
}

from HNL.Tools.helpers import mergeTwoDictionaries
from HNL.Tools.outputTree import cleanName
var_to_rebin = ['lowestmass-e', 'lowmass-e', 'lowestmass-mu', 'lowmass-mu', 'mediummass250400-e', 'mediummass250400-mu', 'mediummass85100-e', 'mediummass85100-mu']
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
                        if k not in var_to_rebin:
                            var_of_choice[cleanName(k)] = (MVA_dict[include_mva][k][2],   np.arange(-1., 1.1, 0.1),         ('MVA score', 'Events'))
                        else:
                            #var_of_choice[cleanName(k)] = (MVA_dict[include_mva][k][2],   np.arange(-1., 1.1, 0.1),         ('MVA score', 'Events'))
                            var_of_choice[cleanName(k)] = (MVA_dict[include_mva][k][2],   'rebin-ewkino',         ('MVA score', 'Events'))
        
        return var_of_choice


signal_couplingsquared = {
        'tau' : {5 : 5e-4, 10 : 5e-4, 20:5e-4, 30:5e-4,  40:6e-4, 50:7e-4, 60:2e-3, 70:2e-2, 75:3e-2, 80:0.1, 85:1.,  100:0.2, 125:0.2, 150:0.2,  200:0.4, 250:0.5, 300:0.7, 350:0.9, 400:1.0, 450:1.0, 500:1.0, 600:1.0, 700:1.0, 800:1.0, 900:1.0, 1000:1.0 },
        'e' : {5 : 4e-6, 10 : 4e-6, 20:4e-6, 30:4e-6, 40:6e-6, 50:1e-5,  60:2e-5, 70:6e-5, 75:5e-4, 80:1e-3, 85:1e-3,  100:1e-3, 125:2e-3, 150:3e-3,  200:5e-3, 250:5e-3, 300:1e-2, 350:2e-2,  400:2e-2, 450:5e-2, 500:5e-2, 600:6e-2, 700:0.1, 800:0.2, 900:0.2, 1000:0.3, 1200:1., 1500:1.},
        'mu' : {5 : 2e-6, 10 : 2e-6, 20:2e-6, 30:2e-6, 40:2e-6, 50:3e-6,  60:6e-6, 70:5e-5, 75:1e-4, 80:4e-4, 85:7e-4,  100:8e-4, 125:1e-3, 150:2e-3,  200:4e-3, 250:5e-3, 300:8e-3, 350:1e-2,  400:2e-2, 450:2e-2, 500:3e-2, 600:4e-2, 700:7e-2, 800:0.1, 900:0.2, 1000:0.2, 1200:1., 1500:1.},
}


final_signal_regions = ['lowMassSR', 'highMassSR']

if __name__ == '__main__':
        print returnVariables(3, True, True)['mva']
