from HNL.Samples.sampleManager import SampleManager
sm = SampleManager('UL', '2018', 'noskim', 'Skimmer/skimlist_UL2018')
sample = sm.getSample('HNL-taulep-m10-Vsq1em3-displaced')
tree = sample.initTree()
nentries = tree.GetEntries()

from HNL.Tools.helpers import progress

tot_sum = 0.
for entry in xrange(nentries):
    tree.GetEntry(entry)
    progress(entry, nentries)
    tot_sum += tree._ctauHN

print tot_sum / nentries
