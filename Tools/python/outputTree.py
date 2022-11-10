from ROOT import TFile

def cleanName(in_name):
    return "".join(i for i in in_name if i not in "\/:*?<>|&- ")

from HNL.Tools.helpers import isValidRootFile
class OutputTree(object):
    
    def __init__(self, name, path, branches = None, branches_already_defined = False):
        self.name = name
        self.path = path

        from ROOT import TTree, gDirectory
        if branches is None:
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
            self.new_vars = makeBranches(self.tree, branches, branches_already_defined)

    def getEntries(self, condition=""):
        return self.tree.GetEntries(condition)
 
    def setTreeVariable(self, var_name, new_value):
        var_name = cleanName(var_name)
        if self.new_vars is not None:
            setattr(self.new_vars, var_name, new_value)
        else:
            raise RuntimeError("Tree in reading mode, you can not change input vars")

    def getTreeVariable(self, var_name, entry = None):
        if entry is not None:
            self.tree.GetEntry(entry)
        attr = getattr(self.tree, var_name)
        return attr

    def fill(self):
        if self.new_vars is not None:
            self.tree.Fill()
        else:
            raise RuntimeError("Tree in reading mode, you can not change input vars")

    def write(self, is_test = None, append = False):
        append_string = 'recreate'
        if append and isValidRootFile(self.path): append_string = 'update'
        if self.new_vars is not None:
            from HNL.Tools.helpers import makeDirIfNeeded
            makeDirIfNeeded(self.path)
            out_file = TFile(self.path, append_string)
            self.tree.Write()
            out_file.Write()
            out_file.Close()
            if is_test is not None:
                from HNL.Tools.helpers import copyFileToTestingArea
                copyFileToTestingArea(self.path, is_test)
        else:
            raise RuntimeError("Tree in reading mode, you can not change input vars")

    def getHistFromTree(self, vname, hname, bins, condition = None, weight = None):
        if weight is None: weight = 'weight'

        dim = 1
        if '-' in vname:
            vname = ":".join(reversed(vname.split('-')))
            dim = len(vname.split(':'))

        hname = ''.join([x for x in hname if x not in ['(', ')']])

        import ROOT
        ROOT.gROOT.SetBatch(True)
   
        if dim == 1: 
            htmp = ROOT.TH1D(hname, hname, len(bins)-1, bins)
        elif dim == 2:
            htmp = ROOT.TH2D(hname, hname, len(bins[0])-1, bins[0], len(bins[1])-1, bins[1])
        elif dim == 3:
            htmp = ROOT.TH3D(hname, hname, len(bins[0])-1, bins[0], len(bins[1])-1, bins[1], len(bins[2])-1, bins[2])
        else:
            raise RuntimeError("Currently no support for 3 dimensional plots")

        final_weight = ''
        if 'Weight' in vname:
            if condition is not None:
                final_weight = '('+condition+')*lumiWeight'
            else:
                final_weight = 'lumiWeight'
        else:
            if condition is not None:
                final_weight = '('+condition+')*'+weight
            else:
                final_weight = weight
        self.tree.Draw(vname+">>"+hname, final_weight)
        if not htmp: return None
        ROOT.gDirectory.cd('PyROOT:/')
        res = htmp.Clone()
        #Add overflow and underflow bins
        if dim == 1:
            from HNL.Tools.helpers import add1Doverflow
            res = add1Doverflow(res)
        if dim == 2:
            from HNL.Tools.helpers import add2Doverflow
            res = add2Doverflow(res)
        if dim == 3:
            from HNL.Tools.helpers import add3Doverflow
            res = add3Doverflow(res)
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

    def setBins(self, bins):
        self.bins = bins

    def getNumerator(self, vname, hname, condition = None, passed_name = 'passed'):
        if condition is None: 
            condition = passed_name
        else:   
            condition += '&&'+passed_name                     
        return super(EfficiencyTree, self).getHistFromTree(vname, hname, self.bins, condition) 
    
    def getDenominator(self, vname, hname, condition = None):
        return super(EfficiencyTree, self).getHistFromTree(vname, hname, self.bins, condition) 
   
    def getEfficiency(self, vname, hname, condition = None, passed_name = 'passed'):
        num = self.getNumerator(vname, hname, condition, passed_name = passed_name).Clone('tmp_'+hname)
        denom = self.getDenominator(vname, hname, condition).Clone('tmp_denom_'+hname)
        from HNL.Tools.efficiency import Efficiency
        return Efficiency(hname, vname, vname, None, efficiency_num = num, efficiency_denom = denom)
