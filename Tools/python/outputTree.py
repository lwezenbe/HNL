from ROOT import TFile
class OutputTree(object):
    
    def __init__(self, name, path, branches = None):
        self.name = name
        self.path = path

        from ROOT import TTree, gDirectory
        if branches is None:
            from HNL.Tools.helpers import isValidRootFile
            if not isValidRootFile(self.path):
                raise RuntimeError("No valid root file at path: {0} \n Please specify branches to create a new tree".format(self.path))
            
            from HNL.Tools.helpers import getObjFromFile
            self.tree = getObjFromFile(self.path, self.name)
                
            if self.tree is None:
                raise RuntimeError("No valid tree with name {0} in root file at {1}".format(self.name, self.path))         
            self.new_vars = None
        else:
            self.tree = TTree(name, name)

            from HNL.Tools.makeBranches import makeBranches
            self.new_vars = makeBranches(self.tree, branches)
    
    def setTreeVariable(self, var_name, new_value):
        if self.new_vars is not None:
            setattr(self.new_vars, var_name, new_value)
        else:
            raise RuntimeError("Tree in reading mode, you can not change input vars")


    def fill(self):
        if self.new_vars is not None:
            self.tree.Fill()
        else:
            raise RuntimeError("Tree in reading mode, you can not change input vars")

    def write(self, is_test = None):
        if self.new_vars is not None:
            from HNL.Tools.helpers import makeDirIfNeeded
            makeDirIfNeeded(self.path)
            out_file = TFile(self.path, 'recreate')
            self.tree.Write()
            out_file.Write()
            out_file.Close()
            if is_test is not None:
                from HNL.Tools.helpers import copyFileToTestingArea
                copyFileToTestingArea(self.path, is_test)
        else:
            raise RuntimeError("Tree in reading mode, you can not change input vars")

    def getHistFromTree(self, vname, hname, bins, condition):
        dim = 1
        if '-' in vname:
            vname = ":".join(reversed(vname.split('-')))
            dim = len(vname.split(':'))

        import ROOT
        ROOT.gROOT.SetBatch(True)
   
        if dim == 1: 
            htmp = ROOT.TH1D(hname, hname, len(bins)-1, bins)
        elif dim == 2:
            htmp = ROOT.TH2D(hname, hname, len(bins[0])-1, bins[0], len(bins[1])-1, bins[1])
        else:
            raise RuntimeError("Currently no support for 3 dimensional plots")

        if 'Weight' in vname: 
            self.tree.Draw(vname+">>"+hname, '('+condition+')*lumiWeight')
        else:
            self.tree.Draw(vname+">>"+hname, '('+condition+')*weight')
        if not htmp: return None
        ROOT.gDirectory.cd('PyROOT:/')
        res = htmp.Clone()
        #Add overflow and underflow bins
        if dim == 1:
            overflow=ROOT.TH1D(hname+'overflow', hname+'overflow', len(bins)-1, bins)
            overflow.SetBinContent(1, htmp.GetBinContent(0))
            overflow.SetBinContent(len(bins)-1, htmp.GetBinContent(len(bins)))
            overflow.SetBinError(1, htmp.GetBinError(0))
            overflow.SetBinError(len(bins)-1, htmp.GetBinError(len(bins)))
            res.Add(overflow)
        return res 

    def closeTree(self):
        self.infile.Close() 

class EfficiencyTree(OutputTree):
    
    def __init__(self, name, path, branches = None):
        if branches is not None: branches.extend(['passed/O'])
        super(EfficiencyTree, self).__init__(name, path, branches)

    def fill(self, passed):
        self.setTreeVariable('passed', passed)
        super(EfficiencyTree, self).fill()

    def getNumerator(self, vname, hname, bins, condition):
        return super(EfficiencyTree, self).getHistFromTree(vname, hname, bins, condition+'&&passed') 
    
    def getDenominator(self, vname, hname, bins, condition):
        return super(EfficiencyTree, self).getHistFromTree(vname, hname, bins, condition) 
   
    def getEfficiency(self, vname, hname, bins, condition, inPercent = False):
        eff = self.getNumerator(vname, hname, bins, condition).Clone('tmp_'+self.name)
        eff.Divide(eff, self.getDenominator(vname, hname, bins, condition), 1., 1., "B")
        if inPercent: eff.Scale(100.)
        return eff
