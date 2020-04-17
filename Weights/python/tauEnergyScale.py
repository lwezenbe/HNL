#
#Tau enery scale class using the tau POG tool
#

from TauPOG.TauIDSFs.TauIDSFTool import TauESTool
from TauPOG.TauIDSFs.TauIDSFTool import TauFESTool

YEARLIB = {2016 : '2016Legacy',
            2017: '2017ReReco',
            2018: '2018ReReco'}

class tauEnergyScale:
    
    def __init__(self, year, algorithm):
        self.testool = TauESTool(YEARLIB[year], algorithm)
        self.tfestool = TauESTool(YEARLIB[year])

    def applyES(tlv, dm, genmatch):
        if genmatch == 1 or genmatch == 3:
            tlv *= self.tfestool.getFES(tlv.Eta(), dm, genmatch)
        else:
            tlv *= self.tfestool.getTES(tlv.Pt(), dm, genmatch)
        return tlv
