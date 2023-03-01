class ChargeMisidWeight:

    sf_dict = {
        '2016pre' : 0.921,
        '2016post' : 0.921,
        '2017' : 1.460,
        '2018' : 1.451
    }

    def __init__(self, chain):
            self.chain = chain

    def getChargeMisidWeight(self, syst = 'nominal', year = None):
        if year = None:
            year = self.chain.year

        if not self.chain.isChargeFlipEvent:
            return 1.
        else:
            if syst == 'nominal':
                return self.sf_dict[year]
            
