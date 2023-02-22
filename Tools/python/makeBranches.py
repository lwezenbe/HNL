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
    'O': 'Bool_t'
}

forbidden_characters = ['-']
def removeAllForbiddenCharacters(original_name):
    return ''.join([x for x in original_name if x not in forbidden_characters])

def prepareBranches(branches):
    branches = [tuple(branch.split('/')) for branch in branches] 
    for i, (name, t) in enumerate(branches):
        for fc in forbidden_characters:
            if fc in name:  print "Forbidden character in name of new branch {0}. Changing name to {1}".format(name, removeAllForbiddenCharacters(name))
            branches[i] = (removeAllForbiddenCharacters(name), t)
            break
    return branches

def createStruct(branches):
    if not hasattr(ROOT, 'newVars'): ROOT.gROOT.ProcessLine('struct newVars {' + ';'.join([cType[t] + ' ' + name for name, t in branches]) + ';};')

#
# Function to add new branches to a tree
# the ProcessLine makes a new structure newVars that contains a sort of list of all branches as objects, as far as I understand
#
def makeBranches(tree, branches, already_defined=False):
    branches = prepareBranches(branches)
    if not hasattr(ROOT, 'newVars'): createStruct(branches)
    
    from ROOT import newVars
    newVars = newVars()
    
    for name, t in sorted(branches):
        tree.Branch(name.split('[')[0], ROOT.AddressOf(newVars, name.split('[')[0]), name+ '/' + t)
    return newVars
