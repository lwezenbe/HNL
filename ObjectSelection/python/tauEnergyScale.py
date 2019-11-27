from HNL.ObjectSelection.tauSelector import default_algo

#
#Tau enery scale class
#


class TauEnergyScale:

    TAU_ENERGY_SCALES_MVA2017V2 = {('2016_ReReco', 0) : (-0.005, 0.012),
                         ('2016_ReReco', 1) : (0.011, 0.012),
                         ('2016_ReReco', 2) : (0.011, 0.012),
                         ('2016_ReReco', 10) : (0.006, 0.012),

                         ('2016_Legacy', 0) : (-0.006, 0.010),
                         ('2016_Legacy', 1) : (-0.005, 0.009),
                         ('2016_Legacy', 2) : (-0.005, 0.009),
                         ('2016_Legacy', 10) : (0.006, 0.012),

                         ('2017_ReReco', 0) : (-0.006, 0.010),
                         ('2017_ReReco', 1) : (-0.005, 0.009),
                         ('2017_ReReco', 2) : (-0.005, 0.009),
                         ('2017_ReReco', 10) : (0.006, 0.012),

                         ('2018_', 0) : (-0.013, 0.011),
                         ('2018_', 1) : (-0.005, 0.009),
                         ('2018_', 2) : (-0.005, 0.009),
                         ('2018_', 10) : (-0.012, 0.008)}

    def __init__(self, chain, algo = default_algo, reco = ''):
        self.reco = reco
        self.algo = algo
        self.year = str(chain.year)
        if not self.reco:
            if self.year == '2016':
                self.reco = 'Legacy'
            elif self.year == '2018':
                pass
            else:
                self.reco = 'ReReco'
        self.era = self.year + '_' + self.reco

    def getES(self, dm):
        if self.algo == 'MVA2017v2': tes = self.TAU_ENERGY_SCALES_MVA2017V2
        else:
            print 'invalid algo in tauEnergyScale'
            return 1.
        es = tes.get((self.era, dm))
        return 1. + es[0]
