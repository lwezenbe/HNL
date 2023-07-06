import ROOT
import numpy as np

ROOT.gROOT.SetBatch(True)

out_file = ROOT.TFile('test.root', 'recreate')

tree = ROOT.TTree('tree', 'tree')

print type(tree)

new_branches = []
new_branches.extend(['x/F', 'cat/I', 'w/F'])

from HNL.Tools.makeBranches import makeBranches
new_vars = makeBranches(tree, new_branches)

for a in [0.5, 1.5, 1.5, 1.5, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 3.5, 3.5, 4.5]:
    new_vars.x = a
    if a < 3: new_vars.cat = 1 
    else: new_vars.cat = 2
    new_vars.w = np.sqrt(a)
    tree.Fill()

branches = tree.GetListOfBranches()
for b in branches:
    print b.GetName()

print branches[0].GetName()
tree.Draw(branches[0].GetName()+'>>h')
print ROOT.gDirectory.Get('h').GetMean(), '+-', ROOT.gDirectory.Get('h').GetMeanError()

test_branch = tree.FindBranch('x').GetFirstEntry()
print test_branch

tree.Write()

out_file.Write()
out_file.Close()


infile = ROOT.TFile('test.root', 'read')
newtree = infile.Get('tree')
myh = ROOT.TH1D("myh", "myh", 4, np.array([0., 1., 2., 4., 5.]))
canv = ROOT.TCanvas('soiejf1', 'soiejf1')
newtree.Draw("x>>myh", '(cat==1)*w')
myh.Draw("Hist")
canv.SaveAs('test.png')