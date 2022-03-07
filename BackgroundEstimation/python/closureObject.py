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

from HNL.Tools.outputTree import OutputTree
class ClosureTree(OutputTree):

    def __init__(self, name, path, branches = None):
        if branches is not None:
            branches.extend(['is_sideband/O', 'weight/F', 'fake_factor/F', 'original_weight/F'])
        super(ClosureTree, self).__init__(name, path, branches)

    def fill(self, weight, fake_factor):
        self.setTreeVariable('is_sideband', fake_factor != 1.) 
        self.setTreeVariable('weight', fake_factor*weight) 
        self.setTreeVariable('fake_factor', fake_factor) 
        self.setTreeVariable('original_weight', weight)
        super(ClosureTree, self).fill() 
   
    def getObserved(self, vname, hname, bins, condition=None):
        new_condition = '!is_sideband' if condition is None else condition + '&&!is_sideband'
        return super(ClosureTree, self).getHistFromTree(vname, hname, bins, new_condition)

    def getSideband(self, vname, hname, bins, condition=None):
        new_condition = 'is_sideband' if condition is None else condition + '&&is_sideband'
        return super(ClosureTree, self).getHistFromTree(vname, hname, bins, new_condition)
