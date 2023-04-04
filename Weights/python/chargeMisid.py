class ChargeMisidWeight:

    sf_dict = {
        '2016pre' : {'nominal' : 0.921, 'up' : 0.921*1.15, 'down': 0.921*0.85},
        '2016post' : {'nominal' : 0.921, 'up' : 0.921*1.15, 'down': 0.921*0.85},
        '2017' : {'nominal' : 1.460, 'up' : 1.460*1.15, 'down': 1.460*0.85},
        '2018' : {'nominal' : 1.451, 'up' : 1.451*1.15, 'down': 1.451*0.85}
    }

    def __init__(self, chain):
            self.chain = chain

    def getChargeMisidWeight(self, syst = 'nominal', year = None):
        if year == None:
            year = self.chain.year

        if not self.chain.is_charge_flip_event:
            return 1.
        else:
            return self.sf_dict[year][syst]
            
