#
#Tau enery scale class using the tau POG tool
#

from TauPOG.TauIDSFs.TauIDSFTool import TauESTool
from TauPOG.TauIDSFs.TauIDSFTool import TauFESTool

YEARLIB = {2016 : '2016Legacy',
            2017: '2017ReReco',
            2018: '2018ReReco'}

ALGOLIB = {'deeptauVSjets' : 'DeepTau2017v2p1VSjet',
            'MVA2017v2'  :  'MVAoldDM2017v2' }

class TauEnergyScale:
    
    def __init__(self, year, algorithm):
        self.testool = TauESTool(YEARLIB[year], ALGOLIB[algorithm])
        self.tfestool = TauESTool(YEARLIB[year])

    #tlv is four vector to correct
    def applyES(self, tlv, dm, genmatch):
        if genmatch == 1 or genmatch == 3:
            if dm == 0 or dm == 1:
                tlv *= self.tfestool.getFES(tlv.Eta(), dm, genmatch)
            else:
                pass
        else:
            tlv *= self.tfestool.getTES(tlv.Pt(), dm, genmatch)
        return tlv

    #tlv is four vector to correct
    def readES(self, tlv, dm, genmatch):
        if genmatch == 1 or genmatch == 3:
            if dm == 0 or dm == 1:
                return self.tfestool.getFES(tlv.Eta(), dm, genmatch)
            else:
                return 1.
        else:
            return self.tfestool.getTES(tlv.Pt(), dm, genmatch)

if __name__ == "__main__":
    #TODO: test needs to be finished
    from HNL.Tools.logger import getLogger, closeLogger
    log = getLogger('INFO')

    from ROOT import TLorentzVector
    test_vec = ROOT.TLorentzVector()
    test_vec.SetPtEtaPhiE(1., 1., 1., 1.)

    tes = TauEnergyScale(2016, 'deeptauVSjets')
    tes = TauEnergyScale(2017, 'deeptauVSjets')
    tes = TauEnergyScale(2018, 'deeptauVSjets')

    closeLogger(log)