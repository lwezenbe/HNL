#
#Tau enery scale class using the tau POG tool
#

from TauPOG.TauIDSFs.TauIDSFTool import TauESTool
from TauPOG.TauIDSFs.TauIDSFTool import TauFESTool

YEARLIB_TES = {'prelegacy2016' : '2016Legacy',
            'prelegacy2017': '2017ReReco',
            'prelegacy2018': '2018ReReco',
            
            'UL2016pre' : 'UL2016_preVFP',
            'UL2016post' : 'UL2016_postVFP',
            'UL2017': 'UL2017',
            'UL2018': 'UL2018'
        }

YEARLIB_FES = {'prelegacy2016' : '2016Legacy',
            'prelegacy2017': '2017ReReco',
            'prelegacy2018': '2018ReReco',
            
            'UL2016pre' : '2016Legacy',
            'UL2016post' : '2016Legacy',
            'UL2017': '2017ReReco',
            'UL2018': '2017ReReco'
        }

ALGOLIB = {'HNL' : 'DeepTau2017v2p1VSjet',
            'HNLtauTest' : 'DeepTau2017v2p1VSjet',
            'ewkino'  :  'MVAoldDM2017v2' }

UNC_LIB = {
    'nominal' : None,
    'tauEnergyScale-e-dm0Up' : 'Up',
    'tauEnergyScale-e-dm1Up' : 'Up',
    'tauEnergyScale-e-dm0Down' : 'Down',
    'tauEnergyScale-e-dm1Down' : 'Down',
    'tauEnergyScale-tau-dm1Up' : 'Up',
    'tauEnergyScale-tau-dm1Down' : 'Down',
    'tauEnergyScale-tau-dm0Up' : 'Up',
    'tauEnergyScale-tau-dm0Down' : 'Down',
    'tauEnergyScale-tau-dm10Up' : 'Up',
    'tauEnergyScale-tau-dm10Down' : 'Down',
    'tauEnergyScale-tau-dm11Up' : 'Up',
    'tauEnergyScale-tau-dm11Down' : 'Down',
}

class TauEnergyScale:
    
    def __init__(self, era, year, algorithm):
        if algorithm != 'prompt':
            self.testool = TauESTool(YEARLIB_TES[era+year], ALGOLIB[algorithm])
            self.tfestool = TauFESTool(YEARLIB_FES[era+year])
        else:
            self.testool = None
            self.tfestool = None

    #tlv is four vector to correct
    def applyES(self, tlv, dm, genmatch):
        if self.testool is None or self.tfestool is None:
            return 1.
        if genmatch == 1 or genmatch == 3:
            if dm == 0 or dm == 1:
                tlv *= self.tfestool.getFES(tlv.Eta(), dm, genmatch)
            else:
                pass
        else:
            tlv *= self.testool.getTES(tlv.Pt(), dm, genmatch)
        return tlv

    #tlv is four vector to correct
    def readES(self, tlv, dm, genmatch, syst = 'nominal'):
        if self.testool is None or self.tfestool is None:
            return 1.
        if genmatch == 1 or genmatch == 3:
            if 'tauEnergyScale-e' in syst:
                if dm == 0 and 'dm0' in syst:
                    return self.tfestool.getFES(tlv.Eta(), dm, genmatch, UNC_LIB[str(syst)])
                elif dm == 1 and 'dm1' in syst:
                    return self.tfestool.getFES(tlv.Eta(), dm, genmatch, UNC_LIB[str(syst)])
                else:
                    return self.tfestool.getFES(tlv.Eta(), dm, genmatch, UNC_LIB['nominal'])
            else:
                return self.tfestool.getFES(tlv.Eta(), dm, genmatch, UNC_LIB['nominal'])
                
        elif genmatch == 5:
            if 'tauEnergyScale-tau' in syst:
                if dm == 0 and 'dm0' in syst:
                    return self.testool.getTES(tlv.Pt(), dm, genmatch, UNC_LIB[str(syst)])
                elif dm == 1 and 'dm1' in syst:
                    return self.testool.getTES(tlv.Pt(), dm, genmatch, UNC_LIB[str(syst)])
                elif dm == 10 and 'dm10' in syst:
                    return self.testool.getTES(tlv.Pt(), dm, genmatch, UNC_LIB[str(syst)])
                elif dm == 11 and 'dm11' in syst:
                    return self.testool.getTES(tlv.Pt(), dm, genmatch, UNC_LIB[str(syst)])
                else:
                    return self.testool.getTES(tlv.Pt(), dm, genmatch, UNC_LIB['nominal'])
            else:
                return self.testool.getTES(tlv.Pt(), dm, genmatch, UNC_LIB['nominal'])
        else:
            return 1.
    

if __name__ == "__main__":
    #TODO: test needs to be finished
    from HNL.Tools.logger import getLogger, closeLogger
    import ROOT
    log = getLogger('INFO')

    from ROOT import TLorentzVector
    test_vec = ROOT.TLorentzVector()
    test_vec.SetPtEtaPhiE(1., 1., 1., 1.)

    tes = TauEnergyScale('UL', '2016pre', 'HNL')
    tes = TauEnergyScale('UL', '2016post', 'HNL')
    tes = TauEnergyScale('UL', '2017', 'HNL')
    tes = TauEnergyScale('UL', '2018', 'HNL')

    closeLogger(log)
