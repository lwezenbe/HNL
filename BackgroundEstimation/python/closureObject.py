from HNL.Tools.histogram import HistogramCollection

class ClosureObject(HistogramCollection):

    def __init__(self, name, var, var_tex, path, bins=None, subdirs=None):    
        sub_names = ['observed', 'sideband']  
        super(ClosureObject, self).__init__(name, sub_names, var, var_tex, path, bins, subdirs)

    def fillObserved(self, chain, weight, index = None):
        self.fill('observed', chain, weight, index = index)

    def fillSideband(self, chain, weight, fake_factor, index = None):
        self.fill('sideband', chain, weight*fake_factor, index = index)

    def fillClosure(self, chain, weight, fake_factor, index = None):
        if fake_factor == 1.:
            self.fillObserved(chain, weight, index = index)
        else:
            self.fillSideband(chain, weight, fake_factor, index = index)
 
    def getObserved(self):
        return self.getHistogram('observed')

    def getSideband(self):
        return self.getHistogram('sideband')