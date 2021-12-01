#
# Create new branches (as ['var1/F','var2/I',...]) on the given tree
# Returns struct with the new variables
#
import ROOT

cType = {
    'b': 'UChar_t',
    'S': 'Short_t',
    's': 'UShort_t',
    'I': 'Int_t',
    'i': 'UInt_t',
    'F': 'Float_t',
    'D': 'Double_t',
    'L': 'Long64_t',
    'l': 'ULong64_t',
    'O': 'Bool_t',
}
#
# Function to add new branches to a tree
# the ProcessLine makes a new structure newVars that contains a sort of list of all branches as objects, as far as I understand
#
def makeBranches(tree, branches, already_defined=False):
    branches = [tuple(branch.split('/')) for branch in branches] 
    if not already_defined: ROOT.gROOT.ProcessLine('struct newVars {' + ';'.join([cType[t] + ' ' + name for name, t in branches]) + ';};')
    
    from ROOT import newVars
    newVars = newVars()
    
    for name, t in sorted(branches):
        tree.Branch(name.split('[')[0], ROOT.AddressOf(newVars, name.split('[')[0]), name+ '/' + t)
    return newVars
